# 02 - Quantization

---

## What is Quantization?

**Quantization** is the trick of representing model weights with fewer bits than the original FP16 (16 bits per number). A Q4 model uses 4 bits per weight — 4x smaller, 4x less RAM, and on most tasks the quality drop is barely noticeable.

Think of a Tunisian map drawn at different resolutions:
- A national-scale map (very detailed) = FP16 weights
- A regional map (less detail, but you still find Sfax) = Q8
- A simple sketch of major cities (less detail, but still useful for directions) = Q4
- A scribble of Tunis only (too little detail) = Q2

For most practical purposes, the regional or simple-sketch level is enough — and fits in your pocket.

---

## What is the Problem?

### Full-precision models are huge

A Mistral 7B model at FP16 takes ~14 GB on disk and in RAM. That's:
- Too big for an 8 GB laptop
- Slow to load and to swap pages from disk
- Wasteful — you're paying for precision you don't notice

The same model at Q4 takes ~4 GB. Quality drops by maybe 1–3 points on benchmarks. For a Tunisian FAQ chatbot, that drop is invisible.

```
Mistral 7B FP16:  14 GB, fits on workstation only, marginal quality boost
Mistral 7B Q4:    4 GB,  fits on every laptop, "good enough"
```

---

## How Does Quantization Work?

### The Math in Plain Terms

A model weight is a decimal number like `0.03174`. In FP16, it gets 16 bits of precision. Quantization squeezes it into fewer bits:

```
Original value:    0.03174
FP16 (16 bits):    0.03174  -> nearly exact
Q8   (8 bits):     0.03150  -> tiny rounding error
Q4   (4 bits):     0.06667  -> visible rounding, but small
Q2   (2 bits):     0.33333  -> large rounding error
```

Each weight loses a little precision. But across 7 billion weights, the errors mostly cancel each other out — so the model's overall behavior barely changes.

### Why It Works

Neural network weights are **redundant**. Many weights are near zero or clustered in small ranges. Quantization exploits this:

1. **Find the range** of weights in each layer (e.g., -0.5 to +0.5)
2. **Divide into buckets** — Q4 gets 16 buckets (2^4), Q8 gets 256 buckets (2^8)
3. **Snap each weight** to the nearest bucket center
4. **Store the bucket index** instead of the full float

Fewer buckets = fewer bits = smaller file = less RAM.

### The K-Quant Variants

Ollama uses the `K-quant` family from llama.cpp:
- **K_S** ("small"): more aggressive compression, slightly lower quality
- **K_M** ("medium"): balanced — the recommended choice
- **K_L** ("large"): less compression, closer to the original

Example: `Q4_K_M` = 4-bit quantization, K-quant family, medium variant.

---

## What is the Solution? Quantized Models From the Ollama Registry!

Ollama tags expose multiple quantization levels:

```bash
ollama pull mistral:7b-instruct-q4_K_M    # ~4 GB, default
ollama pull mistral:7b-instruct-q5_K_M    # ~5 GB, slightly better quality
ollama pull mistral:7b-instruct-q8_0      # ~8 GB, very close to FP16
ollama pull mistral:7b-instruct-fp16      # ~14 GB, max quality
```

The naming pattern: `<model>:<size>-<variant>-<quant>`.

### Size Calculation

You can calculate weight size for any model at any quant level:

```
weight_size = params x bytes_per_param

Bytes per param:
  FP16  -> 2.0 bytes    Q5  -> 0.65 bytes
  Q8    -> 1.0 bytes     Q4  -> 0.5  bytes
                         Q3  -> 0.4  bytes
```

Example: Mistral 7B at Q4 = 7 x 0.5 = 3.5 GB weights + 2 GB overhead = 5.5 GB RAM.

---

## How It Works in Python

### Key words to know:

| Keyword / Concept | What it means |
|---|---|
| `FP16` | 16-bit floating point — baseline |
| `Q8` | 8-bit integer — very small quality drop |
| `Q5_K_M` | 5-bit mixed scheme — common middle ground |
| `Q4_K_M` | 4-bit mixed scheme — recommended default |
| `Q3_K_M` / `Q2_K` | Very aggressive — quality drops noticeably |
| `K_M` / `K_S` | Variants of the K-quant family ("medium" / "small") |
| `perplexity` | How "surprised" the model is by text — lower is better |

### The Golden Rule:
- **Q4_K_M is the right default. Step up to Q5 or Q8 only if you measure a quality regression on YOUR data.** Almost no one needs FP16 in production.

### Seeing Quantization in Action (from demo.py)

