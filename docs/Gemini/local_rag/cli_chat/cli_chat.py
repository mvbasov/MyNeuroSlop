import requests
import sys
from qdrant_client import QdrantClient

# Configuration
OLLAMA_URL = "http://localhost:11434"
QDRANT_URL = "http://localhost:6333"
EMBED_MODEL = "all-minilm" # Suggestion: Change to "paraphrase-multilingual" for better non-English retrieval
LLM_MODEL = "qwen2.5:0.5b" 
COLLECTION_NAME = "rag_documents"

qdrant_client = QdrantClient(url=QDRANT_URL)

def get_embedding(text):
    """Generates embedding for a given text using the local Ollama instance."""
    payload = {"model": EMBED_MODEL, "prompt": text}
    response = requests.post(f"{OLLAMA_URL}/api/embeddings", json=payload)
    return response.json()["embedding"]

def chat_with_docs(query):
    """Performs retrieval and generation with a strict context-only prompt."""
    query_vec = get_embedding(query)
    results = qdrant_client.search(
        collection_name=COLLECTION_NAME, 
        query_vector=query_vec, 
        limit=3
    )
    
    context = "\n\n".join([res.payload.get('text', '') for res in results])
    
    # Strict prompt to force reliance on context
    prompt = (
        f"You are a helpful assistant. Use ONLY the following provided context to answer the question. "
        f"If the answer is not contained within the context, you must state that you do not have enough information to answer. "
        f"Do not use any outside knowledge. Respond in the same language as the context provided.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {query}\n"
        f"Answer:"
    )
    
    response = requests.post(f"{OLLAMA_URL}/api/generate", json={
        "model": LLM_MODEL,
        "prompt": prompt,
        "stream": False
    })
    
    return response.json().get("response", "No answer generated.")

def main():
    print("--- RAG CLI Chat (Type 'exit' to quit) ---")
    while True:
        try:
            query = input("\nYou: ")
            if query.lower() in ['exit', 'quit']:
                break
            
            print("Thinking...")
            answer = chat_with_docs(query)
            print(f"\nAssistant: {answer}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()