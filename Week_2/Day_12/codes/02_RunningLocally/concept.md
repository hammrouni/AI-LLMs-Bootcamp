# 02 - Running Models Locally

---

## What Does "Running Locally" Mean?

A model runs **locally** when the model weights, the inference engine, and the output all happen on your machine. The internet is not part of the loop. Once the model is downloaded, you can pull out the network cable and everything still works.

Think of cooking ojja at home in Tunis:
- A cloud API is ordering it from a restaurant (someone else's kitchen does everything; you wait + pay)
- Running locally is cooking it yourself (your kitchen, your time, no delivery fee)
- The ingredients (the model weights) are bought once; you cook many times

---

## What is the Problem?

### Cloud APIs are great for prototypes but rough at scale

Cloud LLMs have real downsides at production scale:
- **Cost** scales with usage forever
- **Latency** depends on network conditions in Tunis (sometimes great, sometimes spiky)
- **Privacy** — every customer message leaves your servers
- **Availability** — your app dies if the provider has an outage
- **Vendor lock-in** — pricing changes one day and your budget breaks

Local inference flips all five.

---

## What is the Solution? Local Inference With Ollama!

Ollama exposes two main local endpoints:

1. **`chat`** — multi-turn conversations with `system` / `user` / `assistant` messages
2. **`generate`** — single prompt → single completion (no conversation history)

Most apps want `chat`. Use `generate` for one-shot completions (classification, summarization, autocomplete).

```python
import ollama

# Chat
ollama.chat(
    model="mistral",
    messages=[{"role": "user", "content": "Hello!"}],
)

# Generate (one-shot)
ollama.generate(model="mistral", prompt="Translate to French: Hello!")
```

---

## How It Works in Python

### Key words to know:

| Keyword / Concept | What it means |
|---|---|
| `model` | The name you used with `ollama pull` |
| `messages` | List of `{role, content}` dicts — same shape as OpenAI |
| `prompt` | Plain string for `generate()` |
| `stream` | Boolean — true to receive tokens as they're produced |
| `options` | Per-call overrides: `temperature`, `num_predict`, etc. |
| `keep_alive` | How long the model stays loaded after the last request |

### The Golden Rule:
- **Match the conversation pattern to the endpoint.** `chat` for multi-turn (with history). `generate` for stateless one-shots.

### Basic Usage

```python
import ollama

# Multi-turn chat
messages = [
    {"role": "system", "content": "You are a helpful Tunisian travel guide."},
    {"role": "user",   "content": "What should I see in 2 days in Sfax?"},
]
response = ollama.chat(model="mistral", messages=messages)
print(response["message"]["content"])

# Streaming output (tokens as they come)
for chunk in ollama.chat(
    model="mistral",
    messages=messages,
    stream=True,
):
    print(chunk["message"]["content"], end="", flush=True)

# Per-call options
response = ollama.chat(
    model="mistral",
    messages=messages,
    options={"temperature": 0.2, "num_predict": 200},
)
```

### Chat vs Generate

| | `chat` | `generate` |
|---|---|---|
| Message history | Yes (`messages` list) | No (single prompt) |
| Roles | system / user / assistant | n/a |
| Use case | Chatbots, multi-turn agents | One-shot classification, summarize |
| Output | `response["message"]["content"]` | `response["response"]` |

### BAD vs GOOD

```python
# BAD — using generate for a multi-turn conversation
prompt = "User: Hello\nAssistant: Hi!\nUser: What's Sfax famous for?"
ollama.generate(model="mistral", prompt=prompt)   # works but loses structure

# GOOD — use chat with proper messages
ollama.chat(
    model="mistral",
    messages=[
        {"role": "user",      "content": "Hello"},
        {"role": "assistant", "content": "Hi!"},
        {"role": "user",      "content": "What's Sfax famous for?"},
    ],
)
```

---

## Why This Matters for AI Apps

Once you can run a local chat call, you can swap it into anywhere you used Mistral's cloud API. The Tunisian fintech, hospital, or school suddenly has a working AI feature without a Mistral subscription or data leaving the country.

Streaming output is a UX game changer — typing characters as they're produced *feels* fast even when the model is slow.

```
Non-streaming on CPU: 8 second wait, then a wall of text
Streaming on CPU:     first char in 0.5s, words flowing in real time
```

Same model, same speed, but the user perceives it as 10× faster.
