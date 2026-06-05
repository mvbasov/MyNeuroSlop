To deploy your completely open-source, local, CPU-optimized RAG system, you will use a highly modular directory structure containing a single Docker Compose file, a Dockerfile, a requirements.txt file, and a custom Python orchestration script (app.py).

By building and starting this stack while the machine is online, the services will automatically fetch and permanently cache the required base images and model weights. Once initialized, you can completely sever the internet connection; the system will remain fully self-sufficient and operational offline.  

File Structure Setup

First, create a parent directory on your Ubuntu 22.04 machine (e.g., local-rag/) and organize your files like this:

local-rag/
├── docker-compose.yml
├── data/
│   └── (Place your.txt,.md,.html, and.svg files here)
└── app/
├── Dockerfile
├── requirements.txt
└── app.py
1. docker-compose.yml

This orchestration file configures three permanent services (qdrant, ollama, and your rag-app) along with a temporary sidecar utility (model-puller) to automatically pull and cache the models while the server is connected to the internet.
YAML

version: '3.8'

services:
  # Vector Database: Optimized for CPU and strictly bounded in memory [3, 4]
  qdrant:
    image: qdrant/qdrant:v1.12.0
    container_name: qdrant
    ports:
      - "6333:6333" # HTTP REST API [4]
    volumes:
      -./qdrant_storage:/qdrant/storage # Persistent storage of vector database index
    environment:
      # Memory Optimization: Payloads and metadata strictly live on disk [5]
      - QDRANT__STORAGE__ON_DISK_PAYLOAD=true
    deploy:
      resources:
        limits:
          cpus: '2' # Bound CPU utilization [6]
          memory: 1024M # Strict RAM ceiling [6]
    restart: unless-stopped

  # Local LLM and Embedding Service
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      -./ollama_storage:/root/.ollama # Caches downloaded model weights on host disk
    deploy:
      resources:
        limits:
          cpus: '4' # Deduplicate or pin CPU resources [7]
    healthcheck:
      test: # Ensures service is ready
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # One-time automated setup sidecar to pre-download model weights
  model-puller:
    image: curlimages/curl:latest
    container_name: model-puller
    depends_on:
      ollama:
        condition: service_healthy # Wait for Ollama service to start up completely
    entrypoint: >
      sh -c "
      echo 'Pulling embedding model (all-minilm)...';
      curl -s -X POST http://ollama:11434/api/pull -d '{\"name\": \"all-minilm\"}' &&
      echo 'Embedding model cached!';
      echo 'Pulling Small Language Model (qwen2.5:0.5b)...';
      curl -s -X POST http://ollama:11434/api/pull -d '{\"name\": \"qwen2.5:0.5b\"}' &&
      echo 'All models cached locally on disk!'
      "
    restart: "no" # Runs once on setup, then shuts down cleanly

  # Custom python RAG Application
  rag-app:
    build:./app
    container_name: rag-app
    depends_on:
      - qdrant
      - ollama
    volumes:
      -./data:/data # Local folder containing HTML, MD, SVG, and TXT files
    stdin_open: true # Keeps standard input open for interactive console chat
    tty: true
    restart: unless-stopped

2. app/Dockerfile

The Dockerfile for your custom RAG orchestrator uses a lightweight base image and installs Python dependencies cleanly.  

Dockerfile

FROM python:3.10-slim

WORKDIR /app

# Prevent python from buffering console outputs
ENV PYTHONUNBUFFERED=1

COPY requirements.txt.
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py.

# Starts the RAG interactive loop
CMD ["python", "app.py"]

3. app/requirements.txt

Declares minimal, highly targeted dependencies to prevent dependency bloat and eliminate library version collisions:

qdrant-client>=1.8.2
beautifulsoup4>=4.11.1
requests>=2.31.0
4. app/app.py

This lightweight, native script manages the entire RAG cycle. It features custom, high-speed document parsers tailored for HTML, Markdown, Plain Text, and XML namespace-aware Scalable Vector Graphics (SVG).
Python

