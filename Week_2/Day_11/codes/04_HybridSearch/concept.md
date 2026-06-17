# 04 - Hybrid Search

---

## 📦 Packages

```bash
pip install rank-bm25 chromadb mistralai python-dotenv
```

---

## What is Hybrid Search?

**Hybrid search** combines two different retrievers — usually **keyword (BM25)** and **vector (embeddings)** — and merges their results. You get the strengths of both.

Think of looking for a restaurant in Tunis:
- **Keyword** is asking your friend: "Do you know a place called 'Le Petit Soleil'?"
- **Vector** is asking your friend: "Do you know a place with a vibe like that café in Sidi Bou Said?"
- Each finds different restaurants. Together you get the full picture.

Vector search captures meaning. Keyword search captures exact words: brand names, product codes, acronyms, rare technical terms. You want both.

---

## What is the Problem?

### Embeddings struggle with acronyms, codes, and rare terms

Vectors encode meaning, but they squash rare tokens into the average meaning of the surrounding text. Real-world consequences:

```
Query: "Who handles refund escalations at MASTER Soft?"
Vector retriever: finds docs about refunds and MASTER Soft, but may rank them differently
Keyword retriever (BM25): anchors on "refund" + "escalations" + "MASTER Soft" literally
```

The two methods rank positions 2–3 differently. With a larger corpus (1000+ docs), even top-1 diverges:
- Names (`Yasmine Ben Ali`) — exact match beats semantic
- Product codes (`SKU-94823`) — no semantic meaning
- Legal references (`Article 63 de la loi 2023`) — exact match wins

BM25 — a classic IR scoring algorithm — handles these perfectly.

---

## What is the Solution? Combine BM25 + Vectors!

Two strategies:
1. **Score fusion (Reciprocal Rank Fusion)**: get top-k from each, merge by rank
2. **Score blending**: linearly combine `α × vector_score + (1−α) × bm25_score`

RRF is the simplest and most popular. No tuning needed.

```
Vector top-5:  [doc_A, doc_B, doc_C, doc_D, doc_E]
BM25 top-5:    [doc_X, doc_A, doc_Y, doc_B, doc_Z]

RRF formula:   score(d) = Σ 1 / (k + rank_i(d))   over all retrievers i
                          (k usually = 60)

Final order:   doc_A (in both), doc_B (in both), doc_X (only BM25),
               doc_C, doc_Y, ...
```

The doc that appears in both rankings rises to the top — exactly what you want.

---

## How It Works in Python

### Key words to know:

| Keyword / Concept | What it means |
|---|---|
| `BM25` | A scoring formula for keyword matching, robust default |
| `tf-idf` | Predecessor of BM25 — less robust on long docs |
| `RRF` | Reciprocal Rank Fusion — combine rankings, not raw scores |
| `α blending` | Weighted sum of normalized scores |
| `tokenization` | How BM25 splits text into words (matters for Arabic/French) |

### The Golden Rule:
- **Use RRF unless you have a labeled set to tune `α`.** RRF is parameter-free and beats blending on most data without tuning.

### Basic Usage

```python
from rank_bm25 import BM25Okapi

# Tokenize once at index time
tokenized_docs = [d.lower().split() for d in documents]
bm25 = BM25Okapi(tokenized_docs)


def bm25_search(query, k=5):
    tokenized_q = query.lower().split()
    scores = bm25.get_scores(tokenized_q)
    top_idx = sorted(range(len(scores)), key=lambda i: -scores[i])[:k]
    return [(i, documents[i]) for i in top_idx]


def rrf_merge(rankings, k=60, top_k=5):
    """rankings: list of [doc_id, ...] from each retriever."""
    score = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, start=1):
            score[doc_id] = score.get(doc_id, 0) + 1.0 / (k + rank)
    return sorted(score.items(), key=lambda x: -x[1])[:top_k]


vector_ids = [i for i, _ in vector_search(query, k=10)]
bm25_ids   = [i for i, _ in bm25_search(query, k=10)]
final_ids  = [doc_id for doc_id, _ in rrf_merge([vector_ids, bm25_ids], top_k=5)]
```

### BAD vs GOOD

```python
# BAD — vector-only search may miss exact keyword matches
results = retriever.search("Yasmine Ben Ali refund", k=3)   # may rank by meaning, not name
# Users frustrated when the exact person is in the docs but ranked low.

# GOOD — hybrid
v_ids   = vector_top_k("Yasmine Ben Ali refund", 10)
bm_ids  = bm25_top_k("Yasmine Ben Ali refund", 10)
final   = rrf_merge([v_ids, bm_ids], top_k=3)
# BM25 anchors on "Yasmine", vector catches "refund" meaning — both contribute.
```

---

## Why This Matters for AI Apps

Hybrid search saves you on the queries where one method has blind spots:
- SaaS support bot: "Who is Yasmine?" needs keyword, "refund help" needs vector
- E-commerce: SKU lookups need keyword, "similar to this" needs vector
- Legal: article numbers need keyword, "concept of X" needs vector

A pure-vector retriever loses ~15–25% of queries. Hybrid closes most of that gap with one extra index.

```
Vector-only:  recall@5 = 0.74
Hybrid (RRF): recall@5 = 0.88
Cost:         one extra BM25 index in memory + a few ms per query
```

Hybrid + reranking is the gold-standard retrieval stack for production RAG.
