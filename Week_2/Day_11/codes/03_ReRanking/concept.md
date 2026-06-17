# 03 - Re-Ranking

---

## What is Re-Ranking?

**Re-ranking** is a second pass after retrieval that re-orders the top-k candidates using a stronger (and slower) model. The retriever casts a wide net; the re-ranker picks the best fish.

Think of a Tunis recruiter screening CVs:
- First pass: glance at 500 CVs (1 minute each) — keep the top 30 (retriever)
- Second pass: read those 30 carefully (10 minutes each) — pick the top 5 to interview (re-ranker)
- The first pass is cheap and lossy. The second pass is expensive but accurate. You only do it on the survivors.

That's the retriever → re-ranker pattern, exactly.

---

## What is the Problem?

### Top-1 from a bi-encoder retriever isn't always the best chunk

Bi-encoder retrievers (the ones we built in Day 10) embed the query and the document *separately*, then compare vectors. Fast, but coarse. They may put the "almost right" chunk above the "exactly right" one because the embeddings happen to be very close.

```
Query: "How do I get a refund?"
Retriever top 3:
  1. "MASTER Soft builds three products: a CRM platform..."  ← embeds close, wrong topic
  2. "Customers on the Pro plan can request a refund within 14 days..."  ← the actual answer
  3. "Vacation policy: employees accrue 2 paid vacation days..."  ← unrelated
```

The LLM then answers from chunk 1 and produces a wrong answer — even though the right chunk was retrieved.

---

## What is the Solution? Cross-Encoder Re-Ranker!

A **cross-encoder** takes (query, document) *together* and outputs a relevance score. It's much more accurate than bi-encoder similarity, but you can only afford to run it on top-k (e.g., top 20), not on the whole corpus.

```
Stage 1 (cheap): retriever returns top 20 candidates from 100k docs
Stage 2 (slow):  cross-encoder scores each (query, candidate) -> reorders
Stage 3:         keep top 3 after re-ranking -> feed to LLM
```

Two main options for the re-ranker:
1. **Open-source**: `cross-encoder/ms-marco-MiniLM-L-6-v2` from Hugging Face — runs locally
2. **API**: Cohere Rerank, Mistral reranker (when available) — easier deploy, costs money

---

## How It Works in Python

### Key words to know:

| Keyword / Concept | What it means |
|---|---|
| `bi-encoder` | Embeds query and doc separately. Fast, less accurate. |
| `cross-encoder` | Scores (query, doc) jointly. Slower, more accurate. |
| `candidate set` | The top-N from the bi-encoder that the cross-encoder reranks |
| `rerank top-k` | The final number kept after re-ranking |
| `relevance score` | Cross-encoder's output: 0–1 or any real number |

### The Golden Rule:
- **Retrieve more than you need, then rerank.** Retrieve top-20, rerank, keep top-3. The extra recall from a wider retrieval lets the reranker shine.

### Basic Usage (Cross-Encoder, Local)

```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def rerank(query, candidates, top_k=3):
    pairs = [(query, c) for c in candidates]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(scores, candidates), reverse=True)
    return [c for _, c in ranked[:top_k]]
```

### Naive vs Reranked Pipeline

| Stage | Without reranker | With reranker |
|---|---|---|
| Retrieve | top-3 from vector DB | top-20 from vector DB |
| Rerank | — | cross-encoder, keep top-3 |
| Generate | LLM on top-3 chunks | LLM on top-3 *better* chunks |

### BAD vs GOOD

```python
# BAD — rerank everything (10,000 docs) every query
scores = reranker.predict([(query, doc) for doc in all_docs])  # 10s of seconds

# GOOD — narrow down with the bi-encoder first, then rerank
candidates = bi_encoder_retrieve(query, k=20)        # fast
top_chunks = rerank(query, candidates, top_k=3)      # only 20 cross-encoder calls
```

---

## Why This Matters for AI Apps

Re-ranking is the cheapest, highest-impact upgrade to a working RAG:
- Tunisian bank FAQ bot: recall@5 = 0.78 without rerank → 0.91 with rerank
- Internal HR assistant: top-1 accuracy goes from "ok" to "great"
- E-commerce semantic search: conversion from search to click goes up

Cost: an extra 50–200 ms per query and ~50–200 MB of memory for the local cross-encoder. For most apps, that's a free win.

```
No rerank:  retrieval recall@3 = 0.65, end-to-end answer accuracy 70%
With rerank: retrieval recall@3 = 0.85, end-to-end answer accuracy 88%
```

Only skip re-ranking if your retriever is already near-perfect (rare) or you have hard sub-50ms latency budgets.
