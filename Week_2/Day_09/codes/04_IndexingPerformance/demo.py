"""
04 - Indexing & Performance Demo
================================
Benchmarks Qdrant search latency on a synthetic dataset, and shows how to
configure HNSW + payload indexes.

HOW TO RUN THIS FILE:
1. pip install qdrant-client numpy python-dotenv
2. python demo.py
"""

import time
import warnings
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    HnswConfigDiff,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    PayloadSchemaType,
)

DB_PATH = "./qdrant_index_demo"
DIM = 64  # toy dimension for speed
N_VECTORS = 5000


def random_vectors(n, d, seed=0):
    rng = np.random.RandomState(seed)
    return rng.rand(n, d).tolist()


# ============================================================
# PART 1: Problem — Brute-Force Linear Scan
# ============================================================

def show_the_problem():
    """Naive Python brute-force search timing."""
    print("=== PART 1: Brute-Force Linear Scan in Python ===\n")

    vecs = np.array(random_vectors(N_VECTORS, DIM, seed=1))
    query = np.array(random_vectors(1, DIM, seed=2)[0])

    start = time.perf_counter()
    norms = np.linalg.norm(vecs, axis=1) * np.linalg.norm(query)
    sims = (vecs @ query) / norms
    top_k_indices = np.argsort(-sims)[:5]
    elapsed = time.perf_counter() - start

    print(f"Brute-force cosine on {N_VECTORS} vectors x {DIM} dims: {elapsed*1000:.2f} ms")
    print(f"Top 5 indices: {top_k_indices.tolist()}")
    print("Imagine scaling this to 1M vectors and 1024 dims -> way too slow.\n")


# ============================================================
# PART 2: Solution — Qdrant With HNSW
# ============================================================

def show_the_solution():
    """Insert the same vectors into Qdrant and time a search."""
    print("=== PART 2: HNSW Index Search ===\n")

    client = QdrantClient(path=DB_PATH)

    if client.collection_exists("bench"):
        client.delete_collection("bench")
    client.create_collection(
        collection_name="bench",
        vectors_config=VectorParams(
            size=DIM,
            distance=Distance.COSINE,
            hnsw_config=HnswConfigDiff(m=16, ef_construct=200),
        ),
    )

    vecs = random_vectors(N_VECTORS, DIM, seed=1)
    points = [
        PointStruct(id=i, vector=v, payload={"region": "Tunis" if i % 2 else "Sfax"})
        for i, v in enumerate(vecs)
    ]
    # Upsert in batches of 500
    for i in range(0, len(points), 500):
        client.upsert(collection_name="bench", points=points[i : i + 500])

    query = random_vectors(1, DIM, seed=2)[0]

    start = time.perf_counter()
    results = client.query_points(collection_name="bench", query=query, limit=5).points
    elapsed = time.perf_counter() - start

    print(f"HNSW search on {N_VECTORS} vectors: {elapsed*1000:.2f} ms")
    print(f"Top 5 ids: {[r.id for r in results]}")
    print("Scales to millions of vectors with similar latency.\n")

    client.close()


# ============================================================
# PART 3: Payload Index for Faster Filtered Queries
# ============================================================

def real_world_example():
    """Compare filtered query before and after indexing the metadata field."""
    print("=== PART 3: Payload Index Speedup ===\n")

    client = QdrantClient(path=DB_PATH)
    query = random_vectors(1, DIM, seed=2)[0]

    filt = Filter(must=[FieldCondition(key="region", match=MatchValue(value="Tunis"))])

    # Before payload index
    start = time.perf_counter()
    _ = client.query_points("bench", query=query, query_filter=filt, limit=5)
    before = time.perf_counter() - start

    # Create payload index on 'region' (local Qdrant warns this is a no-op —
    # explained in the note printed below)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        client.create_payload_index("bench", field_name="region", field_schema=PayloadSchemaType.KEYWORD)

    # After payload index
    start = time.perf_counter()
    _ = client.query_points("bench", query=query, query_filter=filt, limit=5)
    after = time.perf_counter() - start

    print(f"Filtered search BEFORE payload index: {before*1000:.2f} ms")
    print(f"Filtered search AFTER  payload index: {after*1000:.2f} ms")
    print(
        "\nNote: this script runs Qdrant in LOCAL (file-based) mode, where payload\n"
        "indexes have no effect — timings above may not show a speedup, or may\n"
        "even be noisier 'after'. The index only helps on a real Qdrant SERVER,\n"
        "where it avoids scanning every point's payload to apply the filter.\n"
    )

    client.close()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    show_the_problem()
    show_the_solution()
    real_world_example()

    print("--- Key Takeaways ---")
    print("1. Brute-force search dies past ~100k vectors.")
    print("2. HNSW is the default ANN index — fast at million-scale.")
    print("3. Tune m, ef_construct, ef only when you measure a problem.")
    print("4. Payload indexes make filtered queries fast (region, category...).")
    print("5. Default settings handle 95% of real-world apps.")
