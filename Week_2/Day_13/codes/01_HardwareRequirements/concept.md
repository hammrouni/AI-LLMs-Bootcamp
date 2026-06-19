# 01 - Hardware Requirements

---

## What Are Hardware Requirements For LLMs?

When you run an LLM locally, three numbers matter most:
1. **Model weight size on disk** (~1–40 GB depending on params + quantization)
2. **RAM needed to load it** (~weight size + 2 GB headroom for OS/KV cache)
3. **VRAM needed for GPU acceleration** (similar to RAM if fully offloaded)

If you don't have the RAM, the model won't load. If you don't have VRAM, you fall back to CPU and inference is slow.

Think of buying a Tunisian car: you don't put a 12-seat van in a single garage. Match the vehicle to your garage.

---

## What is the Problem?

### Trying to run a 13B model on a laptop with 8 GB RAM

Sonia hears the bootcamp says "use a 7B model", tries `ollama pull llama2:13b` instead. Result:
- Laptop swaps to disk
- Each token takes 5 seconds to generate
- The fan howls
- The laptop heats up and throttles

She blames Ollama. The real issue: hardware mismatch. The model needs ~9.5 GB; her laptop has 8.

```
Model weight size:     ~7.5 GB (13B Q4)
RAM needed (+ 2 GB):   ~9.5 GB
Sonia's laptop has:    8 GB total (subtract OS, browser tabs...)
```

Predictable failure if you didn't read the spec.

---

## What is the Solution? Read the Spec, Plan the Box!

### Sizing Cheat Sheet

| Model | Params | Q4 weights | RAM needed (+ 2 GB) | Fits on |
|---|---|---|---|---|
| phi3:mini | 3B | ~2 GB | ~4 GB | Anything (incl. Raspberry Pi 5) |
| Mistral 7B / Llama3 8B | 7–8B | ~4–5 GB | ~6–7 GB | Most 8 GB laptops |
| Llama2 13B | 13B | ~7.5 GB | ~9.5 GB | 16 GB laptops (no other apps) |
| CodeLlama 34B | 34B | ~20 GB | ~22 GB | Workstations / servers |
| Llama3 70B | 70B | ~40 GB | ~42 GB | GPU servers |

### How to Measure Your Box

```bash
# Linux / Mac
free -h            # RAM
nvidia-smi          # NVIDIA GPU info (if any)

# Windows (PowerShell)
Get-ComputerInfo | Select-Object CsTotalPhysicalMemory
nvidia-smi          # if NVIDIA GPU drivers installed
```

### How to Estimate Model Footprint

```
RAM needed = (params x bytes_per_param) + 2 GB overhead

Where bytes_per_param depends on quantization:
  FP16       -> 2 bytes
  Q8 (int8)  -> 1 byte
  Q5         -> 0.65 bytes
  Q4 (4-bit) -> 0.5 bytes
  Q3         -> 0.4 bytes
```

Example: Mistral 7B at Q4 = 7 x 0.5 = 3.5 GB weights + 2 GB overhead = ~5.5 GB total.

---

## How It Works in Python

### Key words to know:

| Keyword / Concept | What it means |
|---|---|
| `parameters` | Total number of weights in the model |
| `bytes per parameter` | Depends on precision (FP16, Q8, Q4...) |
| `VRAM` | GPU memory |
| `swap` | When RAM is full, OS uses disk — extremely slow |
| `headroom` | Extra RAM for OS, your app, KV cache (~2 GB) |

### The Golden Rule:
- **Keep at least 2 GB of free RAM after loading the model.** Less than that and the OS starts swapping, killing performance.

### Constants and RAM Estimation (from demo.py)

```python
HEADROOM_GB = 2.0
QUANT_BYTES = {"FP16": 2.0, "Q8": 1.0, "Q5": 0.65, "Q4": 0.5, "Q3": 0.4}

def estimate_ram_gb(params_b, quant="Q4"):
    return params_b * QUANT_BYTES[quant] + HEADROOM_GB
```

### Checking If a Model Fits (from demo.py)

```python
def check_fit(avail_gb, params_b, quant="Q4"):
    weight_gb = params_b * QUANT_BYTES[quant]
    needed = weight_gb + HEADROOM_GB
    if avail_gb >= needed:
        return weight_gb, needed, "OK"
    if avail_gb >= weight_gb:
        return weight_gb, needed, "tight (may swap)"
    return weight_gb, needed, "won't fit"
```

### Inspecting Your Hardware (from demo.py)

```python
import psutil
import subprocess
import shutil

# RAM
vm = psutil.virtual_memory()
total_gb = vm.total / (1024**3)
avail_gb = vm.available / (1024**3)
print(f"Total RAM:     {total_gb:.1f} GB")
print(f"Available RAM: {avail_gb:.1f} GB")
print(f"CPU count:     {psutil.cpu_count(logical=False)} physical / {psutil.cpu_count()} logical")

# GPU (NVIDIA)
def get_gpu_info():
    if not shutil.which("nvidia-smi"):
        return None
    result = subprocess.run(
        ["nvidia-smi", "--query-gpu=name,memory.total,memory.free",
         "--format=csv,noheader,nounits"],
        capture_output=True, text=True, timeout=5,
    )
    if result.returncode != 0:
        return None
    gpus = []
    for line in result.stdout.strip().splitlines():
        name, total, free = [x.strip() for x in line.split(",")]
        gpus.append({"name": name, "total_mb": float(total), "free_mb": float(free)})
    return gpus
```

### Sizing Across All Quant Levels (from demo.py)

```python
for params_b in [3, 7, 13, 70]:
    print(f"--- {params_b}B params ---")
    for quant, bpp in QUANT_BYTES.items():
        ram = estimate_ram_gb(params_b, quant)
        print(f"  {quant}: ~{ram:.1f} GB RAM")
```

### BAD vs GOOD

```python
# BAD — pull a big model without checking
os.system("ollama pull llama3:70b")   # 40 GB download then OOM crash

# GOOD — read the system specs first
import psutil
if psutil.virtual_memory().total < 12 * 1024**3:
    print("Stick with 7B models for now.")
```

---

## Why This Matters for AI Apps

Hardware mismatch is the #1 reason local AI demos fail. Buying or specifying the right box is part of the engineer's job:
- For a Tunisian startup demo: a 16 GB laptop with Q4 7B is fine
- For a small office server: 32 GB RAM, 7B-13B Q4 models
- For high-throughput production: a single L4 / RTX 4090 GPU (~24 GB VRAM)

Save yourself a week of debugging "Ollama is slow" by measuring first.
