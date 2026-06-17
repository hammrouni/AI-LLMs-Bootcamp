"""
04 - Hybrid Search Demo
=======================
Compares vector search, BM25 keyword search, and hybrid (RRF) on the
MASTER Soft corpus to show how combining both improves retrieval.

HOW TO RUN THIS FILE:
1. pip install rank-bm25 chromadb mistralai python-dotenv
2. Copy ../.env.example to ../.env and add your MISTRAL_API_KEY
3. python demo.py
"""

import os
import shutil
from dotenv import load_dotenv

load_dotenv()

DB_PATH = "./chroma_hybrid_demo"

DOCS = [
    "MASTER Soft is a software engineering company based in Tunis, with a satellite office in Sousse.",
    "Customers on the Pro plan can request a refund within 14 days of purchase, no questions asked.",
    "MASTER Soft builds three products: a CRM platform, a billing API, and a mobile app builder.",
    "Working hours are 9:00 to 18:00 Monday to Friday. Remote work is allowed up to 2 days per week.",
    "Vacation policy: employees accrue 2 paid vacation days per month, totalling 24 days per year.",
    "Khaled leads the engineering team, based in the Sousse office.",
    "The CRM platform is the flagship product, used by over 500 businesses across Tunisia.",
    "Yasmine Ben Ali is the head of customer success. Contact her for refund escalations.",
]


def _cosine(a, b):
    from math import sqrt
    dot = sum(x * y for x, y in zip(a, b))
    na = sqrt(sum(x * x for x in a))
    nb = sqrt(sum(y * y for y in b))
    return dot / (na * nb)


def bm25_index(docs):
    from rank_bm25 import BM25Okapi
    return BM25Okapi([d.lower().split() for d in docs])


def bm25_search(bm25, query, k=5):
    scores = bm25.get_scores(query.lower().split())
    return sorted(range(len(scores)), key=lambda i: -scores[i])[:k]


def rrf_merge(rankings, k=60, top_k=3):
    score = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, start=1):
            score[doc_id] = score.get(doc_id, 0) + 1.0 / (k + rank)
    return [d for d, _ in sorted(score.items(), key=lambda x: -x[1])[:top_k]]


# ============================================================
# PART 1: Vector vs BM25 — Different Rankings
# ============================================================

def show_the_problem():
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("=== PART 1: VECTOR vs BM25 (API key required) ===")
        print("Set MISTRAL_API_KEY in codes/.env to run this section.\n")
        return

    try:
        from mistralai.client import Mistral
        from rank_bm25 import BM25Okapi  # noqa: F401
    except ImportError:
        print("Run: pip install mistralai rank-bm25")
        return

    print("=== PART 1: Vector vs BM25 — Different Rankings ===\n")

    mistral = Mistral(api_key=api_key)
    doc_vecs = [d.embedding for d in mistral.embeddings.create(model="mistral-embed", inputs=DOCS).data]
    bm25 = bm25_index(DOCS)

    query = "Who handles refund escalations at MASTER Soft?"
    q_vec = mistral.embeddings.create(model="mistral-embed", inputs=[query]).data[0].embedding
    vec_top = sorted(range(len(DOCS)), key=lambda i: -_cosine(q_vec, doc_vecs[i]))[:3]
    bm25_top = bm25_search(bm25, query, k=3)

    print(f"Query: '{query}'\n")

    print("Vector top-3 (by meaning):")
    for i in vec_top:
        print(f"  [{i}] {DOCS[i]}")

    print(f"\nBM25 top-3 (by keywords):")
    for i in bm25_top:
        print(f"  [{i}] {DOCS[i]}")

    if set(vec_top) != set(bm25_top):
        only_vec = set(vec_top) - set(bm25_top)
        only_bm25 = set(bm25_top) - set(vec_top)
        print(f"\n  Vector found {only_vec} that BM25 missed")
        print(f"  BM25 found {only_bm25} that vector missed")

    print("\nEach method has blind spots. Hybrid combines both.\n")


