# 01 - End-to-End RAG Pipeline

---

## 📦 Packages

```bash
pip install chromadb mistralai langchain-text-splitters python-dotenv
```

---

## What is an End-to-End RAG Pipeline?

An **end-to-end RAG pipeline** wraps the entire flow — chunk → embed → store → retrieve → prompt → generate → return — behind a single function call:

```python
answer = pipeline.ask("What's the refund window?")
```

Think of a Tunisian customer service hotline:
- Customer dials the number (the `.ask()` call)
- The agent (the pipeline) checks the company manual (retrieval), reads the relevant page (context), and answers in their own words (generation)
- The customer hears one clean answer

The customer never sees the manual, the page numbers, or the lookup process — just the result.

---

## What is the Problem?

### Yesterday's retriever returns chunks; users want answers

After Day 10 you have a retriever that returns top-k chunks. But users don't want chunks — they want sentences. They want "14 days", not the paragraph that contains "14 days".

```
User asks: "What's the refund window?"
Retriever returns: 3 chunks of text about refunds
User reaction: "Cool... but what's the actual answer?"
```

We need to turn chunks into a written answer. That's the generation step.

---

## What is the Solution? Wire In the LLM!

Add one more step after retrieval:

```
[question] → [retriever] → [chunks] → [prompted LLM] → [final answer]
```

The LLM reads the chunks and writes a one-paragraph answer that quotes them. The output is a real answer, not a pile of context.

---

## How It Works in Python

### Key words to know:

| Keyword / Concept | What it means |
|---|---|
| `pipeline` | The class that owns retriever + LLM client + prompt template |
| `system prompt` | Instructions that bind the LLM's behavior (always set this) |
| `context` | Chunks joined with separators, fed to the LLM |
| `grounded answer` | Answer based on context only — no hallucinations |
| `citation` | Pointer back to the source chunk for trust |

### The Golden Rule:
- **The pipeline class owns the prompt template.** No code outside the class should construct prompts. That way you can change the prompt in one place.

### Basic Usage

```python
class RAGPipeline:
    def __init__(self, retriever, mistral_client, model="mistral-small-latest"):
        self.retriever = retriever
        self.client = mistral_client
        self.model = model
        self.system_prompt = (
            "You are a helpful assistant for MASTER Soft. "
            "Answer ONLY using the provided context. "
            "If the answer is not in the context, say 'I don't know based on the documents I have.' "
            "End the answer with citations in the form [source: filename]."
        )

    def ask(self, question, k=3):
        results = self.retriever.search(question, k=k)
        chunks = results["documents"][0]
        sources = [m["source"] for m in results["metadatas"][0]]

        context = "\n\n".join(f"[{s}] {c}" for s, c in zip(sources, chunks))

        response = self.client.chat.complete(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user",   "content": f"Context:\n{context}\n\nQuestion: {question}"},
            ],
        )
        return response.choices[0].message.content.strip()
```

### BAD vs GOOD

```python
# BAD — pipeline split across many files, prompt re-built every call
def ask(q):
    chunks = retriever.search(q, k=3)
    context = "\n".join(c for c in chunks["documents"][0])
    prompt = f"Answer this: {q}\n\nContext: {context}"   # no system message, no grounding
    return llm.complete(prompt)

# GOOD — single class, system prompt for grounding, citations
pipeline = RAGPipeline(retriever, mistral_client)
answer = pipeline.ask("What's the refund window?")
```

---

## Why This Matters for AI Apps

This single-function `ask()` is what you actually expose to the rest of your app:
- A chatbot endpoint calls `pipeline.ask(user_message)`
- A Slack bot calls it
- A FastAPI route calls it
- A Streamlit demo calls it

All of them see "question goes in, answer comes out". The complexity stays inside the pipeline.

```
Without RAGPipeline: each surface re-implements retrieval + prompting.
With RAGPipeline: every surface is 1 line of code.
```

Day 11 polishes this pipeline (better prompts, re-ranking, hybrid search, eval). Day 1 of building real apps begins next week.
