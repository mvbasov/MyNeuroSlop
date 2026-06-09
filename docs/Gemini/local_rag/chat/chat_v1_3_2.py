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
    "data_dir": DEFAULT_DATA_DIR,
    "show_sources": True
}

try:
    qdrant_client = QdrantClient(url=QDRANT_URL, timeout=60.0)
except Exception as e:
    logger.error(f"Failed to connect to Qdrant at {QDRANT_URL}: {e}")
    sys.exit(1)


def get_embedding_with_retry(text):
    """
    Generates embedding for a given text using exponential backoff to handle CPU overload safely.
    This prevents intermittent failures during resource spikes.
    """
    payload = {
        "model": EMBED_MODEL, 
        "prompt": text,
        "keep_alive": "5m",
        "options": {
            "num_thread": 2,  # Optimizing for 4 CPU threads
            "num_ctx": 512
        }
    }
    
    # Delays between retries on error (1s, 2s, 4s, 8s, 16s)
    delays = [1, 2, 4, 8, 16]
    for attempt, delay in enumerate(delays):
        try:
            response = requests.post(f"{OLLAMA_URL}/api/embeddings", json=payload, timeout=90)
            response.raise_for_status()
            return response.json()["embedding"]
        except Exception as e:
            if attempt == len(delays) - 1:
                logger.error(f"Failed to retrieve embedding after {len(delays)} attempts: {e}")
                raise e
            time.sleep(delay)


