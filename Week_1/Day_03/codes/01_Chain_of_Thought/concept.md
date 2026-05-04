# 01 - Chain of Thought (CoT)

---

## 📦 Packages

```bash
pip install openai python-dotenv
```

---

## What is Chain of Thought?

**Chain of Thought (CoT)** is a prompting technique where you ask the AI to show its reasoning **step by step** before giving the final answer.

Instead of:
> "What is 17 × 24?" → "408" ← (might be wrong, no reasoning shown)

You get:
> "What is 17 × 24? Think step by step."
> → "17 × 24 = 17 × 20 + 17 × 4 = 340 + 68 = 408" ← (correct, with proof)

---

## Why Does It Work?

Language models predict the next token. When forced to "think out loud," each reasoning step becomes context for the next — the model can't jump to a wrong answer because the intermediate steps constrain it.

Think of it like a student doing math:
- **No CoT:** writes the answer directly → more errors
- **With CoT:** shows work in the margin → catches mistakes before writing the final answer

---

## Two Types of Chain of Thought

### 1. Zero-Shot CoT
Just add a magic phrase to any prompt. No examples needed.

```
"Solve this. Think step by step."
"Reason through this carefully before answering."
"Explain your reasoning, then give the final answer."
```

**When to use:** Quick boost for any reasoning task. Works well for math, logic, classification.

### 2. Few-Shot CoT
Give the model examples that include reasoning, then ask your question.

```
Example 1:
Q: If Yasmine has 5 apples and gives 2 to Mehdi, how many does she have?
A: Yasmine starts with 5 apples. She gives away 2. 5 - 2 = 3. She has 3 apples.

Example 2:
Q: A train travels 60 km/h for 2.5 hours. How far does it go?
A: Distance = speed × time = 60 × 2.5 = 150 km. The train travels 150 km.

Now answer:
Q: A recipe needs 3 cups of flour per batch. How much for 7 batches?
A:
```

**When to use:** When zero-shot CoT isn't accurate enough, or when you need a specific reasoning style/format.

---

## When to Use CoT vs When NOT To

| Situation | Use CoT? | Why |
|---|---|---|
| Multi-step math problem | ✅ Yes | Reasoning helps avoid arithmetic errors |
| Logic puzzle / riddle | ✅ Yes | Forces structured thinking |
| Code debugging | ✅ Yes | Step-by-step trace catches bugs |
| Complex classification | ✅ Yes | Justification improves accuracy |
| "What is the capital of Tunisia?" | ❌ No | Simple factual — CoT adds no value |
| "Translate this word" | ❌ No | One-step task, CoT wastes tokens |
| "Write me a haiku" | ❌ No | Creative tasks don't need reasoning steps |

**Rule of thumb:** If a human would need scratch paper to solve it, use CoT. If the answer is immediate, skip CoT.

---

## CoT Trigger Phrases

These phrases reliably activate step-by-step reasoning in most models:

```
"Think step by step."
"Let's reason through this carefully."
"Explain your reasoning before giving the final answer."
"Work through this problem."
"Break this down step by step."
"Show your work."
```

---

## Advanced: Self-Consistency

Run the same CoT prompt **multiple times** and take the majority answer. This works because different reasoning paths sometimes reach different conclusions — the most common correct answer wins.

```
Run prompt 3 times:
  Run 1: "...so the answer is 42" ✓
  Run 2: "...therefore the answer is 42" ✓
  Run 3: "...the result is 40" ✗  ← outlier

Final answer: 42 (2 out of 3 agree)
```

---

## The Cost Tradeoff

CoT uses **more tokens** — both in the response AND in processing. More tokens = more time + more cost.

- Simple factual question: ~10 tokens answer
- Same question with CoT: ~100-200 tokens answer

Use CoT selectively: on hard problems where accuracy matters more than speed.
