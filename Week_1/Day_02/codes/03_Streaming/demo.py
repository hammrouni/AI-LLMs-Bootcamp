"""
03 - Streaming Demo
===================
Learn how to stream AI responses token by token instead of waiting for the full response.

HOW TO RUN:
    pip install httpx python-dotenv openai
    python demo.py

Get a free Mistral API key at: https://console.mistral.ai
Set MISTRAL_API_KEY in your .env file to run live examples.
"""

import os
import json
import time
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()

MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"


# ============================================================
# PART 1: Show the Difference — Normal vs Streaming (Simulated)
# ============================================================
def simulate_normal_response():
    """Simulate what a non-streaming response feels like."""
    print("=== Normal Response (no streaming) ===\n")

    print("  Sending request to AI...")
    print("  Waiting", end="", flush=True)
    for _ in range(5):
        time.sleep(0.4)
        print(".", end="", flush=True)
    print("\n")

    # All text appears at once after the wait
    full_response = "Yasmine est ingénieure à Tunis. Elle travaille sur un projet d'IA pour analyser les données de la médina. Son collègue Mehdi gère le backend et Nour s'occupe du frontend."
    print(f"  Response received all at once:\n  {full_response}\n")


def simulate_streaming_response():
    """Simulate what streaming feels like — text appears word by word."""
    print("=== Streaming Response ===\n")

    print("  First token in ~0.3s. Text appears as it is generated:\n  ", end="", flush=True)

    words = "Yasmine est ingénieure à Tunis. Elle travaille sur un projet d'IA pour analyser les données de la médina. Son collègue Mehdi gère le backend et Nour s'occupe du frontend.".split()

    for word in words:
        print(word + " ", end="", flush=True)
        time.sleep(0.07)  # simulate token generation time

    print("\n\n  User sees progress immediately — feels much more responsive!\n")


# ============================================================
# PART 2: Manual Streaming with httpx (understanding the protocol)
# ============================================================
async def stream_with_httpx(prompt: str, api_key: str):
    """
    Stream using httpx directly — shows you what's happening under the hood.
    The API sends Server-Sent Events (SSE) line by line.
    """
    print("=== Manual Streaming with httpx ===\n")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "mistral-small-latest",
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,  # KEY: this tells the API to stream
        "max_tokens": 200,
    }

    print(f"  Prompt: {prompt}")
    print("  Response: ", end="", flush=True)

    full_text = ""

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            async with client.stream("POST", MISTRAL_API_URL, headers=headers, json=payload) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if not line.strip():
                        continue

                    # Each line looks like: "data: {...json...}" or "data: [DONE]"
                    if not line.startswith("data: "):
                        continue

                    chunk_str = line[6:]  # strip "data: " prefix

                    if chunk_str == "[DONE]":
                        break

                    try:
                        chunk = json.loads(chunk_str)
                        token = chunk["choices"][0]["delta"].get("content", "")
                        if token:
                            print(token, end="", flush=True)
                            full_text += token
                    except (json.JSONDecodeError, KeyError):
                        continue

    except httpx.HTTPStatusError as e:
        print(f"\n  [ERROR] HTTP {e.response.status_code}")
        return None
    except Exception as e:
        print(f"\n  [ERROR] {e}")
        return None

    print("\n")
    return full_text


# ============================================================
# PART 3: Streaming with the OpenAI SDK (cleaner approach)
# ============================================================
# Mistral is fully compatible with the OpenAI API format.
# We point the OpenAI SDK at Mistral's endpoint — same pattern as Day 01 Instructor demo.
async def stream_with_openai_sdk(prompt: str, api_key: str):
    """
    Stream using the OpenAI SDK pointed at Mistral's endpoint.
    Mistral uses the same API format as OpenAI, so this works perfectly.
    Cleaner than raw httpx — the SDK handles SSE parsing for you.
    """
    print("=== Streaming with OpenAI SDK (Mistral-compatible) ===\n")

    try:
        from openai import AsyncOpenAI
    except ImportError:
        print("  Install with: pip install openai\n")
        return

    # Use Mistral's OpenAI-compatible endpoint — same pattern as Day 01
    client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://api.mistral.ai/v1"
    )

    print(f"  Prompt: {prompt}")
    print("  Response: ", end="", flush=True)

    full_text = ""

    try:
        async with client.chat.completions.stream(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
        ) as stream:
            async for text in stream.text_stream:
                print(text, end="", flush=True)
                full_text += text

    except Exception as e:
        print(f"\n  [ERROR] {e}")
        return None

    print("\n")
    return full_text


