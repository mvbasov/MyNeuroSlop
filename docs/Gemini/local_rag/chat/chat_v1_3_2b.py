import os
import re
import sys
import time
import logging
import requests
import argparse
from qdrant_client import QdrantClient

# Keep version track inside the script
VERSION = "1.3.2"

# Setup basic client logging (suppress verbose messages from third-party libraries)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

# Environment and Network Settings
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "nomic-embed-text")
LLM_MODEL = os.environ.get("LLM_MODEL", "qwen2.5:3b")  # Optimized for 8GB RAM / 4 CPUs
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "rag_documents")

# Intelligent workspace mapping inside container vs host
DEFAULT_DATA_DIR = os.environ.get("DATA_DIR", "/data" if os.path.exists("/data") else "./data")

# Global session configurations
session_config = {
    "limit": 3,              # Default number of chunks to retrieve
    "expand_chars": 1000,    # Default local file context expansion limit
    "data_dir": DEFAULT_DATA_DIR
}

try:
    from flask import Flask, request, jsonify, render_template_string
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False

# Initialize Qdrant Client safely
try:
    qdrant_client = QdrantClient(url=QDRANT_URL)
    # Check if collection exists
    collections = qdrant_client.get_collections().collections
    exists = any(c.name == COLLECTION_NAME for c in collections)
    if not exists:
        logger.warning(f"Collection '{COLLECTION_NAME}' was not found in Qdrant database. Search queries will return empty results.")
except Exception as e:
    logger.error(f"Could not connect to Qdrant at {QDRANT_URL}: {e}")
    qdrant_client = None


# ==========================================
# ROBUST LOCAL CONTEXT SLIDING (THE FIX)
# ==========================================

