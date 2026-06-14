# 04 - Qdrant Basics

---

## 📦 Packages

```bash
pip install qdrant-client mistralai python-dotenv
```

---

## What is Qdrant?

**Qdrant** is a production-grade vector database written in Rust. Same idea as ChromaDB — store vectors, query by similarity — but built for scale, with stronger filtering, payload validation, and clustering.

Think of it like the difference between a personal notebook (Chroma) and a real warehouse with shelves, labels, and a barcode scanner (Qdrant):
- Both can store your recipes
- The notebook is faster to set up
- The warehouse handles 100 million items, multiple users at once, and complex queries

You can run Qdrant in three ways:
1. **In-memory** — `QdrantClient(":memory:")` — for tests
2. **Local file** — `QdrantClient(path="./qdrant_db")` — persists like Chroma
3. **Server** — `QdrantClient(url="http://...")` — for production

For Day 8 we use local file. No Docker needed.

---

## What is the Problem?

### ChromaDB hits limits at scale and complex filtering

ChromaDB is perfect for prototypes, but as your dataset grows you start running into issues:
- Slow queries past a few million vectors
- Limited filtering (single boolean conditions)
- No fine-grained index tuning
- Harder to deploy as a shared service

Tunisian startups building real products (search engine for a marketplace, semantic FAQ for a bank) need a vector DB that can:
- Filter by 5 fields at once (`region=Tunis AND price<100 AND in_stock=True`)
- Stay fast at 10M+ vectors
- Be deployed as a service the whole team queries

---

## What is the Solution? Qdrant!

**Qdrant** offers a richer feature set while keeping a simple Python API. The two main concepts are:

- **Collection:** like Chroma — a named set of vectors
- **Point:** one item — has an `id`, a `vector`, and a `payload` (any JSON)

The payload is where Qdrant shines. You can build complex filters on it and the search still runs in milliseconds.

```python
client.upsert(
    collection_name="recipes",
    points=[PointStruct(id=1, vector=[...], payload={"region": "Sfax", "spicy": True})],
)
```

---

## How It Works in Python

### Key words to know:

| Keyword / Concept | What it means |
|---|---|
| `QdrantClient` | The client object |
| `Distance` | Metric enum: `COSINE`, `DOT`, `EUCLID` |
| `VectorParams` | Schema: dimension + distance |
| `PointStruct` | One stored item: id + vector + payload |
| `payload` | Arbitrary JSON metadata you can filter on |
| `upsert` | Insert or update points |
| `query_points` | Find top-k closest points (optionally with a filter) — returns an object with a `.points` list |
| `Filter` / `FieldCondition` / `MatchValue` | Composable filter building blocks |

### The Golden Rule:
- **Declare the vector dimension once when you create the collection.** Mistral = 1024. Once set, all vectors you insert must match.

### Basic Usage

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

client = QdrantClient(path="./qdrant_db")

client.create_collection(
    collection_name="tunisian_recipes",
    vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
)

client.upsert(
    collection_name="tunisian_recipes",
    points=[
        PointStruct(
            id=1,
            vector=mistral_vector_for("Couscous au poisson de Sfax"),
            payload={"region": "Sfax", "type": "main", "spicy": True},
        ),
        PointStruct(
            id=2,
            vector=mistral_vector_for("Brik à l'oeuf de Tunis"),
            payload={"region": "Tunis", "type": "starter", "spicy": False},
        ),
    ],
)

results = client.query_points(
    collection_name="tunisian_recipes",
    query=mistral_vector_for("spicy fish dish"),
    limit=3,
).points
```

### How to Choose

| | ChromaDB | Qdrant |
|--|----------|--------|
| Setup | `pip install` | `pip install` (or Docker for server) |
| Best for | Prototypes, < 1M vectors | Production, > 1M vectors, team use |
| Filtering | Basic | Rich (nested AND/OR/range) |
| Speed at scale | OK | Excellent |
| Deployment | Embedded only | Embedded, file, or server |

### BAD vs GOOD

```python
# BAD — different dimensions in the same collection
client.upsert(points=[PointStruct(id=1, vector=[0.1]*512, payload={})])
client.upsert(points=[PointStruct(id=2, vector=[0.1]*1024, payload={})])  # ERROR

# GOOD — fix dimension at collection creation, match it on every insert
client.create_collection(
    "recipes",
    vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
)
```

---

## Why This Matters for AI Apps

When your AI app grows beyond a prototype, you'll need real filters and real scale:
- A real estate site in Tunis filtering by `price < 200000 AND rooms >= 3 AND neighborhood IN [La Marsa, Ariana]`
- A support bot filtering past tickets by `language="ar" AND product="mobile"`
- A job board matching CVs to postings with `seniority="senior" AND remote=True`

ChromaDB can do some of this. Qdrant does all of it, faster, with cleaner APIs and production deployment options. Knowing both lets you pick the right tool when the time comes.
