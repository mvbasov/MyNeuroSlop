import os
import re
import sys
import time
import logging
import requests
from qdrant_client import QdrantClient

# Keep version track inside the script
VERSION = "1.2.0"

# Setup basic client logging (suppress verbose messages from third-party libraries)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

# Default configuration matching your local RAG system targets
OLLAMA_URL = "http://localhost:11434"
QDRANT_URL = "http://localhost:6333"
EMBED_MODEL = "nomic-embed-text" 
LLM_MODEL = "qwen2.5:3b"  # Defaulting to the highly capable 3B model
COLLECTION_NAME = "rag_documents"

# Interactive session configuration
session_config = {
    "limit": 3,              # Number of chunks to retrieve from Qdrant by default
    "expand_chars": 1000,    # Character limit for local file context expansion
    "data_dir": "./data",    # Path to the local data directory on the host machine
    "show_sources": True     # Toggle showing sources and context expansion status
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
    Normalizes unicode dash characters and collapses whitespaces
    to guarantee reliable substring mapping across different platforms.
    """
    if not text:
        return ""
    # Standardize different types of hyphens/dashes to standard hyphen
    text = re.sub(r'[\u2012\u2013\u2014\u2212]', '-', text)
    # Collapse multiple whitespaces and newlines into a single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip().lower()


def get_expanded_context(filepath, chunk_text, max_expansion_chars, data_dir):
    """
    Finds the original chunk in the local file on disk and extracts subsequent text
    to restore continuity and coherence for the LLM generation phase.
    """
    if max_expansion_chars <= 0:
        return chunk_text, False, 0, "Expansion disabled"

    # Step 1: Clean filepath from anchor tags (e.g., #2026-05-26-155630)
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

        # Normalize carriage returns
        full_content_norm = full_content.replace('\r\n', '\n')
        chunk_text_norm = chunk_text.replace('\r\n', '\n')

        # Try to locate the exact match first
        orig_idx = full_content_norm.find(chunk_text_norm)
        chunk_end_pos = -1
        found = False

        if orig_idx != -1:
            chunk_end_pos = orig_idx + len(chunk_text_norm)
            found = True
        else:
            # Fallback search: find line by line using normalized representations
            chunk_lines = [line.strip() for line in chunk_text_norm.split('\n') if len(line.strip()) >= 10]
            
            # Iterate backwards starting from the last lines of the chunk
            for line in reversed(chunk_lines):
                # Remove leading bullets, numbers, dashes, and extra spaces
                clean_target = re.sub(r'^[·\-\*\s\d\.\)\(]+', '', line).strip()
                clean_target_norm = normalize_text_for_search(clean_target)
                if len(clean_target_norm) < 6:
                    continue

                # Search through lines of the actual file on disk
                file_lines = full_content_norm.split('\n')
                for idx, f_line in enumerate(file_lines):
                    f_line_clean = re.sub(r'^[·\-\*\s\d\.\)\(]+', '', f_line).strip()
                    f_line_norm = normalize_text_for_search(f_line_clean)
                    
                    # Substring check of the normalized text
                    if clean_target_norm in f_line_norm or f_line_norm in clean_target_norm:
                        # Re-calculate character offset on disk
                        char_pos = sum(len(l) + 1 for l in file_lines[:idx]) + len(f_line)
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
        # Supports both standard '---' and spaced '- - -' horizontal rules, as well as date/time separators
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


def chat_with_docs(query):
    """Performs semantic vector retrieval, aggregates/expands context, and queries the LLM."""
    try:
        query_vec = get_embedding_with_retry(query)
        results = qdrant_client.search(
            collection_name=COLLECTION_NAME, 
            query_vector=query_vec, 
            limit=session_config["limit"]
        )
    except Exception as e:
        return f"Retrieval phase failure: {str(e)}"
    
    if not results:
        return "I do not have enough information to answer (No matching documents found in vector store)."
        
    context_chunks = []
    
    if session_config["show_sources"]:
        print("\n--- Retrieved Sources ---")

    for i, res in enumerate(results, start=1):
        text = res.payload.get('text', '').strip()
        filepath = res.payload.get('filepath', 'Unknown source')
        
        if not text:
            continue

        # Try to expand this chunk's content from local host filesystem
        expanded_text, was_expanded, added_chars, status_msg = get_expanded_context(
            filepath, 
            text, 
            session_config["expand_chars"], 
            session_config["data_dir"]
        )
        
        if session_config["show_sources"]:
            status_str = f" [Expanded by +{added_chars} chars]" if was_expanded else f" [Original] ({status_msg})"
            print(f"{i}. [{filepath}]{status_str}")
            # Format preview to display clean snippet on single line
            preview = text.replace('\n', ' ')[:80] + "..."
            print(f"   Preview: {preview}")

        context_chunks.append(f"[{filepath}]:\n{expanded_text}")
            
    context = "\n\n".join(context_chunks)
    
    # Strict prompt layout to restrain the LLM to database context fields only
    prompt = (
        f"You are a helpful assistant. Use ONLY the following provided context to answer the question. "
        f"If the answer is not contained within the context, you must state that you do not have enough information to answer. "
        f"Do not use any outside knowledge. Respond in the same language as the context provided.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {query}\n"
        f"Answer:"
    )
    
    try:
        # Generation request with generous timeout limits (useful for 3B model execution on 4 CPUs)
        response = requests.post(f"{OLLAMA_URL}/api/generate", json={
            "model": LLM_MODEL,
            "prompt": prompt,
            "stream": False
        }, timeout=150)
        response.raise_for_status()
        return response.json().get("response", "No answer generated.").strip()
    except Exception as e:
        return f"Generation phase failure: {str(e)}"


def print_help():
    """Prints the list of administrative inline commands."""
    print("\nAvailable commands:")
    print("  /limit <num>      - Set the number of retrieval chunks (currently: {})".format(session_config["limit"]))
    print("  /expand <num>     - Set character limit for file context expansion (currently: {})".format(session_config["expand_chars"]))
    print("  /datadir <path>   - Set the path to local host data directory (currently: {})".format(session_config["data_dir"]))
    print("  /sources          - Toggle showing retrieved source details (currently: {})".format(session_config["show_sources"]))
    print("  /help             - Show this help menu")
    print("  exit / quit       - Exit the interactive CLI session")


def main():
    # Parse command line arguments for data directory override and path mapping
    # Handles execution formats like: python cli_chat_v1_2_0.py /data ../data/
    if len(sys.argv) > 1:
        if len(sys.argv) == 3 and sys.argv[1] == "/data":
            session_config["data_dir"] = sys.argv[2]
            print(f"Path mapping registered: /data -> {session_config['data_dir']}")
        else:
            for arg in sys.argv[1:]:
                if os.path.isdir(arg) or arg.startswith("..") or arg.startswith("."):
                    session_config["data_dir"] = arg
                    print(f"Data directory updated to: {session_config['data_dir']}")
                    break

    print("="*60)
    print(f"--- RAG CLI Chat v{VERSION} ---")
    print("="*60)
    print(f"Connected to Qdrant: {QDRANT_URL} | Collection: {COLLECTION_NAME}")
    print(f"Embedding Engine: Ollama ({EMBED_MODEL}) | LLM: {LLM_MODEL}")
    print(f"Local Context Expansion: ACTIVE (Directory: {session_config['data_dir']})")
    print("Type /help to view configuration parameters.")
    print("-"*60)
    
    while True:
        try:
            query = input("\nYou: ").strip()
            if not query:
                continue
            
            # Catch and parse configuration commands
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
            answer = chat_with_docs(query)
            elapsed = time.time() - start_time
            
            print(f"\nAssistant: {answer}")
            print(f"[Request processing time on CPU: {elapsed:.2f} seconds]")
            
        except KeyboardInterrupt:
            print("\nSession interrupted by user. Exiting.")
            break
        except Exception as e:
            print(f"\nUnexpected internal interface error: {e}")


if __name__ == "__main__":
    main()