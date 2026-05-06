# 04 - Query Engine (Search & Retrieval)

---

## 📦 Packages

**Requirements**: Python 3.11 or 3.12 (not 3.13+)

```bash
pip install llama-index llama-index-llms-mistralai python-dotenv
```

---

## What is a Query Engine?

A **Query Engine** orchestrates the retrieval → generation pipeline:

```
User Query: "What is RAG?"
      ↓
  1. Embed the query
      ↓
  2. Search vector store (similarity search)
      ↓
  3. Retrieve top-k chunks + metadata
      ↓
  4. Pass chunks to LLM as context
      ↓
  5. LLM generates response
      ↓
Response + source citations
```

It's the **orchestrator** between the vector store and the LLM.

---

## Query Engines in LlamaIndex

### Default: VectorStoreQueryEngine

```python
# Simplest usage
query_engine = index.as_query_engine(
    similarity_top_k=3,      # Return top 3 chunks
    temperature=0.0,         # 0 = deterministic
)

response = query_engine.query("What is machine learning?")
print(response)                    # The generated text
print(response.source_nodes)       # Where it came from
```

The **default behavior**:
1. Convert query to embedding
2. Search vector store
3. Get top k chunks
4. Synthesize response with LLM

### Custom Retrieval

For more control, use `RetrieverQueryEngine`:

```python
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine

retriever = VectorIndexRetriever(index, similarity_top_k=5)
query_engine = RetrieverQueryEngine(retriever)
```

---

## Understanding Retrieval Quality

### The Retrieval-Generation Pipeline

```
Query: "How do I learn Python?"

┌─────────────────────────────────────────┐
│ RETRIEVAL PHASE                         │
│ ─────────────────────────────────────── │
│ ✓ Search embeddings → Top 3 chunks:     │
│   1. "Python basics..." (score: 0.92)   │
│   2. "Learning roadmap..." (0.85)       │
│   3. "Online resources..." (0.78)       │
└─────────────────────────────────────────┘
       ↓
┌─────────────────────────────────────────┐
│ GENERATION PHASE                        │
│ ─────────────────────────────────────── │
│ Pass chunks to LLM with system prompt:  │
│ "Answer based ONLY on these documents"  │
│                                         │
│ LLM output: "To learn Python, start... │
│ [cites sources above]"                  │
└─────────────────────────────────────────┘
```

**Key insight**: Retrieval quality → generation quality. Bad retrieval = bad response.

---

## Tuning Retrieval

### similarity_top_k

How many chunks to pass to the LLM.

```python
# Top-1: Speed priority
query_engine = index.as_query_engine(similarity_top_k=1)
# Fast but may miss important context

# Top-5: Balanced (⭐ recommended)
query_engine = index.as_query_engine(similarity_top_k=5)
# Good precision + coverage

# Top-10: Coverage priority
query_engine = index.as_query_engine(similarity_top_k=10)
# Comprehensive but may add noise
```

| top_k | Latency | Relevance | Context | Best For |
|-------|---------|-----------|---------|----------|
| 1 | ⚡ ms | ⭐⭐⭐⭐⭐ | 🔴 | Simple queries |
| 3-5 | ⚡ ms | ⭐⭐⭐⭐ | 🟢 | **Most cases** |
| 10 | 10 ms | ⭐⭐⭐ | 🟢🟢 | Complex queries |
| 20+ | 50 ms | ⭐⭐ | 🟡🟡 | Token budget unlimited |

---

## Response Structure

```python
response = query_engine.query("What is Python?")

# Access components:
print(response.response)           # The text answer
print(response.source_nodes)       # List of source chunks
for node in response.source_nodes:
    print(node.text)               # Chunk content
    print(node.score)              # Similarity score (0-1)
    print(node.metadata)           # File, page, etc.
```

---

## Evaluating Retrieval

Ask: Did the query engine retrieve the **right chunks**?

```python
response = query_engine.query("How does RAG work?")

# Check results manually:
print(f"Retrieved {len(response.source_nodes)} chunks")
for i, node in enumerate(response.source_nodes, 1):
    print(f"\n{i}. Score: {node.score:.3f}")
    print(f"   Content: {node.text[:100]}...")
    print(f"   Source: {node.metadata}")

# Good signs:
# ✓ All chunks are relevant to the query
# ✓ Top chunk has score > 0.7
# ✓ Chunks add complementary info (not duplicates)

# Bad signs:
# ✗ Unrelated chunks included
# ✗ Top score < 0.5
# ✗ All chunks are nearly identical
```

---

## Advanced: Filtering & Re-ranking

### Metadata Filters

Restrict search to specific documents:

```python
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.vector_stores import MetadataFilter, MetadataFilters

filters = MetadataFilters(
    filters=[
        MetadataFilter(key="document_type", value="official_docs"),
        MetadataFilter(key="year", value=2024, operator=">="),
    ]
)

retriever = VectorIndexRetriever(index, filters=filters, top_k=5)
query_engine = RetrieverQueryEngine(retriever)
```

### Re-ranking (2-stage retrieval)

Retrieve more, then re-rank:

```python
# Stage 1: Get top 20 by embedding similarity
response = query_engine.query("My question", similarity_top_k=20)

# Stage 2: LLM re-ranks to top 5
# (Does a more expensive semantic re-ranking)
# → More accurate than embedding-only ranking
```

---

## Best Practices

1. **Start with top_k=3**, adjust based on quality
2. **Always review source_nodes** — verify relevance
3. **Use metadata filters** if you have structured data
4. **Monitor latency** — balance speed vs. coverage
5. **Test with real queries** — embeddings work differently on your domain data
