# 02 - Prompt Templates for Grounding

---

## What is a Grounding Prompt?

A **grounding prompt** is the instruction set you wrap around the retrieved context so the LLM answers only from that context. It's how you stop the model from hallucinating outside your documents.

Think of training a new employee at a Tunis bank:
- Day 1: "Welcome. Here are our policies. Always quote the policy when answering customers."
- The new employee answers customers using *only* the policies — not their personal opinion
- That training speech is your grounding prompt

The LLM is the trainee. The prompt is the speech. The context is the policy binder.

---

## What is the Problem?

### Without grounding, the LLM "helps" by inventing

Yesterday you had this prompt:

```
"Answer the question: {question}"
Context: {chunks}
```

The LLM reads the chunks but also feels free to add its own knowledge:

```
Q: "What's our refund window?"
Context: "Refund policy: Customers may request a refund within 14 days..."
A: "Our refund window is 14 days, and most companies extend it to 30 in special cases.
   You can also request store credit or exchange for similar value items."
                ↑ everything past this point is invented
```

Helpful-looking, but completely made up.

---

## What is the Solution? Strict Grounding Prompt!

A good grounding prompt has 4 parts:
1. **Role** — who the assistant is
2. **Rule** — answer only from context
3. **Fallback** — say "I don't know" when missing
4. **Format** — include citations

```
SYSTEM:
You are a support assistant for MASTER Soft.
Answer ONLY using the provided context. Do NOT use outside knowledge.
If the answer is not in the context, reply: "I don't know based on the documents I have."
Always end with citations in the format [source: filename].
```

```
USER:
Context:
[refunds.txt] Refund policy: 14 days, no questions asked.
[products.txt] MASTER Soft builds three products: a CRM platform, a billing API...

Question: What's the refund window?
```

The system message is the contract; the user message is the data.

---

## How It Works in Python

### Key words to know:

| Keyword / Concept | What it means |
|---|---|
| `system message` | Instructions the model follows for the whole conversation |
| `user message` | The actual prompt with context + question |
| `grounding rule` | "Use only context" — non-negotiable in RAG |
| `fallback` | Pre-defined "I don't know" string |
| `citation format` | `[source: filename]` or `[1] [2]` |
| `output format` | If you want structured output, say so explicitly |

### The Golden Rule:
- **Put the grounding rule in the system message, not buried in the user message.** Models pay closer attention to system messages, and you can reuse them across calls.

### Anatomy of a Good Prompt

```python
SYSTEM_PROMPT = """You are a helpful assistant for MASTER Soft, a Tunisian software engineering company.

RULES:
- Answer ONLY using the provided context.
- Do not use outside knowledge, even if you think you know the answer.
- If the answer is not in the context, reply exactly: "I don't know based on the documents I have."
- Be concise: 1–3 sentences.
- End every answer with citations in the format [source: filename].

LANGUAGE:
- Answer in the same language as the question (French, English, or Arabic).
"""


def build_user_message(chunks, sources, question):
    context = "\n\n".join(f"[{src}] {chunk}" for src, chunk in zip(sources, chunks))
    return f"Context:\n{context}\n\nQuestion: {question}"
```

### BAD vs GOOD

```python
# BAD — no system message, no grounding rule, no fallback
messages = [
    {"role": "user", "content": f"Question: {q}\nContext: {ctx}"}
]
# Output: confident invented answers when context is missing

# GOOD — strict grounding contract
messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user",   "content": build_user_message(chunks, sources, q)},
]
# Output: grounded answer with citations, "I don't know" when missing
```

---

## Why This Matters for AI Apps

The prompt template is the single biggest lever for quality after retrieval. Bad prompt → hallucinations even when retrieval is perfect. Good prompt → "I don't know" answers when retrieval misses, which is *the right behavior*.

Real Tunisian use cases that depend on grounding:
- Bank chatbot quoting fee schedules → wrong fees = customer claims / fines
- Hospital protocol assistant → invented dosage = patient harm
- Legal assistant for contracts → invented clause = breach risk

Conservative grounding is not a UX flaw — it's the product. "I don't know" beats "confident wrong" every time in regulated domains.

```
Plain prompt:    answer accuracy 60%, hallucination rate 30%.
Grounded prompt: answer accuracy 88%, hallucination rate 3%, "don't know" rate 9%.
```
