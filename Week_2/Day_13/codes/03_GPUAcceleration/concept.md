# 03 - GPU Acceleration

---

## What is GPU Acceleration For LLMs?

A **GPU (Graphics Processing Unit)** has thousands of small cores designed for parallel math — exactly what LLM matrix multiplications need. On a typical laptop:
- CPU LLM inference: 5–20 tokens/second
- GPU LLM inference: 50–200+ tokens/second

That's 10x faster for the same model. Ollama can offload model layers to your GPU automatically if it detects one.

Think of dragging a fishing net on a beach in Mahdia:
- One person pulling (CPU): slow, tiring
- Twenty people pulling together (GPU): same net, much faster
- The work is the same; the parallelism is what speeds it up

---

## What is the Problem?

### CPU-only inference is fine for demos, painful for production

A Tunisian e-commerce site deploys a local chatbot for customer support. Without GPU:
- 8 tokens/second on a 7B model
- A 150-word answer takes ~25 seconds
- Users abandon mid-conversation
- The bot looks slow next to ChatGPT

With even a modest GPU (RTX 3060 12GB or an NVIDIA L4 on a cloud VM), the same 150-word answer arrives in 3 seconds — competitive with cloud responses.

### The Dangerous Part: Silent Fallback (from demo.py)

Many developers assume that having a GPU means Ollama uses it. In reality, several things can go wrong silently:
- NVIDIA drivers not installed (CUDA unavailable)
- Model too large for VRAM -> layers spill to CPU
- Running inside Docker/WSL without GPU passthrough configured
- AMD GPU with incomplete ROCm support

Ollama won't error out. It just runs on CPU, and your only clue is that generation feels slow.

---

## What is the Solution? Let Ollama Use Your GPU!

Ollama auto-detects GPUs and offloads as many model layers as it can. You usually don't need to configure anything:
- **NVIDIA** (Linux, Windows): CUDA — install NVIDIA drivers, that's it
- **Apple Silicon** (M1/M2/M3 Mac): Metal — used automatically
- **AMD**: ROCm — partial support, varies by platform

When the GPU isn't big enough to fit the whole model, Ollama splits between GPU and CPU. You can control the split with `OLLAMA_NUM_GPU` (number of layers on GPU).

### Verify it's working

```bash
ollama run mistral
# Then watch:
nvidia-smi          # NVIDIA: GPU memory should fill up
sudo intel_gpu_top  # Intel iGPU
# On Mac: open Activity Monitor -> GPU tab
```

---

## How It Works in Python

### Key words to know:

| Keyword / Concept | What it means |
|---|---|
| `CUDA` | NVIDIA's GPU computing platform |
| `Metal` | Apple's equivalent (used on M1/M2/M3 Macs) |
| `VRAM` | GPU memory |
| `layer offload` | Sending some/all of the model layers to GPU |
| `tokens/second (tok/s)` | Standard inference speed metric |
| `TTFT` | Time-to-first-token — how long until generation starts |

### The Golden Rule:
- **Match model size to VRAM. Anything that doesn't fit on GPU silently falls back to CPU for those layers, slowing everything down.**

### Common Setups

| Hardware | What runs well |
|---|---|
| MacBook Air M2 (8 GB) | 3B Q4 — fully on Metal |
| MacBook Pro M3 (18 GB) | 7B Q4 fully on GPU |
| Windows laptop, no GPU | 7B Q4 on CPU only (8 tok/s) |
| Desktop + RTX 3060 12 GB | 7B Q4 fully on GPU (80+ tok/s) |
| Cloud L4 GPU (24 GB) | 13B Q4 fully on GPU |

### Checking GPU Offload With ollama.ps() (from demo.py)

```python
import ollama

# Step 1: Warm the model up (Ollama loads models lazily)
ollama.generate(model="mistral", prompt="hi", options={"num_predict": 5})

# Step 2: Query ollama.ps() — Task Manager for Ollama
ps = ollama.ps()

# Step 3: Calculate GPU offload percentage
for m in ps.get("models", []):
    name = m.get("name") or m.get("model")
    size = m.get("size") or 0          # total model size in bytes
    vram = m.get("size_vram") or 0     # portion loaded on GPU (VRAM)
    if size:
        pct_on_gpu = (vram / size) * 100 if vram else 0
        print(f"  {name}: total={size / 1024**3:.2f} GB, on GPU={vram / 1024**3:.2f} GB ({pct_on_gpu:.0f}%)")
```

What to look for:
- `on GPU=X.XX GB (100%)` -> fully on GPU, maximum speed
- `on GPU=0.00 GB (0%)` -> CPU only, need to fix drivers or pick a smaller model
- Something in between -> partial offload, consider a smaller quantization

### Benchmarking Tokens-Per-Second (from demo.py)

```python
import time, ollama

prompt = "Write a 4-sentence story about Bilel and Yasmine planning a weekend trip to Sidi Bou Said."

start = time.perf_counter()
resp = ollama.generate(model="mistral", prompt=prompt, options={"num_predict": 200})
elapsed = time.perf_counter() - start

text = resp["response"]
tokens = max(1, len(text.split()))
tok_per_sec = tokens / elapsed
print(f"Generated ~{tokens} tokens in {elapsed:.1f}s -> {tok_per_sec:.1f} tok/s")

# Reference baselines:
#   CPU only (M1/M2 Air, 16 GB Windows laptop): ~5-15 tok/s
#   Apple Silicon GPU (M2 Pro/Max, M3 Max):     ~30-60 tok/s
#   NVIDIA RTX 3060/4060:                        ~60-100 tok/s
#   NVIDIA RTX 4090 / L4:                        ~120-200+ tok/s
```

### Forcing Layers to GPU

```python
import ollama

ollama.chat(
    model="mistral",
    messages=[{"role": "user", "content": "Hi"}],
    options={"num_gpu": 35},   # try 35 layers on GPU
)
```

Set this if Ollama isn't detecting your GPU automatically.

### BAD vs GOOD

```python
# BAD — running a 13B model on a 6 GB GPU with default settings
# Ollama loads what fits then thrashes between GPU and CPU = slower than pure CPU

# GOOD — pick a model that fits, or explicitly limit num_gpu
ollama.chat(model="mistral", options={"num_gpu": 28})
```

---

## Why This Matters for AI Apps

For Tunisian production deployments:
- A small server with one $300 NVIDIA L4 GPU serves 50+ concurrent users on a 7B model
- A single workstation with an RTX 4090 handles thousands of internal employees
- Apple Silicon laptops (M2/M3) make great offline AI dev machines

GPU acceleration is the difference between "the bot replies in 20 seconds" and "the bot replies in 2 seconds". That gap is usually the difference between users adopting the tool or ignoring it.