```python
import struct

original = 0.03174

# FP16: 16-bit float — near-exact
fp16_bytes = struct.pack("e", original)
fp16_back  = struct.unpack("e", fp16_bytes)[0]
print(f"Original float64:  {original:.10f}")
print(f"After FP16 round:  {fp16_back:.10f}")

# Simulated quantization at different bit levels
def fake_quantize(value, bits):
    levels = 2 ** bits
    min_val, max_val = -1.0, 1.0
    step = (max_val - min_val) / (levels - 1)
    index = round((value - min_val) / step)
    index = max(0, min(levels - 1, index))
    return min_val + index * step

for bits in [8, 4, 3, 2]:
    q = fake_quantize(original, bits)
    err = abs(q - original)
    print(f"After  Q{bits} round:  {q:+.10f}   (error: {err:.6f})")
```

### Size Calculator Across Quant Levels (from demo.py)

```python
HEADROOM_GB = 2.0
QUANT_BYTES = {
    "FP16":  (16, 2.0),
    "Q8":    (8,  1.0),
    "Q5":    (5,  0.65),
    "Q4":    (4,  0.5),
    "Q3":    (3,  0.4),
    "Q2":    (2,  0.3),
}

models = [("Mistral 7B", 7), ("Llama3 8B", 8), ("Llama2 13B", 13)]

for model_name, params_b in models:
    print(f"--- {model_name} ({params_b}B params) ---")
    fp16_size = params_b * QUANT_BYTES["FP16"][1]
    for quant, (bits, bpp) in QUANT_BYTES.items():
        weight_gb = params_b * bpp
        total_gb  = weight_gb + HEADROOM_GB
        ratio = weight_gb / fp16_size
        print(f"  {quant:<8} {bits:>4} bits  {weight_gb:>8.1f} GB  {total_gb:>10.1f} GB RAM  {ratio:>6.1%} of FP16")
```

### Quality vs Size Trade-Off (typical for Mistral 7B)

| Quant | Size | Speed (rel.) | Quality | Notes |
|---|---|---|---|---|
| FP16 | 14 GB | 1.0x | 100% | baseline, rarely needed |
| Q8 | 8 GB | 1.4x | ~99% | near-perfect, large |
| Q5_K_M | 5 GB | 1.7x | ~97% | great middle ground |
| Q4_K_M | 4 GB | 2.0x | ~95% | **recommended default** |
| Q3_K_M | 3 GB | 2.2x | ~88% | noticeable quality drop |
| Q2_K | 2.5 GB | 2.3x | ~75% | last resort only |

### Live Benchmark — Cold vs Warm (from demo.py)

```python
import time, ollama

PROMPT = "In one short sentence, what is the main reason Tunisian olive oil is famous internationally?"

for m in ["mistral:7b-instruct-q4_K_M", "mistral:7b-instruct-q8_0"]:
    # Cold call (loads weights into memory)
    start = time.perf_counter()
    resp = ollama.generate(model=m, prompt=PROMPT, options={"num_predict": 60})
    cold = time.perf_counter() - start

    # Warm call (weights already in memory)
    start = time.perf_counter()
    resp = ollama.generate(model=m, prompt=PROMPT, options={"num_predict": 60})
    warm = time.perf_counter() - start

    tokens = resp.get("eval_count", 0)
    tok_per_sec = tokens / warm if warm > 0 else 0
    print(f"[{m:35}] cold {cold:5.1f}s | warm {warm:5.1f}s | {tok_per_sec:.1f} tok/s")
```

### BAD vs GOOD

```python
# BAD — running FP16 "for quality" on a 16 GB laptop
ollama.chat(model="mistral:7b-instruct-fp16", messages=[...])
# 30s load time, fan max, tiny quality difference vs Q4

# GOOD — Q4_K_M with selective Q8 for critical tasks
ollama.chat(model="mistral:7b-instruct-q4_K_M", messages=[...])
# Snappy, 1/4 the RAM, 95-99% of the quality
```

---

## Why This Matters for AI Apps

Quantization is the cheapest, largest-impact speedup for local LLMs:
- 4x less RAM -> fits on every Tunisian laptop
- 2x faster inference -> smoother UX
- 4x faster load -> instant startup after restarts
- Negligible quality drop for FAQ-style use cases

Tunisian startups can ship a 7B Q4 chatbot on a 16 GB MacBook Air today. Without quantization, the same model would need a workstation.

```
At Q4:  Mistral 7B answers in ~2s on CPU
At FP16: same model takes ~8s and only fits if nothing else is running
```

The right rule: **always quantize to Q4_K_M unless evaluation says otherwise.**
