# 03 - Batch Operations

---

## 📦 Packages

```bash
pip install chromadb mistralai python-dotenv
```

---

## What is a Batch Operation?

A **batch operation** sends many items in one API call instead of one item per call. For embedding APIs and vector DBs, this is the difference between "minutes" and "seconds".

Think of a Tunisian wholesale market in Bir El Kassaa:
- Buying tomatoes one by one from one stall and walking back to your van each time = takes all morning
- Buying a crate of tomatoes in one trip = takes 5 minutes
- Same tomatoes, same van, totally different time spent

Batching is the same: same data, fewer round trips, drastically less time.

---

## What is the Problem?

### Single-item calls are killers at scale

Sonia is indexing 10,000 product descriptions for her client's site:

```python
for product in products:
    vec = mistral.embeddings.create(model="mistral-embed", inputs=[product["text"]])
    collection.add(documents=[product["text"]], embeddings=[vec.data[0].embedding], ids=[product["id"]])
```

What this actually does:
- 10,000 embedding API calls
- 10,000 round trips to the Mistral server
- 10,000 separate writes to ChromaDB

Result: 20+ minutes of waiting, occasional rate-limit errors, and unnecessary API spend.

---

## What is the Solution? Batches!

**Send 50–200 items per call** to the embedding API and to the vector DB. Both Mistral and Chroma/Qdrant accept lists in a single call.

```python
batch = products[:100]
texts = [p["text"] for p in batch]

# One API call for 100 embeddings
vectors = [d.embedding for d in mistral.embeddings.create(model="mistral-embed", inputs=texts).data]

# One DB call to insert 100 items
collection.add(documents=texts, embeddings=vectors, ids=[p["id"] for p in batch])
```

10,000 items / 100 per batch = 100 round trips. 100× fewer calls. Often 10×–30× faster end to end (network latency dominates).

---

## How It Works in Python

### Key words to know:

| Keyword / Concept | What it means |
|---|---|
| `batch_size` | How many items per call (typically 50–200) |
| `chunking` | Splitting a long list into batches |
| `rate limit` | API caps requests/min — batching helps stay under |
| `retry with backoff` | Re-try a failed batch after a short pause |
| `upsert` | Insert if missing, update if exists |

### The Golden Rule:
- **Find the sweet spot of batch size for your provider and stick to it.** Too small = wasted overhead. Too large = timeouts and memory pressure. For Mistral, 50–100 is safe; for Chroma, 100–500 inserts.

### Basic Usage

```python
def chunked(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


def index_products(products, collection, mistral, batch_size=100):
    for batch in chunked(products, batch_size):
        texts = [p["text"] for p in batch]
        vectors = [
            d.embedding
            for d in mistral.embeddings.create(model="mistral-embed", inputs=texts).data
        ]
        collection.add(
            documents=texts,
            embeddings=vectors,
            metadatas=[p["meta"] for p in batch],
            ids=[p["id"] for p in batch],
        )
```

### How to Choose

| Batch size | When to use | When NOT to use |
|---|---|---|
| 1 | Debugging, tiny datasets | Production |
| 50–100 | Mistral embedding API sweet spot | Small datasets <50 items |
| 500–1000 | Vector DB inserts (Chroma) | If memory tight |

### BAD vs GOOD

```python
# BAD — 1 doc per call
for p in products:
    vec = embed([p["text"]])
    collection.add(documents=[p["text"]], embeddings=[vec], ids=[p["id"]])

# GOOD — 100 docs per call
for batch in chunked(products, 100):
    vectors = embed([p["text"] for p in batch])
    collection.add(
        documents=[p["text"] for p in batch],
        embeddings=vectors,
        ids=[p["id"] for p in batch],
    )
```

---

## Why This Matters for AI Apps

Real datasets are big:
- 10,000 products in a Tunisian e-commerce catalog
- 50,000 customer support tickets
- 200,000 paragraphs from internal company documents

At 100 ms per single API call, indexing 50,000 items one by one takes 1.4 hours. Batched at 100, it takes ~5 minutes. The cost difference is real money. The user experience difference is what makes the project ship on time.
