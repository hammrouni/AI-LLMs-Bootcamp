# 04 - Measuring Latency & Throughput

---

## What Are Latency and Throughput?

- **Latency** is the time the user waits for an answer. The two most important sub-metrics are:
  - **TTFT (Time-To-First-Token)** — how long until the first character appears
  - **TPOT (Time-Per-Output-Token)** — average time per generated token after the first
- **Throughput** is how many tokens (or requests) you can produce per unit of time across the whole system.

Think of a Tunisian cafe:
- TTFT = the moment your espresso arrives at the table
- TPOT = how fast the next sip is poured
- Throughput = how many espressos the cafe serves per hour

Users feel TTFT more than total time. A snappy "first word" with streaming masks a slow tail. A long initial pause kills the experience.

---

## What is the Problem?

### "It feels slow" is not a metric

You ship a local chatbot. Some users complain. Without numbers, you can't tell:
- Is it slow on the *first* token (loading issue)?
- Is it slow on *every* token (CPU bottleneck)?
- Is the *retriever* the problem, not the LLM?
- Is it slow for *some* prompts only (long context)?

You need numbers, not feelings. Each points to a completely different fix:
- High TTFT -> reduce prompt length, use KV cache, check model loading
- Low tok/s -> enable GPU, use smaller quantization, reduce num_predict

---

## What is the Solution? Time the Two Things That Matter!

### Reasonable Targets

| Metric | Good | Acceptable | Bad |
|---|---|---|---|
| TTFT | < 500 ms | < 1.5 s | > 3 s |
| Tok/s (7B Q4) | 30+ (GPU) | 8–15 (CPU) | < 5 |
| Total for 100-token answer | < 2 s | < 8 s | > 15 s |

---

## How It Works in Python

### Key words to know:

| Keyword / Concept | What it means |
|---|---|
| `TTFT` | Time-to-first-token — user-perceived speed |
| `TPOT` | Time-per-output-token — sustained generation speed |
| `tokens/sec` (tok/s) | 1 / TPOT |
| `prefill` | Cost of processing the input prompt before generating |
| `decode` | Cost of generating each output token |
| `KV cache` | Reuses prefill state across turns to lower TTFT |

### The Golden Rule:
- **Always measure TTFT separately from total time.** TTFT is what users feel as "responsiveness". Total time is what they feel as "wait for the answer".

### Measuring TTFT With Streaming (from demo.py)

```python
import time, ollama

start = time.perf_counter()
first_token_time = None
tokens = 0

for chunk in ollama.chat(
    model="mistral",
    messages=[{"role": "user", "content": "Tell me about Sfax."}],
    stream=True,
    options={"num_predict": 120, "temperature": 0.2},
):
    txt = chunk["message"]["content"]
    if first_token_time is None and txt:
        first_token_time = time.perf_counter()
    if txt:
        tokens += max(1, len(txt.split()))

end = time.perf_counter()
total = end - start
ttft = (first_token_time - start) if first_token_time else total
tps = tokens / max(total, 1e-6)

print(f"TTFT: {ttft*1000:.0f} ms")
print(f"Total: {total:.2f}s, ~{tokens} tokens, {tps:.1f} tok/s")
```

### Repeatable Benchmark Function (from demo.py)

```python
import time, statistics, ollama

def benchmark(model, prompt, runs=3, num_predict=120):
    """Return median TTFT and tokens/sec over `runs` warm runs."""
    # Step 1: Warmup — force model loading so it doesn't count
    ollama.generate(model=model, prompt="warmup", options={"num_predict": 5})

    ttfts, tpss, totals = [], [], []

    for _ in range(runs):
        start = time.perf_counter()
        first_token_time = None
        tokens = 0

        # Step 2: Stream to capture TTFT precisely
        for chunk in ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            options={"num_predict": num_predict, "temperature": 0.2},
        ):
            txt = chunk["message"]["content"]
            if first_token_time is None and txt:
                first_token_time = time.perf_counter()
            if txt:
                tokens += max(1, len(txt.split()))

        end = time.perf_counter()
        total = end - start
        ttft = (first_token_time - start) if first_token_time else total
        tps = tokens / max(total, 1e-6)

        ttfts.append(ttft)
        tpss.append(tps)
        totals.append(total)

    # Step 3: Return medians (robust to outliers like GC pauses)
    return {
        "ttft_ms_median": statistics.median(ttfts) * 1000,
        "tps_median":     statistics.median(tpss),
        "total_s_median": statistics.median(totals),
        "tokens_approx":  tokens,
        "runs":           runs,
    }
```

### Testing Across Prompt Lengths (from demo.py)

```python
prompts = [
    ("short",  "Name three Tunisian cities."),
    ("medium", "Explain in 3 sentences why Sfax is famous for olives."),
    ("long",   "Write a 6-sentence story about Bilel discovering a hidden olive press in the Sfax countryside, with vivid sensory details."),
]

print(f"{'label':<8} {'TTFT (ms)':>10} {'tok/s':>8} {'total (s)':>10}")
print("-" * 42)

for label, prompt in prompts:
    m = benchmark(model, prompt, runs=3, num_predict=200)
    print(f"{label:<8} {m['ttft_ms_median']:>10.0f} {m['tps_median']:>8.1f} {m['total_s_median']:>10.2f}")
```

What to look for:
- **TTFT jumps for "long"** -> prefill is the bottleneck
- **tok/s drops for "long"** -> model may be swapping to CPU
- **Both stable** -> good sign, system handles context scaling well

### BAD vs GOOD

```python
# BAD — one warm run, claim it's the answer
start = time.perf_counter()
ollama.generate(model="mistral", prompt="...")
print(time.perf_counter() - start)
# noisy, hides cold-start, doesn't separate TTFT

# GOOD — warmup, multiple runs, median, separate TTFT
m = benchmark("mistral", "Tell me about Sfax.", runs=5)
print(f"TTFT: {m['ttft_ms_median']:.0f} ms, {m['tps_median']:.1f} tok/s")
```

---

## Why This Matters for AI Apps

Tunisian users on mobile have unreliable connections and patience to match. Hard targets you should aim for:
- TTFT under 1 second for chat UIs (with streaming)
- Total answer time under 5 seconds for typical FAQ
- Throughput high enough that a single server can serve your peak hours

You can't optimize what you don't measure. The cycle is: measure -> tune (quantization, GPU, prompt length) -> measure -> ship.

```
"The bot feels fast"                                 -> useless, can't repeat
"TTFT median 380 ms, 65 tok/s on a 7B Q4 model"     -> ship-worthy proof
```
