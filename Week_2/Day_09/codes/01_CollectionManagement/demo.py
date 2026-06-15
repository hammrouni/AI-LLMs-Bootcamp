"""
01 - Collection Management Demo
===============================
Demonstrates creating, listing, and deleting multiple Chroma collections
representing different types of data from a Tunisian delivery app.

HOW TO RUN THIS FILE:
1. pip install chromadb python-dotenv
2. python demo.py
"""

import os
import shutil
import chromadb

DB_PATH = "./chroma_collections_demo"


# ============================================================
# PART 1: The Problem — Mixing Data In One Collection
# ============================================================

def show_the_problem():
    """Show how mixing content types pollutes search results."""
    print("=== PART 1: The Mega-Collection Anti-Pattern ===\n")

    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)
    client = chromadb.PersistentClient(path=DB_PATH)

    mega = client.get_or_create_collection("everything")
    mega.add(
        documents=[
            "Yasmine, 27, lives in Tunis, loves spicy food.",
            "Tunisian couscous with seafood and harissa, Friday family lunch.",
            "Great service at Café Plaza in La Marsa, but slow on weekends.",
            "Bilel ordered 3x harissa jars and 1 kg makroudh.",
        ],
        ids=["user_1", "recipe_1", "review_1", "order_1"],
    )

    results = mega.query(query_texts=["spicy fish couscous"], n_results=3)

    print("Query 'spicy fish couscous' against the mega collection:")
    for i, doc in enumerate(results["documents"][0]):
        snippet = doc[:60] + ("..." if len(doc) > 60 else "")
        print(f"  {i+1}. {snippet}")
    print(
        "\nNotice: only #1 is an actual recipe. #2 is a USER profile that\n"
        "just happens to share the word 'spicy', and #3 is an ORDER record\n"
        "sharing 'harissa'/'couscous'. The embedding model matches on words,\n"
        "not content type — so unrelated documents (users, orders, reviews)\n"
        "compete with real recipes for the top results.\n"
    )


# ============================================================
# PART 2: The Solution — Separate Collections By Type
# ============================================================

def show_the_solution():
    """Create one collection per data type and verify isolation."""
    print("=== PART 2: One Collection Per Data Type ===\n")

    client = chromadb.PersistentClient(path=DB_PATH)

    # Idempotent setup
    for name in ["recipes", "users", "reviews", "orders"]:
        if name in [c.name for c in client.list_collections()]:
            client.delete_collection(name)

    recipes = client.create_collection("recipes")
    users   = client.create_collection("users")
    reviews = client.create_collection("reviews")
    orders  = client.create_collection("orders")

    recipes.add(
        documents=[
            "Couscous au poisson de Sfax avec harissa et oignon",
            "Brik à l'oeuf de Tunis avec thon et persil",
            "Makroudh from Kairouan dipped in honey",
        ],
        ids=["r1", "r2", "r3"],
    )
    users.add(
        documents=[
            "Yasmine, 27, Tunis, loves spicy food",
            "Bilel, 34, Sfax, prefers desserts",
        ],
        ids=["u1", "u2"],
    )
    reviews.add(
        documents=[
            "Café Plaza La Marsa, great service",
            "Bambalouni shop Sidi Bou Said, crowded but worth it",
        ],
        ids=["rv1", "rv2"],
    )
    orders.add(
        documents=[
            "3x harissa jars, 1kg makroudh",
            "2x couscous menu, delivery to Ariana",
        ],
        ids=["o1", "o2"],
    )

    print("Collections created:")
    for c in client.list_collections():
        print(f"  - {c.name:15} {c.count()} docs")

    print("\nQuery 'spicy fish couscous' against the RECIPES collection only:")
    results = recipes.query(query_texts=["spicy fish couscous"], n_results=2)
    for i, doc in enumerate(results["documents"][0]):
        print(f"  {i+1}. {doc}")
    print(
        "\nClean by TYPE — every hit is at least a recipe, never a user/order/review.\n"
        "#2 (a honey dessert) still isn't a great match for 'spicy fish couscous';\n"
        "it only appears because n_results=2 but the collection only has 3 recipes,\n"
        "so the 2nd-best match gets returned regardless of how weak it is.\n"
        "Separating collections fixes the WRONG-TYPE problem, not relevance ranking\n"
        "— that's controlled separately (e.g. similarity thresholds, more data).\n"
    )


# ============================================================
# PART 3: Lifecycle — Listing & Deleting Collections
# ============================================================

def real_world_example():
    """Manage collection lifecycle in a long-running app."""
    print("=== PART 3: Collection Lifecycle ===\n")

    client = chromadb.PersistentClient(path=DB_PATH)

    print("Before cleanup:")
    for c in client.list_collections():
        print(f"  - {c.name}")

    # Drop a test collection (e.g., the 'orders' collection created in Part 2,
    # no longer needed for this app)
    if "orders" in [c.name for c in client.list_collections()]:
        client.delete_collection("orders")
        print("\nDeleted 'orders' (was used for an experiment).")

    print("\nAfter cleanup:")
    for c in client.list_collections():
        print(f"  - {c.name}")

    print()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    show_the_problem()
    show_the_solution()
    real_world_example()

    print("--- Key Takeaways ---")
    print("1. One collection per data type — keep search focused.")
    print("2. Use get_or_create_collection in startup code (idempotent).")
    print("3. list_collections() and delete_collection() manage lifecycle.")
    print("4. Smaller, focused collections = faster, cleaner results.")
    print("5. Plan the schema before adding documents — changing later is painful.")
