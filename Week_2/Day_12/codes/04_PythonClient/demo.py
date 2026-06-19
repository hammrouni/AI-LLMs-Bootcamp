"""
04 - The Ollama Python Client Demo
==================================
Walks through chat, generate, embeddings, streaming, and the OpenAI-compatible
mode. Shows how the local Ollama API matches the cloud SDK shape.

HOW TO RUN THIS FILE:
1. ollama serve in one terminal
2. ollama pull mistral && ollama pull nomic-embed-text
3. pip install ollama openai
4. python demo.py
"""

import os


def model_available(target_substring):
    try:
        import ollama
    except ImportError:
        return None
    try:
        info = ollama.list()
    except Exception:
        return None
    for m in info.get("models", []):
        name = m.get("name") or m.get("model")
        if target_substring in name:
            return name
    return None


# ============================================================
# PART 1: Problem — Raw HTTP Is Tedious
# ============================================================

def show_the_problem():
    print("=" * 60)
    print("  PART 1: Raw HTTP vs Python Client")
    print("=" * 60)
    print()
    print("  Without the client you would:")
    print("    - Call /api/chat with requests")
    print("    - Parse streamed JSON-lines yourself")
    print("    - Handle timeouts and retries manually")
    print()
    print("  With the ollama Python client, it's one function call.")
    print("-" * 60)
    print()


# ============================================================
# PART 2: chat, generate, embeddings
# ============================================================

def show_the_solution():
    print("=" * 60)
    print("  PART 2: Core Functions — chat / generate / embeddings")
    print("=" * 60)
    print()

    try:
        import ollama
    except ImportError:
        print("Run: pip install ollama")
        return

    chat_model = model_available("llama3") or model_available("mistral") or model_available("phi3")
    embed_model = model_available("nomic-embed-text")

    if chat_model:
        print("-" * 40)
        print(f"  [A] ollama.chat() — {chat_model}")
        print("-" * 40)
        print("  Sends a messages list (system/user/assistant roles).")
        print("  Best for: multi-turn conversations.")
        print()
        resp = ollama.chat(
            model=chat_model,
            messages=[{"role": "user", "content": "What is harissa, in one short sentence?"}],
            options={"num_predict": 60},
        )
        print(f"  Q: What is harissa?")
        print(f"  A: {resp['message']['content'].strip()}")
        print()

        print("-" * 40)
        print(f"  [B] ollama.generate() — {chat_model}")
        print("-" * 40)
        print("  Sends a single raw prompt string, returns raw text.")
        print("  Best for: one-shot completions with no role structure.")
        print()
        resp = ollama.generate(
            model=chat_model,
            prompt="Name three Tunisian cities in a comma-separated list.",
            options={"num_predict": 30},
        )
        print(f"  Prompt: Name three Tunisian cities")
        print(f"  Result: {resp['response'].strip()}")
        print()

    if embed_model:
        print("-" * 40)
        print(f"  [C] ollama.embeddings() — {embed_model}")
        print("-" * 40)
        print("  Converts text into a numeric vector (embedding).")
        print("  Best for: similarity search, RAG, clustering.")
        print()
        resp = ollama.embeddings(model=embed_model, prompt="Yasmine loves makroudh from Kairouan.")
        vec = resp["embedding"]
        print(f"  Input:      \"Yasmine loves makroudh from Kairouan.\"")
        print(f"  Dimensions: {len(vec)}")
        print(f"  Preview:    {vec[:5]}")
        print()
    else:
        print("  Pull an embeddings model for the embed demo:")
        print("    ollama pull nomic-embed-text")
        print()


# ============================================================
# PART 3: Streaming + OpenAI-Compatible Mode
# ============================================================

def real_world_example():
    print("=" * 60)
    print("  PART 3: Streaming + OpenAI-Compatible Mode")
    print("=" * 60)
    print()

    try:
        import ollama
    except ImportError:
        print("Run: pip install ollama")
        return

    chat_model = model_available("llama3") or model_available("mistral") or model_available("phi3")
    if not chat_model:
        print("  No chat model pulled. Run: ollama pull mistral")
        return

    print("-" * 40)
    print(f"  [A] Streaming — {chat_model}")
    print("-" * 40)
    print("  Same as chat(), but with stream=True.")
    print("  Tokens print one-by-one as the model generates them.")
    print()
    print(f"  Q: Describe Sidi Bou Said in one sentence.")
    print()
    print("  A: ", end="", flush=True)
    for chunk in ollama.chat(
        model=chat_model,
        messages=[{"role": "user", "content": "Describe Sidi Bou Said in one sentence."}],
        stream=True,
        options={"num_predict": 120},
    ):
        print(chunk["message"]["content"], end="", flush=True)
    print()
    print()

    print("-" * 40)
    print("  [B] OpenAI-Compatible Mode")
    print("-" * 40)
    print("  Uses the standard openai SDK pointed at localhost.")
    print("  Proves Ollama is a drop-in replacement for cloud APIs.")
    print()
    try:
        from openai import OpenAI
    except ImportError:
        print("  Skipped — install openai: pip install openai")
        print()
        return
    client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
    resp = client.chat.completions.create(
        model=chat_model,
        messages=[{"role": "user", "content": "Say hi in Tunisian darija."}],
        max_tokens=40,
    )
    print(f"  Q: Say hi in Tunisian darija.")
    print(f"  A: {resp.choices[0].message.content.strip()}")
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
    print("  1. chat(), generate(), embeddings() cover 95% of use cases")
    print("  2. stream=True yields tokens live — better UX")
    print("  3. OpenAI-compatible API — drop-in replacement for cloud SDKs")
    print("  4. Client(host=...) for remote; AsyncClient for asyncio")
    print("  5. Keep model name in one place (env var or config)")
    print("=" * 60)
