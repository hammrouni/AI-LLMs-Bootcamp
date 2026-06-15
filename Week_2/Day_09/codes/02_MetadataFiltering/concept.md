# 02 - Metadata Filtering

---

## 📦 Packages

```bash
pip install chromadb qdrant-client python-dotenv
```

---

## What is Metadata Filtering?

**Metadata filtering** is the ability to combine *vector similarity* with classic *attribute filters*. The query says "find me things similar to X, but only those that match these conditions".

Think of a Tunisian real-estate site:
- "Find apartments similar to this 3-bedroom place I liked" → vector search
- "...but only in La Marsa, under 200,000 TND, built after 2018" → filter
- The two combined is what users actually want

A vector DB without filtering is just a similarity engine. With filtering, it becomes a real product engine.

---

## What is the Problem?

### Pure similarity returns the right *kind* of thing but the wrong *instance*

Bilel's product team is building a search for an e-commerce site selling Tunisian crafts. They embed everything and ship vector-only search. The result:

```
Query: "modern Tunisian leather wallet"
Top match: handmade Berber wallet from Tozeur — but it's out of stock,
           costs 800 TND, and isn't even leather.
```

The vector match is "leather wallet" similar — yes. But the user implicitly wants:
- in stock
- price under their budget
- shippable to their region

Without filters, your beautiful semantic engine ships products that can't be bought.

---

## What is the Solution? Combine Vector + Filter!

Every modern vector DB supports filtering at query time:
- ChromaDB uses `where` clauses (MongoDB-style)
- Qdrant uses `Filter` objects with `must` / `should` / `must_not`
- The DB applies the filter and *then* (or alongside) does the vector search

Both approaches make the query: "find semantically similar items where field X = value AND field Y is between A and B".

---

## How It Works in Python

### Key words to know:

| Keyword / Concept | What it means |
|---|---|
| `where` (Chroma) | Dict-based filter: `{"region": "Tunis"}` |
| `$and`, `$or` | Logical operators in Chroma's `where` |
| `$in`, `$gte`, `$lte` | Set membership and ranges in Chroma |
| `Filter` (Qdrant) | A composable filter object |
| `must` / `must_not` / `should` (Qdrant) | AND / NOT / OR clauses |
| `FieldCondition` / `MatchValue` / `Range` | Qdrant building blocks |
| `pre-filter` vs `post-filter` | Apply filter before or after vector search — affects correctness when k is small |

### The Golden Rule:
- **Add every filterable field to metadata at write time.** You can't filter on something you didn't store.

### Basic Usage — ChromaDB

```python
results = collection.query(
    query_texts=["modern Tunisian leather wallet"],
    n_results=5,
    where={
        "$and": [
            {"in_stock": True},
            {"price":  {"$lte": 200}},
            {"region": {"$in": ["Tunis", "Sousse"]}},
        ]
    },
)
```

### Basic Usage — Qdrant

```python
from qdrant_client.models import Filter, FieldCondition, MatchValue, Range

filt = Filter(
    must=[
        FieldCondition(key="in_stock", match=MatchValue(value=True)),
        FieldCondition(key="price",    range=Range(lte=200)),
    ],
    should=[
        FieldCondition(key="region", match=MatchValue(value="Tunis")),
        FieldCondition(key="region", match=MatchValue(value="Sousse")),
    ],
)

results = client.query_points(
    collection_name="products",
    query=query_vec,
    query_filter=filt,
    limit=5,
).points
```

### How to Choose

| Filter style | Tool | Strength |
|---|---|---|
| Mongo-like `where` dict | Chroma | Easy to read, embedded clients |
| `Filter` objects | Qdrant | Composable, faster at scale, supports geo & nested |

### BAD vs GOOD

```python
# BAD — fetch everything, filter in Python
all_results = collection.query(query_texts=[q], n_results=1000)
filtered = [
    d for d, m in zip(all_results["documents"][0], all_results["metadatas"][0])
    if m["price"] <= 200 and m["region"] == "Tunis"
]
top = filtered[:5]   # might be empty if top-1000 didn't have any matches

# GOOD — filter in the DB
results = collection.query(
    query_texts=[q],
    n_results=5,
    where={"price": {"$lte": 200}, "region": "Tunis"},
)
```

---

## Why This Matters for AI Apps

Almost every production RAG/search app needs filtering:
- A chatbot that only quotes documents from the user's company (filter by `tenant_id`)
- A legal-doc search that filters by jurisdiction
- A real-estate app that filters by price / rooms / city
- A multilingual FAQ that filters by language

Vector similarity gives relevance. Metadata filters give correctness and personalization. You need both.