# ============================================================
# PART 4: Stream + Collect Full Response (OpenAI SDK)
# ============================================================
async def stream_and_collect(prompt: str, api_key: str) -> str | None:
    """
    Stream tokens to the screen AND collect the full response.
    Useful when you need both: live display + full text for later processing.
    Uses the OpenAI SDK with Mistral's endpoint.
    """
    print("=== Stream + Collect Full Response ===\n")

    try:
        from openai import AsyncOpenAI
    except ImportError:
        print("  Install with: pip install openai\n")
        return None

    # Same Mistral-compatible setup as Part 3
    client = AsyncOpenAI(api_key=api_key, base_url="https://api.mistral.ai/v1")

    print(f"  Prompt: {prompt}")
    print("  Streaming: ", end="", flush=True)

    tokens = []

    try:
        async with client.chat.completions.stream(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
        ) as stream:
            async for text in stream.text_stream:
                print(text, end="", flush=True)
                tokens.append(text)

    except Exception as e:
        print(f"\n  [ERROR] {e}")
        return None

    full_response = "".join(tokens)
    print(f"\n\n  Total chunks received: {len(tokens)}")
    print(f"  Full response length: {len(full_response)} characters\n")
    return full_response


# ============================================================
# PART 5: Streaming with a Loading Indicator (when no API key)
# ============================================================
async def show_streaming_pattern_demo():
    """Show streaming patterns without needing an API key."""
    print("=== Streaming Pattern (no API key needed) ===\n")

    # Simulate what streaming looks like in a real app
    fake_tokens = [
        "Tunis", " is", " the", " capital", " and", " largest", " city",
        " of", " Tunisia", ".", " It", " is", " home", " to", " the",
        " medina", " of", " Tunis", ",", " a", " UNESCO", " World",
        " Heritage", " Site", "."
    ]

    print("  Streaming tokens as they arrive:\n  ", end="", flush=True)
    for token in fake_tokens:
        print(token, end="", flush=True)
        await asyncio.sleep(0.08)
    print("\n")

    # Show the raw SSE data format
    print("  What the raw API sends (Server-Sent Events format):")
    for i, token in enumerate(fake_tokens[:4]):
        chunk = {
            "choices": [{"delta": {"content": token}, "finish_reason": None}]
        }
        print(f'  data: {json.dumps(chunk)}')
    print("  data: [DONE]\n")


# ============================================================
# MAIN
# ============================================================
async def main():
    simulate_normal_response()
    simulate_streaming_response()

    await show_streaming_pattern_demo()

    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("--- Live API Examples ---")
        print("Set MISTRAL_API_KEY in .env to run live streaming examples.\n")
    else:
        await stream_with_httpx(
            "En 3 phrases, décris la médina de Tunis.", api_key
        )
        await stream_with_openai_sdk(
            "Quelles sont les principales exportations de la Tunisie ? Liste 4.", api_key
        )
        await stream_and_collect(
            "Cite 3 sites historiques tunisiens célèbres et un fait sur chacun.", api_key
        )

    print("--- Key Takeaways ---")
    print('1. Add "stream": True to the payload to enable streaming')
    print('2. Mistral sends Server-Sent Events: "data: {...}" lines, ending with "data: [DONE]"')
    print("3. httpx approach: parse SSE lines manually — good for understanding the protocol")
    print("4. OpenAI SDK approach: Mistral is OpenAI-compatible, point base_url at Mistral")
    print("5. Collect tokens in a list and ''.join(tokens) to get the full response")
    print("6. Don't use streaming with Instructor (it needs the full response to parse)")


if __name__ == "__main__":
    asyncio.run(main())
