"""
01 - Hardware Requirements Demo
===============================
Inspects the local machine's RAM and GPU (if available) and computes
whether specific Ollama model sizes will fit comfortably.

HOW TO RUN THIS FILE:
1. pip install psutil
2. python demo.py
"""

import psutil
import subprocess
import shutil

HEADROOM_GB = 2.0
QUANT_BYTES = {"FP16": 2.0, "Q8": 1.0, "Q5": 0.65, "Q4": 0.5, "Q3": 0.4}


def estimate_ram_gb(params_b, quant="Q4"):
    return params_b * QUANT_BYTES[quant] + HEADROOM_GB


def check_fit(avail_gb, params_b, quant="Q4"):
    weight_gb = params_b * QUANT_BYTES[quant]
    needed = weight_gb + HEADROOM_GB
    if avail_gb >= needed:
        return weight_gb, needed, "OK"
    if avail_gb >= weight_gb:
        return weight_gb, needed, "tight (may swap)"
    return weight_gb, needed, "won't fit"


# ============================================================
# PART 1: Problem — Picking a Model Bigger Than Your RAM
# ============================================================

def show_the_problem():
    print("=== PART 1: Model > RAM = Disaster ===\n")
    print("Trying to run Llama2 13B Q4 on an 8 GB laptop:")
    print("  - Heavy swap to SSD")
    print("  - 5+ seconds per token")
    print("  - Laptop throttles, fan max")
    print("  - Sometimes OOM kill -> Ollama daemon dies")
    print()


# ============================================================
# PART 2: Solution — Inspect The Box First
# ============================================================

def get_gpu_info():
    if not shutil.which("nvidia-smi"):
        return None
    try:
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
            gpus.append({
                "name": name,
                "total_mb": float(total),
                "free_mb": float(free),
            })
        return gpus
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def show_the_solution():
    print("=== PART 2: Inspecting Your Hardware ===\n")

    vm = psutil.virtual_memory()
    total_gb = vm.total / (1024**3)
    avail_gb = vm.available / (1024**3)
    print(f"Total RAM:     {total_gb:.1f} GB")
    print(f"Available RAM: {avail_gb:.1f} GB")
    print(f"CPU count:     {psutil.cpu_count(logical=False)} physical / {psutil.cpu_count()} logical")
    print()

    gpus = get_gpu_info()
    if gpus:
        for i, gpu in enumerate(gpus):
            print(f"GPU {i}: {gpu['name']}")
            print(f"  VRAM total: {gpu['total_mb'] / 1024:.1f} GB")
            print(f"  VRAM free:  {gpu['free_mb'] / 1024:.1f} GB")
        print()
    else:
        print("GPU: none detected (CPU-only inference)\n")

    # (name, params_billions, quantization) — sizes are CALCULATED, not hardcoded
    models = [
        ("phi3:mini",    3,  "Q4"),
        ("mistral 7B",   7,  "Q4"),
        ("llama3 8B",    8,  "Q4"),
        ("gemma2 9B",    9,  "Q4"),
        ("llama2 13B",  13,  "Q4"),
        ("mistral 7B",   7,  "Q8"),
        ("llama3 70B",  70,  "Q4"),
    ]

    print(f"Cheat sheet (RAM = params x bytes_per_param + {HEADROOM_GB:.0f} GB overhead):")
    print(f"  {'Model':<22} {'Params':>6}  {'Quant':>5}  {'Weights':>8}  {'Total RAM':>10}  {'Status'}")
    print("  " + "-" * 72)
    for name, params_b, quant in models:
        weight_gb, needed, status = check_fit(avail_gb, params_b, quant)
        label = f"{name} {quant}"
        print(f"  {label:<22} {params_b:>4}B  {quant:>5}  {weight_gb:>6.1f} GB  {needed:>8.1f} GB   [{status}]")
    print()


# ============================================================
# PART 3: Sizing a Custom Model
# ============================================================

def real_world_example():
    print("=== PART 3: Sizing a Custom Model ===\n")
    print(f"Formula: RAM needed = params x bytes_per_param + {HEADROOM_GB:.0f} GB overhead\n")

    for params_b in [3, 7, 13, 70]:
        print(f"--- {params_b}B params ---")
        for quant, bpp in QUANT_BYTES.items():
            ram = estimate_ram_gb(params_b, quant)
            print(f"  {quant}: ~{ram:.1f} GB RAM")
        print()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    show_the_problem()
    show_the_solution()
    real_world_example()

    print("--- Key Takeaways ---")
    print("1. RAM needed = params * bytes/param + ~2 GB overhead.")
    print("2. Leave 2 GB free RAM after loading or the OS will swap.")
    print("3. Quantization (Q4) shrinks RAM by ~4x vs FP16.")
    print("4. Check available RAM before pulling huge models.")
    print("5. 7B Q4 is the safe default for 8 GB laptops.")
