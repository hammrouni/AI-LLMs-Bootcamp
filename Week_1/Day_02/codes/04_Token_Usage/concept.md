# 04 - Token Usage & Cost Tracking

---

## 📦 Packages

```bash
pip install httpx python-dotenv
```

---

## What is a Token?

AI models don't read words — they read **tokens**.

A token is roughly:
- 1 word ≈ 1-2 tokens
- 4 characters ≈ 1 token
- "Hello" = 1 token
- "unbelievable" = 3-4 tokens
- "تونس" (Arabic) = 2-4 tokens (Arabic uses more tokens per word)

**Why does this matter?** Because AI APIs charge you per token.

---

## Input vs Output Tokens

Every API call has two token counts:

| Type | What it is | Typical cost |
|---|---|---|
| **Prompt tokens** | Tokens you SEND (your question + system prompt) | Cheaper |
| **Completion tokens** | Tokens the AI generates (the answer) | More expensive |
| **Total tokens** | prompt + completion | — |

Example:
```
You ask: "What is the capital of Tunisia?" → 8 prompt tokens
AI answers: "The capital of Tunisia is Tunis." → 8 completion tokens
Total: 16 tokens
```

---

## Where Are Token Counts in the API Response?

Every Mistral/OpenAI API response includes a `usage` field:

```json
{
  "choices": [...],
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 48,
    "total_tokens": 73
  }
}
```

You just read `response["usage"]` to get the counts.

---

## Estimating Cost

Mistral pricing (approximate, check current pricing):

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|---|---|---|
| mistral-small | $0.20 | $0.60 |
| mistral-medium | $2.70 | $8.10 |
| mistral-large | $8.00 | $24.00 |

Formula:
```python
cost = (prompt_tokens / 1_000_000 * input_price) + (completion_tokens / 1_000_000 * output_price)
```

For Mistral Small:
```
25 prompt tokens + 48 completion tokens:
cost = (25/1_000_000 * 0.20) + (48/1_000_000 * 0.60)
     = $0.000005 + $0.0000288
     = $0.0000338 (about 0.003 cents)
```

One call is tiny. But 10,000 calls per day adds up.

---

## Why Track Token Usage?

1. **Cost control** — Know how much you're spending before the bill arrives
2. **Debugging** — A prompt that should be 50 tokens but is 5,000 tokens means you have a bug
3. **Optimization** — Shorter prompts = faster responses + lower cost
4. **Rate limits** — Most APIs limit you by tokens/minute, not just requests/minute

---

## Prompt Optimization Tips

| Technique | Example | Token savings |
|---|---|---|
| Be concise | "Capital of Tunisia?" vs "Can you please tell me what is the capital city of Tunisia?" | 70% |
| No pleasantries | Remove "Please", "Thank you", "I would appreciate" | 5-15% |
| Use system prompts | Move instructions to system (often cached = cheaper) | varies |
| Limit output | `max_tokens=100` stops runaway generation | prevents waste |
| Structured output | Ask for JSON directly | reduces preamble tokens |

---

## Session-Level Tracking

In a real app, you want to track:
- Total tokens used per session
- Total cost per session  
- Tokens per request (to spot expensive prompts)
- Running total for the day/month

This is how you build a simple counter:

```python
class TokenTracker:
    def __init__(self):
        self.total_prompt = 0
        self.total_completion = 0

    def track(self, usage: dict):
        self.total_prompt += usage.get("prompt_tokens", 0)
        self.total_completion += usage.get("completion_tokens", 0)

    @property
    def total_tokens(self):
        return self.total_prompt + self.total_completion

    @property
    def estimated_cost_usd(self):
        return (self.total_prompt / 1_000_000 * 0.20) + \
               (self.total_completion / 1_000_000 * 0.60)
```