def get_local_context(file_path, db_text, expand_chars=1000):
    """
    Intelligently locates the exact location of a database text chunk inside 
    the physical file on disk, handling virtual dividers, hyphenated anchors, 
    and structured bookmark payloads cleanly.
    """
    if not file_path:
        return db_text

    # 1. Clean path prefixes and isolate URL anchors
    clean_path = file_path.replace("file://", "")
    anchor = None
    if "#" in clean_path:
        clean_path, anchor = clean_path.split("#", 1)

    # Standardize HTML pelican paths back to raw Markdown source
    if "html/" in clean_path:
        clean_path = clean_path.replace("html/", "").replace(".html", ".md")

    data_dir = session_config.get("data_dir", DEFAULT_DATA_DIR)
    
    # Handle absolute paths mapped from outer volumes
    if os.path.isabs(clean_path):
        if "git/OMNotes/" in clean_path:
            clean_path = clean_path.split("git/OMNotes/")[-1]
        else:
            clean_path = os.path.basename(clean_path)

    clean_path = clean_path.lstrip("/")
    full_path = os.path.join(data_dir, clean_path)

    # Case-insensitive recursive search if the file is moved or path is slightly off
    if not os.path.exists(full_path):
        filename = os.path.basename(clean_path)
        found = False
        for root, dirs, files in os.walk(data_dir):
            for f in files:
                if f.lower() == filename.lower():
                    full_path = os.path.join(root, f)
                    found = True
                    break
            if found:
                break

    # If file cannot be found on host, gracefully fall back to the original DB vector chunk
    if not os.path.exists(full_path):
        return f"[Original chunk] (File not found on host: {clean_path})\n\n{db_text}"

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()

        start_idx = -1

        # Strategy A: Resolve hyphenated Anchor Timestamp
        if anchor:
            # Try matching direct anchor string
            start_idx = content.find(anchor)
            
            # Reconstruct 'YYYY-MM-DD-HHMMSS' anchor to raw file format 'YYYY-MM-DD HH:MM:SS'
            if start_idx == -1:
                m = re.match(r"(\d{4}-\d{2}-\d{2})-(\d{2})(\d{2})(\d{2})", anchor)
                if m:
                    reconstructed = f"{m.group(1)} {m.group(2)}:{m.group(3)}:{m.group(4)}"
                    start_idx = content.find(reconstructed)
                else:
                    # Reconstruct simple date 'YYYY-MM-DD'
                    date_m = re.match(r"(\d{4}-\d{2}-\d{2})", anchor)
                    if date_m:
                        start_idx = content.find(date_m.group(1))

        # Strategy B: Bookmark Meta-Field Extraction (Highly Robust for JSON Files)
        if start_idx == -1:
            # Extract URL if present inside the DB text block
            url_match = re.search(r"URL:\s*(https?://\S+)", db_text)
            if url_match:
                start_idx = content.find(url_match.group(1).strip())

            # Extract Title if URL search fails
            if start_idx == -1:
                title_match = re.search(r"Title:\s*(.+)", db_text)
                if title_match:
                    start_idx = content.find(title_match.group(1).strip())

        # Strategy C: Longest Distinct Line Search
        if start_idx == -1:
            # Filter and clean lines of DB text, searching for the longest unique block
            lines = [l.strip() for l in db_text.split("\n") if len(l.strip()) > 12]
            for line in sorted(lines, key=len, reverse=True):
                clean_line = re.sub(r"^[-\s*#>\d.]+", "", line).strip()  # Strip list formatting symbols
                if len(clean_line) > 10:
                    start_idx = content.find(clean_line)
                    if start_idx != -1:
                        break

        # Strategy D: Raw Prefix Match Fallback
        if start_idx == -1:
            prefix = db_text[:40].strip()
            if len(prefix) > 8:
                start_idx = content.find(prefix)

        # Strategy E: First Line Match
        if start_idx == -1:
            lines = [l.strip() for l in db_text.split("\n") if l.strip()]
            if lines:
                start_idx = content.find(lines[0])

        # CRITICAL PROTECTION FIX:
        # If all search methods fail, do NOT set start_idx = 0.
        # Defaulting to 0 reads from the beginning, causing duplicate header pollution.
        # Instead, return the original DB text directly.
        if start_idx == -1:
            logger.warning(f"Could not locate matching index context for chunk inside {clean_path}. Falling back to DB text.")
            return db_text

        # 2. Extract context slice (symmetric expansion)
        # We slide slightly backwards (e.g. 150 chars) to fetch headings or preceding thoughts,
        # and expand up to expand_chars forward.
        slice_start = max(0, start_idx - 150)
        slice_end = min(len(content), start_idx + expand_chars)

        # Align slice_start to the beginning of a physical line for clean aesthetics
        if slice_start > 0:
            newline_before = content.rfind("\n", 0, start_idx)
            if newline_before != -1 and newline_before >= slice_start - 200:
                slice_start = newline_before + 1

        # Align slice_end to the end of a physical line
        if slice_end < len(content):
            newline_after = content.find("\n", slice_end, slice_end + 200)
            if newline_after != -1:
                slice_end = newline_after

        expanded_text = content[slice_start:slice_end]
        added_chars = len(expanded_text) - len(db_text)
        logger.info(f"[{clean_path}] Found match at char {start_idx}. Expanded context by +{added_chars} chars.")
        
        return expanded_text

    except Exception as e:
        logger.error(f"Error reading file {full_path} on host: {e}")
        return db_text


# ==========================================
# RAG PIPELINE OPERATIONS
# ==========================================

def get_embeddings(text):
    """Fetches text embeddings from Ollama server."""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": EMBED_MODEL, "prompt": text},
            timeout=10
        )
        response.raise_for_status()
        return response.json()["embedding"]
    except Exception as e:
        logger.error(f"Error generating embeddings via Ollama ({EMBED_MODEL}): {e}")
        return None


def search_qdrant(query_text, limit=None):
    """Queries Qdrant for matching text chunks."""
    if not qdrant_client:
        return []
    
    query_vector = get_embeddings(query_text)
    if not query_vector:
        return []

    search_limit = limit if limit is not None else session_config["limit"]
    
    try:
        results = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=search_limit
        )
        return results
    except Exception as e:
        logger.error(f"Failed to query Qdrant collection: {e}")
        return []


def query_llm(system_prompt, user_query, context):
    """Sends structured context prompt to Ollama LLM."""
    # Strict prompt architecture optimized for low resource sub-3B models
    formatted_prompt = f"""<system>
{system_prompt}
</system>

<context>
{context}
</context>

<question>
{user_query}
</question>

Instruction: Rely ONLY on facts from the context. Answer in the language of the question."""

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": LLM_MODEL,
                "prompt": formatted_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,  # Low temperature to keep answers highly grounded
                    "num_ctx": 4096
                }
            },
            timeout=45
        )
        response.raise_for_status()
        return response.json().get("response", "")
    except Exception as e:
        logger.error(f"Error calling local LLM ({LLM_MODEL}): {e}")
        return f"Error: Failed to fetch response from local LLM. Check if Ollama service is running. Details: {e}"


