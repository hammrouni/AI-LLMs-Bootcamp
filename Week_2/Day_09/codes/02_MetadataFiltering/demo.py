"""
02 - Metadata Filtering Demo
============================
Builds a small Tunisian craft-products collection and shows how to combine
vector similarity with metadata filters in ChromaDB.

HOW TO RUN THIS FILE:
1. pip install chromadb python-dotenv
2. python demo.py
"""

import os
import shutil
import chromadb

DB_PATH = "./chroma_filtering_demo"

PRODUCTS = [
    ("p1", "Modern Tunisian leather wallet, brown, slim",      {"region": "Tunis",  "price": 75,  "in_stock": True,  "category": "wallet"}),
    ("p2", "Handmade Berber leather wallet, brown",            {"region": "Tozeur", "price": 120, "in_stock": True,  "category": "wallet"}),
    ("p3", "Vintage leather wallet, deep red",                 {"region": "Sfax",   "price": 95,  "in_stock": False, "category": "wallet"}),
    ("p4", "Ceramic plate with classic Tunisian blue pattern", {"region": "Nabeul", "price": 40,  "in_stock": True,  "category": "ceramic"}),
    ("p5", "Olive-wood salad bowl from Sfax",                  {"region": "Sfax",   "price": 60,  "in_stock": True,  "category": "wood"}),
    ("p6", "Hand-woven kilim rug, Kairouan style, large",      {"region": "Kairouan","price": 350, "in_stock": True, "category": "rug"}),
    ("p7", "Silver fibula brooch, Berber design",              {"region": "Tozeur", "price": 220, "in_stock": True,  "category": "jewelry"}),
    ("p8", "Small leather pouch with stitched edges",          {"region": "Tunis",  "price": 35,  "in_stock": True,  "category": "wallet"}),
]


# ============================================================
# PART 1: Problem — Pure Vector Search Returns Junk
# ============================================================

def show_the_problem():
    """Show how vector-only search picks an out-of-stock or out-of-budget item."""
    print("=== PART 1: Pure Similarity Is Not Enough ===\n")

    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)
    client = chromadb.PersistentClient(path=DB_PATH)
    coll = client.create_collection("crafts")

    coll.add(
        documents=[p[1] for p in PRODUCTS],
        metadatas=[p[2] for p in PRODUCTS],
        ids=[p[0] for p in PRODUCTS],
    )

    results = coll.query(
        query_texts=["modern Tunisian leather wallet"],
        n_results=3,
    )

    print("Query: 'modern Tunisian leather wallet' (no filter)\n")
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        flag = "" if meta["in_stock"] else "  [OUT OF STOCK]"
        print(f"  {meta['price']:>4} TND | {meta['region']:>8} | {doc}{flag}")
    print(
        "\nVector search only looks at TEXT similarity, so it happily returns the\n"
        "95 TND wallet even though it's OUT OF STOCK — the embedding has no idea\n"
        "about 'in_stock' or 'price'. A customer can't buy this result.\n"
    )


# ============================================================
# PART 2: Solution — Vector + Filter
# ============================================================

def show_the_solution():
    """Add a where clause to filter in-stock items under budget."""
    print("=== PART 2: Vector Search With Filters ===\n")

    client = chromadb.PersistentClient(path=DB_PATH)
    coll = client.get_collection("crafts")

    results = coll.query(
        query_texts=["modern Tunisian leather wallet"],
        n_results=3,
        where={
            "$and": [
                {"in_stock": True},
                {"price": {"$lte": 100}},
                {"category": "wallet"},
            ]
        },
    )

    print("Query: 'modern Tunisian leather wallet'")
    print("Filter: in_stock=True AND price<=100 AND category=wallet\n")

    docs = results["documents"][0]
    if not docs:
        print("  (no products match the filter)")
    for doc, meta in zip(docs, results["metadatas"][0]):
        print(f"  {meta['price']:>4} TND | {meta['region']:>8} | {doc}")
    print(
        "\nThe out-of-stock wallet (95 TND) and the over-budget one (120 TND)\n"
        "are gone — Chroma applied the 'where' filter BEFORE ranking, so only\n"
        "buyable wallets in budget were ever candidates for the result.\n"
    )


# ============================================================
# PART 3: Advanced Filters — Ranges and IN lists
# ============================================================

def real_world_example():
    """Show range filters and IN-set filters."""
    print("=== PART 3: Advanced Filters ===\n")

    client = chromadb.PersistentClient(path=DB_PATH)
    coll = client.get_collection("crafts")

    # Filter 1: price range
    print("Filter: price between 50 and 150 TND, any category")
    results = coll.query(
        query_texts=["handmade Tunisian craft"],
        n_results=5,
        where={"$and": [{"price": {"$gte": 50}}, {"price": {"$lte": 150}}]},
    )
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        print(f"  {meta['price']:>4} TND | {meta['region']:>8} | {doc}")
    print(
        "\nAll 4 results have price between 50-150 TND, across different\n"
        "categories (wallet, wood) — the $gte/$lte range filter doesn't care\n"
        "about category, only price. Out-of-stock items are NOT excluded here\n"
        "since this filter has no 'in_stock' condition.\n"
    )

    # Filter 2: region IN [..]
    print("Filter: region IN [Tunis, Sfax]")
    results = coll.query(
        query_texts=["traditional Tunisian craft"],
        n_results=5,
        where={"region": {"$in": ["Tunis", "Sfax"]}},
    )
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        print(f"  {meta['price']:>4} TND | {meta['region']:>8} | {doc}")
    print(
        "\n'$in' matches any product whose region is Tunis OR Sfax, regardless\n"
        "of category or price — useful for 'show me everything from these\n"
        "regions' style queries, then ranked by similarity to the text.\n"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    show_the_problem()
    show_the_solution()
    real_world_example()

    print("--- Key Takeaways ---")
    print("1. Pure vector similarity returns out-of-stock / wrong-budget items.")
    print("2. Filtering at the DB is faster and correct vs filtering in Python.")
    print("3. Chroma 'where' supports $and, $or, $in, $gte, $lte.")
    print("4. Store every filterable field in metadata at write time.")
    print("5. Vector + filter = real production search.")
