# 02 - Few-Shot Learning

---

## 📦 Packages

```bash
pip install openai python-dotenv
```

---

## What is Few-Shot Learning?

**Few-Shot Learning** means giving the AI a small number of **examples** (called "shots") that demonstrate the exact task you want it to perform — before asking it to do the real task.

You are not training the model. You are giving it context that says:
> "This is the pattern. This is the format. This is what I expect. Now do it for this new input."

---

## The Spectrum: 0-Shot → 1-Shot → Few-Shot

### 0-Shot (no examples)
You give only the instruction:
```
Classify this review as Positive or Negative:
"The food was cold and the service was slow."
```
The model uses its training to decide what to do. Works for simple, well-known tasks.

### 1-Shot (one example)
You give one example before the real task:
```
Classify reviews as Positive or Negative.

Review: "Amazing coffee and friendly staff!"
Classification: Positive

Review: "The food was cold and the service was slow."
Classification:
```
One example makes the format crystal clear.

### Few-Shot (2-5 examples)
You give 2-5 examples:
```
Classify reviews as Positive or Negative.

Review: "Amazing coffee and friendly staff!"
Classification: Positive

Review: "Had to wait 40 minutes and the food was wrong."
Classification: Negative

Review: "Decent price but nothing special."
Classification: Neutral

Review: "The food was cold and the service was slow."
Classification:
```
More examples help with ambiguous cases and edge cases.

---

## Why Does Few-Shot Work?

The model has seen millions of "completion" patterns during training. When you give it examples, you're activating a pattern-matching process:

1. Model reads your examples
2. Extracts the pattern: INPUT → OUTPUT
3. Applies the same pattern to the new input

It's like showing someone 3 examples of a math sequence: 2, 4, 8... and asking "what comes next?" — they infer the rule (×2) and answer 16.

---

## What Makes a Good Few-Shot Example?

### ✅ Good examples are:
- **Diverse** — cover different cases, not all easy ones
- **Clear** — the pattern is obvious from input to output
- **Representative** — similar style/domain to your real task
- **Balanced** — if classifying 3 categories, show examples of each

### ❌ Bad examples:
- All very similar (doesn't help with varied inputs)
- Inconsistent format (model gets confused about what the output should look like)
- Too long (wastes tokens, may confuse the model)
- All from one category (biases the model)

---

## Format Matters — Be Consistent

The model learns from your format exactly. If your examples use `Classification:` but sometimes `Label:`, the model may flip between both.

**Pick one format and stick to it:**

```
# BAD — inconsistent
Input: "good"
Output: Positive

Input: "terrible"
Label: Negative    ← different keyword!

# GOOD — consistent
Input: "good"
Classification: Positive

Input: "terrible"
Classification: Negative

Input: [new input]
Classification:
```

---

## Few-Shot for Different Tasks

### Text Classification
```
Tweet: "Just landed in Tunis! So excited!"
Sentiment: Positive

Tweet: "Missed my train again, terrible morning."
Sentiment: Negative

Tweet: "Flight was on time."
Sentiment:
```

### Format Transformation
```
Input: "Ahmed Ben Ali, 25, Software Engineer"
Output: {"name": "Ahmed Ben Ali", "age": 25, "role": "Software Engineer"}

Input: "Fatima Zahra, 31, Doctor"
Output: {"name": "Fatima Zahra", "age": 31, "role": "Doctor"}

Input: "Karim Mansour, 28, Data Scientist"
Output:
```

### Text Style Transfer
```
Formal: "We regret to inform you that your application has not been successful."
Casual: "Sorry, we couldn't take you this time."

Formal: "Please be advised that the meeting has been rescheduled to Thursday."
Casual: "Heads up — the meeting moved to Thursday."

Formal: "Your order will be dispatched within 3-5 business days."
Casual:
```

---

## How Many Examples Do You Need?

| Task complexity | Recommended shots |
|---|---|
| Simple binary classification | 1-2 shots |
| Multi-class classification (3-5 classes) | 2-3 shots per class |
| Format transformation | 2-3 shots |
| Complex reasoning | 3-5 shots with reasoning |
| Highly specialized domain | 5+ shots |

**Rule:** More shots = better accuracy but more tokens. Find the minimum that gives you the quality you need.