import os
import sys
import time
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# System Constants
DATA_DIR = "/data"
QDRANT_URL = "http://qdrant:6333"
OLLAMA_URL = "http://ollama:11434"
EMBED_MODEL = "all-minilm"
LLM_MODEL = "qwen2.5:0.5b"
COLLECTION_NAME = "local_rag_documents"

client = QdrantClient(url=QDRANT_URL)

def wait_for_services():
    """Wait for database and model initialization to complete before launching."""
    print("Waiting for Qdrant and Ollama to be initialized...")
    while True:
        try:
            client.get_collections()
            response = requests.get(f"{OLLAMA_URL}/api/tags")
            if response.status_code == 200:
                models = [m['name'] for m in response.json().get('models',)]
                # Ollama lists models with a ':latest' tag
                if f"{EMBED_MODEL}:latest" in models or EMBED_MODEL in models:
                    break
            print("Services are online, but models are still downloading. Retrying in 10s...")
        except Exception:
            print("Containers are starting. Retrying connection in 5s...")
        time.sleep(5)

def parse_svg(file_path):
    """Natively extract text components from SVG files, resolving XML namespaces."""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Explicitly map the standard SVG namespace [10]
        namespaces = {'svg': 'http://www.w3.org/2000/svg'}
        
        # Locate text and tspans directly using namespaced lookups [10]
        text_elements = root.findall('.//svg:text', namespaces)
        tspan_elements = root.findall('.//svg:tspan', namespaces)
        
        extracted_texts =
        for el in text_elements:
            if el.text:
                extracted_texts.append(el.text.strip())
        for el in tspan_elements:
            if el.text:
                extracted_texts.append(el.text.strip())
                
        # Robust fallback: use itertext() to scrape strings if namespace differs [11]
        if not extracted_texts:
            extracted_texts = [text.strip() for text in root.itertext() if text.strip()]
            
        return " ".join(extracted_texts).strip()
    except Exception as e:
        print(f"Error parsing SVG {file_path}: {e}")
        return ""

def parse_html(file_path):
    """Parse HTML documents cleanly, discarding scripts, styles and attributes.[12]"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            # Aggressively prune active styling/script blocks to eliminate structural noise
            for s in soup(["script", "style"]):
                s.decompose()
            return soup.get_text(separator=' ', strip=True)
    except Exception as e:
        print(f"Error parsing HTML {file_path}: {e}")
        return ""

def chunk_text(text, chunk_size=600, overlap=120):
    """Partition text cleanly within the model context window.[13, 14]"""
    chunks =
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += (chunk_size - overlap)
    return chunks

def initialize_collection():
    """Verify and initialize the memory-optimized Qdrant Collection."""
    try:
        collections = client.get_collections().collections
        exists = any(c.name == COLLECTION_NAME for c in collections)
        
        if not exists:
            print(f"Initializing Qdrant collection: {COLLECTION_NAME}...")
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=384, # all-minilm features 384 dimensions [14]
                    distance=Distance.COSINE, # Cosine metric
                    on_disk=True # Restricts raw vector footprint strictly to disk [15]
                ),
            )
            print("Collection initialized.")
    except Exception as e:
        print(f"Failed to configure Qdrant collection: {e}")
        sys.exit(1)

def get_embedding(text):
    """Generate floating-point vector representations using local Ollama service."""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": EMBED_MODEL, "prompt": text}
        )
        if response.status_code == 200:
            return response.json().get("embedding")
    except Exception as e:
        print(f"Inference embedding error: {e}")
    return None

def ingest_documents():
    """Scrapes files from the local storage drive and writes database indexes."""
    initialize_collection()
    print("Scanning storage mount directory...")
    
    if not os.path.exists(DATA_DIR):
        print(f"Warning: Mount directory {DATA_DIR} does not exist.")
        return

    files =
    
    for filename in files:
        file_path = os.path.join(DATA_DIR, filename)
        ext = os.path.splitext(filename).[1]lower()
        
        content = ""
        if ext in [".txt", ".md"]:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        elif ext in [".html", ".htm"]:
            content = parse_html(file_path)
        elif ext == ".svg":
            content = parse_svg(file_path)
        else:
            continue # Bypass unsupported formats
            
        if not content.strip():
            continue
            
        print(f"Processing: {filename}...")
        chunks = chunk_text(content)
        
        points =
        for idx, chunk in enumerate(chunks):
            vector = get_embedding(chunk)
            if not vector:
                continue
            
            # Create a unique 64-bit unsigned integer ID using file and chunk index
            point_id = hash(f"{filename}_{idx}") & 0xffffffffffffffff
            points.append({
                "id": point_id,
                "vector": vector,
                "payload": {
                    "source": filename,
                    "chunk_index": idx,
                    "text": chunk
                }
            })
            
        if points:
            # Batch upload values to Qdrant [16]
            client.upsert(
                collection_name=COLLECTION_NAME,
                points=points
            )
            print(f"Ingested {len(points)} chunks from {filename}.")

def retrieve_context(query, limit=3):
    """Fetch nearest-neighbor text segments from Qdrant vector index.[17]"""
    query_vector = get_embedding(query)
    if not query_vector:
        return
        
    search_result = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=limit
    )
    
    return [hit.payload["text"] for hit in search_result]

def run_rag_loop(query, contexts):
    """Run CPU-quantized local LLM synthesis over facts gathered from local files."""
    context_text = "\n---\n".join(contexts)
    prompt = f"""You are a helpful, local RAG assistant. Use the following context elements parsed from local files to answer the user's question truthfully. If the context does not contain the answer, politely respond that you do not know based on the offline document repository.