def normalize_text_for_search(text):
    """
    Normalizes unicode dash characters and collapses whitespaces.
    Strips JSON artifacts (quotes, colons, brackets) to ensure raw Text blocks 
    from Qdrant accurately map back to native JSON structures inside the file.
    """
    if not text:
        return ""
    text = re.sub(r'["\',:{}\[\]<>]', '', text)
    text = re.sub(r'[\u2012\u2013\u2014\u2212]', '-', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip().lower()


def get_expanded_context(filepath, chunk_text, max_expansion_chars, data_dir):
    """
    Finds the original chunk in the local file on disk and extracts subsequent text
    to restore continuity and coherence for the LLM generation phase.
    """
    if max_expansion_chars <= 0:
        return chunk_text, False, 0, "Expansion disabled"

    # Step 1: Clean filepath from anchor tags
    filepath_clean = filepath.split('#')[0]

    # Step 2: Align absolute paths inside containers (/data/...) to relative paths on the host
    rel_path = filepath_clean
    if filepath_clean.startswith('/data/'):
        rel_path = filepath_clean[6:]
    elif filepath_clean.startswith('data/'):
        rel_path = filepath_clean[5:]

    # Step 3: Search for the target file using various relative routes on the host filesystem
    possible_paths = [
        os.path.join(data_dir, rel_path),
        os.path.join(".", "data", rel_path),
        os.path.abspath(os.path.join(data_dir, rel_path)),
        filepath_clean
    ]

    target_file = None
    for path in possible_paths:
        if os.path.isfile(path):
            target_file = path
            break

    if not target_file:
        checked_paths = ", ".join([os.path.join(data_dir, rel_path), filepath_clean])
        return chunk_text, False, 0, f"File not found on host (checked: {checked_paths})"

    try:
        with open(target_file, 'r', encoding='utf-8', errors='ignore') as f:
            full_content = f.read()

        # --- Virtual File Anchor Search Boundary ---
        # If the file path contains an anchor, we find its location in the document
        # to ensure we don't accidentally expand a duplicate chunk from the wrong section.
        search_start_pos = 0
        if '#' in filepath:
            anchor = filepath.split('#')[1]
            possible_markers = [anchor]
            
            # Reconstruct datetime from anchors if formatted as YYYY-MM-DD-HHMMSS
            if re.match(r'^\d{4}-\d{2}-\d{2}-\d{6}$', anchor):
                possible_markers.append(f"{anchor[:10]} {anchor[11:13]}:{anchor[13:15]}:{anchor[15:17]}")
            elif re.match(r'^\d{4}-\d{2}-\d{2}$', anchor):
                possible_markers.append(anchor)
                
            full_content_lower = full_content.lower()
            for marker in possible_markers:
                marker_idx = full_content_lower.find(marker.lower())
                if marker_idx != -1:
                    search_start_pos = marker_idx
                    break

        # Normalize carriage returns
        full_content_norm = full_content.replace('\r\n', '\n')
        chunk_text_norm = chunk_text.replace('\r\n', '\n')

        # Try to locate the exact match first (starting AFTER the virtual file boundary)
        orig_idx = full_content_norm.find(chunk_text_norm, search_start_pos)
        chunk_end_pos = -1
        found = False

        if orig_idx != -1:
            chunk_end_pos = orig_idx + len(chunk_text_norm)
            found = True
        else:
            # Fallback search: find line by line using normalized representations
            chunk_lines = [line.strip() for line in chunk_text_norm.split('\n') if len(line.strip()) >= 10]
            
            # Sort lines by length (longest first) to lock onto highly unique strings (like URLs) 
            # rather than short, repeating keywords (like "Tags: FreeCAD")
            chunk_lines.sort(key=len, reverse=True)
            
            # Search through lines of the file, bounded strictly by the virtual separator
            file_section = full_content_norm[search_start_pos:]
            file_lines = file_section.split('\n')
            
            for line in chunk_lines:
                clean_target = re.sub(r'^[·\-\*\s\d\.\)\(]+', '', line).strip()
                clean_target_norm = normalize_text_for_search(clean_target)
                if len(clean_target_norm) < 6:
                    continue

                for idx, f_line in enumerate(file_lines):
                    f_line_clean = re.sub(r'^[·\-\*\s\d\.\)\(]+', '', f_line).strip()
                    f_line_norm = normalize_text_for_search(f_line_clean)
                    
                    # Prevent empty line bug (where "" in "target" evaluated to True and triggered premature matches)
                    if f_line_norm and (clean_target_norm in f_line_norm or (len(f_line_norm) >= 10 and f_line_norm in clean_target_norm)):
                        char_pos = search_start_pos + sum(len(l) + 1 for l in file_lines[:idx]) + len(f_line)
                        chunk_end_pos = char_pos
                        found = True
                        break
                if found:
                    break

        if not found:
            return chunk_text, False, 0, "Chunk text not found inside file (desync)"

        # Extract following characters
        subsequent_text = full_content_norm[chunk_end_pos:chunk_end_pos + max_expansion_chars]

        # Stop expansion if we encounter virtual file boundaries (Pelican tags or Markdown page separators)
        separator_pattern = re.compile(
            r'\n\s*[-*_](?:\s*[-*_]){2,}\s*\n|'    # Matches horizontal rules (e.g. ---, - - -, ***)
            r'\n##### \d{4}-\d{2}-\d{2}|'           # Matches Pelican/diary headers
            r'\n\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}' # Matches standard timestamp lines
        )
        match = separator_pattern.search(subsequent_text)
        if match:
            subsequent_text = subsequent_text[:match.start()]

        subsequent_clean = subsequent_text.strip()
        if subsequent_clean:
            expanded = f"{chunk_text}\n[FILE EXTENSION]:\n{subsequent_clean}"
            return expanded, True, len(subsequent_clean), "Success"
        else:
            return chunk_text, False, 0, "End of section/file (no text to append)"

    except Exception as e:
        return chunk_text, False, 0, f"File read error: {str(e)}"


def perform_rag_query(query, limit, expand_chars, data_dir):
    """
    Central core RAG processor.
    Queries Qdrant database, expands context from disk, and generates the LLM response.
    Returns a dictionary containing the answer and source list metadata.
    """
    try:
        query_vec = get_embedding_with_retry(query)
        results = qdrant_client.search(
            collection_name=COLLECTION_NAME, 
            query_vector=query_vec, 
            limit=limit
        )
    except Exception as e:
        return {
            "answer": f"Retrieval phase failure: {str(e)}",
            "sources": []
        }
    
    if not results:
        return {
            "answer": "I do not have enough information to answer (No matching documents found in vector store).",
            "sources": []
        }
        
    context_chunks = []
    sources_metadata = []

    for i, res in enumerate(results, start=1):
        text = res.payload.get('text', '').strip()
        filepath = res.payload.get('filepath', 'Unknown source')
        score = res.score
        
        if not text:
            continue

        expanded_text, was_expanded, added_chars, status_msg = get_expanded_context(
            filepath, 
            text, 
            expand_chars, 
            data_dir
        )
        
        sources_metadata.append({
            "index": i,
            "filepath": filepath,
            "score": f"{score:.4f}",
            "was_expanded": was_expanded,
            "added_chars": added_chars,
            "status_msg": status_msg,
            "original_text": text,
            "expanded_text": expanded_text
        })

        context_chunks.append(f"[{filepath}]:\n{expanded_text}")
            
    context = "\n\n".join(context_chunks)
    
    # Low resource model prompt
    prompt = (
        "You are a strict, factual local retrieval assistant. Your task is to answer the user's question relying strictly on the provided context.\n\n"
        "CRITICAL RULES:\n"
        "1. Only use facts directly mentioned in the <context> block. Do not assume, extrapolate, or bring in external knowledge.\n"
        "2. If the exact answer is not contained within the context, you MUST respond exactly with: 'I do not have enough information to answer.'\n"
        "3. Keep your response extremely brief, direct, and factual. Avoid conversational filler or introductory phrases (e.g., 'Based on the context...').\n"
        "4. Respond in the same language as the user's Question below.\n\n"
        f"<context>\n{context}\n</context>\n\n"
        f"Question: {query}\n"
        "Answer:"
    )

    
    try:
        response = requests.post(f"{OLLAMA_URL}/api/generate", json={
            "model": LLM_MODEL,
            "prompt": prompt,
            "stream": False
        }, timeout=150)
        response.raise_for_status()
        answer = response.json().get("response", "No answer generated.").strip()
        return {
            "answer": answer,
            "sources": sources_metadata
        }
    except Exception as e:
        return {
            "answer": f"Generation phase failure: {str(e)}",
            "sources": sources_metadata
        }


# ==========================================
# CLI CHAT MODULE
# ==========================================

def run_cli_mode():
    """Runs the traditional terminal-based interactive CLI loop."""
    print("="*60)
    print(f"--- RAG CLI Chat v{VERSION} ---")
    print("="*60)
    print(f"Connected to Qdrant: {QDRANT_URL} | Collection: {COLLECTION_NAME}")
    print(f"Embedding Engine: Ollama ({EMBED_MODEL}) | LLM: {LLM_MODEL}")
    print(f"Local Context Expansion: ACTIVE (Directory: {session_config['data_dir']})")
    print("Type /help to view configuration parameters.")
    print("-"*60)
    
    def print_help():
        print("\nAvailable commands:")
        print("  /limit <num>      - Set the number of retrieval chunks (currently: {})".format(session_config["limit"]))
        print("  /expand <num>     - Set character limit for file context expansion (currently: {})".format(session_config["expand_chars"]))
        print("  /datadir <path>   - Set the path to local host data directory (currently: {})".format(session_config["data_dir"]))
        print("  /sources          - Toggle showing retrieved source details (currently: {})".format(session_config["show_sources"]))
        print("  /help             - Show this help menu")
        print("  exit / quit       - Exit the interactive CLI session")

    while True:
        try:
            query = input("\nYou: ").strip()
            if not query:
                continue
            
            if query.startswith('/'):
                parts = query.split(maxsplit=1)
                cmd = parts[0].lower()
                arg = parts[1] if len(parts) > 1 else None
                
                if cmd == '/help':
                    print_help()
                elif cmd == '/limit':
                    if arg and arg.isdigit():
                        session_config["limit"] = int(arg)
                        print(f"Retrieval limit set to: {session_config['limit']} chunks.")
                    else:
                        print("Please specify a number. Example: /limit 5")
                elif cmd == '/expand':
                    if arg and arg.isdigit():
                        session_config["expand_chars"] = int(arg)
                        print(f"Context expansion limit set to: {session_config['expand_chars']} characters.")
                    else:
                        print("Please specify a number. Example: /expand 800")
                elif cmd == '/datadir':
                    if arg:
                        session_config["data_dir"] = arg.strip()
                        print(f"Data directory path changed to: {session_config['data_dir']}")
                    else:
                        print("Please specify a path. Example: /datadir ./data")
                elif cmd == '/sources':
                    session_config["show_sources"] = not session_config["show_sources"]
                    print(f"Display sources: {'ON' if session_config['show_sources'] else 'OFF'}")
                else:
                    print("Unknown command. Type /help to see the available commands.")
                continue

            if query.lower() in ['exit', 'quit']:
                print("Exiting CLI Chat tool. Goodbye.")
                break
            
            print("Searching and reasoning...")
            start_time = time.time()
            result = perform_rag_query(
                query, 
                session_config["limit"], 
                session_config["expand_chars"], 
                session_config["data_dir"]
            )
            elapsed = time.time() - start_time
            
            if session_config["show_sources"] and result["sources"]:
                print("\n--- Retrieved Sources ---")
                for s in result["sources"]:
                    status_str = f" [Expanded by +{s['added_chars']} chars]" if s['was_expanded'] else f" [Original] ({s['status_msg']})"
                    print(f"{s['index']}. [{s['filepath']}]{status_str}")
                    preview = s['original_text'].replace('\n', ' ')[:80] + "..."
                    print(f"   Preview: {preview}")
            
            print(f"\nAssistant: {result['answer']}")
            print(f"[Request processing time on CPU: {elapsed:.2f} seconds]")
            
        except KeyboardInterrupt:
            print("\nSession interrupted by user. Exiting.")
            break
        except Exception as e:
            print(f"\nUnexpected internal interface error: {e}")


# ==========================================
# WEB SERVICE MODULE (Flask Server)
# ==========================================

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RAG Web Chat Console</title>
    <style>
        :root {
            --bg-color: #121214;
            --sidebar-bg: #1a1a1e;
            --border-color: #2c2c35;
            --accent-color: #6366f1;
            --accent-hover: #4f46e5;
            --text-main: #e2e8f0;
            --text-secondary: #94a3b8;
            --chat-bubble-user: #2563eb;
            --chat-bubble-assistant: #222228;
            --success-color: #10b981;
            --warning-color: #f59e0b;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-main);
            height: 100vh;
            display: flex;
            overflow: hidden;
        }

        /* Sidebar Configurations */
        .sidebar {
            width: 320px;
            background-color: var(--sidebar-bg);
            border-right: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            padding: 24px;
            z-index: 10;
        }

        .sidebar-header {
            margin-bottom: 30px;
        }

        .sidebar-title {
            font-size: 1.25rem;
            font-weight: 700;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .version-badge {
            font-size: 0.75rem;
            background: #2c2c35;
            padding: 2px 8px;
            border-radius: 12px;
            color: var(--text-secondary);
        }

        .setting-group {
            margin-bottom: 24px;
        }

        .setting-label {
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
        }

        .setting-value {
            font-weight: 600;
            color: #fff;
        }

        input[type="range"] {
            width: 100%;
            accent-color: var(--accent-color);
            margin-top: 6px;
        }

        .info-box {
            background-color: #222228;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 12px;
            font-size: 0.8rem;
            line-height: 1.4;
            color: var(--text-secondary);
            margin-top: auto;
        }

        .info-box span {
            color: #fff;
            font-weight: 600;
        }

        /* Main Chat Area */
        .chat-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            height: 100%;
            background-color: var(--bg-color);
        }

        .chat-header {
            padding: 20px 30px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .chat-header h1 {
            font-size: 1.1rem;
            font-weight: 600;
            color: #fff;
        }

        .connection-status {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.85rem;
            color: var(--text-secondary);
        }

        .status-indicator {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: var(--success-color);
        }

        .messages-area {
            flex: 1;
            overflow-y: auto;
            padding: 30px;
            display: flex;
            flex-direction: column;
            gap: 24px;
        }

        .message-row {
            display: flex;
            width: 100%;
        }

        .message-row.user {
            justify-content: flex-end;
        }

        .message-row.assistant {
            justify-content: flex-start;
        }

        .message-bubble {
            max-width: 80%;
            padding: 16px 20px;
            border-radius: 12px;
            line-height: 1.5;
            font-size: 0.95rem;
            word-wrap: break-word;
        }

        .message-row.user .message-bubble {
            background-color: var(--chat-bubble-user);
            color: #fff;
            border-bottom-right-radius: 2px;
        }

        .message-row.assistant .message-bubble {
            background-color: var(--chat-bubble-assistant);
            color: var(--text-main);
            border-bottom-left-radius: 2px;
            border: 1px solid var(--border-color);
        }

        /* Sources Inspector CSS */
        .sources-section {
            margin-top: 14px;
            border-top: 1px dashed var(--border-color);
            padding-top: 10px;
        }

        .sources-toggle {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 0.8rem;
            color: var(--text-secondary);
            cursor: pointer;
            user-select: none;
            transition: color 0.2s;
        }

        .sources-toggle:hover {
            color: #fff;
        }

        .sources-toggle::before {
            content: "▶";
            font-size: 0.65rem;
            transition: transform 0.2s;
            display: inline-block;
        }

        .sources-toggle.active::before {
            transform: rotate(90deg);
        }

        .sources-content {
            display: none;
            margin-top: 10px;
            gap: 10px;
            flex-direction: column;
        }

        .sources-content.active {
            display: flex;
        }

        .source-card {
            background-color: #16161a;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 10px 14px;
        }

        .source-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.75rem;
            margin-bottom: 6px;
        }

        .source-path {
            color: var(--accent-color);
            font-family: monospace;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            max-width: 70%;
        }

        .source-badge {
            background-color: #2c2c35;
            padding: 2px 6px;
            border-radius: 4px;
            color: var(--text-main);
        }

        .source-badge.expanded {
            background-color: rgba(16, 185, 129, 0.15);
            color: var(--success-color);
            border: 1px solid rgba(16, 185, 129, 0.3);
        }

        .source-text {
            font-size: 0.8rem;
            color: var(--text-secondary);
            line-height: 1.4;
            white-space: pre-wrap;
            max-height: 150px;
            overflow-y: auto;
            background-color: #121214;
            padding: 8px;
            border-radius: 4px;
            border: 1px solid #222228;
            font-family: monospace;
        }

        /* Input Controls Area */
        .input-area {
            padding: 20px 30px 30px 30px;
            border-top: 1px solid var(--border-color);
        }

        .input-form {
            display: flex;
            gap: 12px;
            max-width: 1000px;
            margin: 0 auto;
            position: relative;
        }

        .chat-input {
            flex: 1;
            background-color: #1a1a1e;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 16px 20px;
            color: #fff;
            font-size: 0.95rem;
            outline: none;
            transition: border-color 0.2s;
        }

        .chat-input:focus {
            border-color: var(--accent-color);
        }

        .send-button {
            background-color: var(--accent-color);
            color: #fff;
            border: none;
            border-radius: 8px;
            padding: 0 24px;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }

        .send-button:hover {
            background-color: var(--accent-hover);
        }

        .send-button:disabled {
            background-color: #2c2c35;
            color: var(--text-secondary);
            cursor: not-allowed;
        }

        /* Shimmer loading effect */
        .loading-shimmer {
            animation: shimmer 1.5s infinite linear;
            background: linear-gradient(to right, #222228 4%, #2c2c35 25%, #222228 36%);
            background-size: 1000px 100%;
            border-radius: 4px;
            height: 16px;
            margin-bottom: 8px;
        }
        .loading-shimmer.short { width: 40%; }
        .loading-shimmer.medium { width: 75%; }
        .loading-shimmer.long { width: 100%; }

        @keyframes shimmer {
            0% { background-position: -1000px 0; }
            100% { background-position: 1000px 0; }
        }

        /* Scrollbar Optimization */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: transparent;
        }
        ::-webkit-scrollbar-thumb {
            background: #2c2c35;
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #3e3e4a;
        }
    </style>
</head>
<body>

    <!-- Sidebar Configurations -->
    <div class="sidebar">
        <div class="sidebar-header">
            <div class="sidebar-title">
                RAG Chat Console <span class="version-badge">v{{ version }}</span>
            </div>
        </div>

        <div class="setting-group">
            <div class="setting-label">
                <span>Retrieval Chunks</span>
                <span class="setting-value" id="limit-val">3</span>
            </div>
            <input type="range" id="limit-slider" min="1" max="10" value="3" oninput="updateConfigValue('limit', this.value)">
        </div>

        <div class="setting-group">
            <div class="setting-label">
                <span>Context Extension</span>
                <span class="setting-value" id="expand-val">1000 ch</span>
            </div>
            <input type="range" id="expand-slider" min="0" max="5000" step="100" value="1000" oninput="updateConfigValue('expand_chars', this.value)">
        </div>

        <div class="setting-group">
            <div class="setting-label">
                <span>Data Directory</span>
            </div>
            <div style="font-family: monospace; font-size: 0.8rem; background: #222228; padding: 10px; border-radius: 6px; border: 1px solid var(--border-color); overflow-x: auto; word-break: break-all;">
                {{ data_dir }}
            </div>
        </div>

        <div class="info-box">
            <span>Network Context</span><br>
            Qdrant: <span style="font-family: monospace;">{{ qdrant_url }}</span><br>
            Ollama: <span style="font-family: monospace;">{{ ollama_url }}</span><br>
            Embedding: <span style="font-family: monospace;">{{ embed_model }}</span><br>
            LLM: <span style="font-family: monospace;">{{ llm_model }}</span>
        </div>
    </div>

    <!-- Main Chat Container -->
    <div class="chat-container">
        <div class="chat-header">
            <h1>Offline Conversational Dashboard</h1>
            <div class="connection-status">
                <div class="status-indicator"></div>
                Connected Locally
            </div>
        </div>

        <div class="messages-area" id="messages-container">
            <!-- Initial Greeting -->
            <div class="message-row assistant">
                <div class="message-bubble">
                    Hello! I am your offline RAG assistant. Ask me anything based on your indexed local documentation.
                </div>
            </div>
        </div>

        <div class="input-area">
            <form class="input-form" id="chat-form" onsubmit="submitQuery(event)">
                <input type="text" class="chat-input" id="user-input" placeholder="Ask a question..." autocomplete="off" required>
                <button type="submit" class="send-button" id="submit-btn">
                    <!-- Clean SVG Inline Arrow Icon -->
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
                    Send
                </button>
            </form>
        </div>
    </div>

    <script>
        // Sync configuration variables on load
        let currentConfig = {
            limit: 3,
            expand_chars: 1000
        };

        window.onload = function() {
            fetch('/api/config')
                .then(res => res.json())
                .then(data => {
                    currentConfig = data;
                    document.getElementById('limit-slider').value = data.limit;
                    document.getElementById('limit-val').textContent = data.limit;
                    document.getElementById('expand-slider').value = data.expand_chars;
                    document.getElementById('expand-val').textContent = data.expand_chars + ' ch';
                });
        };

        function updateConfigValue(key, val) {
            currentConfig[key] = parseInt(val);
            if (key === 'limit') {
                document.getElementById('limit-val').textContent = val;
            } else if (key === 'expand_chars') {
                document.getElementById('expand-val').textContent = val + ' ch';
            }

            // Push state updates back to Python Flask backend
            fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(currentConfig)
            });
        }

        function toggleSources(el) {
            el.classList.toggle('active');
            const target = el.nextElementSibling;
            target.classList.toggle('active');
        }

        function submitQuery(event) {
            event.preventDefault();
            const inputField = document.getElementById('user-input');
            const queryText = inputField.value.trim();
            if (!queryText) return;

            // Render User Bubble
            const messagesContainer = document.getElementById('messages-container');
            const userRow = document.createElement('div');
            userRow.className = 'message-row user';
            userRow.innerHTML = `<div class="message-bubble">${escapeHtml(queryText)}</div>`;
            messagesContainer.appendChild(userRow);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;

            inputField.value = '';
            inputField.disabled = true;
            document.getElementById('submit-btn').disabled = true;

            // Render Temporary Assistant Loading Shimmer Row
            const loadingRow = document.createElement('div');
            loadingRow.className = 'message-row assistant';
            loadingRow.id = 'loading-shimmer-row';
            loadingRow.innerHTML = `
                <div class="message-bubble" style="width: 50%;">
                    <div class="loading-shimmer long"></div>
                    <div class="loading-shimmer medium"></div>
                    <div class="loading-shimmer short"></div>
                </div>
            `;
            messagesContainer.appendChild(loadingRow);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;

            // Fetch generation response
            fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: queryText })
            })
            .then(res => res.json())
            .then(data => {
                // Clear Shimmer
                loadingRow.remove();

                // Format and append assistant content
                const assistantRow = document.createElement('div');
                assistantRow.className = 'message-row assistant';
                
                let sourcesHtml = '';
                if (data.sources && data.sources.length > 0) {
                    sourcesHtml = `
                        <div class="sources-section">
                            <div class="sources-toggle" onclick="toggleSources(this)">Retrieved Sources (${data.sources.length})</div>
                            <div class="sources-content">
                    `;
                    
                    data.sources.forEach(s => {
                        const badgeClass = s.was_expanded ? 'source-badge expanded' : 'source-badge';
                        const badgeLabel = s.was_expanded ? `Expanded +${s.added_chars} chars` : s.status_msg;
                        
                        sourcesHtml += `
                            <div class="source-card">
                                <div class="source-header">
                                    <div class="source-path" title="${escapeHtml(s.filepath)}">${escapeHtml(s.filepath)}</div>
                                    <div class="${badgeClass}">${escapeHtml(badgeLabel)}</div>
                                </div>
                                <div class="source-text">${escapeHtml(s.expanded_text)}</div>
                            </div>
                        `;
                    });
                    
                    sourcesHtml += `</div></div>`;
                }

                assistantRow.innerHTML = `
                    <div class="message-bubble">
                        <div>${escapeHtml(data.answer).replace(/\\n/g, '<br>')}</div>
                        ${sourcesHtml}
                    </div>
                `;
                
                messagesContainer.appendChild(assistantRow);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            })
            .catch(err => {
                loadingRow.remove();
                const errRow = document.createElement('div');
                errRow.className = 'message-row assistant';
                errRow.innerHTML = `<div class="message-bubble" style="color: #ef4444; border-color: rgba(239, 68, 68, 0.3);">Failed to connect with model daemon: ${escapeHtml(err.message)}</div>`;
                messagesContainer.appendChild(errRow);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            })
            .finally(() => {
                inputField.disabled = false;
                document.getElementById('submit-btn').disabled = false;
                inputField.focus();
            });
        }

        function escapeHtml(text) {
            const map = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            };
            return text.replace(/[&<>"']/g, function(m) { return map[m]; });
        }
    </script>
</body>
</html>
"""


def start_web_server():
    """Initializes and runs the Flask server to host the RAG web console."""
    from flask import Flask, jsonify, request, render_template_string
    
    app = Flask(__name__)
    
    # Silence Flask startup server logs for cleaner container logs
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    @app.route("/")
    def index():
        return render_template_string(
            HTML_TEMPLATE, 
            version=VERSION, 
            data_dir=session_config["data_dir"],
            qdrant_url=QDRANT_URL,
            ollama_url=OLLAMA_URL,
            embed_model=EMBED_MODEL,
            llm_model=LLM_MODEL
        )

    @app.route("/api/config", methods=["GET", "POST"])
    def config_endpoint():
        if request.method == "POST":
            data = request.get_json()
            if "limit" in data:
                session_config["limit"] = max(1, min(10, int(data["limit"])))
            if "expand_chars" in data:
                session_config["expand_chars"] = max(0, min(5000, int(data["expand_chars"])))
            logger.info(f"Updated configuration state: Chunk limit={session_config['limit']}, Context extension={session_config['expand_chars']} chars")
            return jsonify({"status": "updated"})
        return jsonify({
            "limit": session_config["limit"],
            "expand_chars": session_config["expand_chars"]
        })

    @app.route("/api/chat", methods=["POST"])
    def chat_endpoint():
        data = request.get_json()
        query = data.get("query", "").strip()
        if not query:
            return jsonify({"error": "Empty query"}), 400
            
        result = perform_rag_query(
            query, 
            session_config["limit"], 
            session_config["expand_chars"], 
            session_config["data_dir"]
        )
        return jsonify(result)

    logger.info("=" * 60)
    logger.info(f"--- Launching RAG Web Chat Server v{VERSION} ---")
    logger.info("=" * 60)
    logger.info(f"Qdrant DB: {QDRANT_URL} | Collection: {COLLECTION_NAME}")
    logger.info(f"Embedding Engine: {EMBED_MODEL} | LLM Engine: {LLM_MODEL}")
    logger.info(f"Workspace path mapping points to: {session_config['data_dir']}")
    logger.info("Access the Web Chat Console at: http://localhost:5001")
    logger.info("-" * 60)
    
    app.run(host="0.0.0.0", port=5001)


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

    if args.cli:
        run_cli_mode()
    else:
        # Defaults to web server mode when run in Docker context
        start_web_server()