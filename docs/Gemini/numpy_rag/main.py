import os
import sys

# 1. Force strict offline mode & suppress progress animations
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TQDM_DISABLE"] = "1"

import json
import re
import urllib.request
import numpy as np
from sentence_transformers import SentenceTransformer

# System Configuration
DOCS_DIR = "./md"
VECTORS_FILE = "embeddings.npy"
METADATA_FILE = "chunks_metadata.json"
STATE_FILE = "indexer_state.json"

OLLAMA_URL = "http://localhost:11434/api/generate"
LLM_MODEL = "qwen2.5:3b"

# Lazy-loaded model to keep startup fast when not embedding
_model = None


def get_model():
    global _model
    if _model is None:
        from transformers import logging as transformers_logging

        transformers_logging.set_verbosity_error()
        _model = SentenceTransformer("intfloat/multilingual-e5-small")
        _model.show_progress_bar = False
    return _model


def parse_and_chunk_markdown(file_path, filename):
    """Parses Pelican Markdown headers and cuts by date markers."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    body_start_idx = 0
    for i, line in enumerate(lines):
        if line.strip() == "" or (
            ":" not in line and not line.startswith("- - -")
        ):
            body_start_idx = i
            break
    body_content = "\n".join(lines[body_start_idx:])

    pattern = r"- - -\s*\n#####\s+\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}"
    markers = re.findall(pattern, body_content)
    sections = re.split(pattern, body_content)
    chunks = []

    if not markers:
        text = body_content.strip()
        if text:
            chunks.append(
                {"source_file": filename, "pseudo_title": "Main", "text": text}
            )
    else:
        if sections[0].strip():
            chunks.append(
                {
                    "source_file": filename,
                    "pseudo_title": "Intro",
                    "text": sections[0].strip(),
                }
            )
        for i, section_text in enumerate(sections[1:]):
            text = section_text.strip()
            if text:
                clean_marker = (
                    markers[i].replace("- - -", "").replace("#", "").strip()
                )
                chunks.append(
                    {
                        "source_file": filename,
                        "pseudo_title": f"Log {clean_marker}",
                        "text": text,
                    }
                )
    return chunks


def check_for_changes():
    """Recursively scans all subfolders to detect file changes."""
    if not os.path.exists(DOCS_DIR):
        return False

    current_state = {}
    for root, dirs, files in os.walk(DOCS_DIR):
        for filename in files:
            if filename.endswith(".md") or filename.endswith(".markdown"):
                full_path = os.path.join(root, filename)
                current_state[full_path] = os.path.getmtime(full_path)

    if not os.path.exists(STATE_FILE) or not os.path.exists(VECTORS_FILE):
        return True

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            saved_state = json.load(f)
    except Exception:
        return True

    return current_state != saved_state


def save_current_state():
    """Saves deep relative paths and modification timestamps to disk."""
    current_state = {}
    if os.path.exists(DOCS_DIR):
        for root, dirs, files in os.walk(DOCS_DIR):
            for filename in files:
                if filename.endswith(".md") or filename.endswith(".markdown"):
                    full_path = os.path.join(root, filename)
                    current_state[full_path] = os.path.getmtime(full_path)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(current_state, f, ensure_ascii=False)


def build_index(force=False):
    """Deep-scans subdirectories and encodes chunks only on valid data modifications."""
    if not force and not check_for_changes():
        print("No document changes detected. Index is up to date.")
        return False

    print(
        "Changes detected! Re-indexing markdown pseudo-files across all folder depths..."
    )
    all_chunks = []
    if not os.path.exists(DOCS_DIR):
        print(f"Error: Folder '{DOCS_DIR}' not found.")
        return False

    for root, dirs, files in os.walk(DOCS_DIR):
        for filename in files:
            if filename.endswith(".md") or filename.endswith(".markdown"):
                full_path = os.path.join(root, filename)
                # Extract the direct parent directory name
                parent_folder = os.path.basename(root) if os.path.basename(root) else "Root"
                # Prefix the filename with the folder name for clearer tracking
                display_name = f"{parent_folder}/{filename}"
                all_chunks.extend(parse_and_chunk_markdown(full_path, display_name))

    if not all_chunks:
        print("No text data found to vector map.")
        return False

    print(f"Total chunks extracted for embedding: {len(all_chunks)}")
    prepared_texts = [f"passage: {chunk['text']}" for chunk in all_chunks]

    embed_model = get_model()
    embeddings = embed_model.encode(
        prepared_texts, convert_to_tensor=False, normalize_embeddings=True
    )

    np.save(VECTORS_FILE, embeddings)
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    save_current_state()
    print("Index successfully built and cached deeply.")
    return True

# 1. Add top_k=7 (or whatever number you want) as a default parameter
def run_rag_query_in_memory(query_str, embeddings, chunks, embed_model, top_k=5):
    """Executes vector cross-lingual retrieval using pre-loaded RAM structures."""
    query_vector = embed_model.encode(
        f"query: {query_str}", convert_to_tensor=False, normalize_embeddings=True
    )

    # Vector calculation instantly over memory array
    similarities = np.dot(embeddings, query_vector)
    
    # 2. Use the dynamic top_k parameter here instead of a hardcoded number
    actual_top_k = min(top_k, len(chunks))
    top_indices = np.argsort(similarities)[::-1][:actual_top_k]

    context_str = ""
    print("\n[Retrieved Context Data]")
    for i, idx in enumerate(top_indices, 1):
        hit = chunks[idx]
        context_str += f"--- CONTEXT BLOCK #{i} (File: {hit['source_file']} | {hit['pseudo_title']}) ---\n{hit['text']}\n\n"
        print(f" -> Hit #{i}: {hit['source_file']} ({hit['pseudo_title']}) | Score: {similarities[idx]:.4f}")

    system_instruction = (
        "You are a strict local RAG engine. Use ONLY the provided context blocks to answer "
        "the user question. If the information is missing, say you don't know. "
        "Answer in the exact language used by the user query."
    )

    payload = {
        "model": LLM_MODEL,
        "prompt": f"{system_instruction}\n\nContext:\n{context_str}\nQuestion: {query_str}\nAnswer:",
        "stream": True,
    }

    print("\n[Ollama Streaming Output]: ", end="", flush=True)
    try:
        req = urllib.request.Request(
            OLLAMA_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as response:
            for line in response:
                if line:
                    print(
                        json.loads(line.decode("utf-8")).get("response", ""),
                        end="",
                        flush=True,
                    )
        print("\n" + "=" * 60 + "\n")
    except Exception as e:
        print(
            f"\nAPI Error: Could not talk to Ollama ({e}). Make sure your Docker container is running."
        )


def start_interactive_chat():
    """Loads all disk assets to RAM exactly once and stays open for endless queries."""
    if not os.path.exists(VECTORS_FILE) or not os.path.exists(METADATA_FILE):
        print(
            "Vector database files missing. Running an initial indexing pass first..."
        )
        build_index(force=True)

    print("Loading embedding model and system memory vectors into RAM...")
    embed_model = get_model()
    cached_embeddings = np.load(VECTORS_FILE)

    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        cached_chunks = json.load(f)

    print(
        f"Database Ready! Loaded {len(cached_chunks)} chunks completely in memory."
    )
    print("Type your questions below. Type 'exit' or 'quit' to stop.\n")

    while True:
        try:
            user_query = input("RAG Chat Engine> ").strip()
            if not user_query:
                continue
            if user_query.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            # Run search instantly using data structures already inside RAM
            run_rag_query_in_memory(
                user_query, cached_embeddings, cached_chunks, embed_model
            )

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--index":
        build_index(force=True)
    else:
        # Check files for changes at startup before entering RAM loop
        build_index(force=False)
        start_interactive_chat()

