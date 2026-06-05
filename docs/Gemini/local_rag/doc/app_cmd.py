import os
import time
import requests
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# 1. Read environment variables defined in docker-compose.yaml
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://ollama:11434")
QDRANT_URL = os.environ.get("QDRANT_URL", "qdrant")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", 6333))

# Model and Collection Config
EMBED_MODEL = "all-minilm"
COLLECTION_NAME = "rag_documents"
DATA_DIR = "/data"

# 2. Initialize Qdrant Client using the Docker network hostname
client = QdrantClient(host=QDRANT_URL, port=QDRANT_PORT)

def parse_file(filepath):
    """Simple helper function to read text from files."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return ""

def chunk_text(text, max_chars=150):
    """Splits text using a small character limit to accommodate multi-byte/Asian characters."""
    return [text[i:i + max_chars] for i in range(0, len(text), max_chars)]

def get_embedding_with_retry(text, retries=10):
    """Call Ollama with retry logic."""
    
    # Adding back strict limits because stability is the priority over speed
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
        time.sleep(wait_time) # Progressive backoff
    raise Exception("Ollama failed to generate embedding after retries")

def ingest_documents():
    """Reads files from the data directory and stores their embeddings in Qdrant."""
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(COLLECTION_NAME, vectors_config=VectorParams(size=384, distance=Distance.COSINE))
    
    # Ensure data directory exists
    if not os.path.exists(DATA_DIR):
        print(f"Directory {DATA_DIR} not found. Creating empty directory.")
        os.makedirs(DATA_DIR, exist_ok=True)

    for root, _, files in os.walk(DATA_DIR):
        for filename in files:
            path = os.path.join(root, filename)
            try:
                text = parse_file(path).strip()
                if not text: continue
                
                # Split into safely sized chunks by characters to strictly avoid token limits
                chunks = chunk_text(text, max_chars=150)
                for j, chunk in enumerate(chunks):
                    # Skip chunks that are purely whitespace to avoid API errors
                    if not chunk.strip():
                        continue
                        
                    try:
                        print(f"Processing {filename} (chunk {j+1}/{len(chunks)})...")
                        vec = get_embedding_with_retry(chunk)
                        
                        # Hash the path and chunk index so it is deterministic
                        doc_id = abs(hash(f"{path}_chunk_{j}")) % (2**63 - 1)
                        
                        client.upsert(COLLECTION_NAME, [{"id": doc_id, "vector": vec, "payload": {"text": chunk}}])
                        print(f"Indexed: {filename} (chunk {j+1}/{len(chunks)})")
                        
                        # Increased sleep time to prioritize stability over speed
                        time.sleep(2) 
                        
                    except Exception as e:
                        # Skip just this chunk, don't fail the whole file!
                        print(f"Failed to index chunk {j+1} of {filename}: {e}")
                        print("Continuing with next chunk...")
                
            except Exception as e:
                print(f"Failed to process file {filename}: {e}")

def main():
    print("Starting RAG Application...")
    print(f"Connecting to Qdrant at {QDRANT_URL}:{QDRANT_PORT}")
    print(f"Connecting to Ollama at {OLLAMA_URL}")
    
    # Let services fully initialize
    time.sleep(3) 

    print("Ingesting documents...")
    ingest_documents()
    print("Ingestion complete!")

    # 3. Interactive loop prevents the container from exiting
    while True:
        try:
            print("\n--- RAG Search ---")
            query = input("Enter search query (or 'exit' to quit): ")
            
            if query.lower() in ['quit', 'exit']:
                print("Exiting...")
                break
                
            if not query.strip():
                continue
                
            query_vec = get_embedding_with_retry(query)
            
            results = client.search(
                collection_name=COLLECTION_NAME,
                query_vector=query_vec,
                limit=3
            )
            
            print("\nTop Results:")
            for res in results:
                # Print score and a snippet of the found text
                snippet = res.payload.get('text', '')[:200].replace('\n', ' ')
                print(f"[Score: {res.score:.4f}] {snippet}...")
                
        except EOFError:
            # Handles background execution smoothly if TTY isn't attached yet
            time.sleep(5)
        except Exception as e:
            print(f"Error during search: {e}")

if __name__ == "__main__":
    main()