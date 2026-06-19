"""
02 - Quantization Demo
======================
Shows what quantization does to numbers, how it shrinks model sizes,
then benchmarks different quant levels on the same prompt via Ollama.

HOW TO RUN THIS FILE:
1. python demo.py                   (parts 1-3 run without Ollama)
2. For the live benchmark (part 4):
   ollama serve
   ollama pull mistral:7b-instruct-q4_K_M
   ollama pull mistral:7b-instruct-q8_0
   pip install ollama
   python demo.py
"""

import struct
import time


# ============================================================
# Constants
# ============================================================

HEADROOM_GB = 2.0
QUANT_BYTES = {
    "FP16":  (16, 2.0),
    "Q8":    (8,  1.0),
    "Q5":    (5,  0.65),
    "Q4":    (4,  0.5),
    "Q3":    (3,  0.4),
    "Q2":    (2,  0.3),
}


PROMPT = (
    "In one short sentence, what is the main reason Tunisian olive oil "
    "is famous internationally?"
)


# ============================================================
# PART 1: Problem — What Do We Lose When We Quantize?
# ============================================================

def show_the_problem():
    print("=== PART 1: What Quantization Does to Numbers ===\n")

    print("A neural network is millions of decimal weights like 0.03174.")
    print("FP16 stores them in 16 bits. Quantization crams them into fewer bits.")
    print("Fewer bits = less precision = some rounding error.\n")

    original = 0.03174
    fp16_bytes = struct.pack("e", original)
    fp16_back  = struct.unpack("e", fp16_bytes)[0]

    print(f"  Original float64:  {original:.10f}")
    print(f"  After FP16 round:  {fp16_back:.10f}   (16-bit, ~exact)")

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
        print(f"  After  Q{bits} round:  {q:+.10f}   (error: {err:.6f})")

    print()
    print("Key insight: Q4 error is tiny for ONE weight.")
    print("Across 7 billion weights, small errors mostly cancel out,")
    print("so quality drops only ~5% while RAM drops 4×.\n")


# ============================================================
# PART 2: Solution — Size Calculator Across Quant Levels
# ============================================================

def show_the_solution():
    print("=== PART 2: How Quantization Shrinks Model Size ===\n")

    print("Formula: weight_size = params × bytes_per_param")
    print(f"         total_RAM  = weight_size + {HEADROOM_GB:.0f} GB overhead\n")

    models = [
        ("Mistral 7B",  7),
        ("Llama3 8B",   8),
        ("Llama2 13B", 13),
    ]

    for model_name, params_b in models:
        print(f"--- {model_name} ({params_b}B params) ---")
        print(f"  {'Quant':<8} {'Bits':>4}  {'Weights':>10}  {'+ RAM total':>12}  {'vs FP16'}")
        print("  " + "-" * 55)
        fp16_size = params_b * QUANT_BYTES["FP16"][1]
        for quant, (bits, bpp) in QUANT_BYTES.items():
            weight_gb = params_b * bpp
            total_gb  = weight_gb + HEADROOM_GB
            ratio = weight_gb / fp16_size
            print(f"  {quant:<8} {bits:>4}  {weight_gb:>8.1f} GB  {total_gb:>10.1f} GB  {ratio:>6.1%}")
        print()


# ============================================================
# PART 3: Quality vs Size Trade-Off Table
# ============================================================

def show_tradeoff():
    print("=== PART 3: Quality vs Size Trade-Off ===\n")

    print("Typical benchmark results (Mistral 7B, perplexity on wiki text):\n")

    rows = [
        ("FP16",   14.0, "1.0×", "100%",  "baseline, rarely needed"),
        ("Q8",      8.0, "1.4×", "~99%",  "near-perfect, large"),
        ("Q5_K_M",  5.0, "1.7×", "~97%",  "great middle ground"),
        ("Q4_K_M",  4.0, "2.0×", "~95%",  "recommended default"),
        ("Q3_K_M",  3.0, "2.2×", "~88%",  "noticeable quality drop"),
        ("Q2_K",    2.5, "2.3×", "~75%",  "last resort only"),
    ]

    print(f"  {'Quant':<10} {'Size':>6}  {'Speed':>6}  {'Quality':>8}  {'Notes'}")
    print("  " + "-" * 60)
    for quant, size, speed, quality, notes in rows:
        print(f"  {quant:<10} {size:>4.1f} GB  {speed:>6}  {quality:>8}  {notes}")

    print()
    print("Rule of thumb:")
    print("  - Start with Q4_K_M (best size/quality balance)")
    print("  - Step up to Q5 or Q8 ONLY if you measure a quality regression")
    print("  - FP16 is almost never worth the 4× RAM cost\n")


# ============================================================
# PART 4: Live Benchmark — Compare Quant Levels via Ollama
# ============================================================

def candidates():
    try:
        import ollama
    except ImportError:
        return []
    try:
        info = ollama.list()
    except Exception:
        return []
    names = [m.get("name") or m.get("model") for m in info.get("models", [])]
    return sorted(
        [n for n in names if any(q in n.lower() for q in
         ["q2", "q3", "q4", "q5", "q6", "q8", "fp16"])]
    )


def live_benchmark():
    print("=== PART 4: Live Speed Benchmark Per Quant ===\n")

    try:
        import ollama
    except ImportError:
        print("Skipped — run: pip install ollama\n")
        return

    found = candidates()
    if not found:
        print("No quantized model tags found locally.")
        print("Try pulling at least two variants:")
        print("  ollama pull mistral:7b-instruct-q4_K_M")
        print("  ollama pull mistral:7b-instruct-q8_0\n")
        return

    print("Quantized models available:")
    for m in found:
        print(f"  - {m}")
    print()

    print(f"Prompt: \"{PROMPT}\"\n")

    results = []
    for m in found:
        try:
            start = time.perf_counter()
            resp = ollama.generate(
                model=m,
                prompt=PROMPT,
                options={"num_predict": 60},
            )
            cold = time.perf_counter() - start

            start = time.perf_counter()
            resp = ollama.generate(
                model=m,
                prompt=PROMPT,
                options={"num_predict": 60},
            )
            warm = time.perf_counter() - start

            output = resp["response"].strip().replace("\n", " ")
            tokens = resp.get("eval_count", 0)
            tok_per_sec = tokens / warm if warm > 0 else 0

            results.append((m, cold, warm, tok_per_sec, output))
            print(f"[{m:35}] cold {cold:5.1f}s | warm {warm:5.1f}s | {tok_per_sec:.1f} tok/s")
            print(f"  -> {output[:120]}")
        except Exception as e:
            print(f"[{m}] ERROR: {e}")

    if len(results) >= 2:
        print()
        fastest = min(results, key=lambda r: r[2])
        slowest = max(results, key=lambda r: r[2])
        speedup = slowest[2] / fastest[2] if fastest[2] > 0 else 0
        print(f"Fastest: {fastest[0]} ({fastest[2]:.1f}s)")
        print(f"Slowest: {slowest[0]} ({slowest[2]:.1f}s)")
        print(f"Speedup: {speedup:.1f}×")
    print()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    show_the_problem()
    show_the_solution()
    show_tradeoff()
    live_benchmark()

    print("--- Key Takeaways ---")
    print("1. Quantization = fewer bits per weight. Q4 = 4 bits (vs 16 for FP16).")
    print("2. Q4_K_M is the recommended default — 4× smaller, ~5% quality drop.")
    print("3. Step up to Q5/Q8 only if you measure a regression on YOUR data.")
    print("4. FP16 is rarely worth its 4× RAM cost for production use.")
    print("5. Always benchmark cold vs warm — first call hides model load time.")
