"""
01 - What Are Embeddings Demo
=============================
Shows how text is converted into a vector of numbers using Mistral's embedding model,
and how those vectors capture meaning across languages.

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
# PART 1: The Problem — Keyword Search Fails on Meaning
# ============================================================

def show_the_problem():
    """Show why exact-string matching is not enough."""
    print("=== PART 1: Why Keyword Search Fails ===\n")

    documents = [
        "Kouskosi bel hout men Sfax",
        "Couscous au poisson — recette de Tunis",
        "Tajine malsouka with eggs and cheese",
        "Harissa paste from Nabeul",
    ]

    query = "couscous au poisson"

    print(f"User query: '{query}'\n")
    print("Naive keyword match:")
    for doc in documents:
        match = query.lower() in doc.lower()
        print(f"  {'YES' if match else 'NO '} | {doc}")

    print("\nProblem: 'Kouskosi bel hout' means the same thing but matches NOTHING.\n")


# ============================================================
# PART 2: The Solution — Embed Text Into Vectors
# ============================================================

def show_the_solution():
    """Demonstrate what an embedding looks like (simulated, no API)."""
    print("=== PART 2: What a Vector Looks Like ===\n")

    fake_embedding = np.random.RandomState(42).rand(1024).round(4)

    print("An embedding is a list of numbers like this:")
    print(f"  First 10 values: {fake_embedding[:10].tolist()}")
    print(f"  Total length:    {len(fake_embedding)} (Mistral uses 1024)\n")
    print("Each number captures a tiny piece of meaning.")
    print("Texts with similar meaning have similar vectors.\n")


# ============================================================
# PART 3: Real Embeddings With Mistral
# ============================================================

def real_world_example():
    """Embed real Tunisian texts and show the vectors."""
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

    client = Mistral(api_key=api_key)

    print("=== PART 3: Real Mistral Embeddings ===\n")

    texts = [
        "Bilel loves couscous from Sfax",
        "Yasmine eats kouskousi every Friday in Tunis",
        "The weather in Sousse is hot today",
    ]

    print("Embedding 3 sentences in a single batch call...\n")

    response = client.embeddings.create(
        model="mistral-embed",
        inputs=texts,
    )

    for i, item in enumerate(response.data):
        vec = item.embedding
        print(f"[{i}] '{texts[i]}'")
        print(f"    Dimensions: {len(vec)}")
        print(f"    Preview:    {vec[:5]}\n")

    print("Note: sentences 0 and 1 talk about couscous - their vectors are close.")
    print("Sentence 2 is about weather - its vector is far from the others.\n")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    show_the_problem()
    show_the_solution()
    real_world_example()

    print("--- Key Takeaways ---")
    print("1. An embedding is a vector of numbers (1024 for Mistral) representing meaning.")
    print("2. Same meaning in different languages -> nearby vectors.")
    print("3. Always batch embedding calls - one API call, many inputs.")
    print("4. Use the same model for queries and documents.")
    print("5. This is the foundation of every semantic-search and RAG system.")
