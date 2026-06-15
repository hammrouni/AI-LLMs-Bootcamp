# 03 - Text Chunking

---

## 📦 Packages

```bash
pip install langchain-text-splitters
```

---

## What is Chunking?

**Chunking** is the act of splitting a long document into smaller pieces ("chunks") that:
1. Fit comfortably in an LLM's context window
2. Each contain a self-contained idea
3. Have just enough overlap with neighbors so meaning isn't cut in half

Think of a Tunisian school textbook:
- The whole book is too long to give a student in one piece for "find the answer"
- Each chapter is better — but a chapter is still 30 pages
- A few paragraphs at a time is ideal — that's a chunk

The trick is choosing how big each piece should be and where to cut.

---

## What is the Problem?

### Cutting at the wrong place destroys meaning

Sonia tries naive chunking: every 500 characters, no exceptions.

```
Chunk 23 ends with: "...customers can request a re-"
Chunk 24 starts with: "fund within 14 days..."
```

When the retriever searches for "refund policy", it finds chunk 24 — but chunk 24 doesn't even contain the word "refund" (it was cut off!). The retrieval misses the most relevant chunk entirely.

Also, chunks too small lose context. Chunks too large dilute the embedding signal. There's a sweet spot.

---

## What is the Solution? Smart Splitters!

Three common strategies:

| Strategy | What it does | Good for |
|---|---|---|
| Fixed-size | Cut every N characters/tokens | Quick prototypes, uniform docs |
| Recursive | Try paragraphs → sentences → words, in order | The default — works on most text |
| Semantic | Split where the topic shifts (use embeddings) | Long, dense docs (medical, legal) |

Recursive splitters (like LangChain's `RecursiveCharacterTextSplitter`) are the default in production. They try to break on natural boundaries (double newlines, then single newlines, then sentences, then words) before giving up and cutting arbitrarily.

---

## How It Works in Python

### Key words to know:

| Keyword / Concept | What it means |
|---|---|
| `chunk_size` | Target size — usually in characters or tokens |
| `chunk_overlap` | How many chars/tokens neighbors share (50–100 is typical) |
| `separators` | Ordered list of preferred split points |
| `recursive splitter` | Try big separators first, fall back to small ones |
| `token-based` | Use tokenizer (more accurate for LLM context) |

### The Golden Rule:
- **Aim for 300–500 tokens per chunk with 50–100 token overlap.** Smaller for short Q&A, larger for technical docs.

### Basic Usage

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,        # characters
    chunk_overlap=80,
    separators=["\n\n", "\n", ". ", " ", ""],
)

chunks = splitter.split_text(long_text)
```

### How to Choose

| chunk_size | When to use |
|---|---|
| 100–200 chars | FAQ entries, short policy bullets |
| 300–500 chars | Default for paragraphs |
| 800–1500 chars | Long technical sections, legal clauses |

| chunk_overlap | When to use |
|---|---|
| 0–20 chars | Independent items (FAQs, product entries) |
| 50–100 chars | Flowing prose — preserves cross-sentence context |
| 200+ chars | Documents where ideas span paragraphs |

### BAD vs GOOD

```python
# BAD — fixed-size cut without separators (breaks words and sentences)
def naive_split(text, size=500):
    return [text[i:i+size] for i in range(0, len(text), size)]

# GOOD — recursive, respects natural boundaries
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=80)
chunks = splitter.split_text(text)
```

---

## Why This Matters for AI Apps

Chunking quality directly drives retrieval recall:
- A FAQ bot with chunks=200 returns the exact answer
- The same bot with chunks=2000 returns a chunk that *contains* the answer + 5 other topics — the LLM gets confused
- A legal bot with chunks=200 cuts clauses in half — useless
- The same bot with chunks=1200 keeps the clause whole — retrieval works

Tunisian use cases:
- Bank fees PDF: chunk per fee entry (~200 chars)
- University course catalog: chunk per course (~500 chars)
- Legal contract: chunk per clause (~1200 chars)

```
Wrong chunk size: retrieval recall@5 = 30%, users frustrated.
Right chunk size: retrieval recall@5 = 90%, users happy.
```

There is no universal "best" — measure on your data.
