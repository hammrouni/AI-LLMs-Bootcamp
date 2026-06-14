"""
05 - Tunisian Recipe Search (Capstone) Demo
===========================================
Builds a semantic search engine over a small list of Tunisian recipes using
Mistral embeddings + ChromaDB. Users can search in French, English, or Arabic.

HOW TO RUN THIS FILE:
1. pip install chromadb mistralai python-dotenv
2. Copy ../.env.example to ../.env and add your MISTRAL_API_KEY
3. python demo.py
"""

import os
import shutil
from dotenv import load_dotenv

load_dotenv()

DB_PATH = "./recipe_search_db"


# ── A tiny Tunisian recipe corpus ─────────────────────────────
RECIPES = [
    {
        "id": "r1",
        "text": "Couscous au poisson de Sfax avec harissa, oignon et tomate. Plat principal du vendredi.",
        "region": "Sfax",
        "type": "main",
    },
    {
        "id": "r2",
        "text": "Brik a l'oeuf de Tunis - pate fine, oeuf coulant, thon et persil.",
        "region": "Tunis",
        "type": "starter",
    },
    {
        "id": "r3",
        "text": "Lablabi from La Goulette: chickpeas soup with cumin, garlic, and stale bread.",
        "region": "Tunis",
        "type": "soup",
    },
    {
        "id": "r4",
        "text": "Tajine malsouka: savory baked egg and tuna pie with cheese and parsley, a main course from Sousse.",
        "region": "Sousse",
        "type": "main",
    },
    {
        "id": "r5",
        "text": "Makroudh from Kairouan: sweet semolina dessert stuffed with dates, fried, then dipped in honey.",
        "region": "Kairouan",
        "type": "dessert",
    },
    {
        "id": "r6",
        "text": "Salade mechouia tunisienne - grilled peppers and tomatoes, garlic, tuna on top.",
        "region": "Tunis",
        "type": "starter",
    },
    {
        "id": "r7",
        "text": "Kosksi bel hout men Sfax - traditional Friday dish with harissa and olive oil.",
        "region": "Sfax",
        "type": "main",
    },
    {
        "id": "r8",
        "text": "Bambalouni: sweet Tunisian dessert of fried doughnuts dusted with sugar, popular in Sidi Bou Said.",
        "region": "Tunis",
        "type": "dessert",
    },
]


# ============================================================
# PART 1: The Problem — Exact-Match Search Fails
# ============================================================

def show_the_problem():
    """Show that string `in` fails on cross-language queries."""
    print("=== PART 1: Naive Search vs. Reality ===\n")

    queries = ["spicy fish dish", "kosksi", "Tunisian sweet with dates"]

    for q in queries:
        hits = [r["id"] for r in RECIPES if q.lower() in r["text"].lower()]
        print(f"Query: {q!r:35} -> naive hits: {hits if hits else 'NONE'}")
    print("\nMost real-user queries return nothing with keyword matching.\n")


# ============================================================
# PART 2: The Pipeline With ChromaDB's Local Embedder (No API Key)
# ============================================================

def show_the_solution():
    """Run the real pipeline using ChromaDB's free local embedder."""
    print("=== PART 2: The Semantic Search Pipeline (local embedder) ===\n")

    try:
        import chromadb
    except ImportError:
        print("Run: pip install chromadb")
        return

    local_db_path = "./recipe_search_db_local"
    if os.path.exists(local_db_path):
        shutil.rmtree(local_db_path)

    client = chromadb.PersistentClient(path=local_db_path)
    collection = client.get_or_create_collection(name="tunisian_recipes_local")

    collection.add(
        documents=[r["text"] for r in RECIPES],
        metadatas=[{"region": r["region"], "type": r["type"]} for r in RECIPES],
        ids=[r["id"] for r in RECIPES],
    )
    print(f"Step 1-3: Embedded and stored {collection.count()} recipes (local embedder, no API key).\n")

    query = "spicy fish couscous"
    results = collection.query(query_texts=[query], n_results=2)

    print(f"Step 4: Query: {query!r}")
    for doc, meta, dist in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        snippet = doc[:60] + ("..." if len(doc) > 60 else "")
        print(f"  distance={dist:.4f} | {meta['region']:>8} | {snippet}")
    print()
    print("This local embedder works offline but is English-only and less accurate.")
    print("PART 3 swaps it for Mistral's multilingual embeddings.\n")


# ============================================================
# PART 3: Real Search — End-to-End
# ============================================================

def real_world_example():
    """Build the index and run real searches."""
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("=== PART 3: REAL SEARCH (API key required) ===")
        print("Set MISTRAL_API_KEY in codes/.env to run this section.\n")
        return

    try:
        import chromadb
        from mistralai.client import Mistral
    except ImportError:
        print("Run: pip install chromadb mistralai")
        return

    print("=== PART 3: Tunisian Recipe Semantic Search ===\n")

    mistral = Mistral(api_key=api_key)

    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)
    chroma = chromadb.PersistentClient(path=DB_PATH)
    collection = chroma.get_or_create_collection(name="tunisian_recipes")

    # --- Build index (once) ---
    print(f"Embedding {len(RECIPES)} recipes...")
    texts = [r["text"] for r in RECIPES]
    embeddings = [
        d.embedding
        for d in mistral.embeddings.create(model="mistral-embed", inputs=texts).data
    ]

    collection.add(
        documents=texts,
        embeddings=embeddings,
        metadatas=[{"region": r["region"], "type": r["type"]} for r in RECIPES],
        ids=[r["id"] for r in RECIPES],
    )
    print(f"Indexed {collection.count()} recipes.\n")

    # --- Try a few queries (mixed languages) ---
    test_queries = [
        "spicy fish couscous on Friday",
        "Tunisian dessert with dates",
        "plat de poisson epice",  # French: "spicy fish dish"
        "fried sweet pastry",
    ]

    for query in test_queries:
        q_vec = mistral.embeddings.create(
            model="mistral-embed", inputs=[query]
        ).data[0].embedding

        results = collection.query(query_embeddings=[q_vec], n_results=2)

        print(f"Query: {query!r}")
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            snippet = doc[:60] + ("..." if len(doc) > 60 else "")
            print(f"  distance={dist:.4f} | {meta['region']:>8} | {snippet}")
        print()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    show_the_problem()
    show_the_solution()
    real_world_example()

    print("--- Key Takeaways ---")
    print("1. End-to-end semantic search = embed corpus once, embed query each call.")
    print("2. The same pipeline works for FAQ bots, e-commerce, doc Q&A.")
    print("3. Cross-language search comes for free with multilingual embeddings.")
    print("4. Metadata in the vector DB lets you filter results later.")
    print("5. Next: scale this up, add filters, then plug an LLM on top (RAG, Day 10).")
