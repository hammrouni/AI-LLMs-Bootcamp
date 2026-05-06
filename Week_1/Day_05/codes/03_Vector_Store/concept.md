# 03 - Vector Store (Storage & Indexing)

---

## 📦 Packages

**Requirements**: Python 3.11 or 3.12 (not 3.13+)

```bash
pip install llama-index python-dotenv
```

---

## The Problem: Brute-Force Search is Slow

You have 100,000 chunks with embeddings. A user asks a question. To find the **top 10 most relevant chunks**, naive approach:

```
Compare query_embedding against all 100,000 chunk embeddings
= 100,000 comparisons
= ~500ms to several seconds
❌ Too slow for real-time
```

**Solution**: Vector Store — a database optimized for fast **k-nearest neighbor** (kNN) search.

---

## What is a Vector Store?

A **Vector Store** (or vector database):
1. **Stores** embeddings + their associated metadata
2. **Indexes** embeddings for fast retrieval (e.g., HNSW, IVF)
3. **Searches** by similarity in milliseconds
4. **Optionally persists** to disk/cloud

```
Documents + Embeddings
        ↓
    Vector Store
        ↓
    Indexed for fast search
        ↓
    User query (in seconds)
        ↓
    Top-k similar embeddings (in ms)
```

---

## Vector Store Options

| Store | Type | Setup | Speed | Cost | Scale |
|-------|------|-------|-------|------|-------|
| **SimpleVectorStore** | In-memory | None (built-in) | 🐌 Slow | 💰 Free | < 10K |
| **Chroma** | Embedded | `pip install` | ⚡ Fast | 💰 Free | < 1M |
| **SQLite + sqlite-vec** | Local | `pip install` | ⚡ Fast | 💰 Free | < 100K |
| **FAISS** | In-memory | `pip install` | ⚡ Fast | 💰 Free | < 1M |

---

## Choosing a Vector Store

**For learning & demos**: Use `SimpleVectorStore` (built-in, no setup).

**For small projects** (< 100K vectors):
- SQLite + sqlite-vec (persistent, zero config)
- Chroma (embeddable, clean API)

**For production** (> 100K vectors):
- Elasticsearch (full-text + vector hybrid search)

---

## Using Vector Stores in LlamaIndex

### Option 1: Built-in (SimpleVectorStore)

```python
from llama_index.core import VectorStoreIndex
from llama_index.core.storage import StorageContext
from llama_index.core.vector_stores import SimpleVectorStore

# Create a vector store
vector_store = SimpleVectorStore()

# Create a storage context
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Create an index
index = VectorStoreIndex.from_documents(
    documents,
    storage_context=storage_context
)
```

---

## How Search Works

1. **User asks**: "What is machine learning?"
2. **Convert to embedding**: `[0.12, -0.45, 0.78, ..., 0.23]`
3. **Query vector store**: "Find top 5 nearest embeddings"
4. **Index returns**: 5 chunks with highest cosine similarity
5. **Pass to LLM**: Chunks + user query → generate response

---

## Persistence: Saving Your Index

Once built, **save the index** so you don't recompute embeddings:

```python
# Save
index.storage_context.persist(persist_dir="./storage")

# Load later
from llama_index.core import StorageContext, load_index_from_storage

storage_context = StorageContext.from_defaults(persist_dir="./storage")
index = load_index_from_storage(storage_context)
```

---

## Updating an Index

Add new documents to an existing index:

```python
# Get the vector store from an existing index
vector_store = index.vector_store

# Insert new documents
new_nodes = parser.get_nodes_from_documents(new_documents)
vector_store.add(new_nodes)

# Index is now updated
```

---

## Key Parameters

**similarity_top_k**: How many results to return from the search

```python
query_engine = index.as_query_engine(similarity_top_k=5)
# Returns top 5 most similar chunks
```

- `top_k=1`: Fast, but may miss context
- `top_k=5`: Balanced (⭐ recommended)
- `top_k=20`: Comprehensive, but includes noise

---

## Best Practices

1. **For demos/testing**: Use SimpleVectorStore
2. **For production**: Use Chroma or Elasticsearch
3. **Always persist** if using file-based storage
4. **Monitor search latency** — if > 100ms, consider optimization
5. **Use metadata filters** — "only search recent documents"
