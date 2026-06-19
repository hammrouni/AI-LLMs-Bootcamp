# 04 - The Ollama Python Client

---

## Packages

```bash
pip install ollama openai
```

---

## What is the Ollama Python Client?

The **`ollama` Python package** wraps the local Ollama HTTP server (`localhost:11434`) with a clean Python API. It mirrors the OpenAI SDK shape for `chat`, but everything runs locally.

Think of it as a Tunisian taxi-app SDK pointed at your own car instead of a fleet:
- The same calls (`request_ride`, `get_status`)
- The car is in your own garage
- No driver, no surge pricing, no waiting

Same interface, completely different deployment.

---

## What is the Problem?

### Hand-rolled HTTP calls work but are tedious

You could talk to the Ollama daemon with `requests`:

```python
import requests
r = requests.post(
    "http://localhost:11434/api/chat",
    json={
        "model": "mistral",
        "messages": [{"role": "user", "content": "Hi"}],
        "stream": False,
    },
)
print(r.json()["message"]["content"])
```

It works, but you have to:
- Remember endpoint paths
- Handle streaming JSON-lines yourself
- Re-implement type hints
- Build retry/timeout logic

The `ollama` package gives you all of that for free.

---

## What is the Solution? Use the Official Python Client!

```python
import ollama

# Chat
ollama.chat(model="mistral", messages=[...])

# Generate
ollama.generate(model="mistral", prompt="...")

# Embeddings
ollama.embeddings(model="nomic-embed-text", prompt="Bilel loves couscous.")

# List local models
ollama.list()

# Streaming (yields chunks)
for chunk in ollama.chat(model="mistral", messages=[...], stream=True):
    print(chunk["message"]["content"], end="", flush=True)
```

Five functions cover 95% of what you need.

---

## How It Works in Python

### Key words to know:

| Keyword / Concept | What it means |
|---|---|
| `ollama.Client` | A configurable client (custom host, headers) |
| `ollama.AsyncClient` | Async/await version for FastAPI, asyncio apps |
| `embeddings()` | Returns `{"embedding": [...]}` — single vector |
| `pull()` | Programmatically download a model |
| `show()` | Inspect a model's metadata (architecture, license, parameters) |

### The Golden Rule:
- **Use `ollama.Client(host=...)` only when you need a non-default host or async.** Otherwise the module-level functions (`ollama.chat`, `ollama.embeddings`) are enough.

### Auto-Detecting Available Models (from demo.py)

```python
import ollama

def model_available(target_substring):
    try:
        info = ollama.list()
    except Exception:
        return None
    for m in info.get("models", []):
        name = m.get("name") or m.get("model")
        if target_substring in name:
            return name
    return None

chat_model = model_available("llama3") or model_available("mistral") or model_available("phi3")
embed_model = model_available("nomic-embed-text")
```

### chat() — Multi-Turn Conversations (from demo.py)

```python
resp = ollama.chat(
    model=chat_model,
    messages=[{"role": "user", "content": "What is harissa, in one short sentence?"}],
    options={"num_predict": 60},
)
print(resp["message"]["content"].strip())
```

### generate() — One-Shot Completions (from demo.py)

```python
resp = ollama.generate(
    model=chat_model,
    prompt="Name three Tunisian cities in a comma-separated list.",
    options={"num_predict": 30},
)
print(resp["response"].strip())
```

### embeddings() — Text to Vector (from demo.py)

```python
resp = ollama.embeddings(model=embed_model, prompt="Yasmine loves makroudh from Kairouan.")
vec = resp["embedding"]
print(f"Dimensions: {len(vec)}")
print(f"Preview:    {vec[:5]}")
```

### Streaming — Tokens Arrive Live (from demo.py)

```python
for chunk in ollama.chat(
    model=chat_model,
    messages=[{"role": "user", "content": "Describe Sidi Bou Said in one sentence."}],
    stream=True,
    options={"num_predict": 120},
):
    print(chunk["message"]["content"], end="", flush=True)
```

### OpenAI-Compatible Mode (from demo.py)

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
resp = client.chat.completions.create(
    model=chat_model,
    messages=[{"role": "user", "content": "Say hi in Tunisian darija."}],
    max_tokens=40,
)
print(resp.choices[0].message.content.strip())
```

This is huge: any code written for Mistral/OpenAI's cloud SDK can be redirected to a local Ollama model with a one-line base URL change.

### Common Patterns

```python
# Custom host (e.g., running on a server in the local network)
client = ollama.Client(host="http://192.168.1.20:11434")
client.chat(model="mistral", messages=[{"role": "user", "content": "Hi"}])

# Async (for FastAPI / asyncio)
import asyncio
async def go():
    client = ollama.AsyncClient()
    resp = await client.chat(model="mistral", messages=[{"role": "user", "content": "Hi"}])
    print(resp["message"]["content"])
asyncio.run(go())
```

### BAD vs GOOD

```python
# BAD — pin the model name in 30 files
ollama.chat(model="mistral", messages=...)
# Tomorrow you switch to phi3, now you grep through 30 files

# GOOD — read model from one config / env var
import os
MODEL = os.environ.get("OLLAMA_MODEL", "mistral")
ollama.chat(model=MODEL, messages=...)
```

---

## Why This Matters for AI Apps

The Ollama Python client is the bridge between your existing AI code and local inference. Because the API mirrors OpenAI/Mistral, you can usually:

1. Add an env var `USE_LOCAL=true`
2. Switch between `ollama.chat(...)` and `mistral.chat.complete(...)` based on it
3. Ship a single app that runs in the cloud for production and on a local laptop for demos

For a Tunisian dev who can't always rely on internet at the office or a stable Mistral API key, this is gold. Your demo never crashes because of WiFi.
