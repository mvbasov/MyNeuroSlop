import os
import time
import requests
import threading
import hashlib
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from flask import Flask, request, jsonify, render_template_string

# 1. Read environment variables from docker-compose.yaml
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://ollama:11434")
QDRANT_URL = os.environ.get("QDRANT_URL", "qdrant")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", 6333))

# Model and collection settings
EMBED_MODEL = "all-minilm"
COLLECTION_NAME = "rag_documents"
DATA_DIR = "/data"

# Global state to track indexing
INDEXING_STATUS = {"is_indexing": False}

# Initialize Flask App
app = Flask(__name__)

# --- WEB INTERFACE TEMPLATE ---
HTML_TEMPLATE = """
<!DOCTYPE html>
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
                    setTimeout(checkStatus, 3000); // Check again in 3 seconds
                } else {
                    if (statusDiv.style.display === 'block' && statusDiv.className !== 'status-banner status-ready') {
                        statusDiv.className = 'status-banner status-ready';
                        statusDiv.innerHTML = '✅ Indexing complete!';
                        setTimeout(() => { statusDiv.style.display = 'none'; }, 4000); // Hide after 4 seconds
                    }
                }
            } catch (err) {
                console.error("Failed to fetch status", err);
                setTimeout(checkStatus, 5000);
            }
        }

        // Start checking status as soon as the page loads
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
                    div.innerHTML = `
                        <div class="filename">📄 ${res.filepath}</div>
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
</html>
"""

def get_qdrant_client():
    """Creates a fresh client per thread to prevent connection errors."""
    return QdrantClient(url=f"http://{QDRANT_URL}:{QDRANT_PORT}")

def parse_file(filepath):
    """Function to read text from files."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return ""

def chunk_text(text, max_chars=150):
    """Splits text by character limit to support multi-byte/Asian/Cyrillic characters."""
    return [text[i:i + max_chars] for i in range(0, len(text), max_chars)]

def get_embedding_with_retry(text, retries=10):
    """Call Ollama with retry logic."""
    payload = {
        "model": EMBED_MODEL, 
        "prompt": text,
        "keep_alive": "5m",
        "options": {
            "num_thread": 1
        }
    }
    for i in range(retries):
        try:
            res = requests.post(f"{OLLAMA_URL}/api/embeddings", json=payload, timeout=60)
            if res.status_code == 200:
                return res.json()["embedding"]
            else:
                wait_time = 3 + (i * 2)
                print(f"Ollama returned {res.status_code}, retrying in {wait_time}s...")
        except Exception as e:
            wait_time = 3 + (i * 2)
            print(f"Request failed: {e}, retrying in {wait_time}s...")
        time.sleep(wait_time)
    raise Exception("Ollama failed to generate embedding after all retries")

def ingest_documents():
    """Reads files from the data directory and saves their vectors to Qdrant."""
    global INDEXING_STATUS
    INDEXING_STATUS["is_indexing"] = True
    client = get_qdrant_client() 
    
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(COLLECTION_NAME, vectors_config=VectorParams(size=384, distance=Distance.COSINE))
    
    if not os.path.exists(DATA_DIR):
        print(f"Directory {DATA_DIR} not found. Creating an empty directory.")
        os.makedirs(DATA_DIR, exist_ok=True)

    for root, _, files in os.walk(DATA_DIR):
        for filename in files:
            path = os.path.join(root, filename)
            rel_path = os.path.relpath(path, DATA_DIR)
            try:
                text = parse_file(path).strip()
                if not text: continue
                
                chunks = chunk_text(text, max_chars=150)
                for j, chunk in enumerate(chunks):
                    if not chunk.strip(): continue
                        
                    try:
                        print(f"Processing {filename} (chunk {j+1}/{len(chunks)})...")
                        vec = get_embedding_with_retry(chunk)
                        
                        # Using hashlib ensures a stable ID across restarts
                        chunk_id_str = f"{path}_chunk_{j}"
                        doc_id = int(hashlib.md5(chunk_id_str.encode('utf-8')).hexdigest()[:15], 16)
                        
                        client.upsert(COLLECTION_NAME, [{"id": doc_id, "vector": vec, "payload": {"text": chunk, "filepath": rel_path}}])
                        print(f"Indexed: {rel_path} (chunk {j+1}/{len(chunks)})")
                        time.sleep(2) 
                    except Exception as e:
                        print(f"Failed to index chunk {j+1} of file {rel_path}: {e}")
                        print("Moving to the next chunk...")
            except Exception as e:
                print(f"Error processing file {rel_path}: {e}")
                
    print("Background indexing complete.")
    INDEXING_STATUS["is_indexing"] = False

# --- FLASK ROUTES ---
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/status', methods=['GET'])
def status():
    """Endpoint for the frontend to check if indexing is currently running."""
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
        
        try:
            results = client.search(
                collection_name=COLLECTION_NAME,
                query_vector=query_vec,
                limit=5  
            )
        except AttributeError:
            results = client.query_points(
                collection_name=COLLECTION_NAME,
                query=query_vec,
                limit=5
            ).points
        
        output = []
        for res in results:
            snippet = res.payload.get('text', '').replace('\n', ' ')
            doc_path = res.payload.get('filepath', res.payload.get('filename', 'Unknown document'))
            output.append({
                'score': res.score,
                'text': snippet,
                'filepath': doc_path,
                'filename': doc_path  # Added to prevent browser cache "undefined" errors!
            })
            
        return jsonify({'results': output})
    except Exception as e:
        print(f"Error during search: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    print("Starting web application...")
    print(f"Connecting to Qdrant at {QDRANT_URL}:{QDRANT_PORT}")
    print(f"Connecting to Ollama at {OLLAMA_URL}")
    time.sleep(3) 

    print("Starting background document indexing...")
    ingest_thread = threading.Thread(target=ingest_documents)
    ingest_thread.daemon = True  
    ingest_thread.start()
    
    print("Web server is starting immediately on port 5000!")
    app.run(host="0.0.0.0", port=5000)