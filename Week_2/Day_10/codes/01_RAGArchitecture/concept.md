# 01 - RAG Architecture

---

## What is RAG?

**RAG (Retrieval Augmented Generation)** is a pattern that combines a **retriever** (a vector search over your documents) with a **generator** (an LLM). When the user asks a question, the retriever finds the most relevant pieces of *your* documents, and the LLM generates the answer using those pieces as context.

Think of a Tunisian lawyer's assistant in Tunis:
- The lawyer asks: "What did the contract from 2019 say about late payments?"
- The assistant doesn't memorize every contract. Instead, she goes to the filing cabinet, finds the right contract, finds the right page, and reads it aloud while the lawyer drafts the answer.
- The cabinet = vector DB. The reading = retrieval. The drafting = generation.

RAG = retrieval + generation, working together.

---

## What is the Problem?

### LLMs hallucinate when they don't know

An LLM by itself only knows what was in its training data — and even that, imperfectly. If Mehdi asks a Mistral model "What's our company's refund policy?", the model will *invent* a policy. It sounds confident. It's wrong.

```
User: "What's the refund window in our 2024 customer contract?"
LLM (no RAG): "Customers have 30 days to request a refund..."  ← made up
Reality:                                             14 days
```

Hallucinations destroy trust. You can't ship an AI chatbot to a bank, a hospital, or a law firm if it makes things up.

---

## What is the Solution? RAG!

**Inject the relevant document chunks into the prompt before the LLM answers.** The LLM stops guessing because it has the actual text to quote.

```
User question
   ↓
[Embed the question]
   ↓
[Vector search → top-k chunks from your docs]
   ↓
[Prompt the LLM with: "Answer using only these chunks: ..."]
   ↓
Grounded answer (with citations if you ask for them)
```

The LLM no longer remembers your data — it *reads* your data, every time.

---

## How It Works in Python

### Key words to know:

| Keyword / Concept | What it means |
|---|---|
| `corpus` | The collection of source documents (PDFs, web pages, DB rows) |
| `chunk` | A small piece (200–500 tokens) of one document |
| `embedding` | Vector representation of a chunk (covered Day 8) |
| `retriever` | The component that returns top-k chunks for a query |
| `context window` | Max tokens you can fit in the prompt (Mistral varies by model) |
| `generator` | The LLM (mistral-small, mistral-large, etc.) |
| `grounding` | Forcing the LLM to answer only from the provided context |

### The Golden Rule:
- **Retrieval quality caps the entire system.** If the retriever returns the wrong chunks, the LLM can't recover. Spend more time on retrieval than on prompt tuning.

### Basic Usage

```python
def rag_answer(question, retriever, llm):
    # 1. Retrieve
    chunks = retriever.search(question, k=3)
    context = "\n\n".join(chunks)

    # 2. Generate
    prompt = f"""Answer the question using ONLY the context below.
If the answer is not in the context, say "I don't know."

Context:
{context}

Question: {question}
Answer:"""

    return llm.complete(prompt)
```

That's it. Everything else (chunking, embedding model, vector DB choice, re-ranking) is engineering around those two lines.

### RAG vs Other Patterns

| Pattern | When to use | When NOT to use |
|---|---|---|
| Pure LLM call | General knowledge, creative writing | Anything domain-specific |
| Fine-tuning | Style change, domain adaptation | Frequently changing data |
| RAG | Custom docs, frequently updated knowledge | Tiny / static knowledge |

### BAD vs GOOD

```python
# BAD — stuff a huge document into the prompt every time
context = open("entire_handbook.pdf").read()  # 200k tokens, exceeds limit, slow, expensive

# GOOD — retrieve only the relevant 3 chunks
chunks = retriever.search(question, k=3)
context = "\n\n".join(chunks)  # ~1500 tokens, fast, cheap
```

---

## Why This Matters for AI Apps

RAG is the dominant pattern for AI apps that touch private data:
- A bank chatbot grounded in product PDFs (BIAT, ATB, BNA in Tunisia)
- A hospital assistant grounded in medical protocols
- A help desk grounded in past tickets
- A legal assistant grounded in contracts

Without RAG: the AI invents. With RAG: the AI quotes. The difference is the difference between a demo and a product.

```
Demo (no RAG): "Looks impressive but says wrong things 30% of the time."
Product (RAG): "Sounds boring but is correct 95% of the time — and shows sources."
```

The rest of Day 10 builds the retrieval half of this pipeline, piece by piece.
