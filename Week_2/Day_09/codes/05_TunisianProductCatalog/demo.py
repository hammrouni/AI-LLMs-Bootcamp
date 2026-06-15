"""
05 - Tunisian Product Catalog (Capstone) Demo
=============================================
Glues together everything from Day 9: collection setup, batch embedding,
HNSW + payload indexes, vector + filter queries.

HOW TO RUN THIS FILE:
1. pip install qdrant-client mistralai python-dotenv
2. Copy ../.env.example to ../.env and add your MISTRAL_API_KEY
3. python demo.py
"""

import os
import warnings
from dotenv import load_dotenv

load_dotenv()

DB_PATH = "./qdrant_catalog_demo"
DIM = 1024  # Mistral embedding dim

PRODUCTS = [
    {"id": 1,  "text": "Modern Tunisian leather wallet, slim, brown.",                    "meta": {"region": "Tunis",    "category": "wallet",  "price": 75,  "in_stock": True}},
    {"id": 2,  "text": "Handmade Berber leather wallet from Tozeur, dark brown.",         "meta": {"region": "Tozeur",   "category": "wallet",  "price": 120, "in_stock": True}},
    {"id": 3,  "text": "Vintage red leather wallet — limited edition.",                   "meta": {"region": "Sfax",     "category": "wallet",  "price": 95,  "in_stock": False}},
    {"id": 4,  "text": "Hand-painted ceramic plate, classic Tunisian blue pattern.",      "meta": {"region": "Nabeul",   "category": "ceramic", "price": 40,  "in_stock": True}},
    {"id": 5,  "text": "Olive-wood salad bowl from Sfax, food-safe finish.",              "meta": {"region": "Sfax",     "category": "wood",    "price": 60,  "in_stock": True}},
    {"id": 6,  "text": "Hand-woven kilim rug, Kairouan style, 2x3 meters.",               "meta": {"region": "Kairouan", "category": "rug",     "price": 350, "in_stock": True}},
    {"id": 7,  "text": "Silver Berber fibula brooch with engraved details.",              "meta": {"region": "Tozeur",   "category": "jewelry", "price": 220, "in_stock": True}},
    {"id": 8,  "text": "Small leather pouch, hand-stitched edges, for coins.",            "meta": {"region": "Tunis",    "category": "wallet",  "price": 35,  "in_stock": True}},
    {"id": 9,  "text": "Glazed Nabeul tagine pot, deep blue and white.",                  "meta": {"region": "Nabeul",   "category": "ceramic", "price": 85,  "in_stock": True}},
    {"id": 10, "text": "Olive-wood cutting board with handle, Sfax craftsmanship.",       "meta": {"region": "Sfax",     "category": "wood",    "price": 45,  "in_stock": True}},
    {"id": 11, "text": "Traditional Berber wool rug from Tozeur, geometric patterns.",    "meta": {"region": "Tozeur",   "category": "rug",     "price": 280, "in_stock": False}},
    {"id": 12, "text": "Silver bangle bracelet inspired by Carthage motifs.",             "meta": {"region": "Tunis",    "category": "jewelry", "price": 160, "in_stock": True}},
]


