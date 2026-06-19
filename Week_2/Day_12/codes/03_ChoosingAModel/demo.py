"""
03 - Choosing a Model Demo
==========================
Benchmarks multiple local Ollama models on the same prompt and prints
per-model latency and output. Helps you choose the right size for your laptop.

HOW TO RUN THIS FILE:
1. Make sure ollama serve is running.
2. Pull a few models to compare, for example:
   ollama pull phi3
   ollama pull mistral
3. pip install ollama
4. python demo.py
"""

import time


def list_local_models():
    try:
        import ollama
    except ImportError:
        return []
    try:
        info = ollama.list()
    except Exception:
        return []
    return [m.get("name") or m.get("model") for m in info.get("models", [])]


# ============================================================
# PART 1: Problem — Choosing the Biggest Model "to be safe"
# ============================================================

def show_the_problem():
    print("=" * 60)
    print("  PART 1: 'Bigger Is Always Better' (Wrong)")
    print("=" * 60)
    print()
    print("  Common beginner mistake: pull llama3:70b on a 16 GB laptop.")
    print("  Result: 3-minute load, 30s/query, possibly OOM crash.")
    print()
    print("  Reality: a 7B instruct model handles 80% of practical tasks.")
    print("-" * 60)
    print()


# ============================================================
# PART 2: Solution — Benchmark a Few Local Models
# ============================================================

def show_the_solution():
    print("=" * 60)
    print("  PART 2: Side-by-Side Benchmark")
    print("=" * 60)
    print()

    try:
        import ollama
    except ImportError:
        print("Run: pip install ollama")
        return

    available = list_local_models()
    search_terms = ["llama3.1", "llama3", "mistral", "phi3", "phi"]
    candidates = []
    seen = set()
    for term in search_terms:
        for name in available:
            if term in name and name not in seen:
                candidates.append(name)
                seen.add(name)

    if not candidates:
        print("  No comparable models pulled. Run, for example:")
        print("    ollama pull llama3.1:8b")
        print("    ollama pull mistral")
        return

    prompt = (
        "Summarize in one sentence: "
        "'Tunisia is a country in North Africa famous for couscous, Carthage, and olive oil.'"
    )

    print(f"  Prompt: {prompt}")
    print()
    print(f"  {'Model':<30} {'Time':>6}   {'Output'}")
    print("  " + "-" * 56)

    for m in candidates:
        try:
            # warmup: load model into memory (not timed)
            ollama.generate(model=m, prompt="hi", options={"num_predict": 1})

            start = time.perf_counter()
            resp = ollama.generate(model=m, prompt=prompt, options={"num_predict": 80})
            elapsed = time.perf_counter() - start
            output = resp["response"].strip().replace("\n", " ")
            print(f"  {m:<30} {elapsed:5.1f}s   {output[:120]}")
        except Exception as e:
            print(f"  {m:<30}  ERROR: {e}")
    print()


# ============================================================
# PART 3: Trade-off Summary
# ============================================================

def real_world_example():
    print("=" * 60)
    print("  PART 3: Pick By Task, Not By Size")
    print("=" * 60)
    print()
    print(f"  {'Task':<28} {'Recommended':<22} {'RAM'}")
    print("  " + "-" * 56)
    print(f"  {'Simple chat / FAQ':<28} {'llama3.1:8b':<22} {'~ 8 GB'}")
    print(f"  {'Code generation':<28} {'codellama (7B)':<22} {'~ 8 GB'}")
    print(f"  {'Multilingual AR/FR/EN':<28} {'mistral (7B)':<22} {'~ 8 GB'}")
    print(f"  {'Embeddings':<28} {'nomic-embed-text':<22} {'< 1 GB'}")
    print(f"  {'Heavy reasoning':<28} {'llama3:70b (GPU)':<22} {'48+ GB'}")
    print()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    show_the_problem()
    show_the_solution()
    real_world_example()

    print("=" * 60)
    print("  KEY TAKEAWAYS")
    print("=" * 60)
    print("  1. Pick by RAM first, then by quality")
    print("  2. 7B/8B models are the sweet spot for most laptop tasks")
    print("  3. Use nomic-embed-text for local embeddings (small, fast)")
    print("  4. Benchmark before committing — 5 min of testing saves days")
    print("  5. Scale up only when measurements show you need to")
    print("=" * 60)
