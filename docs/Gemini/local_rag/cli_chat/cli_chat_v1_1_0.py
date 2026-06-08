import requests
import sys
import logging
from qdrant_client import QdrantClient

# Setup basic client logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration matching app.py v1.7.0 targets
OLLAMA_URL = "http://localhost:11434"
QDRANT_URL = "http://localhost:6333"
EMBED_MODEL = "all-minilm" 
LLM_MODEL = "qwen2.5:0.5b" 
COLLECTION_NAME = "rag_documents"

try:
    qdrant_client = QdrantClient(url=QDRANT_URL, timeout=60.0)
except Exception as e:
    logger.error(f"Failed to connect to Qdrant at {QDRANT_URL}: {e}")
    sys.exit(1)

def get_embedding(text):
    """Generates embedding for a given text using the local Ollama instance matching app.py parameters."""
    payload = {
        "model": EMBED_MODEL, 
        "prompt": text,
        "keep_alive": "5m",
        "options": {
            "num_thread": 1,
            "num_ctx": 512
        }
    }
    try:
        response = requests.post(f"{OLLAMA_URL}/api/embeddings", json=payload, timeout=90)
        response.raise_for_status()
        return response.json()["embedding"]
    except Exception as e:
        logger.error(f"Ollama embedding extraction failed: {e}")
        raise e

def chat_with_docs(query):
    """Performs semantic vector retrieval against Qdrant and generates a grounded response via Ollama."""
    try:
        query_vec = get_embedding(query)
        results = qdrant_client.search(
            collection_name=COLLECTION_NAME, 
            query_vector=query_vec, 
            limit=3
        )
    except Exception as e:
        return f"Retrieval phase failure: {str(e)}"
    
    if not results:
        return "I do not have enough information to answer (No matching documents found in vector store)."
        
    # Build text blocks context safely matching the schema saved by your server
    context_chunks = []
    for res in results:
        text = res.payload.get('text', '').strip()
        filepath = res.payload.get('filepath', 'Unknown source')
        if text:
            context_chunks.append(f"[{filepath}]:\n{text}")
            
    context = "\n\n".join(context_chunks)
    
    # Strict prompt architecture to restrict the LLM to database context data fields only
    prompt = (
        f"You are a helpful assistant. Use ONLY the following provided context to answer the question. "
        f"If the answer is not contained within the context, you must state that you do not have enough information to answer. "
        f"Do not use any outside knowledge. Respond in the same language as the context provided.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {query}\n"
        f"Answer:"
    )
    
    try:
        response = requests.post(f"{OLLAMA_URL}/api/generate", json={
            "model": LLM_MODEL,
            "prompt": prompt,
            "stream": False
        }, timeout=120)
        response.raise_for_status()
        return response.json().get("response", "No answer generated.").strip()
    except Exception as e:
        return f"Generation phase failure: {str(e)}"

def main():
    print("--- RAG CLI Chat (Type 'exit' to quit) ---")
    print(f"Connected to Qdrant: {QDRANT_URL} | Collection: {COLLECTION_NAME}")
    print(f"Embedding Engine: Ollama ({EMBED_MODEL}) | LLM: {LLM_MODEL}")
    
    while True:
        try:
            query = input("\nYou: ").strip()
            if not query:
                continue
            if query.lower() in ['exit', 'quit']:
                print("Exiting CLI Chat tool. Goodbye.")
                break
            
            print("Thinking...")
            answer = chat_with_docs(query)
            print(f"\nAssistant: {answer}")
            
        except KeyboardInterrupt:
            print("\nSession interrupted. Exiting.")
            break
        except Exception as e:
            print(f"\nUnexpected internal interface error: {e}")

if __name__ == "__main__":
    main()