def chunked(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


# ============================================================
# The Problem — Pretty Demo vs Production
# ============================================================

def show_the_problem():
    """Highlight the gap between toy and production search."""
    print("=== From Toy Search to Production ===\n")
    print("A toy demo: 3 hardcoded products + 1 perfect query.")
    print("A real catalog needs:")
    print("  - Multiple metadata fields (region, category, price, in_stock)")
    print("  - Fast vector + filter queries")
    print("  - Batched inserts for thousands of items")
    print("  - Multilingual queries from real users")
    print("Day 9 stack handles all of that — we'll wire it up now.\n")


# ============================================================
# Setup — Collection, Indexes, Batch Insert
# ============================================================

def show_the_solution():
    """No-API-key version: print the pipeline architecture."""
    print("=== Pipeline Overview ===\n")
    print("Step 1: Create Qdrant collection with HNSW + cosine.")
    print("Step 2: Create payload indexes (region, category, price, in_stock).")
    print("Step 3: Embed product texts in batches of 50.")
    print("Step 4: Upsert vectors + payload into Qdrant.")
    print("Step 5: At query time, embed user query and apply filters.\n")
    print("Run PART 3 with an API key to see this end-to-end.\n")


# ============================================================
# Real End-to-End Catalog
# ============================================================

def real_world_example():
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("=== PART 3: REAL CATALOG (API key required) ===")
        print("Set MISTRAL_API_KEY in codes/.env to run this section.\n")
        return

    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import (
            Distance,
            VectorParams,
            PointStruct,
            Filter,
            FieldCondition,
            MatchValue,
            Range,
            PayloadSchemaType,
        )
        from mistralai.client import Mistral
    except ImportError:
        print("Run: pip install qdrant-client mistralai")
        return

    print("=== PART 3: Tunisian Product Catalog (End to End) ===\n")

    mistral = Mistral(api_key=api_key)
    qdrant = QdrantClient(path=DB_PATH)

    # --- Setup ---
    if qdrant.collection_exists("products"):
        qdrant.delete_collection("products")
    qdrant.create_collection(
        collection_name="products",
        vectors_config=VectorParams(size=DIM, distance=Distance.COSINE),
    )
    # Payload indexes are a no-op in local Qdrant (server-only feature), but
    # we create them anyway to mirror the production setup.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        for field, schema in [
            ("region",   PayloadSchemaType.KEYWORD),
            ("category", PayloadSchemaType.KEYWORD),
            ("price",    PayloadSchemaType.INTEGER),
            ("in_stock", PayloadSchemaType.BOOL),
        ]:
            qdrant.create_payload_index("products", field_name=field, field_schema=schema)

    # --- Batch index ---
    print(f"Embedding and indexing {len(PRODUCTS)} products...")
    for batch in chunked(PRODUCTS, 50):
        texts = [p["text"] for p in batch]
        vectors = [
            d.embedding
            for d in mistral.embeddings.create(model="mistral-embed", inputs=texts).data
        ]
        qdrant.upsert(
            "products",
            points=[
                PointStruct(id=p["id"], vector=v, payload={**p["meta"], "text": p["text"]})
                for p, v in zip(batch, vectors)
            ],
        )
    print(f"Catalog ready. {qdrant.count('products').count} products indexed.\n")

    # --- Real queries ---
    def search(query, region=None, max_price=None, category=None, k=3):
        q_vec = mistral.embeddings.create(
            model="mistral-embed", inputs=[query]
        ).data[0].embedding

        must = [FieldCondition(key="in_stock", match=MatchValue(value=True))]
        if region:
            must.append(FieldCondition(key="region", match=MatchValue(value=region)))
        if max_price is not None:
            must.append(FieldCondition(key="price", range=Range(lte=max_price)))
        if category:
            must.append(FieldCondition(key="category", match=MatchValue(value=category)))

        return qdrant.query_points(
            "products", query=q_vec, query_filter=Filter(must=must), limit=k
        ).points

    queries = [
        ("modern leather wallet under 100",        {"max_price": 100, "category": "wallet"}),
        ("hand-painted Tunisian pottery",          {"category": "ceramic"}),
        ("traditional rug from Kairouan",          {"region": "Kairouan"}),
        ("silver Tunisian jewelry",                {"category": "jewelry"}),
    ]

    for query, filters in queries:
        results = search(query, **filters)
        print(f"Query: {query!r}  filters={filters}")
        for r in results:
            payload = r.payload
            print(
                f"  score={r.score:.3f} | {payload['price']:>4} TND | "
                f"{payload['region']:>8} | {payload['text']}"
            )
        print()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    show_the_problem()
    show_the_solution()
    real_world_example()

    print("--- Key Takeaways ---")
    print("1. Production catalogs combine vectors + payload indexes + filters.")
    print("2. Batch the embedding and upsert steps for speed and cost.")
    print("3. Payload indexes make filtered queries fast at scale.")
    print("4. The same blueprint powers e-commerce, jobs, real estate, docs.")
    print("5. Tomorrow: add an LLM on top of retrieval -> full RAG.")
