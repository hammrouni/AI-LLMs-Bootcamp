"""
01 - Ollama Setup Demo
======================
Verifies Ollama is installed, the daemon is running, and at least one model
is pulled. Prints helpful messages if anything is missing.

HOW TO RUN THIS FILE:
1. Install Ollama from https://ollama.com
2. In one terminal: ollama serve
3. In another:      ollama pull mistral
4. pip install ollama python-dotenv
5. python demo.py
"""

import os
import sys


# ============================================================
# PART 1: The Problem — Forgetting To Set Up Before Coding
# ============================================================

def show_the_problem():
    print("=== PART 1: Why Setup First ===\n")
    print("Without setup, every Python call will fail with:")
    print("  ConnectionError: [Errno 61] Connection refused")
    print("  -> daemon is not running")
    print()
    print("Or:")
    print("  ollama.ResponseError: model not found")
    print("  -> model isn't pulled yet")
    print()
    print("This demo checks both before you write real code.\n")


# ============================================================
# PART 2: Verify Daemon + Models
# ============================================================

def show_the_solution():
    print("=== PART 2: Verifying the Ollama Daemon ===\n")

    try:
        import ollama
    except ImportError:
        print("Run: pip install ollama")
        return

    try:
        info = ollama.list()
    except Exception as e:
        print("Could not reach the Ollama daemon.")
        print(f"  Error: {e}")
        print("\nFix:")
        print("  1. Install Ollama from https://ollama.com")
        print("  2. Start it with: ollama serve")
        print("  3. Re-run this script.")
        return

    models = info.get("models", [])
    if not models:
        print("Ollama is running but no models are pulled.")
        print("Run, e.g.:")
        print("  ollama pull mistral")
        print("  ollama pull nomic-embed-text")
        return

    print(f"Ollama daemon is up. {len(models)} model(s) available:")
    for m in models:
        name = m.get("name") or m.get("model")
        size_gb = (m.get("size") or 0) / (1024 ** 3)
        print(f"  - {name:30}  {size_gb:.2f} GB")
    print()


# ============================================================
# PART 3: First Local LLM Call
# ============================================================

def real_world_example():
    print("=== PART 3: A First Local Chat Call ===\n")

    try:
        import ollama
    except ImportError:
        print("Run: pip install ollama")
        return

    try:
        info = ollama.list()
    except Exception:
        print("Ollama daemon not reachable — skipping. See PART 2 for setup.")
        return

    names = [m.get("name") or m.get("model") for m in info.get("models", [])]
    candidate_models = ["llama3", "mistral", "phi"]
    pulled = None
    for c in candidate_models:
        match = next((n for n in names if c in n), None)
        if match:
            pulled = match
            break

    if not pulled:
        print("No common chat model found. Run:")
        print("  ollama pull mistral")
        return

    print(f"Using model: {pulled}\n")
    response = ollama.chat(
        model=pulled,
        messages=[
            {"role": "user", "content": "In one sentence, what is couscous?"},
        ],
    )

    answer = response["message"]["content"].strip()
    print(f"Q: In one sentence, what is couscous?")
    print(f"A: {answer}\n")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    show_the_problem()
    show_the_solution()
    real_world_example()

    print("--- Key Takeaways ---")
    print("1. Ollama = local server (:11434) + CLI + model registry.")
    print("2. Install once, pull each model once, then it's all local.")
    print("3. Verify with `ollama list` before writing Python code.")
    print("4. 7B models fit comfortably on a 16 GB laptop.")
    print("5. From here on, every LLM call is offline and free.")
