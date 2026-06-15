"""
03 - Batch Operations Demo
==========================
Compares one-by-one indexing vs batched indexing on a Tunisian-product dataset,
measuring time taken.

HOW TO RUN THIS FILE:
1. pip install chromadb mistralai python-dotenv
2. Copy ../.env.example to ../.env and add your MISTRAL_API_KEY (for PART 3)
3. python demo.py
"""

import os
import time
import shutil
import random
from dotenv import load_dotenv

load_dotenv()

DB_PATH = "./chroma_batch_demo"


def make_fake_products(n=500):
    regions = ["Tunis", "Sfax", "Sousse", "Nabeul", "Kairouan", "Tozeur"]
    categories = ["wallet", "ceramic", "wood", "rug", "jewelry"]
    products = []
    for i in range(n):
        products.append(
            {
                "id": f"p{i:04d}",
                "text": f"Tunisian {random.choice(categories)} #{i} from {random.choice(regions)}",
                "meta": {"region": random.choice(regions), "price": random.randint(20, 400)},
            }
        )
    return products


def chunked(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


# ============================================================
# PART 1: Problem — One-at-a-Time Inserts
# ============================================================

def show_the_problem():
    """Insert 200 fake products one by one and time it."""
    print("=== PART 1: One-at-a-Time Inserts ===\n")

    import chromadb

    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)
    client = chromadb.PersistentClient(path=DB_PATH)
    coll = client.create_collection("one_by_one")

    products = make_fake_products(200)

    start = time.perf_counter()
    for p in products:
        coll.add(documents=[p["text"]], metadatas=[p["meta"]], ids=[p["id"]])
    elapsed = time.perf_counter() - start

    print(f"Inserted {coll.count()} products one-by-one in {elapsed:.2f}s")
    print("(Each .add() call is a separate write to the DB.)\n")


# ============================================================
# PART 2: Solution — Batched Inserts
# ============================================================

def show_the_solution():
    """Insert the same 200 products in batches of 50 and time it."""
    print("=== PART 2: Batched Inserts (batch=50) ===\n")

    import chromadb

    client = chromadb.PersistentClient(path=DB_PATH)
    if "batched" in [c.name for c in client.list_collections()]:
        client.delete_collection("batched")
    coll = client.create_collection("batched")

    products = make_fake_products(200)

    start = time.perf_counter()
    for batch in chunked(products, 50):
        coll.add(
            documents=[p["text"] for p in batch],
            metadatas=[p["meta"] for p in batch],
            ids=[p["id"] for p in batch],
        )
    elapsed = time.perf_counter() - start

    print(f"Inserted {coll.count()} products in batches in {elapsed:.2f}s")
    print("Same data, far fewer DB writes.\n")


# ============================================================
# PART 3: Real Batching With Mistral Embeddings
# ============================================================

def real_world_example():
    """Compare 1-per-call vs 50-per-call embedding API behavior."""
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("=== PART 3: REAL EMBEDDINGS (API key required) ===")
        print("Set MISTRAL_API_KEY in codes/.env to run this section.\n")
        return

    try:
        from mistralai.client import Mistral
    except ImportError:
        print("Run: pip install mistralai")
        return

    print("=== PART 3: Batched Embedding Calls (Mistral) ===\n")

    mistral = Mistral(api_key=api_key)
    texts = [f"Product description {i} from a Tunisian shop" for i in range(50)]

    # --- One by one ---
    start = time.perf_counter()
    one_by_one_vectors = []
    for t in texts[:10]:  # only 10 to keep cost low
        vec = mistral.embeddings.create(model="mistral-embed", inputs=[t])
        one_by_one_vectors.append(vec.data[0].embedding)
    elapsed_one = time.perf_counter() - start
    print(f"10 one-by-one calls: {elapsed_one:.2f}s")

    # --- Batched ---
    start = time.perf_counter()
    batched = mistral.embeddings.create(model="mistral-embed", inputs=texts[:50])
    batched_vectors = [d.embedding for d in batched.data]
    elapsed_batch = time.perf_counter() - start
    print(f"50 in one batch:     {elapsed_batch:.2f}s")

    print(f"\nResult: {len(batched_vectors)} vectors of dim {len(batched_vectors[0])}.\n")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    show_the_problem()
    show_the_solution()
    real_world_example()

    print("--- Key Takeaways ---")
    print("1. Batching cuts both DB writes and API calls.")
    print("2. Mistral embeddings: 50-100 inputs per call is a good default.")
    print("3. ChromaDB add() accepts lists — pass them all at once.")
    print("4. Always wrap batches in a small helper like chunked(seq, size).")
    print("5. On rate-limit errors, retry the batch with exponential backoff.")
