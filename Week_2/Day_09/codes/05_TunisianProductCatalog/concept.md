# 05 - Tunisian Product Catalog (Capstone)

---

## 📦 Packages

```bash
pip install qdrant-client mistralai python-dotenv
```

---

## What is This Capstone?

A **production-style product catalog** for a Tunisian craft marketplace, with:
- Real Mistral embeddings of product descriptions
- Multiple metadata fields (region, price, category, in_stock)
- Batched inserts (concept 03)
- HNSW + payload indexes (concept 04)
- Combined vector + filter queries (concept 02)
- All in one Qdrant collection set up the right way (concept 01)

Think of it as the backbone of a Jumia/Carrefour-style search box, but tuned for Tunisian crafts: leather goods from Tunis, ceramics from Nabeul, rugs from Kairouan, olive wood from Sfax.

---

## What is the Problem?

### A "search bar" that works in marketing slides but not in real shops

Most ecommerce demos cherry-pick three products and a perfect query. Real production catalogs face:
- 5k–500k items
- Multi-field filters from facets (category, region, price range, in stock)
- Multilingual queries (Arabic, French, English, darija)
- Sub-second response times on small VPS hardware

Day 9 tools, combined, handle all of this on a single $20/month server.

---

## What is the Solution? Glue All Day-9 Concepts Together!

```
[products.json]
      ↓ batch-embed (concept 03)
[1024-dim vectors]
      ↓ upsert into Qdrant collection (concept 01)
[Qdrant HNSW + payload indexes] (concept 04)
      ↓ vector + filter query (concept 02)
[top-k matching products]
```

This is the *exact* architecture used in production by most teams shipping AI search today.

---

## How It Works in Python

### The Golden Rule:
- **Build the index in one shot at startup; query forever after.** Catalog updates (new product, price change) become tiny upserts, not full rebuilds.

### Architecture Outline

```python
def setup_catalog(client, products, mistral):
    """One-time setup: collection + payload indexes + batch insert."""
    if client.collection_exists("products"):
        client.delete_collection("products")
    client.create_collection(
        "products",
        vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
    )

    for field, schema in [
        ("region",   "keyword"),
        ("category", "keyword"),
        ("price",    "integer"),
        ("in_stock", "bool"),
    ]:
        client.create_payload_index("products", field_name=field, field_schema=schema)

    for batch in chunked(products, 50):
        texts = [p["text"] for p in batch]
        vectors = embed_batch(mistral, texts)
        client.upsert(
            "products",
            points=[
                PointStruct(id=p["id"], vector=v, payload=p["meta"] | {"text": p["text"]})
                for p, v in zip(batch, vectors)
            ],
        )


def search(client, mistral, query, region=None, max_price=None, k=5):
    """Vector + filter query."""
    q_vec = embed_batch(mistral, [query])[0]

    must = [FieldCondition(key="in_stock", match=MatchValue(value=True))]
    if region:
        must.append(FieldCondition(key="region", match=MatchValue(value=region)))
    if max_price is not None:
        must.append(FieldCondition(key="price", range=Range(lte=max_price)))

    return client.query_points(
        "products",
        query=q_vec,
        query_filter=Filter(must=must),
        limit=k,
    ).points
```

### BAD vs GOOD

```python
# BAD — rebuild index on every server start
for p in products:
    upsert(p)  # repeated, wasteful, slow

# GOOD — only rebuild on data change
if client.count("products") < len(products):
    rebuild_index(client, products)
else:
    print("Index is up to date.")
```

---

## Why This Matters for AI Apps

This capstone is the blueprint for:
- **E-commerce search** (Carrefour Tunis, Jumia, MyTek): vector + facet filters
- **Job boards** (TanitJobs-style): match CV embeddings, filter by city/seniority
- **Real estate** (Mubawab/Tayara): "find apartments like this" + price/rooms filters
- **Document search** (legal/medical): "find similar contracts" + jurisdiction/year filters

Master this pipeline and you can ship 80% of production AI-search features tomorrow.

```
Hayet's marketplace, before Day 9 stack: 800ms search, no filters.
After Day 9 stack: 40ms search, four-field filters, batch-rebuild in 90s.
```

The same patterns will return in Day 10–11 when we add an LLM on top to build full RAG.