# ============================================================
# PART 2: Solution — Hybrid Search With RRF
# ============================================================

def show_the_solution():
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("=== PART 2: HYBRID SEARCH (API key required) ===")
        print("Set MISTRAL_API_KEY in codes/.env to run this section.\n")
        return

    try:
        from mistralai.client import Mistral
        from rank_bm25 import BM25Okapi  # noqa: F401
    except ImportError:
        print("Run: pip install mistralai rank-bm25")
        return

    print("=== PART 2: Hybrid Search With RRF ===\n")

    mistral = Mistral(api_key=api_key)
    doc_vecs = [d.embedding for d in mistral.embeddings.create(model="mistral-embed", inputs=DOCS).data]
    bm25 = bm25_index(DOCS)

    query = "Who handles refund escalations at MASTER Soft?"
    q_vec = mistral.embeddings.create(model="mistral-embed", inputs=[query]).data[0].embedding
    vec_top = sorted(range(len(DOCS)), key=lambda i: -_cosine(q_vec, doc_vecs[i]))[:5]
    bm25_top = bm25_search(bm25, query, k=5)
    merged = rrf_merge([vec_top, bm25_top], top_k=3)

    print(f"Query: '{query}'\n")
    print(f"Vector top-3: {vec_top[:3]}  |  BM25 top-3: {bm25_top[:3]}  |  Hybrid top-3: {merged}\n")
    for i in merged:
        print(f"  [{i}] {DOCS[i]}")
    print("\nRRF boosts docs that appear in both rankings.\n")


# ============================================================
# PART 3: Multiple Queries — Hybrid in Action
# ============================================================

def real_world_example():
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("=== PART 3: MULTI-QUERY HYBRID (API key required) ===")
        print("Set MISTRAL_API_KEY in codes/.env to run this section.\n")
        return

    try:
        import chromadb
        from mistralai.client import Mistral
        from rank_bm25 import BM25Okapi  # noqa: F401
    except ImportError:
        print("Run: pip install chromadb mistralai rank-bm25")
        return

    print("=== PART 3: Hybrid Search on Multiple Queries ===\n")

    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)

    mistral = Mistral(api_key=api_key)
    chroma = chromadb.PersistentClient(path=DB_PATH)
    collection = chroma.get_or_create_collection("docs")

    vectors = [d.embedding for d in mistral.embeddings.create(model="mistral-embed", inputs=DOCS).data]
    collection.add(documents=DOCS, embeddings=vectors, ids=[f"d{i}" for i in range(len(DOCS))])
    bm25 = bm25_index(DOCS)

    queries = [
        "Who handles refund escalations at MASTER Soft?",
        "What products does the company build?",
        "Is remote work allowed?",
    ]

    for q in queries:
        q_vec = mistral.embeddings.create(model="mistral-embed", inputs=[q]).data[0].embedding
        vec_results = collection.query(query_embeddings=[q_vec], n_results=5)
        vec_ids = [int(i[1:]) for i in vec_results["ids"][0]]
        bm_ids = bm25_search(bm25, q, k=5)
        merged = rrf_merge([vec_ids, bm_ids], top_k=3)

        print(f"Q: {q}")
        print(f"  Vector: {vec_ids[:3]}  BM25: {bm_ids[:3]}  Hybrid: {merged}")
        print(f"  -> {DOCS[merged[0]][:70]}...")
        print()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    show_the_problem()
    show_the_solution()
    real_world_example()

    print("--- Key Takeaways ---")
    print("1. Vector search finds meaning; BM25 finds exact words.")
    print("2. Each method has blind spots the other covers.")
    print("3. RRF fuses rankings without tuning any parameter.")
    print("4. Hybrid + reranking = production-grade retrieval stack.")
    print("5. Cost: one BM25 index in memory, ~ms per query.")
