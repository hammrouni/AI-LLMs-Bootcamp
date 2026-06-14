"""
04 - Qdrant Basics Demo
=======================
Spins up a local Qdrant collection, inserts Tunisian recipes with payloads,
and runs vector + filtered searches.

HOW TO RUN THIS FILE:
1. pip install qdrant-client mistralai python-dotenv
2. Copy ../.env.example to ../.env and add your MISTRAL_API_KEY (optional for PART 3)
3. python demo.py
"""

import os
import shutil
import random
import time
from dotenv import load_dotenv

load_dotenv()

QDRANT_PATH = "./qdrant_db_demo"
DIM = 8  # toy dimension for PART 2 (no API needed)


# ============================================================
# PART 1: Why Move From Chroma to Qdrant?
# ============================================================

def show_the_problem():
    """Highlight where ChromaDB starts to feel tight."""
    print("=== PART 1: When You Outgrow Chroma ===\n")

    print("Imagine a Tunisian classified-ads site:")
    print("  - 5 million listings")
    print("  - Filters: region IN [Tunis, Sfax, Sousse] AND price < 50000 AND year >= 2018")
    print("  - 200 queries per second from mobile users\n")
    print("ChromaDB can technically work, but you start hitting:")
    print("  - Slower searches past a few million points")
    print("  - Limited filter combinations")
    print("  - No multi-tenant/server mode out of the box\n")
    print("Qdrant is designed for this exact scenario.\n")

    print("--- A taste of the problem: brute-force filtering ---\n")

    random.seed(42)
    regions_pool = ["Tunis", "Sfax", "Sousse", "Kairouan", "Bizerte"]
    listings = [
        {
            "region": random.choice(regions_pool),
            "price": random.randint(5_000, 100_000),
            "year": random.randint(2010, 2024),
        }
        for _ in range(200_000)
    ]

    target_regions = {"Tunis", "Sfax", "Sousse"}
    start = time.perf_counter()
    matches = [
        listing for listing in listings
        if listing["region"] in target_regions
        and listing["price"] < 50_000
        and listing["year"] >= 2018
    ]
    elapsed_ms = (time.perf_counter() - start) * 1000

    print(f"Scanned {len(listings):,} listings (plain Python list) in {elapsed_ms:.1f} ms")
    print(f"Found {len(matches):,} matches for the filter above.\n")
    print(f"At 200 req/s, that's ~{elapsed_ms * 200:,.0f} ms of CPU per second")
    print("for filtering ALONE - before any vector similarity math runs.")
    print("This is a 200K-row in-memory scan; the real dataset is 5M rows")
    print("backed by a database, where filtering is even more expensive.\n")


# ============================================================
# PART 2: Toy Vectors — No API Key Needed
# ============================================================

def show_the_solution():
    """Insert and query random vectors with a real Qdrant client (local file)."""
    print("=== PART 2: Qdrant With Local File Storage ===\n")

    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import (
            Distance,
            VectorParams,
            PointStruct,
            Filter,
            FieldCondition,
            MatchValue,
        )
    except ImportError:
        print("Run: pip install qdrant-client")
        return

    if os.path.exists(QDRANT_PATH):
        shutil.rmtree(QDRANT_PATH)

    client = QdrantClient(path=QDRANT_PATH)

    client.create_collection(
        collection_name="recipes",
        vectors_config=VectorParams(size=DIM, distance=Distance.COSINE),
    )

    random.seed(42)
    recipes = [
        (1, "Couscous au poisson de Sfax",  {"region": "Sfax",     "type": "main"}),
        (2, "Brik a l'oeuf de Tunis",       {"region": "Tunis",    "type": "starter"}),
        (3, "Lablabi from La Goulette",     {"region": "Tunis",    "type": "soup"}),
        (4, "Makroudh from Kairouan",       {"region": "Kairouan", "type": "dessert"}),
        (5, "Tajine malsouka Sousse",       {"region": "Sousse",   "type": "main"}),
    ]

    points = [
        PointStruct(id=rid, vector=[random.random() for _ in range(DIM)], payload=meta | {"name": name})
        for rid, name, meta in recipes
    ]
    client.upsert(collection_name="recipes", points=points)

    print(f"Inserted {len(points)} recipes into Qdrant at {QDRANT_PATH}\n")

    query_vec = [random.random() for _ in range(DIM)]

    print("--- Plain vector search ---")
    results = client.query_points(collection_name="recipes", query=query_vec, limit=3).points
    for r in results:
        print(f"  score={r.score:.4f} | {r.payload['name']} ({r.payload['region']})")

    print("\n--- Filtered search: only Tunis recipes ---")
    results = client.query_points(
        collection_name="recipes",
        query=query_vec,
        query_filter=Filter(
            must=[FieldCondition(key="region", match=MatchValue(value="Tunis"))]
        ),
        limit=3,
    ).points
    for r in results:
        print(f"  score={r.score:.4f} | {r.payload['name']} ({r.payload['region']})")
    print()


# ============================================================
# PART 3: Real Embeddings — Mistral + Qdrant
# ============================================================

def real_world_example():
    """Embed real text with Mistral and store in Qdrant."""
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("=== PART 3: REAL EMBEDDINGS (API key required) ===")
        print("Set MISTRAL_API_KEY in codes/.env to run this section.\n")
        return

    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams, PointStruct
        from mistralai.client import Mistral
    except ImportError:
        print("Run: pip install qdrant-client mistralai")
        return

    print("=== PART 3: Real Mistral Embeddings in Qdrant ===\n")

    mistral = Mistral(api_key=api_key)
    path = QDRANT_PATH + "_mistral"
    if os.path.exists(path):
        shutil.rmtree(path)
    qdrant = QdrantClient(path=path)

    qdrant.create_collection(
        collection_name="recipes",
        vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
    )

    docs = [
        "Spicy fish couscous from Sfax with harissa and onion",
        "Crispy egg brik pastry from Tunis",
        "Lablabi chickpea soup from La Goulette with cumin and bread",
        "Sweet date and honey makroudh dessert from Kairouan",
        "Almond and honey baklawa pastry from Sousse",
    ]

    vectors = [
        d.embedding
        for d in mistral.embeddings.create(model="mistral-embed", inputs=docs).data
    ]

    qdrant.upsert(
        collection_name="recipes",
        points=[
            PointStruct(id=i + 1, vector=v, payload={"name": d})
            for i, (v, d) in enumerate(zip(vectors, docs))
        ],
    )

    query = "Tunisian dessert with dates"
    query_vec = mistral.embeddings.create(
        model="mistral-embed", inputs=[query]
    ).data[0].embedding

    results = qdrant.query_points(collection_name="recipes", query=query_vec, limit=2).points

    print(f"Query: '{query}'\n")
    for r in results:
        print(f"  score={r.score:.4f} | {r.payload['name']}")
    print()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    show_the_problem()
    show_the_solution()
    real_world_example()

    print("--- Key Takeaways ---")
    print("1. Qdrant scales further than Chroma and supports rich filtering.")
    print("2. Run it locally (file or :memory:) for dev - no Docker needed.")
    print("3. Each point = id + vector + payload (JSON).")
    print("4. Filters use Filter + FieldCondition + MatchValue - composable.")
    print("5. Pick Chroma for prototypes, Qdrant for production.")
