"""
02 - Running Models Locally Demo
================================
Demonstrates ollama.chat, ollama.generate, streaming, and per-call options
on a local Mistral (or phi3) model.

HOW TO RUN THIS FILE:
1. Make sure `ollama serve` is running and you have pulled at least one model:
   ollama pull mistral
2. pip install ollama
3. python demo.py
"""

import os


def pick_model():
    try:
        import ollama
    except ImportError:
        return None
    try:
        info = ollama.list()
    except Exception:
        return None
    names = [m.get("name") or m.get("model") for m in info.get("models", [])]
    for cand in ["llama3", "mistral", "mistral", "phi"]:
        for n in names:
            if cand in n:
                return n
    return None


# ============================================================
# PART 1: Problem — generate vs chat Confusion
# ============================================================

def show_the_problem():
    print("=" * 60)
    print("  PART 1: generate() vs chat() — When to Use Which")
    print("=" * 60)
    print()
    print("Common mistakes beginners make:")
    print("  1. Using generate() for multi-turn conversations")
    print("     -> loses conversation history between calls")
    print("  2. Building chat context with string concatenation")
    print("     -> instead of using a messages list")
    print("  3. Forgetting stream=True")
    print("     -> waiting 8+ seconds for a wall of text")
    print()
    print("This demo shows the right way for each scenario.")
    print("-" * 60)
    print()


# ============================================================
# PART 2: chat() and generate() Side by Side
# ============================================================

def show_the_solution():
    print("=" * 60)
    print("  PART 2: chat() vs generate() — Side by Side")
    print("=" * 60)
    print()

    try:
        import ollama
    except ImportError:
        print("Run: pip install ollama")
        return

    model = pick_model()
    if not model:
        print("No local model found. Run: ollama pull mistral")
        return

    print(f"  Model: {model}")
    print()

    print("-" * 40)
    print("  [A] ollama.chat() — system + user")
    print("-" * 40)
    resp = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": "You are a brief Tunisian travel guide."},
            {"role": "user",   "content": "Top 1 thing to do in Tunisia in one short sentence?"},
        ],
        options={"num_predict": 80},
    )
    print(f"  Q: Top 1 thing to do in Tunisia?")
    print(f"  A: {resp['message']['content'].strip()}")
    print()

    print("-" * 40)
    print("  [B] ollama.generate() — one-shot")
    print("-" * 40)
    resp = ollama.generate(
        model=model,
        prompt="Translate to Tunisian darija (one short sentence): 'Hello, how are you today?'",
        options={"num_predict": 60},
    )
    print(f"  Prompt: Translate 'Hello, how are you today?' to arab tunisian darija")
    print(f"  Result: {resp['response'].strip()}")
    print()


# ============================================================
# PART 3: Streaming + Options
# ============================================================

def real_world_example():
    print("=" * 60)
    print("  PART 3: Streaming Output — Watch Tokens Arrive Live")
    print("=" * 60)
    print()

    try:
        import ollama
    except ImportError:
        print("Run: pip install ollama")
        return

    model = pick_model()
    if not model:
        print("No local model found. Run: ollama pull mistral")
        return

    print(f"  Model: {model}")
    print(f"  Q: A 2-sentence story about Bilel discovering a hidden café in Tunis.")
    print()
    print("  A: ", end="", flush=True)

    for chunk in ollama.chat(
        model=model,
        messages=[
            {"role": "user", "content": "In two sentences, tell a small story about Bilel finding a hidden café in Tunis."},
        ],
        stream=True,
        options={"temperature": 0.6, "num_predict": 200},
    ):
        print(chunk["message"]["content"], end="", flush=True)
    print()
    print()
    print("-" * 60)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    show_the_problem()
    show_the_solution()
    real_world_example()

    print()
    print("=" * 60)
    print("  KEY TAKEAWAYS")
    print("=" * 60)
    print("  1. chat()     -> multi-turn conversations (messages list)")
    print("  2. generate() -> one-shot completions (single prompt)")
    print("  3. stream=True is a UX game-changer for long answers")
    print("  4. options={temperature, num_predict, top_p} tunes per call")
    print("  5. Everything is offline, free, and on your machine")
    print("=" * 60)