Context:
{context_text}

Question: {query}
Answer:"""

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": LLM_MODEL,
                "prompt": prompt,
                "stream": True # Stream output tokens back to the user in real time
            },
            stream=True
        )
        
        print("\nAssistant Response: ", end="", flush=True)
        for line in response.iter_lines():
            if line:
                part = line.decode('utf-8')
                try:
                    import json
                    json_data = json.loads(part)
                    print(json_data.get("response", ""), end="", flush=True)
                except Exception:
                    pass
        print("\n")
    except Exception as e:
        print(f"\nGenerative LLM error: {e}")

def main():
    wait_for_services()
    ingest_documents()
    
    print("\n" + "="*60)
    print("Local CPU-Optimized RAG Engine Ready for Offline Queries!")
    print("="*60)
    
    while True:
        try:
            query = input("\nEnter your query (or type 'exit' to quit): ").strip()
            if not query:
                continue
            if query.lower() in ['exit', 'quit']:
                print("Shutting down engine...")
                break
                
            print("Searching vector store...")
            contexts = retrieve_context(query)
            if not contexts:
                print("No relevant context found. Generating general answer...")
            
            run_rag_loop(query, contexts)
        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()

Step-by-Step Installation & Running Guide
Step 1: Initialize Stack (While Online)

Make sure your Ubuntu 22.04 server is online. Navigate to your parent directory (local-rag/) and boot the containers to build your custom orchestrator, download necessary packages, and trigger Ollama's model caches:
Bash

docker compose up -d

Step 2: Verification of Download

You can track the progress of the automated model downloads using:
Bash

docker logs -f model-puller

Once the sidecar states 'All models cached locally on disk!', the initial pulling phase is complete. The sidecar container will safely enter a stopped state and release its resources.
Step 3: Go Offline

At this point, you can completely unplug your internet cable or turn off Wi-Fi. All container images, standard python libraries, and localized GGUF weights reside safely on your system drive.  

Step 4: Feed Documents and Query your RAG

    Put any combination of .txt, .md, .html, or .svg files inside the newly generated ./data/ folder on your host machine.

    Hook into the interactive console terminal of your running RAG container to chat with your local documents:

Bash

docker attach rag-app

The system will automatically recognize the files in your folder, parse them natively using standard XML or Beautiful Soup trees, build the CPU-optimized mathematical embeddings, and allow you to search and generate responses completely locally on your CPU!
