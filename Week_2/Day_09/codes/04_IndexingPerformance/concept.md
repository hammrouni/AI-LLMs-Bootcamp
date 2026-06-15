# 04 - Indexing & Performance

---

## 📦 Packages

```bash
pip install qdrant-client numpy python-dotenv
```

---

## What is an Index in a Vector DB?

An **index** is a data structure that makes "find the nearest vector" fast — typically O(log N) instead of O(N). Without it, every query scans every vector. With it, a million-vector collection still answers in milliseconds.

Think of a Tunisian library catalog in Tunis:
- No catalog: walk through every shelf to find a book → hours
- A simple printed list of titles: faster, but still linear → minutes
- A computerized catalog with topic/author indices: seconds

A vector index is the equivalent: a clever shortcut structure built once, queried millions of times.

---

## What is the Problem?

### Brute-force search dies past a few hundred thousand vectors

Hayet's Tunisian recipe site grows to 100,000 recipes. Without an index, every search compares the query to all 100,000 vectors. Latency goes from "instant" to "user keeps refreshing":

```
1k vectors:   2 ms     (fine)
10k vectors:  20 ms    (still fine)
100k vectors: 200 ms   (user notices)
1M vectors:   2000 ms  (user leaves)
```

Brute-force is fine for prototypes. For production, you need an Approximate Nearest Neighbor (ANN) index.

---

## What is the Solution? HNSW (and friends)!

**HNSW (Hierarchical Navigable Small World)** is the most popular ANN index. It's the default in Qdrant, Chroma, Pinecone, and most modern vector DBs.

Intuition: build a multi-layer graph. Top layers have few nodes with long-range links. Bottom layers have all nodes with short-range links. To search, start at the top, hop toward the query, descend a layer, repeat.

You don't have to implement HNSW. You only have to know the **two knobs** that matter:

- `m` — how many neighbors per node in the graph (default 16). Higher = better recall, more memory.
- `ef_construction` — how many candidates the build process keeps (default 200). Higher = better quality index, slower build.
- `ef` (search) — how many candidates to consider at query time. Higher = better recall, slower queries.

That's it. You rarely need to touch anything else.

---

## How It Works in Python

### Key words to know:

| Keyword / Concept | What it means |
|---|---|
| `ANN` | Approximate Nearest Neighbor — fast but not exact |
| `recall` | % of true top-k results that the ANN returned |
| `HNSW` | The default graph-based ANN index |
| `IVF` | Inverted File index — partitions vectors into clusters |
| `m`, `ef_construction`, `ef` | The HNSW knobs (graph degree, build width, search width) |
| `payload_index` | A secondary index on metadata fields (for fast filtering) |

### The Golden Rule:
- **Default HNSW settings are good 95% of the time.** Tune only if you have measurements showing slow queries or low recall.

### Basic Usage — Qdrant

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, HnswConfigDiff

client = QdrantClient(path="./qdrant_db")

if client.collection_exists("products"):
    client.delete_collection("products")
client.create_collection(
    collection_name="products",
    vectors_config=VectorParams(
        size=1024,
        distance=Distance.COSINE,
        hnsw_config=HnswConfigDiff(m=16, ef_construct=200),
    ),
)

# Speed up filtered searches by indexing metadata fields
client.create_payload_index(
    collection_name="products",
    field_name="region",
    field_schema="keyword",
)
client.create_payload_index(
    collection_name="products",
    field_name="price",
    field_schema="integer",
)
```

### How to Choose

| Index | When to use | When NOT to use |
|---|---|---|
| Flat (brute force) | < 10k vectors, tiny servers | Anything bigger |
| HNSW | Default for almost everything | When memory is extremely tight |
| IVF | Very large datasets (10M+), batch search | Live single-query apps |

### BAD vs GOOD

```python
# BAD — slow filtered query because metadata isn't indexed
client.query_points(
    "products",
    query=q_vec,
    query_filter=Filter(must=[FieldCondition(key="region", match=MatchValue(value="Tunis"))]),
)
# Qdrant scans all points for matching region every query

# GOOD — index the field once, fast filtered queries forever
client.create_payload_index("products", field_name="region", field_schema="keyword")
```

---

## Why This Matters for AI Apps

Anything user-facing needs sub-100ms search:
- A semantic search box on a Tunisian e-commerce site: 50ms target
- A FAQ bot doing retrieval before generation: 100ms total budget for retrieval
- A real-time recommendation widget on a news site: 30ms target

Without HNSW + payload indexes, you hit these limits at very small data sizes. With them, you have headroom for years of growth.

```
Search 1M vectors with HNSW (default ef=64): ~5 ms
Same search with brute force:                ~1500 ms
```
