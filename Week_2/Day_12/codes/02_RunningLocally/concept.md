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

### Common mistakes beginners make (from demo.py)

1. Using `generate()` for multi-turn conversations — loses conversation history between calls
2. Building chat context with string concatenation — instead of using a messages list
3. Forgetting `stream=True` — waiting 8+ seconds for a wall of text

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

### chat() With System + User Roles (from demo.py)

```python
import ollama

resp = ollama.chat(
    model=model,
    messages=[
        {"role": "system", "content": "You are a brief Tunisian travel guide."},
        {"role": "user",   "content": "Top 1 thing to do in Tunisia in one short sentence?"},
    ],
    options={"num_predict": 80},
)
print(resp["message"]["content"].strip())
```

### generate() — One-Shot Completion (from demo.py)

```python
resp = ollama.generate(
    model=model,
    prompt="Translate to Tunisian darija (one short sentence): 'Hello, how are you today?'",
    options={"num_predict": 60},
)
print(resp["response"].strip())
```

### Streaming Output — Watch Tokens Arrive Live (from demo.py)

```python
for chunk in ollama.chat(
    model=model,
    messages=[
        {"role": "user", "content": "In two sentences, tell a small story about Bilel finding a hidden café in Tunis."},
    ],
    stream=True,
    options={"temperature": 0.6, "num_predict": 200},
):
    print(chunk["message"]["content"], end="", flush=True)
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

Same model, same speed, but the user perceives it as 10x faster.
