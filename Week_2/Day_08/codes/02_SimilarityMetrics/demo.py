"""
02 - Similarity Metrics Demo
============================
Computes cosine, dot product, and Euclidean distance between embedding vectors
and shows why cosine is the right choice for text.

HOW TO RUN THIS FILE:
1. pip install mistralai numpy python-dotenv
2. Copy ../.env.example to ../.env and add your MISTRAL_API_KEY
3. python demo.py
"""

import os
import numpy as np
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# PART 1: Toy Vectors — Build Intuition Without an API
# ============================================================

def show_the_problem():
    """Show how different metrics rank the same pair differently."""
    print("=== PART 1: How Each Metric Behaves ===\n")

    # Two vectors pointing in the same direction but very different lengths
    short = np.array([1.0, 1.0, 1.0])
    long_ = np.array([10.0, 10.0, 10.0])
    other = np.array([1.0, -1.0, 0.5])

    def cosine(a, b):
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    def euclid(a, b):
        return float(np.linalg.norm(a - b))

    print("Pair 1: short vs long (same direction, different magnitude)")
    print(f"  Cosine sim:    {cosine(short, long_):.4f}  (1.0 = identical direction)")
    print(f"  Euclidean:     {euclid(short, long_):.4f}  (large = looks 'far')\n")

    print("Pair 2: short vs other (different direction)")
    print(f"  Cosine sim:    {cosine(short, other):.4f}")
    print(f"  Euclidean:     {euclid(short, other):.4f}\n")

    print("Takeaway: Euclidean is fooled by magnitude. Cosine sees meaning.\n")


# ============================================================
# PART 2: Implement Cosine Similarity From Scratch
# ============================================================

def show_the_solution():
    """Implement the formula step by step."""
    print("=== PART 2: Cosine Similarity Step by Step ===\n")

    a = np.array([0.9, 0.1, 0.2])  # "couscous Tunis"
    b = np.array([0.85, 0.15, 0.25])  # "couscous Sfax"

    dot_ab = float(np.dot(a, b))
    norm_a = float(np.linalg.norm(a))
    norm_b = float(np.linalg.norm(b))
    cosine = dot_ab / (norm_a * norm_b)

    print(f"Vector A (couscous Tunis): {a}")
    print(f"Vector B (couscous Sfax):  {b}")
    print(f"  Dot product A.B:       {dot_ab:.4f}")
    print(f"  Norm |A|:              {norm_a:.4f}")
    print(f"  Norm |B|:              {norm_b:.4f}")
    print(f"  Cosine similarity:     {cosine:.4f}\n")
    print("Very close to 1.0 -> the texts are nearly identical in meaning.\n")


# ============================================================
# PART 3: Real Embeddings — Rank Tunisian Sentences
# ============================================================

def real_world_example():
    """Embed sentences and rank by cosine similarity to a query."""
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("=== PART 3: REAL RANKING (API key required) ===")
        print("Set MISTRAL_API_KEY in codes/.env to run this section.\n")
        return

    try:
        from mistralai.client import Mistral
    except ImportError:
        print("Run: pip install mistralai")
        return

    client = Mistral(api_key=api_key)

    print("=== PART 3: Ranking Documents by Cosine Similarity ===\n")

    documents = [
        "Bilel ate spicy fish couscous in Sfax last night.",
        "Yasmine is studying machine learning in Tunis.",
        "The harissa from Nabeul is famous all over Tunisia.",
        "Mehdi loves seafood tajine on Fridays.",
        "The motorbike traffic in Sousse is intense in summer.",
    ]
    query = "fish dish with hot pepper"

    embed = lambda texts: [
        d.embedding
        for d in client.embeddings.create(model="mistral-embed", inputs=texts).data
    ]

    doc_vectors = np.array(embed(documents))
    query_vector = np.array(embed([query])[0])

    def cosine_batch(q, mat):
        q_norm = q / np.linalg.norm(q)
        mat_norm = mat / np.linalg.norm(mat, axis=1, keepdims=True)
        return mat_norm @ q_norm

    scores = cosine_batch(query_vector, doc_vectors)
    ranked = sorted(zip(scores, documents), reverse=True)

    print(f"Query: '{query}'\n")
    print("Ranked results (highest cosine first):")
    for score, doc in ranked:
        print(f"  {score:.4f} | {doc}")
    print()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    show_the_problem()
    show_the_solution()
    real_world_example()

    print("--- Key Takeaways ---")
    print("1. Cosine similarity ignores magnitude - perfect for text.")
    print("2. Range [-1, 1]; for text embeddings you usually see 0.0 - 1.0.")
    print("3. Dot product == cosine when vectors are normalized (Mistral does this).")
    print("4. Euclidean distance is misled by vector length - avoid for text.")
    print("5. Vector databases use cosine by default - now you know why.")
