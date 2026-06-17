# 05 - Tunisian FAQ Bot (Capstone)

---

## 📦 Packages

```bash
pip install chromadb mistralai langchain-text-splitters rank-bm25 python-dotenv
```

---

## What is This Capstone?

A **full RAG FAQ bot** for a Tunisian company. It ties together everything from Day 10 and Day 11:
- Document preparation (Day 10 concept 02)
- Chunking (Day 10 concept 03)
- A retriever class (Day 10 concept 04)
- Eval set + recall@k (Day 10 concept 05)
- End-to-end pipeline with grounded prompt (Day 11 concepts 01–02)
- Hybrid search (Day 11 concept 04)
- Citations + fallback

The bot answers questions about MASTER Soft (the fictional Tunisian software engineering company we've been using), quoting the source file for each answer.

---

## What is the Problem?

### Every concept worked in isolation; now we need them working together

Each Day 10/11 concept demoed one piece. A real product has to run all of them in one process, end to end, with a single `ask(question)` call that:
1. Cleans / loads docs (if needed)
2. Chunks them
3. Indexes both vector and BM25
4. On a user query, runs hybrid retrieval
5. Builds a grounded prompt with citations
6. Calls the LLM
7. Returns the answer + sources

A capstone forces you to make the seams match.

---

## What is the Solution? One Class, One ask() Method!

```python
class TunisianFAQBot:
    def __init__(self, mistral, corpus: dict, chunk_size=300, chunk_overlap=50):
        # Chunk + embed + store in Chroma + build BM25 index
        ...

    def ask(self, question: str, k=3) -> dict:
        # Hybrid retrieve (vector + BM25 + RRF) -> grounded prompt -> LLM -> answer + sources
        ...
```

`corpus` is a `{"filename.txt": "content..."}` mapping. Internally, the bot chunks, embeds, BM25-indexes, and is ready for queries.

Output is a dict:

```python
{
    "answer":  "Refund window is 14 days, no questions asked.",
    "sources": ["refunds.txt"],
    "raw_question": "What's the refund window?",
}
```

The downstream code (CLI, REST API, Slack bot) only sees this clean shape.

---

## How It Works in Python

### The Golden Rule:
- **Capstones expose a stable contract, not the internals.** External code calls `.ask()`. If you change the chunker or the embedding model, the contract stays the same.

### Architecture

```
Corpus dict
   │
   ├── chunk + embed -> vector DB (Chroma)
   └── tokenize     -> BM25 index
                ↓
            ask(question, k=3)
                ↓
       hybrid retrieve top-N (RRF)
                ↓
        grounded prompt build
                ↓
              Mistral LLM
                ↓
       {answer, sources, raw_question}
```

### Citation Discipline

| Output field | Source | Example |
|---|---|---|
| `answer`  | LLM | "Refund window is 14 days..." |
| `sources` | Retriever metadata | `["refunds.txt"]` |
| `raw_question` | Echoed input | "What's the refund window?" |

### BAD vs GOOD

```python
# BAD — capstone exposes internals
answer = bot.llm.chat.complete(...)   # caller has to know about Mistral, prompts, retriever

# GOOD — single contract
result = bot.ask("What's the refund window?")
print(result["answer"], result["sources"])
```

---

## Why This Matters for AI Apps

This capstone is the architectural template for any FAQ / support / knowledge-base AI app:
- A Tunisian Telecom support bot
- A SaaS product knowledge base
- An internal HR assistant for a startup
- A municipality info bot ("What documents do I need to renew my passeport in Tunis?")

Tomorrow we'll explore local models (Ollama) so the same pipeline can run without a cloud API call — important for any Tunisian institution worried about data residency or sovereignty.

```
At the end of Day 11, you can ship a working RAG product.
The rest of the week is about making it cheaper, more reliable, and measurable.
```
