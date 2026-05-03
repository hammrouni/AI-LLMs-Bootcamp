"""
01 - Error Handling Demo
========================
Learn how to handle API errors gracefully instead of letting your program crash.

HOW TO RUN:
    pip install httpx python-dotenv
    python demo.py

For the live API examples (Parts 3+), set your MISTRAL_API_KEY in a .env file.
Get a free key at: https://console.mistral.ai
"""

import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# PART 1: The Problem — Unhandled Errors Crash Everything
# ============================================================
def show_the_problem():
    """What happens when you don't handle errors."""
    print("=== THE PROBLEM: No Error Handling ===\n")

    print("Imagine this code — Bilel wrote it at 2am (DO NOT run — it will crash!):")
    print("""
    import httpx

    # Bilel's chatbot calls Mistral to answer Yasmine's question
    # But if the server is down or the internet cuts out...
    response = httpx.get("https://api.mistral.ai/v1/models")
    data = response.json()
    print(data["models"])   # KeyError if response is unexpected

    # The ENTIRE app crashes. Yasmine sees:
    # ConnectError: [Errno 11001] getaddrinfo failed
    # And nothing else — very bad user experience!
    """)

    print("The fix: wrap every API call in try/except.\n")


# ============================================================
# PART 2: The try/except Pattern
# ============================================================
def safe_divide(a, b):
    """Simple example of try/except before we touch APIs."""
    try:
        result = a / b
        print(f"  {a} / {b} = {result}")
        return result
    except ZeroDivisionError:
        print(f"  Cannot divide {a} by zero!")
        return None


def basic_try_except_demo():
    """Show the try/except pattern with simple examples."""
    print("=== try/except Pattern ===\n")

    safe_divide(10, 2)    # works
    safe_divide(10, 0)    # caught — no crash

    # Multiple except blocks
    print("\nMultiple except blocks:")
    for value in ["42", "hello", None]:
        try:
            number = int(value)
            print(f"  Converted '{value}' → {number}")
        except (TypeError, ValueError) as e:
            print(f"  Could not convert '{value}': {e}")

    print()


# ============================================================
# PART 3: HTTP Error Handling with httpx
# ============================================================
async def handle_http_errors():
    """Demonstrate handling different HTTP error types."""
    print("=== HTTP Error Handling ===\n")

    test_urls = [
        ("https://httpbin.org/status/200", "200 OK"),
        ("https://httpbin.org/status/401", "401 Unauthorized"),
        ("https://httpbin.org/status/429", "429 Too Many Requests"),
        ("https://httpbin.org/status/500", "500 Server Error"),
    ]

    async with httpx.AsyncClient(timeout=10) as client:
        for url, description in test_urls:
            try:
                response = await client.get(url)
                # raise_for_status() raises an exception for 4xx/5xx codes
                response.raise_for_status()
                print(f"  ✓ {description} — success")

            except httpx.HTTPStatusError as e:
                status = e.response.status_code
                if status == 401:
                    print(f"  ✗ {description} — bad API key, check your credentials")
                elif status == 429:
                    print(f"  ✗ {description} — rate limited, slow down your requests")
                elif status >= 500:
                    print(f"  ✗ {description} — server error, try again later")
                else:
                    print(f"  ✗ {description} — HTTP error {status}")

            except httpx.TimeoutException:
                print(f"  ✗ {description} — request timed out")

            except httpx.ConnectError:
                print(f"  ✗ {description} — could not connect to server")

    print()


# ============================================================
# PART 4: A Safe API Caller Function
# ============================================================
async def safe_api_call(url: str, headers: dict, payload: dict) -> dict | None:
    """
    A reusable wrapper that handles all common API errors.
    Returns the JSON response on success, None on failure.
    """
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()

    except httpx.TimeoutException:
        print("  [ERROR] Request timed out. The server took too long to respond.")
        return None

    except httpx.ConnectError:
        print("  [ERROR] Cannot connect. Check your internet connection.")
        return None

    except httpx.HTTPStatusError as e:
        status = e.response.status_code
        if status == 401:
            print("  [ERROR] 401 Unauthorized — your API key is wrong or missing.")
        elif status == 429:
            print("  [ERROR] 429 Rate Limited — you are sending too many requests.")
        elif status == 422:
            print(f"  [ERROR] 422 Bad Request — check your request format: {e.response.text}")
        elif status >= 500:
            print(f"  [ERROR] {status} Server Error — the API is having problems.")
        else:
            print(f"  [ERROR] HTTP {status}: {e.response.text}")
        return None


# ============================================================
# PART 5: Real Mistral API — Error Handling in Practice
# ============================================================
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"


async def call_mistral_safely(prompt: str, api_key: str) -> str | None:
    """Call Mistral with full error handling."""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "mistral-small-latest",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 200,
    }

    result = await safe_api_call(MISTRAL_API_URL, headers, payload)

    if result is None:
        return None

    # Even if we got a response, protect against unexpected structure
    try:
        return result["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        print(f"  [ERROR] Unexpected response format: {e}")
        print(f"  Full response: {result}")
        return None


async def test_with_bad_key():
    """Demonstrate what happens with a wrong API key."""
    print("--- Test: Wrong API Key ---")
    result = await call_mistral_safely("Hello!", "wrong-key-123")
    if result is None:
        print("  Handled gracefully — no crash!\n")


async def test_with_real_key():
    """Call Mistral with real key if available."""
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("--- Test: Real API Call ---")
        print("  [SKIPPED] Set MISTRAL_API_KEY in .env to run this test.\n")
        return

    print("--- Test: Real API Call ---")
    reply = await call_mistral_safely(
        "En une phrase, qui était Hannibal Barca de Carthage ?", api_key
    )
    if reply:
        print(f"  Mistral: {reply}\n")


# ============================================================
# PART 6: The finally Block — Cleanup Always Runs
# ============================================================
async def show_finally_block():
    """Demonstrate that finally always runs, success or failure."""
    print("=== The finally Block ===\n")

    for should_fail in [False, True]:
        url = "https://httpbin.org/status/500" if should_fail else "https://httpbin.org/get"
        print(f"  Calling URL (will {'fail' if should_fail else 'succeed'})...")
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(url)
                response.raise_for_status()
                print("  ✓ Request succeeded")
        except httpx.HTTPStatusError as e:
            print(f"  ✗ Request failed: HTTP {e.response.status_code}")
        finally:
            # This ALWAYS runs — perfect for cleanup, logging, closing resources
            print("  [finally] Cleanup done (always runs)\n")


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    show_the_problem()
    basic_try_except_demo()

    asyncio.run(handle_http_errors())

    print("=== Safe API Caller ===\n")
    asyncio.run(test_with_bad_key())
    asyncio.run(test_with_real_key())

    asyncio.run(show_finally_block())

    print("--- Key Takeaways ---")
    print("1. Always wrap API calls in try/except — never let them crash raw")
    print("2. Catch SPECIFIC errors first (TimeoutException, ConnectError, HTTPStatusError)")
    print("3. response.raise_for_status() converts 4xx/5xx into catchable exceptions")
    print("4. HTTP 401 = bad key | 429 = rate limited | 500 = server problem")
    print("5. finally: block always runs — use it for cleanup and logging")
    print("6. Return None on error, let the caller decide what to do")
