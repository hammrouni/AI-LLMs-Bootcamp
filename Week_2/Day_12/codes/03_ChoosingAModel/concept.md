# 03 - Choosing a Model

---

## What Does "Choosing a Model" Mean?

When you say "I'm running a local LLM", you're really choosing along three axes at once:
1. **Family** — Mistral, Llama, Phi, Qwen, Gemma, etc.
2. **Size** — 1B, 3B, 7B, 13B, 70B parameters
3. **Quantization** — how aggressively the weights are compressed (Q2, Q4, Q5, Q8, FP16)

The right combination depends on your hardware and your task. There's no "best" — there's "best for your laptop and your problem".

Think of choosing a car in Tunis:
- A Peugeot 208 (small, cheap, gets the kids to school): a 3B model
- A Hyundai Tucson (mid-range, daily use): a 7B model
- A Toyota Land Cruiser (overkill but you can): a 70B model
- You don't drive a Land Cruiser to buy a baguette

---

## What is the Problem?

### "Use the biggest model" wastes resources and crashes laptops

Beginners often jump to `llama3:70b` because bigger sounds better. Reality:
- Loading takes ~3 minutes
- Inference takes 30+ seconds per response on most laptops
- Most laptops can't even load it — out of memory
- For 80% of tasks (classification, FAQ, simple chat), a 7B is enough

```
Task: Classify customer support tickets in Arabic/French
Mistral 7B  on Tunisian laptop: 90% accuracy, 1s/query
Llama3 70B  on rented GPU:      94% accuracy, 8s/query, 100x cost
```

The bigger model is only 4% better but 100x more expensive. Pick wisely.

---

## What is the Solution? Match the Model to the Task!

| Task | Recommended | RAM |
|---|---|---|
| Simple chat, FAQ | `mistral` (7B) or `phi3` | 8 GB |
| Summarization | `mistral` (7B) | 8 GB |
| Code generation | `codellama` (7B) | 8 GB |
| Multilingual (Arabic, French) | `mistral` (7B) — strong at multilingual | 8 GB |
| Embeddings | `nomic-embed-text` | < 1 GB |
| Heavy reasoning, long chains | `llama3:70b` | 48+ GB / GPU |

Start with **`mistral:latest` (7B instruct, Q4_K_M quantization)** unless you have a reason to deviate.

---

## How It Works in Python

### Key words to know:

| Keyword / Concept | What it means |
|---|---|
| `parameters` | The numbers inside the model — more = bigger, slower |
| `quantization` | Lower precision to save memory (Q4 = 4 bits per weight) |
| `instruct` | Trained to follow instructions (the version you almost always want) |
| `chat` | Trained for conversational style |
| `base` | Untuned — usually NOT what you want |
| `Q4_K_M` | A specific quantization scheme — good default trade-off |

### The Golden Rule:
- **Choose by RAM first, then by quality.** A model that doesn't fit in memory is infinitely slow.

### Listing Available Models (from demo.py)

```python
import ollama

info = ollama.list()
available = [m.get("name") or m.get("model") for m in info.get("models", [])]
print(available)
```

### Benchmarking Models Side by Side (from demo.py)

```python
import ollama, time

prompt = (
    "Summarize in one sentence: "
    "'Tunisia is a country in North Africa famous for couscous, Carthage, and olive oil.'"
)

candidates = ["mistral", "phi3"]  # whichever you've pulled

for m in candidates:
    # Warmup: load model into memory (not timed)
    ollama.generate(model=m, prompt="hi", options={"num_predict": 1})

    # Timed generation
    start = time.perf_counter()
    resp = ollama.generate(model=m, prompt=prompt, options={"num_predict": 80})
    elapsed = time.perf_counter() - start
    output = resp["response"].strip().replace("\n", " ")
    print(f"[{m:<30}] {elapsed:5.1f}s   {output[:120]}")
```

### BAD vs GOOD

```python
# BAD — picking the biggest model "to be safe"
ollama.chat(model="llama3:70b", messages=[...])
# 30s response time, laptop fan screaming, possibly crashes

# GOOD — picking the right-sized model for the task
ollama.chat(model="mistral", messages=[...])
# 1s response, smooth, leaves headroom for other apps
```

---

## Why This Matters for AI Apps

Model choice drives every metric you care about:
- **Latency**: smaller = faster
- **Cost** (electricity, time): smaller = cheaper
- **Quality**: bigger usually better, but with diminishing returns
- **Maintenance**: bigger models are pickier about hardware

For Tunisian startups on lean budgets:
- A 7B model on a single $30/month VPS handles 100k+ FAQ queries per day
- The same workload on a hosted 70B might cost 500 TND / month
- The user experience is often indistinguishable

The mantra: **start with 7B, only scale up when measurements show you need to.**
