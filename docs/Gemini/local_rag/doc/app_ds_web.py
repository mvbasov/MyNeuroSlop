import os
import re
import time
import requests
import threading
import hashlib
import logging
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, Filter, FieldCondition, MatchValue
from flask import Flask, request, jsonify, render_template_string

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Environment variables
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://ollama:11434")
QDRANT_URL = os.environ.get("QDRANT_URL", "qdrant")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", 6333))
HTML_BASE_PATH = os.environ.get("HTML_BASE_PATH", "/home/mvb/git/OMNotes/html/")  # Base path for file:// links

EMBED_MODEL = "all-minilm"
COLLECTION_NAME = "rag_documents"
DATA_DIR = "/data"

INDEXING_STATUS = {"is_indexing": False}
app = Flask(__name__)

# ---------- HTML TEMPLATE (unchanged) ----------
HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>Local RAG Search</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; background-color: #f9f9f9; color: #333; }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h2 { margin-top: 0; color: #2c3e50; }
        .status-banner { background-color: #f39c12; color: white; padding: 12px; text-align: center; border-radius: 5px; margin-bottom: 20px; font-weight: bold; display: none; }
        .status-ready { background-color: #27ae60; }
        .search-box { display: flex; gap: 10px; margin-bottom: 20px; }
        input[type="text"] { flex-grow: 1; padding: 12px; font-size: 16px; border: 1px solid #ccc; border-radius: 5px; }
        button { padding: 12px 24px; font-size: 16px; cursor: pointer; background-color: #3498db; color: white; border: none; border-radius: 5px; transition: background 0.3s; }
        button:hover { background-color: #2980b9; }
        .result { border-bottom: 1px solid #eee; padding: 15px 0; }
        .result:last-child { border-bottom: none; }
        .filename { font-weight: bold; color: #2c3e50; margin-bottom: 8px; font-size: 0.95em; }
        .filename a { color: #1e3a8a; text-decoration: none; border-bottom: 1px dotted #1e3a8a; }
        .filename a:hover { text-decoration: underline; }
        .score { color: #7f8c8d; font-size: 0.85em; margin-top: 5px; font-weight: bold; }
        .text-snippet { line-height: 1.5; }
        #loading { color: #f39c12; font-weight: bold; display: none; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Local Document Search</h2>
        <div id="indexing-status" class="status-banner">⚙️ Indexing documents in the background... Search results may be incomplete.</div>
        <div class="search-box">
            <input type="text" id="query" placeholder="Ask a question or enter a search query..." onkeypress="if(event.key === 'Enter') executeSearch()">
            <button onclick="executeSearch()">Search</button>
        </div>
        <div id="loading">Searching...</div>
        <div id="results"></div>
    </div>
    <script>
        async function checkStatus() {
            try {
                const response = await fetch('/status');
                const data = await response.json();
                const statusDiv = document.getElementById('indexing-status');
                if (data.is_indexing) {
                    statusDiv.style.display = 'block';
                    statusDiv.className = 'status-banner';
                    statusDiv.innerHTML = '⚙️ Indexing documents in the background... Search results may be incomplete.';
                    setTimeout(checkStatus, 3000);
                } else {
                    if (statusDiv.style.display === 'block' && statusDiv.className !== 'status-banner status-ready') {
                        statusDiv.className = 'status-banner status-ready';
                        statusDiv.innerHTML = '✅ Indexing complete!';
                        setTimeout(() => { statusDiv.style.display = 'none'; }, 4000);
                    }
                }
            } catch (err) {
                console.error("Failed to fetch status", err);
                setTimeout(checkStatus, 5000);
            }
        }
        window.onload = checkStatus;
        async function executeSearch() {
            const query = document.getElementById('query').value;
            if (!query) return;
            const loading = document.getElementById('loading');
            const resultsDiv = document.getElementById('results');
            loading.style.display = 'block';
            resultsDiv.innerHTML = '';
            try {
                const response = await fetch('/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: query })
                });
                const data = await response.json();
                loading.style.display = 'none';
                if (data.error) {
                    resultsDiv.innerHTML = `<p style="color:red">Error: ${data.error}</p>`;
                    return;
                }
                if (data.results.length === 0) {
                    resultsDiv.innerHTML = '<p>No results found.</p>';
                    return;
                }
                data.results.forEach(res => {
                    const div = document.createElement('div');
                    div.className = 'result';
                    let fileDisplay = res.filepath;
                    if (res.file_url) {
                        fileDisplay = `<a href="${res.file_url}" target="_blank">📄 ${res.filepath}</a>`;
                    } else {
                        fileDisplay = `📄 ${res.filepath}`;
                    }
                    div.innerHTML = `
                        <div class="filename">${fileDisplay}</div>
                        <div class="text-snippet">${res.text}</div>
                        <div class="score">Similarity Score: ${(res.score * 100).toFixed(1)}%</div>
                    `;
                    resultsDiv.appendChild(div);
                });
            } catch (err) {
                loading.style.display = 'none';
                resultsDiv.innerHTML = `<p style="color:red">Connection error. Make sure the server is running.</p>`;
            }
        }
    </script>
</body>
</html>"""

def get_qdrant_client():
    return QdrantClient(url=f"http://{QDRANT_URL}:{QDRANT_PORT}", timeout=60.0)

def ensure_ollama_model():
    """Check if model exists, pull if missing."""
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=10)
        if resp.status_code == 200:
            models = resp.json().get("models", [])
            if any(m.get("name", "").startswith(EMBED_MODEL) for m in models):
                logger.info(f"Model {EMBED_MODEL} already present.")
                return True
        logger.info(f"Model {EMBED_MODEL} not found. Pulling (may take a few minutes)...")
        pull_resp = requests.post(f"{OLLAMA_URL}/api/pull", json={"name": EMBED_MODEL}, timeout=300)
        if pull_resp.status_code == 200:
            logger.info(f"Successfully pulled {EMBED_MODEL}")
            return True
        else:
            logger.error(f"Failed to pull model: {pull_resp.status_code}")
            return False
    except Exception as e:
        logger.error(f"Error checking/pulling model: {e}")
        return False

def sanitize_text(text, max_len=250):
    """Remove control characters and truncate to safe length for all-minilm."""
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    if len(cleaned) > max_len:
        cleaned = cleaned[:max_len].rsplit(' ', 1)[0]
        if len(cleaned) > max_len:
            cleaned = cleaned[:max_len]
    return cleaned.strip()

def chunk_text_smart(text, max_chars=250):
    """Split text into chunks not exceeding max_chars, preserving words."""
    if len(text) <= max_chars:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        if end >= len(text):
            chunks.append(text[start:])
            break
        cut = text.rfind(' ', start, end)
        if cut == -1 or cut <= start:
            cut = end
        chunks.append(text[start:cut])
        start = cut
    return chunks

def get_embedding_with_retry(text, max_retries=12):
    sanitized = sanitize_text(text)
    if not sanitized:
        raise ValueError("Empty text after sanitization")
    payload = {
        "model": EMBED_MODEL,
        "prompt": sanitized,
        "keep_alive": "5m",
        "options": {"num_thread": 1}
    }
    for attempt in range(max_retries):
        try:
            res = requests.post(f"{OLLAMA_URL}/api/embeddings", json=payload, timeout=90)
            if res.status_code == 200:
                return res.json()["embedding"]
            else:
                wait_time = min(2 ** attempt, 60)
                logger.warning(f"Ollama returned {res.status_code} (attempt {attempt+1}/{max_retries}), body: {res.text[:200]}, waiting {wait_time}s")
                time.sleep(wait_time)
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout on attempt {attempt+1}")
            time.sleep(2 ** attempt)
        except Exception as e:
            logger.warning(f"Request exception: {e}")
            time.sleep(2 ** attempt)
    raise Exception(f"Ollama failed after {max_retries} retries for text: {sanitized[:100]}...")

def split_md_sections(content, filename, rel_path):
    """
    Split markdown by --- and timestamp heading.
    Returns list of dicts with text, anchor, timestamp, and file_url.
    file_url uses HTML_BASE_PATH and .html extension with anchor.
    """
    sections = []
    lines = content.splitlines()
    i = 0
    current_section_lines = []
    current_anchor = None
    current_timestamp = None

    # Prepare HTML file name: basename .md -> .html
    base_name = os.path.basename(filename)
    html_filename = base_name.replace('.md', '.html')
    file_url_base = f"file://{HTML_BASE_PATH.rstrip('/')}/{html_filename}"

    while i < len(lines):
        line = lines[i]
        if line.strip() == '- - -' and i + 1 < len(lines):
            next_line = lines[i+1].strip()
            match = re.match(r'^#####\s+(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})$', next_line)
            if match:
                if current_section_lines:
                    text = '\n'.join(current_section_lines).strip()
                    if text:
                        sections.append({
                            'text': text,
                            'anchor': current_anchor,
                            'timestamp': current_timestamp,
                            'file_url': f"{file_url_base}#{current_anchor}" if current_anchor else None
                        })
                date_str, time_str = match.group(1), match.group(2)
                dt_str = f"{date_str} {time_str}"
                anchor = dt_str.replace(' ', '-').replace(':', '')
                current_anchor = anchor
                current_timestamp = dt_str
                current_section_lines = []
                i += 2
                continue
        current_section_lines.append(line)
        i += 1

    if current_section_lines:
        text = '\n'.join(current_section_lines).strip()
        if text:
            sections.append({
                'text': text,
                'anchor': current_anchor,
                'timestamp': current_timestamp,
                'file_url': f"{file_url_base}#{current_anchor}" if current_anchor else None
            })

    # Further split each section into smaller chunks if needed
    final_chunks = []
    for sec in sections:
        text = sec['text']
        if len(text) > 250:
            sub_chunks = chunk_text_smart(text, max_chars=250)
            for idx, sub in enumerate(sub_chunks):
                final_chunks.append({
                    'text': sub,
                    'anchor': sec['anchor'] + f"_part{idx+1}" if sec['anchor'] else None,
                    'timestamp': sec['timestamp'],
                    'file_url': sec['file_url']  # anchor may not match exactly but fine
                })
        else:
            final_chunks.append(sec)
    return final_chunks

def chunk_text_legacy(text, max_chars=250):
    return chunk_text_smart(text, max_chars)

def parse_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading {filepath}: {e}")
        return ""

def ingest_documents():
    global INDEXING_STATUS
    INDEXING_STATUS["is_indexing"] = True

    if not ensure_ollama_model():
        logger.error("Ollama model not available. Aborting indexing.")
        INDEXING_STATUS["is_indexing"] = False
        return

    client = get_qdrant_client()
    for _ in range(5):
        try:
            if not client.collection_exists(COLLECTION_NAME):
                client.create_collection(COLLECTION_NAME, vectors_config=VectorParams(size=384, distance=Distance.COSINE))
            break
        except Exception as e:
            logger.warning(f"Qdrant not ready: {e}, retrying...")
            time.sleep(3)

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)

    consecutive_failures = 0
    for root, _, files in os.walk(DATA_DIR):
        for filename in files:
            if consecutive_failures >= 10:
                logger.error("Too many consecutive failures, stopping ingestion.")
                break
            path = os.path.join(root, filename)
            rel_path = os.path.relpath(path, DATA_DIR)
            try:
                # Delete existing points for this file
                client.delete(
                    collection_name=COLLECTION_NAME,
                    points_selector=Filter(must=[FieldCondition(key="filepath", match=MatchValue(value=rel_path))])
                )

                content = parse_file(path)
                if not content.strip():
                    continue

                if filename.lower().endswith('.md'):
                    sections = split_md_sections(content, filename, rel_path)
                    for idx, sec in enumerate(sections):
                        if not sec['text'].strip():
                            continue
                        logger.info(f"Processing {rel_path} sub-chunk {idx+1}/{len(sections)}")
                        try:
                            vec = get_embedding_with_retry(sec['text'])
                            chunk_id_str = f"{path}_sec_{idx}_{sec.get('anchor', '')}"
                            doc_id = int(hashlib.md5(chunk_id_str.encode('utf-8')).hexdigest()[:15], 16)
                            payload = {
                                "text": sec['text'],
                                "filepath": rel_path,
                                "anchor": sec.get('anchor'),
                                "timestamp": sec.get('timestamp'),
                                "file_url": sec.get('file_url')
                            }
                            client.upsert(COLLECTION_NAME, [{"id": doc_id, "vector": vec, "payload": payload}])
                            consecutive_failures = 0
                            time.sleep(1)
                        except Exception as e:
                            logger.error(f"Failed to index sub-chunk {idx+1} of {rel_path}: {e}")
                            consecutive_failures += 1
                            if consecutive_failures >= 5:
                                break
                else:
                    # Non-markdown files: keep old behavior, no file_url (or could build one)
                    text = parse_file(path).strip()
                    if not text:
                        continue
                    chunks = chunk_text_legacy(text, max_chars=250)
                    for j, chunk in enumerate(chunks):
                        if not chunk.strip():
                            continue
                        logger.info(f"Processing {filename} chunk {j+1}/{len(chunks)}")
                        try:
                            vec = get_embedding_with_retry(chunk)
                            chunk_id_str = f"{path}_chunk_{j}"
                            doc_id = int(hashlib.md5(chunk_id_str.encode('utf-8')).hexdigest()[:15], 16)
                            payload = {"text": chunk, "filepath": rel_path, "anchor": None, "file_url": None}
                            client.upsert(COLLECTION_NAME, [{"id": doc_id, "vector": vec, "payload": payload}])
                            consecutive_failures = 0
                            time.sleep(1)
                        except Exception as e:
                            logger.error(f"Failed to index chunk {j+1} of {filename}: {e}")
                            consecutive_failures += 1
                            if consecutive_failures >= 5:
                                break
            except Exception as e:
                logger.error(f"Error processing file {rel_path}: {e}")

    logger.info("Background indexing complete.")
    INDEXING_STATUS["is_indexing"] = False

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/status', methods=['GET'])
def status():
    return jsonify(INDEXING_STATUS)

@app.route('/search', methods=['POST'])
def api_search():
    data = request.json
    query = data.get('query', '')
    if not query:
        return jsonify({'error': 'Empty query'}), 400
    try:
        client = get_qdrant_client()
        query_vec = get_embedding_with_retry(query)
        results = client.search(collection_name=COLLECTION_NAME, query_vector=query_vec, limit=5)
        output = []
        for res in results:
            output.append({
                'score': res.score,
                'text': res.payload.get('text', ''),
                'filepath': res.payload.get('filepath', ''),
                'file_url': res.payload.get('file_url')
            })
        return jsonify({'results': output})
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    logger.info("Starting web application...")
    time.sleep(3)
    ingest_thread = threading.Thread(target=ingest_documents)
    ingest_thread.daemon = True
    ingest_thread.start()
    app.run(host="0.0.0.0", port=5000)
