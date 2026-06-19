"""
03 - GPU Acceleration Demo
==========================
Detects GPU usage by Ollama via the ps() endpoint and benchmarks one prompt.
Useful for confirming the GPU is actually being used.

WHY GPU MATTERS FOR LLMs:
    LLM inference is mostly matrix multiplications — thousands of them per token.
    A CPU processes these sequentially (few cores, high clock speed).
    A GPU has thousands of small cores that do these multiplications in parallel.

    Result:
      - CPU inference:  ~5-20 tokens/second
      - GPU inference:  ~50-200+ tokens/second  (10x faster for the same model)

    Analogy: dragging a fishing net on a beach.
      - 1 person pulling = CPU (slow, one step at a time)
      - 20 people pulling = GPU (same net, much faster, parallel effort)

KEY CONCEPTS:
    CUDA   — NVIDIA's GPU computing platform (Linux/Windows)
    Metal  — Apple's GPU framework (M1/M2/M3 Macs, used automatically)
    VRAM   — GPU memory; the model must fit here for full GPU acceleration
    Layer offload — Ollama sends model layers to GPU; layers that don't fit
                    stay on CPU (slower for those layers)
    tok/s  — tokens per second, the standard inference speed metric

THE GOLDEN RULE:
    Match model size to VRAM. Anything that doesn't fit on the GPU silently
    falls back to CPU for those layers, slowing everything down.

    Examples:
      MacBook Air M2 (8 GB)      → 3B Q4 fully on Metal
      MacBook Pro M3 (18 GB)     → 7B Q4 fully on GPU
      Desktop + RTX 3060 (12 GB) → 7B Q4 fully on GPU (~80+ tok/s)
      Cloud L4 GPU (24 GB)       → 13B Q4 fully on GPU

HOW TO RUN THIS FILE:
1. ollama serve
2. ollama pull mistral
3. pip install ollama
4. python demo.py
"""

import time


def pick_model():
    """
    Auto-detect which model is already pulled in Ollama.

    Why: We don't want the demo to fail because the user pulled a different
    model name. This checks ollama.list() for common small models and returns
    the first match. Preference order: mistral > phi3 > llama3.
    """
    try:
        import ollama
    except ImportError:
        return None
    try:
        # ollama.list() returns all locally available models
        info = ollama.list()
    except Exception:
        return None

    # Extract model names from the response
    names = [m.get("name") or m.get("model") for m in info.get("models", [])]

    # Try candidates in order of preference
    for cand in ["mistral", "mistral:latest", "phi3", "llama3"]:
        for n in names:
            if cand in n:
                return n
    return None


# ============================================================
# PART 1: Problem — Assuming GPU Is Being Used
# ============================================================
# Many developers assume that having a GPU means Ollama uses it.
# In reality, several things can go wrong silently:
#   - NVIDIA drivers not installed (CUDA unavailable)
#   - Model too large for VRAM → layers spill to CPU
#   - Running inside Docker/WSL without GPU passthrough configured
#   - AMD GPU with incomplete ROCm support
#
# The dangerous part: Ollama won't error out. It just runs on CPU,
# and your only clue is that generation feels slow.
# ============================================================

def show_the_problem():
    """
    Explains why GPU idling is a common hidden issue.

    In production, this matters enormously:
      - CPU-only on a 7B model: ~8 tok/s → a 150-word answer takes ~25 seconds
      - With GPU (RTX 3060):    ~80 tok/s → same answer in ~3 seconds
    Users abandon chatbots that take 25 seconds to reply.
    """
    print("=== PART 1: 'Why Is My GPU Idle?' ===\n")
    print("Common cause: drivers missing, model too big for VRAM,")
    print("              or running inside a container with no GPU passthrough.")
    print("Symptom: tok/s feels like CPU only (~5-10) despite having a GPU.")
    print()


# ============================================================
# PART 2: Solution — Inspect VRAM Usage With ollama.ps()
# ============================================================
# The fix is simple: don't guess — measure.
#
# ollama.ps() is like "Task Manager for Ollama". It returns every
# model currently loaded in memory and tells you exactly:
#   - size      → total model size in bytes
#   - size_vram → how many bytes are on the GPU
#
# If size_vram == size → 100% GPU (best case)
# If size_vram == 0    → 100% CPU (GPU not being used at all)
# If size_vram < size  → partial offload (GPU does some layers, CPU the rest)
#
# This is equivalent to running `nvidia-smi` on the command line
# but accessible programmatically from Python.
# ============================================================