# ==========================================
# INTERACTIVE CLI CONSOLE MODE
# ==========================================

def interactive_cli():
    """Runs interactive command-line interface."""
    print("=" * 60)
    print(f"--- RAG CLI Chat Console (v{VERSION}) ---")
    print(f"Embedding Engine: {EMBED_MODEL} | LLM Engine: {LLM_MODEL}")
    print(f"Data Directory: {session_config['data_dir']}")
    print("Type '/limit <num>' to adjust search depth. Type '/datadir <path>' to change path mapping.")
    print("Type 'exit' or 'quit' to close.")
    print("=" * 60)

    # Standard system instructions designed to prevent hallucinations in small models
    system_instruction = (
        "You are a helpful, precise RAG assistant. Answer the question using ONLY the facts "
        "provided in the context segments. Do not assume or hallucinate details. If you cannot find "
        "the answer in the context, explicitly say that you do not have that information."
    )

    while True:
        try:
            query = input("\nUser > ").strip()
            if not query:
                continue
            
            if query.lower() in ["exit", "quit"]:
                break

            # CLI Command Handlers
            if query.startswith("/limit "):
                try:
                    val = int(query.split()[1])
                    session_config["limit"] = val
                    print(f"[*] Retrieval limit updated to: {val}")
                except (IndexError, ValueError):
                    print("[!] Invalid argument. Use: /limit <number>")
                continue

            if query.startswith("/datadir "):
                try:
                    path = query.split(maxsplit=1)[1]
                    session_config["data_dir"] = path
                    print(f"[*] Workspace directory updated to: {path}")
                except IndexError:
                    print("[!] Invalid argument. Use: /datadir <path>")
                continue

            print("[*] Retrieving matching vectors from Qdrant...")
            results = search_qdrant(query)
            
            if not results:
                print("[!] No matching documents found inside your database collection.")
                continue

            # Process context sliding expansion
            context_segments = []
            print(f"\n--- Retrieved Sources ({len(results)} matches) ---")
            for i, hit in enumerate(results, 1):
                payload = hit.payload
                path = payload.get("file_path", "Unknown File")
                raw_chunk = payload.get("text", "")
                
                # Fetch expanded local file text
                expanded_chunk = get_local_context(path, raw_chunk, session_config["expand_chars"])
                context_segments.append(expanded_chunk)

                # CLI Output display
                preview_title = payload.get("title", path)
                print(f"[{i}] {preview_title}")
                print(f"    Source: {path}")
                print(f"    Raw length: {len(raw_chunk)} chars | Context length: {len(expanded_chunk)} chars")
                print("-" * 50)

            # Build aggregated prompt payload
            merged_context = "\n\n=== Context Block ===\n\n".join(context_segments)
            
            print("[*] Generating local answer via local LLM...")
            start_time = time.time()
            llm_response = query_llm(system_instruction, query, merged_context)
            elapsed = time.time() - start_time
            
            print(f"\nAssistant > {llm_response}\n")
            print(f"[Timing: {elapsed:.2f}s]")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\n[!] Error during processing loop: {e}")


# ==========================================
# INTERACTIVE FLASK WEB SERVER MODE
# ==========================================

