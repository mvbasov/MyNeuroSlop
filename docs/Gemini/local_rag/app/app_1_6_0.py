import os
import re
import time
import requests
import threading
import hashlib
import logging
import json
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, Filter, FieldCondition, MatchValue
from flask import Flask, request, jsonify, render_template_string

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Make third-party HTTP logging switchable off by default
if os.environ.get("ENABLE_HTTP_LOGS", "false").lower() != "true":
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("qdrant_client.http").setLevel(logging.WARNING)

# Versioning bumped to 1.6.0
VERSION = "1.6.0"

# Environment variables
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://ollama:11434")
QDRANT_URL = os.environ.get("QDRANT_URL", "qdrant")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", 6333))
HTML_BASE_PATH = os.environ.get("HTML_BASE_PATH", "/home/mvb/git/OMNotes/html/")  # Base path for file:// links

EMBED_MODEL = "all-minilm"
COLLECTION_NAME = "rag_documents"
DATA_DIR = "/data"
HASH_CACHE_FILE = os.path.join(DATA_DIR, ".indexer_hash_cache.json")

INDEXING_STATUS = {"is_indexing": False}
app = Flask(__name__)

# ---------- HTML TEMPLATE ----------
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
        .score { color: #7f8c8d; font-size: 0.85em; margin-top: 10px; font-weight: bold; }
        .text-snippet { line-height: 1.5; white-space: pre-wrap; font-family: inherit; margin-top: 10px; padding: 10px; background: #f8fafc; border-left: 3px solid #cbd5e1;}
        .metadata-tag { font-size: 0.85em; background: #e2e8f0; padding: 4px 10px; border-radius: 12px; margin-right: 6px; font-weight: normal; color: #1e293b; text-decoration: none; display: inline-block; margin-top: 4px; transition: background 0.2s;}
        .metadata-tag:hover { background: #cbd5e1; }
        .url-link { color: #3498db; text-decoration: none; word-break: break-all; }
        .url-link:hover { text-decoration: underline; }
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
                    
                    // Render File Link
                    let fileDisplay = res.filepath;
                    if (res.file_url) {
                        fileDisplay = `<a href="${res.file_url}" target="_blank">📄 ${res.filepath}</a>`;
                    } else {
                        fileDisplay = `📄 ${res.filepath}`;
                    }
                    
                    // Render Clickable URL from Metadata
                    let urlDisplay = '';
                    if (res.metadata && res.metadata.url && res.metadata.url !== '#') {
                        urlDisplay = `<div style="margin-top: 5px;"><strong>URL:</strong> <a href="${res.metadata.url}" class="url-link" target="_blank">${res.metadata.url}</a></div>`;
                    }
                    
                    // Render Separated Local File:// Tags
                    let tagsDisplay = '';
                    if (res.metadata && res.metadata.tags) {
                        let tags = res.metadata.tags;
                        if (typeof tags === 'string') tags = tags.split(',').map(t => t.trim());
                        
                        if (Array.isArray(tags) && tags.length > 0) {
                            let tagLinks = tags.map(tag => {
                                const tagAnchor = tag.replace(/ /g, '-');
                                const tagUrl = `file:///home/mvb/git/OMNotes/html/Tags.html#${tagAnchor}`;
                                return `<a href="${tagUrl}" class="metadata-tag" target="_blank">🏷️ ${tag}</a>`;
                            }).join('');
                            tagsDisplay = `<div style="margin-top: 10px;"><strong>Tags:</strong><br>${tagLinks}</div>`;
                        }
                    }

                    div.innerHTML = `
                        <div class="filename">${fileDisplay}</div>
                        ${urlDisplay}
                        ${tagsDisplay}
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
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=10)
        if resp.status_code == 200:
            models = resp.json().get("models", [])
            if any(m.get("name", "").startswith(EMBED_MODEL) for m in models):
                logger.info(f"Model {EMBED_MODEL} already present.")
                return True
        logger.info(f"Model {EMBED_MODEL} not found. Pulling...")
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

def sanitize_text(text, max_len=2000):
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    if len(cleaned) > max_len:
        cleaned = cleaned[:max_len].rsplit(' ', 1)[0]
        if len(cleaned) > max_len:
            cleaned = cleaned[:max_len]
    return cleaned.strip()

def chunk_text_smart(text, max_chars=150):
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
        "options": {
            "num_thread": 1,
            "num_ctx": 512
        }
    }
    for attempt in range(max_retries):
        try:
            res = requests.post(f"{OLLAMA_URL}/api/embeddings", json=payload, timeout=90)
            if res.status_code == 200:
                return res.json()["embedding"]
            else:
                wait_time = min(2 ** attempt, 60)
                logger.warning(f"Ollama returned {res.status_code} (attempt {attempt+1}/{max_retries}), waiting {wait_time}s")
                time.sleep(wait_time)
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout on attempt {attempt+1}")
            time.sleep(2 ** attempt)
        except Exception as e:
            logger.warning(f"Request exception: {e}")
            time.sleep(2 ** attempt)
    raise Exception(f"Ollama failed after {max_retries} retries.")

def get_file_url(rel_path, anchor=None):
    rel_path = rel_path.replace('\\', '/')
    if rel_path.lower().endswith('.md'):
        html_path = rel_path[:-3] + '.html'
    else:
        html_path = rel_path
    base = HTML_BASE_PATH.rstrip('/')
    url = f"file://{base}/{html_path}"
    if anchor:
        url += f"#{anchor}"
    return url

def clean_json_string(s):
    """Cleans malformed JSON by removing HTML comments, trailing commas, and invalid escapes."""
    # Remove HTML comments like <!-- Don't edit body below this line -->
    s = re.sub(r'<!--.*?-->', '', s, flags=re.DOTALL)
    # Remove trailing commas before closing brackets/braces
    s = re.sub(r',\s*([\]}])', r'\1', s)
    # Fix invalid backslash escapes (like \m or stray \)
    s = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', s)
    return s

# --- MD5 Cache Management ---
def load_hash_cache():
    if os.path.exists(HASH_CACHE_FILE):
        try:
            with open(HASH_CACHE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read hash cache: {e}")
    return {}

def save_hash_cache(cache):
    try:
        with open(HASH_CACHE_FILE, 'w') as f:
            json.dump(cache, f)
    except Exception as e:
        logger.error(f"Failed to write hash cache: {e}")

def get_file_md5(filepath):
    hash_md5 = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        logger.error(f"Error hashing file {filepath}: {e}")
        return None

# --- Advanced Document Parsing ---
def process_json_item(item, rel_path, global_metadata):
    """Convert JSON struct into a formatted textual chunk with metadata."""
    title = item.get('title', '')
    url = item.get('url', '')
    
    tags = item.get('tags', [])
    tags_str = ', '.join([str(t) for t in tags]) if isinstance(tags, list) else str(tags)
    
    notes = item.get('notes', [])
    notes_str = '\n'.join([str(n) for n in notes]) if isinstance(notes, list) else str(notes)
    
    text_parts = []
    if title: text_parts.append(f"Title: {title}")
    if url: text_parts.append(f"URL: {url}")
    if tags_str: text_parts.append(f"Tags: {tags_str}")
    if notes_str: text_parts.append(f"Notes:\n{notes_str}")
    
    text = '\n'.join(text_parts).strip()
    if not text:
        return []
        
    date_str = item.get('date', '')
    anchor = date_str.replace(' ', '-').replace(':', '') if date_str else None
    
    meta = global_metadata.copy()
    meta.update(item)
    
    return [{
        'text': text,
        'anchor': anchor,
        'timestamp': date_str,
        'file_url': get_file_url(rel_path, anchor),
        'metadata': meta
    }]

def split_md_sections(content, rel_path, global_metadata):
    """Split markdown by '- - -' and timestamp headers."""
    sections = []
    lines = content.splitlines()
    i = 0
    current_section_lines = []
    current_anchor = None
    current_timestamp = None

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
                            'text': text, 'anchor': current_anchor, 'timestamp': current_timestamp,
                            'file_url': get_file_url(rel_path, current_anchor), 'metadata': global_metadata.copy()
                        })
                date_str, time_str = match.group(1), match.group(2)
                dt_str = f"{date_str} {time_str}"
                anchor = dt_str.replace(' ', '-').replace(':', '')
                current_anchor, current_timestamp = anchor, dt_str
                current_section_lines = []
                i += 2
                continue
        current_section_lines.append(line)
        i += 1

    if current_section_lines:
        text = '\n'.join(current_section_lines).strip()
        if text:
            sections.append({
                'text': text, 'anchor': current_anchor, 'timestamp': current_timestamp,
                'file_url': get_file_url(rel_path, current_anchor), 'metadata': global_metadata.copy()
            })

    final_chunks = []
    for sec in sections:
        text = sec['text']
        if len(text) > 150:
            sub_chunks = chunk_text_smart(text, max_chars=150)
            for idx, sub in enumerate(sub_chunks):
                sub_anchor = sec['anchor'] + f"_part{idx+1}" if sec['anchor'] else None
                final_chunks.append({
                    'text': sub, 'anchor': sub_anchor, 'timestamp': sec['timestamp'],
                    'file_url': get_file_url(rel_path, sec['anchor']), 'metadata': sec['metadata']
                })
        else:
            final_chunks.append(sec)
    return final_chunks

def process_file_content(content, rel_path):
    """Master pipeline: Parses JSON entirely, strips Pelican headers, extracts embedded JSON, chunks markdown."""
    chunks = []
    global_metadata = {}
    
    # 1. Attempt to parse entire file as pure JSON
    try:
        data = json.loads(clean_json_string(content))
        if isinstance(data, list):
            for item in data:
                chunks.extend(process_json_item(item, rel_path, global_metadata))
            return chunks
        elif isinstance(data, dict):
            chunks.extend(process_json_item(data, rel_path, global_metadata))
            return chunks
    except json.JSONDecodeError:
        pass # Not a pure JSON file, proceed with Markdown parsing
        
    # 2. Extract Pelican Header Block (Contiguous block of Key: Value at start of file)
    lines = content.splitlines()
    header_end = 0
    is_pelican = True
    for idx, line in enumerate(lines):
        if not line.strip(): 
            header_end = idx
            break
        match = re.match(r'^([A-Za-z_-]+):\s+(.*)$', line)
        if match:
            global_metadata[match.group(1).lower()] = match.group(2)
        else:
            is_pelican = False
            break
            
    if is_pelican and header_end > 0:
        content = '\n'.join(lines[header_end:]).strip()
        
    # 3. Extract Embedded JSON Blocks (```json ... ```)
    json_blocks = re.findall(r'```json\s*(.*?)\s*```', content, re.DOTALL | re.IGNORECASE)
    for block in json_blocks:
        try:
            data = json.loads(clean_json_string(block))
            if isinstance(data, list):
                for item in data:
                    chunks.extend(process_json_item(item, rel_path, global_metadata))
            elif isinstance(data, dict):
                chunks.extend(process_json_item(data, rel_path, global_metadata))
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse embedded JSON in {rel_path}: {e}")
            
    # Strip the JSON blocks from standard markdown parsing so we don't duplicate indexing
    content = re.sub(r'```json\s*.*?\s*```', '', content, flags=re.DOTALL | re.IGNORECASE).strip()

    # 4. Extract Embedded Bookmarks JSON (<script>bookmarks = [...]</script>)
    bookmark_scripts = re.finditer(r'<script[^>]*>\s*bookmarks\s*=\s*(.*?)\s*(?:;)?\s*</script>', content, re.DOTALL | re.IGNORECASE)
    for match in bookmark_scripts:
        block = match.group(1)
        try:
            data = json.loads(clean_json_string(block))
            if isinstance(data, list):
                for item in data:
                    chunks.extend(process_json_item(item, rel_path, global_metadata))
            elif isinstance(data, dict):
                chunks.extend(process_json_item(data, rel_path, global_metadata))
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse bookmarks JSON in {rel_path}: {e}")
            
    # Strip the bookmarks scripts from standard markdown parsing so we don't duplicate indexing
    content = re.sub(r'<script[^>]*>\s*bookmarks\s*=\s*.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE).strip()
    
    # 5. Process remaining Markdown text via Separator Rules
    if content:
        md_chunks = split_md_sections(content, rel_path, global_metadata)
        chunks.extend(md_chunks)
        
    return chunks

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
                # Using size 384 for all-minilm. Change if switching to paraphrase-multilingual.
                client.create_collection(COLLECTION_NAME, vectors_config=VectorParams(size=384, distance=Distance.COSINE))
            break
        except Exception as e:
            logger.warning(f"Qdrant not ready: {e}, retrying...")
            time.sleep(3)

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)

    cache = load_hash_cache()
    current_files = set()
    consecutive_failures = 0

    # Pass 1: Identify all current files
    for root, _, files in os.walk(DATA_DIR):
        for filename in files:
            if filename == ".indexer_hash_cache.json": continue
            path = os.path.join(root, filename)
            rel_path = os.path.relpath(path, DATA_DIR)
            current_files.add(rel_path)

    # Pass 2: Clean up deleted files from Qdrant
    for cached_rel_path in list(cache.keys()):
        if cached_rel_path not in current_files:
            logger.info(f"File {cached_rel_path} was deleted. Removing from index...")
            client.delete(
                collection_name=COLLECTION_NAME,
                points_selector=Filter(must=[FieldCondition(key="filepath", match=MatchValue(value=cached_rel_path))])
            )
            del cache[cached_rel_path]
            save_hash_cache(cache)

    # Pass 3: Process New and Modified files
    for rel_path in current_files:
        if consecutive_failures >= 10:
            logger.error("Too many consecutive failures, stopping ingestion.")
            break
            
        path = os.path.join(DATA_DIR, rel_path)
        file_md5 = get_file_md5(path)
        
        # Check Cache!
        if file_md5 and cache.get(rel_path) == file_md5:
            logger.debug(f"Skipping {rel_path} (Unchanged)")
            continue

        try:
            # Delete old points for this file to prevent duplication on modification
            client.delete(
                collection_name=COLLECTION_NAME,
                points_selector=Filter(must=[FieldCondition(key="filepath", match=MatchValue(value=rel_path))])
            )

            content = parse_file(path)
            if not content.strip():
                cache[rel_path] = file_md5
                continue

            chunks = process_file_content(content, rel_path)
            
            for idx, chunk in enumerate(chunks):
                if not chunk['text'].strip(): continue
                logger.info(f"Indexing {rel_path} chunk {idx+1}/{len(chunks)}")
                try:
                    vec = get_embedding_with_retry(chunk['text'])
                    chunk_id_str = f"{path}_chunk_{idx}_{chunk.get('anchor', '')}"
                    doc_id = int(hashlib.md5(chunk_id_str.encode('utf-8')).hexdigest()[:15], 16)
                    
                    payload = {
                        "text": chunk['text'],
                        "filepath": rel_path,
                        "anchor": chunk.get('anchor'),
                        "timestamp": chunk.get('timestamp'),
                        "file_url": chunk.get('file_url'),
                        "metadata": chunk.get('metadata', {})
                    }
                    client.upsert(COLLECTION_NAME, [{"id": doc_id, "vector": vec, "payload": payload}])
                    consecutive_failures = 0
                    time.sleep(0.5)
                except Exception as e:
                    logger.error(f"Failed to index chunk {idx+1} of {rel_path}: {e}")
                    consecutive_failures += 1
                    if consecutive_failures >= 5: break
                    
            # Successfully indexed! Update cache.
            if file_md5:
                cache[rel_path] = file_md5
                save_hash_cache(cache)
                
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

@app.route('/version', methods=['GET'])
def version():
    return jsonify({"version": VERSION})

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
                'file_url': res.payload.get('file_url'),
                'metadata': res.payload.get('metadata', {})
            })
        return jsonify({'results': output})
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    logger.info(f"Starting web application version {VERSION}...")
    time.sleep(3)
    ingest_thread = threading.Thread(target=ingest_documents)
    ingest_thread.daemon = True
    ingest_thread.start()
    app.run(host="0.0.0.0", port=5000)