def show_the_solution():
    """
    Uses ollama.ps() to verify GPU is actually being used.

    How ollama.ps() works:
      1. We first run a tiny inference to "warm up" the model
         (Ollama loads the model into memory on first request)
      2. Then ollama.ps() reports what's loaded and WHERE it's loaded
      3. We compare size_vram (GPU memory) vs size (total) to get a percentage

    What to look for in the output:
      - "on GPU=X.XX GB (100%)" → fully on GPU, maximum speed
      - "on GPU=0.00 GB (0%)"  → CPU only, need to fix drivers or pick a smaller model
      - Something in between    → partial offload, consider using a smaller quantization
    """
    print("=== PART 2: Is The GPU Actually Doing Work? ===\n")

    try:
        import ollama
    except ImportError:
        print("Run: pip install ollama")
        return

    model = pick_model()
    if not model:
        print("Pull a model first: ollama pull mistral")
        return

    # STEP 1: Warm the model up by running one tiny inference.
    # Ollama loads models lazily — they aren't in memory until the first request.
    # We send a trivial prompt ("hi") with num_predict=5 to force loading
    # without wasting time on a long generation.
    print(f"Loading {model}...")
    _ = ollama.generate(model=model, prompt="hi", options={"num_predict": 5})

    # STEP 2: Query ollama.ps() — this is the key diagnostic tool.
    # It returns a dict with "models" list, each containing:
    #   name, size (total bytes), size_vram (bytes on GPU), digest, expires_at, etc.
    try:
        ps = ollama.ps()
    except Exception as e:
        print(f"Could not read ollama.ps(): {e}")
        return

    # STEP 3: Calculate and display the GPU offload percentage.
    # size_vram / size = fraction of model on GPU.
    # 100% means full GPU acceleration; anything less means some layers are on CPU.
    print("\nLoaded models (ollama.ps):")
    for m in ps.get("models", []):
        name = m.get("name") or m.get("model")
        size = m.get("size") or 0          # total model size in bytes
        vram = m.get("size_vram") or 0     # portion loaded on GPU (VRAM) in bytes
        if size:
            pct_on_gpu = (vram / size) * 100 if vram else 0
            # Convert bytes to GB (1024^3) for readability
            print(f"  {name}: total={size / 1024**3:.2f} GB, on GPU={vram / 1024**3:.2f} GB ({pct_on_gpu:.0f}%)")
    if not ps.get("models"):
        print("  (no model loaded — ran a warmup but it may have unloaded)")
    print()


# ============================================================
# PART 3: Benchmark Tokens-Per-Second
# ============================================================
# Knowing the GPU is being used (Part 2) isn't enough — we need
# to MEASURE the actual speed to confirm it's performing well.
#
# Why tokens/second (tok/s)?
#   - It's the universal metric for LLM inference speed
#   - It's hardware-comparable (same model, different GPUs)
#   - It directly maps to user experience:
#       ~10 tok/s  = painfully slow, users notice lag
#       ~40 tok/s  = acceptable for chatbots
#       ~80 tok/s  = feels responsive, like ChatGPT
#       ~150 tok/s = near-instant for short answers
#
# How we measure:
#   1. Record wall-clock time before and after generation
#   2. Count tokens in the response (approximated by word count)
#   3. tokens / elapsed_time = tok/s
#
# Note: word count ≈ token count is a rough approximation.
# Real tokenizers produce ~1.3 tokens per word on average,
# but for a quick benchmark, word count is close enough.
# ============================================================

def real_world_example():
    """
    Benchmarks the model's generation speed in tokens/second.

    This is the most practical test: forget specs and config — if your
    tok/s is high, the GPU is working. If it's low (~5-15), you're on
    CPU regardless of what nvidia-smi shows.

    The reference table at the end helps you compare your result to
    known hardware baselines and spot problems.
    """
    print("=== PART 3: Tokens/Second Benchmark ===\n")

    try:
        import ollama
    except ImportError:
        print("Run: pip install ollama")
        return

    model = pick_model()
    if not model:
        print("Pull a model first: ollama pull mistral")
        return

    prompt = "Write a 4-sentence story about Bilel and Yasmine planning a weekend trip to Sidi Bou Said."

    print(f"Model: {model}")
    print(f"Prompt: {prompt}\n")

    # time.perf_counter() gives the highest-resolution timer available.
    # We measure wall-clock time (not CPU time) because that's what
    # the user actually experiences.
    start = time.perf_counter()

    # num_predict=200 caps the output at 200 tokens so the benchmark
    # doesn't run forever on verbose models.
    resp = ollama.generate(model=model, prompt=prompt, options={"num_predict": 200})
    elapsed = time.perf_counter() - start

    # Approximate token count using word splits.
    # Real tokenizers (BPE/SentencePiece) would give a more accurate count,
    # but word count is sufficient for a speed sanity check.
    text = resp["response"]
    tokens = max(1, len(text.split()))
    tok_per_sec = tokens / elapsed

    print(f"Generated ~{tokens} tokens in {elapsed:.1f}s -> {tok_per_sec:.1f} tok/s")
    print()

    # Reference baselines to compare your result against.
    # If your tok/s is much lower than expected for your hardware,
    # go back to Part 2 and check the GPU offload percentage.
    print("Reference:")
    print("  CPU only (M1/M2 Air, 16 GB Windows laptop): ~5-15 tok/s")
    print("  Apple Silicon GPU (M2 Pro/Max, M3 Max):     ~30-60 tok/s")
    print("  NVIDIA RTX 3060/4060:                        ~60-100 tok/s")
    print("  NVIDIA RTX 4090 / L4:                        ~120-200+ tok/s")
    print()


# ============================================================
# MAIN
# ============================================================
# The demo flows in three logical steps:
#
#   Part 1 (show_the_problem):
#     Explains WHY GPU idling is a common silent issue.
#     No code runs — just awareness.
#
#   Part 2 (show_the_solution):
#     Uses ollama.ps() to VERIFY whether the model is on GPU.
#     This is the diagnostic step — run this first when debugging.
#
#   Part 3 (real_world_example):
#     MEASURES actual tok/s to confirm real-world performance.
#     This is the proof — numbers don't lie.
#
# Together: Awareness → Diagnosis → Measurement
# ============================================================

if __name__ == "__main__":
    show_the_problem()       # Step 1: Understand the risk
    show_the_solution()      # Step 2: Check GPU offload status
    real_world_example()     # Step 3: Benchmark actual speed

    print("--- Key Takeaways ---")
    print("1. Ollama auto-detects GPUs — check ollama.ps() to confirm.")
    print("2. size_vram tells you how much of the model is on GPU.")
    print("3. Mac Metal and NVIDIA CUDA are well supported out of the box.")
    print("4. For models bigger than VRAM, set options={'num_gpu': N}.")
    print("5. Measure tokens/sec — that's the real speed metric.")
