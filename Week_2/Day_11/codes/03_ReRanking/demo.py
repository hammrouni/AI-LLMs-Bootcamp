"""
03 - Re-Ranking Demo
====================
Shows how re-ranking improves the order of retrieved chunks — first with
Mistral bi-encoder embeddings, then with a real cross-encoder model.

HOW TO RUN THIS FILE:
1. pip install mistralai python-dotenv sentence-transformers
2. Copy ../.env.example to ../.env and add your MISTRAL_API_KEY
3. python demo.py
"""

import os
from dotenv import load_dotenv

load_dotenv()


CANDIDATES = [
    "MASTER Soft is a software engineering company based in Tunis, with a satellite office in Sousse.",
    "Customers on the Pro plan can request a refund within 14 days of purchase, no questions asked.",
    "MASTER Soft builds three products: a CRM platform, a billing API, and a mobile app builder.",
    "Working hours are 9:00 to 18:00 Monday to Friday, with remote work up to 2 days per week.",
    "Vacation policy: employees accrue 2 paid vacation days per month, totalling 24 days per year.",
]

QUERY = "How do I get a refund?"


# ============================================================
# PART 1: The Problem — Bi-Encoder Ranking
# ============================================================

def show_the_problem():
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("=== PART 1: BI-ENCODER RANKING (API key required) ===")
        print("Set MISTRAL_API_KEY in codes/.env to run this section.\n")
        return

    try:
        from mistralai.client import Mistral
    except ImportError:
        print("Run: pip install mistralai")
        return

    print("=== PART 1: Bi-Encoder Ranking (Mistral Embeddings) ===\n")

    from math import sqrt

    def cosine(a, b):
        dot = sum(x * y for x, y in zip(a, b))
        na = sqrt(sum(x * x for x in a))
        nb = sqrt(sum(y * y for y in b))
        return dot / (na * nb)

    client = Mistral(api_key=api_key)
    doc_vecs = [d.embedding for d in client.embeddings.create(model="mistral-embed", inputs=CANDIDATES).data]
    q_vec = client.embeddings.create(model="mistral-embed", inputs=[QUERY]).data[0].embedding

    scored = sorted(
        ((cosine(q_vec, dv), c) for dv, c in zip(doc_vecs, CANDIDATES)),
        reverse=True,
    )

    print(f"Query: {QUERY}\n")
    print("Bi-encoder ranking (cosine similarity):")
    for sim, c in scored:
        print(f"  {sim:.4f} | {c}")
    print("\nBi-encoders embed query and doc separately — fast but coarse.")
    print("The top-1 chunk is not always the most precise answer.\n")


# ============================================================
# PART 2: Solution — Cross-Encoder Re-Ranking
# ============================================================

def show_the_solution():
    try:
        from sentence_transformers import CrossEncoder
    except ImportError:
        print("=== PART 2: CROSS-ENCODER RERANKING ===")
        print("Run: pip install sentence-transformers\n")
        return

    print("=== PART 2: Cross-Encoder Re-Ranking ===\n")

    reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    pairs = [(QUERY, c) for c in CANDIDATES]
    scores = reranker.predict(pairs)

    reranked = sorted(zip(scores, CANDIDATES), reverse=True)

    print(f"Query: {QUERY}\n")
    print("Cross-encoder scoring (query + doc jointly):")
    for s, c in reranked:
        print(f"  {s:+.4f} | {c}")
    print("\nCross-encoder reads (query, doc) together — slower but more accurate.")
    print("The true refund-policy chunk now sits at top-1.\n")


# ============================================================
# PART 3: Full Retrieve → Rerank Pipeline
# ============================================================

def real_world_example():
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("=== PART 3: RETRIEVE + RERANK PIPELINE (API key required) ===")
        print("Set MISTRAL_API_KEY in codes/.env to run this section.\n")
        return

    try:
        from mistralai.client import Mistral
        from sentence_transformers import CrossEncoder
    except ImportError:
        print("Run: pip install mistralai sentence-transformers")
        return

    print("=== PART 3: Full Retrieve → Rerank Pipeline ===\n")

    from math import sqrt

    def cosine(a, b):
        dot = sum(x * y for x, y in zip(a, b))
        na = sqrt(sum(x * x for x in a))
        nb = sqrt(sum(y * y for y in b))
        return dot / (na * nb)

    client = Mistral(api_key=api_key)
    reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    # Step 1: bi-encoder retrieves top-5 (wide net)
    doc_vecs = [d.embedding for d in client.embeddings.create(model="mistral-embed", inputs=CANDIDATES).data]
    q_vec = client.embeddings.create(model="mistral-embed", inputs=[QUERY]).data[0].embedding
    bi_ranked = sorted(range(len(CANDIDATES)), key=lambda i: -cosine(q_vec, doc_vecs[i]))

    print(f"Query: {QUERY}\n")
    print("Step 1 — Bi-encoder top-5 (wide net):")
    for i in bi_ranked:
        print(f"  {cosine(q_vec, doc_vecs[i]):.4f} | {CANDIDATES[i]}")

    # Step 2: cross-encoder reranks, keep top-3
    pairs = [(QUERY, CANDIDATES[i]) for i in bi_ranked]
    scores = reranker.predict(pairs)
    reranked = sorted(zip(scores, bi_ranked), reverse=True)

    print("\nStep 2 — Cross-encoder rerank, keep top-3:")
    for s, i in reranked[:3]:
        print(f"  {s:+.4f} | {CANDIDATES[i]}")
    print("\nPattern: retrieve top-N (cheap), rerank (precise), keep top-k for the LLM.\n")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    show_the_problem()
    show_the_solution()
    real_world_example()

    print("--- Key Takeaways ---")
    print("1. Bi-encoders are fast but coarse — top-1 can be wrong.")
    print("2. Cross-encoders score (query, doc) together — more accurate.")
    print("3. Pattern: retrieve top-20, rerank, keep top-3.")
    print("4. Most apps see a sizeable accuracy lift from reranking.")
    print("5. Skip reranking only if recall is already near 1.0 or latency is critical.")