if HAS_FLASK:
    app = Flask(__name__)

    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Local RAG Chat Console</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            ::-webkit-scrollbar { width: 6px; }
            ::-webkit-scrollbar-track { background: #1f2937; }
            ::-webkit-scrollbar-thumb { background: #4b5563; border-radius: 3px; }
        </style>
    </head>
    <body class="bg-gray-950 text-gray-100 min-h-screen flex flex-col font-sans">
        
        <!-- Header -->
        <header class="bg-gray-900 border-b border-gray-800 px-6 py-4 flex justify-between items-center shadow-md">
            <div class="flex items-center space-x-3">
                <span class="text-xl font-extrabold tracking-wider text-indigo-400">LOCAL RAG</span>
                <span class="text-xs bg-indigo-900 text-indigo-200 px-2 py-0.5 rounded font-mono">v{{ version }}</span>
            </div>
            <div class="flex space-x-6 text-sm text-gray-400 font-mono">
                <div>Model: <span class="text-gray-200">{{ llm_model }}</span></div>
                <div>Embed: <span class="text-gray-200">{{ embed_model }}</span></div>
            </div>
        </header>

        <!-- Main Workspace -->
        <div class="flex-1 flex overflow-hidden">
            
            <!-- Sidebar Controls -->
            <aside class="w-80 bg-gray-900 border-r border-gray-800 p-6 flex flex-col justify-between hidden md:flex">
                <div class="space-y-6">
                    <div>
                        <h3 class="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-3">System Constants</h3>
                        <div class="bg-gray-950 p-4 rounded-lg border border-gray-800 space-y-2 text-xs font-mono">
                            <p class="text-gray-400">QDRANT: <span class="text-gray-200">{{ qdrant_url }}</span></p>
                            <p class="text-gray-400">OLLAMA: <span class="text-gray-200">{{ ollama_url }}</span></p>
                            <p class="text-gray-400">COLLECTION: <span class="text-gray-200">{{ collection }}</span></p>
                        </div>
                    </div>

                    <!-- Config Sliders -->
                    <div class="space-y-4">
                        <h3 class="text-sm font-semibold text-gray-300 uppercase tracking-wider">Parameters</h3>
                        
                        <div>
                            <div class="flex justify-between text-xs font-mono mb-1">
                                <span class="text-gray-400">Search Limit:</span>
                                <span id="limit-val" class="text-indigo-400 font-bold">3</span>
                            </div>
                            <input type="range" id="limit-slider" min="1" max="10" value="3" 
                                class="w-full h-1.5 bg-gray-800 rounded-lg appearance-none cursor-pointer accent-indigo-500">
                        </div>

                        <div>
                            <div class="flex justify-between text-xs font-mono mb-1">
                                <span class="text-gray-400">Expansion chars:</span>
                                <span id="chars-val" class="text-indigo-400 font-bold">1000</span>
                            </div>
                            <input type="range" id="chars-slider" min="100" max="3000" step="100" value="1000" 
                                class="w-full h-1.5 bg-gray-800 rounded-lg appearance-none cursor-pointer accent-indigo-500">
                        </div>

                        <div>
                            <label class="block text-xs font-mono text-gray-400 mb-1">Local Data Path Override:</label>
                            <input type="text" id="datadir-input" class="w-full bg-gray-950 border border-gray-800 rounded px-3 py-1.5 text-xs text-gray-200 font-mono focus:outline-none focus:border-indigo-500">
                        </div>
                    </div>
                </div>
                
                <div class="text-center">
                    <button id="save-config-btn" class="w-full bg-indigo-600 hover:bg-indigo-500 text-white text-sm py-2 rounded font-semibold transition">
                        Update Parameters
                    </button>
                </div>
            </aside>

            <!-- Chat Panel -->
            <main class="flex-1 flex flex-col bg-gray-950">
                <div id="chat-messages" class="flex-1 overflow-y-auto p-6 space-y-6">
                    <!-- Welcome Msg -->
                    <div class="flex space-x-3 max-w-3xl">
                        <div class="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-xs font-bold font-mono">AI</div>
                        <div class="bg-gray-900 border border-gray-800 rounded-lg p-4 space-y-2">
                            <p class="text-sm">Привет! Я локальный RAG-ассистент. Задавайте вопросы по вашим документам, и я отвечу на них, опираясь исключительно на контекст векторной базы.</p>
                            <p class="text-xs text-gray-400">Все расчёты производятся на 100% локально и изолированно на CPU.</p>
                        </div>
                    </div>
                </div>

                <!-- Input area -->
                <div class="p-6 bg-gray-900 border-t border-gray-800">
                    <form id="chat-form" class="max-w-4xl mx-auto flex space-x-4">
                        <input type="text" id="user-input" placeholder="Спросите меня о чём-нибудь..." required
                            class="flex-1 bg-gray-950 border border-gray-800 rounded-lg px-4 py-3 text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:border-indigo-500">
                        <button type="submit" class="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-6 py-3 rounded-lg text-sm transition shadow-md">
                            Отправить
                        </button>
                    </form>
                </div>
            </main>
        </div>

        <script>
            const chatMessages = document.getElementById('chat-messages');
            const chatForm = document.getElementById('chat-form');
            const userInput = document.getElementById('user-input');
            const limitSlider = document.getElementById('limit-slider');
            const limitVal = document.getElementById('limit-val');
            const charsSlider = document.getElementById('chars-slider');
            const charsVal = document.getElementById('chars-val');
            const datadirInput = document.getElementById('datadir-input');
            const saveBtn = document.getElementById('save-config-btn');

            // Sync sliders
            limitSlider.addEventListener('input', () => limitVal.innerText = limitSlider.value);
            charsSlider.addEventListener('input', () => charsVal.innerText = charsSlider.value);

            // Fetch active configs on load
            async function loadConfigs() {
                const res = await fetch('/api/config');
                const data = await res.json();
                limitSlider.value = data.limit;
                limitVal.innerText = data.limit;
                charsSlider.value = data.expand_chars;
                charsVal.innerText = data.expand_chars;
                datadirInput.value = data.data_dir;
            }
            loadConfigs();

            // Save configs
            saveBtn.addEventListener('click', async () => {
                await fetch('/api/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        limit: parseInt(limitSlider.value),
                        expand_chars: parseInt(charsSlider.value),
                        data_dir: datadirInput.value
                    })
                });
                alert('Параметры успешно сохранены!');
            });

            // Chat loop
            chatForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const text = userInput.value.trim();
                if (!text) return;

                // Add User Message
                appendMessage('USER', text);
                userInput.value = '';

                // Add temporary typing placeholder
                const placeholderId = appendPlaceholder();

                try {
                    const res = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: text })
                    });
                    const data = await res.json();
                    
                    document.getElementById(placeholderId).remove();

                    if (data.error) {
                        appendMessage('AI', `Ошибка: ${data.error}`);
                    } else {
                        appendMessage('AI', data.response, data.sources);
                    }
                } catch (err) {
                    document.getElementById(placeholderId).remove();
                    appendMessage('AI', `Не удалось соединиться с сервером: ${err.message}`);
                }
            });

            function appendMessage(role, text, sources = []) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `flex space-x-3 max-w-4xl ${role === 'USER' ? 'ml-auto justify-end' : ''}`;
                
                let avatar = `<div class="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-xs font-bold font-mono">AI</div>`;
                let bgColor = 'bg-gray-900 border border-gray-800';
                
                if (role === 'USER') {
                    avatar = '';
                    bgColor = 'bg-indigo-950 border border-indigo-900 text-indigo-100';
                }

                let sourceHTML = '';
                if (sources && sources.length > 0) {
                    sourceHTML = `
                        <div class="mt-4 pt-3 border-t border-gray-800">
                            <details class="text-xs text-gray-400">
                                <summary class="cursor-pointer font-semibold text-indigo-400 hover:underline">Изучить источники (${sources.length})</summary>
                                <div class="mt-2 space-y-2 max-h-60 overflow-y-auto pr-2 font-mono text-[11px]">
                                    ${sources.map((s, idx) => `
                                        <div class="bg-gray-950 p-2 rounded border border-gray-800">
                                            <p class="text-indigo-300 font-semibold">[${idx+1}] ${s.title || s.file_path}</p>
                                            <p class="text-gray-500 text-[10px] mt-0.5">Путь: ${s.file_path}</p>
                                            <pre class="mt-2 whitespace-pre-wrap text-gray-300 bg-gray-900 p-2 rounded max-h-40 overflow-y-auto">${s.expanded_text}</pre>
                                        </div>
                                    `).join('')}
                                </div>
                            </details>
                        </div>
                    `;
                }

                messageDiv.innerHTML = `
                    ${role !== 'USER' ? avatar : ''}
                    <div class="${bgColor} rounded-lg p-4 space-y-1 max-w-2xl shadow-sm">
                        <p class="text-sm whitespace-pre-wrap">${text}</p>
                        ${sourceHTML}
                    </div>
                    ${role === 'USER' ? avatar : ''}
                `;
                
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }

            function appendPlaceholder() {
                const id = 'placeholder-' + Math.random().toString(36).substr(2, 9);
                const messageDiv = document.createElement('div');
                messageDiv.className = 'flex space-x-3 max-w-3xl';
                messageDiv.id = id;
                messageDiv.innerHTML = `
                    <div class="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-xs font-bold font-mono">AI</div>
                    <div class="bg-gray-900 border border-gray-800 rounded-lg p-4 flex items-center space-x-2 text-sm text-gray-400">
                        <span class="animate-bounce">●</span>
                        <span class="animate-bounce [animation-delay:0.2s]">●</span>
                        <span class="animate-bounce [animation-delay:0.4s]">●</span>
                        <span class="ml-2">Думаю локально...</span>
                    </div>
                `;
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
                return id;
            }
        </script>
    </body>
    </html>
    """

    @app.route("/")
    def index():
        return render_template_string(
            HTML_TEMPLATE,
            version=VERSION,
            llm_model=LLM_MODEL,
            embed_model=EMBED_MODEL,
            qdrant_url=QDRANT_URL,
            ollama_url=OLLAMA_URL,
            collection=COLLECTION_NAME
        )

    @app.route("/api/config", methods=["GET", "POST"])
    def api_config():
        if request.method == "POST":
            data = request.json
            if "limit" in data:
                session_config["limit"] = int(data["limit"])
            if "expand_chars" in data:
                session_config["expand_chars"] = int(data["expand_chars"])
            if "data_dir" in data:
                session_config["data_dir"] = data["data_dir"].strip()
            return jsonify({"status": "updated", "config": session_config})
        return jsonify(session_config)

    @app.route("/api/chat", methods=["POST"])
    def api_chat():
        data = request.json
        query = data.get("query", "").strip()
        if not query:
            return jsonify({"error": "Empty search query"}), 400

        # Retrieve points from Qdrant
        results = search_qdrant(query)
        if not results:
            return jsonify({
                "response": "В вашей базе данных не найдено релевантных документов для ответа на этот вопрос.",
                "sources": []
            })

        context_segments = []
        source_details = []

        # Process each matching vector chunk
        for hit in results:
            payload = hit.payload
            path = payload.get("file_path", "Unknown File")
            raw_text = payload.get("text", "")

            # Perform local sliding expansion
            expanded_text = get_local_context(path, raw_text, session_config["expand_chars"])
            context_segments.append(expanded_text)

            source_details.append({
                "title": payload.get("title", path),
                "file_path": path,
                "score": hit.score,
                "raw_text": raw_text,
                "expanded_text": expanded_text
            })

        # Aggregated grounded prompt format
        merged_context = "\n\n=== Context Block ===\n\n".join(context_segments)
        system_instruction = (
            "You are a helpful, precise RAG assistant. Answer the question using ONLY the facts "
            "provided in the context segments. Do not assume or hallucinate details. If you cannot find "
            "the answer in the context, explicitly say that you do not have that information."
        )

        llm_response = query_llm(system_instruction, query, merged_context)

        return jsonify({
            "response": llm_response,
            "sources": source_details
        })


# ==========================================
# MAIN EXECUTION ROUTER
# ==========================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-mode Local RAG Conversational Client")
    parser.add_argument("--cli", action="store_true", help="Launch interactive CLI Console mode directly")
    parser.add_argument("/data", type=str, nargs="?", help="Argument parsing mapping path mirror")
    parser.add_argument("host_data_path", type=str, nargs="?", help="Mapped directory path reference on host")
    
    args = parser.parse_args()

    # Capture manual path arguments matching host structure: python cli_chat_v1_2_0.py /data ../data/
    if args.host_data_path:
        session_config["data_dir"] = args.host_data_path
    elif args.cli:
        # Fallback inline path detection for CLI execution formats
        if len(sys.argv) > 2:
            for item in sys.argv:
                if os.path.isdir(item) or item.startswith("..") or item.startswith("."):
                    session_config["data_dir"] = item
                    break

    if args.cli or not HAS_FLASK:
        if not HAS_FLASK:
            logger.warning("Flask was not found in your environment. Defaulting to CLI interface mode.")
        interactive_cli()
    else:
        logger.info("-" * 60)
        logger.info(f"RAG Web Console Initialization (v{VERSION})")
        logger.info(f"Embedding Engine: {EMBED_MODEL} | LLM Engine: {LLM_MODEL}")
        logger.info(f"Workspace path mapping points to: {session_config['data_dir']}")
        logger.info("Access the Web Chat Console at: http://localhost:5001")
        logger.info("-" * 60)
        
        app.run(host="0.0.0.0", port=5001)