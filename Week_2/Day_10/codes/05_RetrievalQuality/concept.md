# 05 - Retrieval Quality (Capstone)

---

## 📦 Packages

```bash
pip install chromadb mistralai python-dotenv
```

---

## What is Retrieval Quality?

**Retrieval quality** is *how often the retriever returns the right chunks for a given query*. It's measured with numbers, not by feel.

Think of a Tunisian university exam:
- The student studied (you indexed documents)
- The student is asked a question (the user query)
- Did the student turn to the right page in their notes (top-k chunks)?
- We grade with a number — that's retrieval quality

If you can't measure it, you can't improve it.

---

## What is the Problem?

### "It feels good" is not a metric

After Day 10 concept 04, you have a retriever that "seems to work". You try 3 queries, they look right, you ship it.

A week later:
- Some users complain
- Some don't
- You have no idea what % of queries return useful chunks
- You can't tell whether your tweak yesterday made things better or worse

Without metrics, retrieval improvements are guesses.

---

## What is the Solution? Eval With a Labeled Set!

Build a small **evaluation set**: a list of (question, correct_source) pairs. Then compute:

| Metric | What it asks | Range |
|---|---|---|
| **recall@k** | Of the questions, what % have the right chunk in the top-k? | 0–1 |
| **MRR** (Mean Reciprocal Rank) | On average, at what rank does the right chunk appear? Higher is better | 0–1 |
| **hit rate** | Same as recall@k but binary per question | 0–1 |

Start with 20–50 questions. That's enough to tell whether chunk_size=300 beats chunk_size=500 on your data.

---

## How It Works in Python

### Key words to know:

| Keyword / Concept | What it means |
|---|---|
| `eval set` | List of (question, correct_sources) pairs |
| `top-k` | Number of chunks the retriever returns per query |
| `recall@k` | (# queries where any correct chunk is in top-k) / (# queries) |
| `MRR` | Average of `1/rank` of the first correct chunk |
| `ablation` | Change one knob (chunk_size), re-run eval, compare |

### The Golden Rule:
- **Build the eval set early, before you tune anything.** You need a baseline to know whether changes help.

### Basic Usage

```python
EVAL_SET = [
    {"question": "What's the refund window?",             "correct_sources": {"refunds.txt"}},
    {"question": "What products does MASTER Soft build?", "correct_sources": {"products.txt"}},
    {"question": "How many vacation days per year?",      "correct_sources": {"vacation.txt"}},
    # ... 20-50 entries total
]


def evaluate(retriever, eval_set, k=5):
    hits = 0
    mrr_sum = 0.0

    for item in eval_set:
        results = retriever.search(item["question"], k=k)
        sources = [m["source"] for m in results["metadatas"][0]]
        found_rank = None
        for rank, source in enumerate(sources, start=1):
            if source in item["correct_sources"]:
                found_rank = rank
                break

        if found_rank:
            hits += 1
            mrr_sum += 1.0 / found_rank

    return {
        "recall@k": hits / len(eval_set),
        "MRR": mrr_sum / len(eval_set),
    }
```

### BAD vs GOOD

```python
# BAD — eyeballing 3 queries and shipping
for q in ["test 1", "test 2", "test 3"]:
    print(retriever.search(q, k=3))   # subjective, biased, no track record

# GOOD — run eval set, log scores, compare across changes
baseline = evaluate(retriever, EVAL_SET, k=5)
# change chunk_size=300 to 500
new = evaluate(retriever_v2, EVAL_SET, k=5)
print(baseline, new)   # objective comparison
```

---

## Why This Matters for AI Apps

Without retrieval eval, every "improvement" is a coin flip:
- "Try a bigger chunk_size" — does it help? No idea
- "Switch embedding model" — better? No idea
- "Add a re-ranker" — worth the cost? No idea

With eval:
- recall@5 went from 0.62 → 0.81 ⇒ ship it
- MRR went from 0.45 → 0.39 ⇒ revert it

Real teams shipping RAG (Tunisian fintechs, e-commerce, support tools) all maintain an internal eval set, and they grow it every time a user reports a missed answer.

```
The eval set is your retriever's quality control.
Without it, you ship vibes. With it, you ship product.
```

Tomorrow (Day 11) we add the LLM on top — and you can now measure end-to-end whether the answers are grounded.
