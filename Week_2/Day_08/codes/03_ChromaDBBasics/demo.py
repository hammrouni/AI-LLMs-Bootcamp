"""
03 - ChromaDB Basics Demo
=========================
Creates a persistent ChromaDB collection, adds Tunisian-themed documents,
and runs semantic queries.

HOW TO RUN THIS FILE:
1. pip install chromadb mistralai python-dotenv
2. Copy ../.env.example to ../.env and add your MISTRAL_API_KEY (optional for PART 3)
3. python demo.py
"""

import os
import shutil
from dotenv import load_dotenv

load_dotenv()

DB_PATH = "./chroma_db_demo"


# ============================================================
# PART 1: The Problem — Storing Embeddings By Hand
# ============================================================

def show_the_problem():
    """Show why ad-hoc storage breaks down."""
    print("=== PART 1: Why You Need a Vector DB ===\n")

    fake_store = {
        "recipe_1": {"vec": [0.1, 0.2, 0.3], "text": "Couscous Sfax"},
        "recipe_2": {"vec": [0.4, 0.1, 0.5], "text": "Brik Tunis"},
    }

    print("Storing vectors in a dict 'works' for 2 docs:")
    for k, v in fake_store.items():
        print(f"  {k}: {v['text']}")
    print()
    print("Now imagine 10,000 documents:")
    print("  - Every query loops over 10,000 entries by hand")
    print("  - Restarting the script loses everything")
    print("  - No metadata filters, no indexing\n")


# ============================================================
# PART 2: The Solution — ChromaDB In 5 Lines
# ============================================================

def show_the_solution():
    """Use ChromaDB's default local embedding model — no API key needed."""
    print("=== PART 2: ChromaDB With the Default Embedder ===\n")

    try:
        import chromadb
    except ImportError:
        print("Run: pip install chromadb")
        return

    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)

    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_or_create_collection(name="tunisian_recipes")

    collection.add(
        documents=[
            "Spicy fish couscous from Sfax with harissa and onion",
            "Crispy egg brik pastry from Tunis",
            "Lablabi chickpea soup from La Goulette with cumin and bread",
            "Tuna and cheese tajine with eggs from Sousse",
            "Sweet date and honey makroudh dessert from Kairouan",
        ],
        metadatas=[
            {"region": "Sfax",     "type": "main"},
            {"region": "Tunis",    "type": "starter"},
            {"region": "Tunis",    "type": "soup"},
            {"region": "Sousse",   "type": "main"},
            {"region": "Kairouan", "type": "dessert"},
        ],
        ids=["recipe_1", "recipe_2", "recipe_3", "recipe_4", "recipe_5"],
    )

    print(f"Stored {collection.count()} recipes in ChromaDB at {DB_PATH}\n")

    results = collection.query(
        query_texts=["spicy fish dish"],
        n_results=3,
    )

    print("Query: 'spicy fish dish'\n")
    print("Top 3 matches:")
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        print(f"  distance={dist:.4f} | {meta['region']:>8} | {doc}")
    print()


# ============================================================
# PART 3: Real Usage — Bring Your Own Mistral Embeddings
# ============================================================

def real_world_example():
    """Use mistral-embed to embed and store documents in Chroma."""
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("=== PART 3: REAL USAGE (API key required) ===")
        print("Set MISTRAL_API_KEY in codes/.env to run this section.\n")
        return

    try:
        import chromadb
        from mistralai.client import Mistral
    except ImportError:
        print("Run: pip install chromadb mistralai")
        return

    print("=== PART 3: Storing Mistral Embeddings in Chroma ===\n")

    client_mistral = Mistral(api_key=api_key)
    client_chroma = chromadb.PersistentClient(path=DB_PATH + "_mistral")
    if "tunisian_recipes_mistral" in [c.name for c in client_chroma.list_collections()]:
        client_chroma.delete_collection("tunisian_recipes_mistral")
    collection = client_chroma.create_collection(name="tunisian_recipes_mistral")

    docs = [
        "Spicy fish couscous from Sfax with harissa and onion",
        "Crispy egg brik pastry from Tunis",
        "Lablabi chickpea soup from La Goulette with cumin and bread",
        "Sweet date and honey makroudh dessert from Kairouan",
        "Almond and honey baklawa pastry from Sousse",
    ]

    response = client_mistral.embeddings.create(model="mistral-embed", inputs=docs)
    embeddings = [d.embedding for d in response.data]

    collection.add(
        documents=docs,
        embeddings=embeddings,
        ids=[f"r{i}" for i in range(len(docs))],
    )

    query = "Tunisian dessert with dates"
    query_vec = client_mistral.embeddings.create(
        model="mistral-embed", inputs=[query]
    ).data[0].embedding

    results = collection.query(query_embeddings=[query_vec], n_results=2)

    print(f"Query: '{query}'\n")
    print("Top 2 matches (Mistral embeddings):")
    for doc, dist in zip(results["documents"][0], results["distances"][0]):
        print(f"  distance={dist:.4f} | {doc}")
    print()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    show_the_problem()
    show_the_solution()
    real_world_example()

    print("--- Key Takeaways ---")
    print("1. ChromaDB = pip install, no server, no config.")
    print("2. PersistentClient(path=...) keeps data across restarts.")
    print("3. Add documents with ids + optional metadata + optional embeddings.")
    print("4. Query by text (default embedder) or by embeddings (your own model).")
    print("5. distance is L2 by default - lower = more similar.")
