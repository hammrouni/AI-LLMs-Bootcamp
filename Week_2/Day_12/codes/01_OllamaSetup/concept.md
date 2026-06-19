# 01 - Ollama Setup

---

## What is Ollama?

**Ollama** is a tool that lets you download and run large language models (LLMs) locally on your laptop — no cloud API, no subscription, no internet. Think of it as `docker run` for LLMs.

Think of buying olive oil in Tunisia:
- Buying every meal from a restaurant = paying every time (cloud API)
- Buying a 5L bottle from the souk in Sfax once and using it at home = one-time cost (local model)
- You give up some convenience and the dish quality might be 90% of a top chef's, but you control the supply and the cost

Ollama is the 5L bottle of olive oil for LLMs.

---

## What is the Problem?

### Cloud APIs work — until they don't

A Tunisian fintech building a customer service bot using Mistral's cloud API hits walls:
- Every customer message = API call = money
- Customer data leaves the country to Mistral servers
- BCT compliance review flags this as a data sovereignty issue
- Internet outage in the office means the bot dies

```
Cloud API monthly bill for 100k queries: ~150 TND
Same workload on a local 7B model:       ~0 TND
                                         (after a one-time GPU/RAM cost)
```

Plus, for some regulated industries (banking, health, government), local inference isn't a preference — it's a legal requirement.

---

## What is the Solution? Ollama!

Ollama bundles two things:
1. A **server** (a small daemon) that runs on `localhost:11434`
2. A **CLI** that downloads models from a registry and talks to the server

You install once, pull a model once, and from then on every LLM call is a local HTTP request.

```
ollama pull mistral              # download mistral 7B (~4GB)
ollama run mistral "Hello!"      # chat in your terminal
```

In Python, the `ollama` package wraps the local server with a clean client.

---

## How It Works in Python

### Key words to know:

| Keyword / Concept | What it means |
|---|---|
| `Ollama daemon` | The local server, default port `11434` |
| `model registry` | The list at `ollama.com/library` of models you can `pull` |
| `pull` | Download a model to your machine (one-time per model) |
| `run` | Start a chat session in the terminal |
| `quantization tag` | Like `:Q4_K_M` or `:7b-instruct-q4_K_M` — controls size/quality |

### The Golden Rule:
- **Pull the model before you write the Python code.** The Python client will fail loudly if the model isn't downloaded. Pulling is a one-time, multi-GB step.

### Setup Steps (One Time)

| OS | Install |
|---|---|
| Windows | Download installer from [ollama.com](https://ollama.com) |
| macOS | `brew install ollama` or download .dmg from ollama.com |
| Linux | `curl -fsSL https://ollama.com/install.sh \| sh` |

After installing:
```bash
# Start the daemon (leave running in a terminal)
ollama serve

# In another terminal, pull a model
ollama pull mistral             # 7B instruct, ~4 GB
ollama pull nomic-embed-text    # embedding model, ~270 MB

# Verify
ollama list
```

### Hardware Notes

| Model size | RAM needed | Speed (CPU only) |
|---|---|---|
| 3B (e.g., phi3:mini) | 4–6 GB | usable |
| 7B (e.g., mistral)   | 8–12 GB | slow but usable |
| 13B                  | 16 GB+ | slow on CPU |
| 70B                  | 48 GB+ | needs GPU |

For Tunisian users with a standard 16 GB laptop, **7B models are the sweet spot**.

### Verifying the Daemon + Models (from demo.py)

```python
import ollama

# Check if daemon is running and list models
try:
    info = ollama.list()
except Exception as e:
    print(f"Could not reach Ollama daemon: {e}")
    print("Fix: ollama serve")

# Inspect available models
models = info.get("models", [])
for m in models:
    name = m.get("name") or m.get("model")
    size_gb = (m.get("size") or 0) / (1024 ** 3)
    print(f"  {name:30}  {size_gb:.2f} GB")
```

### Making Your First Local Chat Call (from demo.py)

```python
import ollama

# Auto-pick a model from what's pulled
info = ollama.list()
names = [m.get("name") or m.get("model") for m in info.get("models", [])]
candidate_models = ["llama3", "mistral", "phi"]
pulled = None
for c in candidate_models:
    match = next((n for n in names if c in n), None)
    if match:
        pulled = match
        break

# Make a chat call
response = ollama.chat(
    model=pulled,
    messages=[
        {"role": "user", "content": "In one sentence, what is couscous?"},
    ],
)
answer = response["message"]["content"].strip()
print(f"A: {answer}")
```

### BAD vs GOOD

```python
# BAD — assume the model is pulled, no verification
ollama.chat(model="some-random-model", messages=[...])   # crash

# GOOD — check ollama.list() first, fail fast with a clear message
info = ollama.list()
models = info.get("models", [])
if not models:
    print("No models pulled. Run: ollama pull mistral")
```

---

## Why This Matters for AI Apps

Local LLMs unlock entire categories of Tunisian AI use cases:
- Banking apps where data can't leave the country
- Hospital triage assistants on internal networks
- Government document classifiers
- School-aged kids' tutors that work offline
- Demo apps you run on a laptop on stage in Tunis with no Wi-Fi

The Mistral/OpenAI cloud APIs are still better quality, but for many real Tunisian deployments, "good enough and local" beats "great and cloud".
