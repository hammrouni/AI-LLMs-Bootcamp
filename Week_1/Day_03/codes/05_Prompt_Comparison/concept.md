# 05 - Prompt Comparison & Quality Evaluation

---

## 📦 Packages

```bash
pip install openai python-dotenv
```

---

## Why Compare Prompts?

Prompt engineering is an **iterative experiment**. You write a prompt, you test it, you improve it. Without a systematic way to compare versions, you're guessing.

Two prompts that look similar can produce dramatically different results:

```
Prompt A: "Summarize this."
Prompt B: "Summarize this article in 3 bullet points. Each bullet must be under 20 words. Focus on actionable takeaways, not background context."

Prompt A gives: a paragraph of text you have to post-process
Prompt B gives: exactly what you need, ready to use
```

---

## What Makes a Prompt "Good"?

A good prompt is one that **consistently** produces output that meets your requirements. Evaluate on these axes:

| Criterion | Question to ask |
|---|---|
| **Format compliance** | Does the output match the format I asked for? |
| **Accuracy** | Is the information correct? |
| **Completeness** | Did it answer everything I asked? |
| **Conciseness** | Is it appropriately short? No unnecessary padding? |
| **Consistency** | Does it behave the same way on repeated runs? |
| **Edge case handling** | What happens with unusual inputs? |

---

## A Simple Scoring Framework

Score each criterion 1-5, then compare totals:

```
Prompt A scores:
  Format:       2/5  (gave a paragraph when I asked for bullets)
  Accuracy:     4/5  (information was mostly correct)
  Completeness: 3/5  (missed one key point)
  Conciseness:  2/5  (too long, lots of filler)
  Total: 11/20

Prompt B scores:
  Format:       5/5  (perfect bullet points)
  Accuracy:     4/5  (same accuracy)
  Completeness: 4/5  (covered main points)
  Conciseness:  5/5  (tight, no filler)
  Total: 18/20
```

---

## The Weak Prompt vs Strong Prompt Pattern

Every prompt improvement follows this pattern:

| Weakness | Fix |
|---|---|
| Too vague ("summarize this") | Add specifics ("3 bullet points, under 20 words each") |
| No role | Add persona ("You are a senior data analyst") |
| No format requirement | Specify format ("Use markdown headers") |
| No length constraint | Add length ("Under 100 words") |
| No audience specification | Add audience ("for a non-technical manager") |
| No constraint on content | Add focus ("Only actionable insights, no background") |

---

## A/B Testing Prompts

The most reliable way to compare prompts is to run them against the **same set of test inputs** and score each:

```python
test_inputs = [
    "input 1",
    "input 2",
    "input 3",
]

for input_text in test_inputs:
    result_A = call_model(prompt_A + input_text)
    result_B = call_model(prompt_B + input_text)
    score_A = evaluate(result_A)
    score_B = evaluate(result_B)
    # compare
```

**Key principle:** Use the SAME inputs for both prompts — never compare prompts on different inputs.

---

## Common Prompt Weaknesses and Fixes

### Weakness 1: No output format specified
```
WEAK:   "List the main risks."
STRONG: "List exactly 3 main risks as bullet points. Each bullet: Risk name — one sentence explanation."
```

### Weakness 2: Ambiguous task scope
```
WEAK:   "Analyze this."
STRONG: "Analyze the sentiment, key topics, and urgency of this customer message. Rate urgency 1-5."
```

### Weakness 3: No constraint on length
```
WEAK:   "Explain how async works."
STRONG: "Explain async/await in Python in under 100 words, for someone who knows synchronous Python."
```

### Weakness 4: Missing context
```
WEAK:   "Improve this email."
STRONG: "Improve this email. The sender is a junior developer writing to their CTO. Goal: ask for a code review without sounding demanding. Keep it under 5 sentences."
```

---

## The Iterative Improvement Loop

```
1. Write a prompt (version 1)
2. Test on 5-10 examples
3. Find the most common failure pattern
4. Fix that specific weakness → version 2
5. Test again on the SAME examples
6. Compare scores
7. Repeat until quality is acceptable
```

Don't try to fix everything at once — fix ONE weakness per iteration. This way you know which change caused the improvement.
