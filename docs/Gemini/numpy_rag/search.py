import os
import sys

# Suppress progress animations and force offline checking for the embed model
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TQDM_DISABLE"] = "1"

import json
import numpy as np
from sentence_transformers import SentenceTransformer

# Index storage locations
VECTORS_FILE = "embeddings.npy"
METADATA_FILE = "chunks_metadata.json"


def run_pure_search(query_str, top_k=5):
    """Loads weights and scans the vector space using optimized matrix dot product."""
    if not os.path.exists(VECTORS_FILE) or not os.path.exists(METADATA_FILE):
        print(
            "Error: Database index files missing. Run 'python main.py --index' first."
        )
        return

    # 1. Load your local vector database files instantly into RAM
    embeddings = np.load(VECTORS_FILE)
    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    # 2. Spin up the tiny ~118M parameter embedding model locally
    from transformers import logging as transformers_logging

    transformers_logging.set_verbosity_error()
    model = SentenceTransformer("intfloat/multilingual-e5-small")
    model.show_progress_bar = False

    # 3. Vectorize user text query using the mandatory E5 format instruction
    query_vector = model.encode(
        f"query: {query_str}", convert_to_tensor=False, normalize_embeddings=True
    )

    # 4. Perform vector similarity lookup via NumPy matrix manipulation
    similarities = np.dot(embeddings, query_vector)
    actual_top_k = min(top_k, len(chunks))
    top_indices = np.argsort(similarities)[::-1][:actual_top_k]

    # 5. Output structured search fragments to the terminal window
    print(f"\nSearch Results for: '{query_str}'")
    print("=" * 70)

    for i, idx in enumerate(top_indices, 1):
        hit = chunks[idx]
        score = similarities[idx]

        print(
            f"Hit #{i} | Match Score: {score:.4f} | File: {hit['source_file']} ({hit['pseudo_title']})"
        )
        print("-" * 70)
        # Indent the matching file content snippet to make it scannable
        indented_text = "\n".join(f"  {line}" for line in hit["text"].split("\n"))
        print(indented_text)
        print("=" * 70)


if __name__ == "__main__":
    # Ensure a search string was provided via terminal argument
    if len(sys.argv) < 2:
        print("Usage: python search.py \"your search query terms here\"")
        sys.exit(0)

    # Take everything passed in arguments as a single query string
    user_query = " ".join(sys.argv[1:])
    run_pure_search(user_query, top_k=4)

