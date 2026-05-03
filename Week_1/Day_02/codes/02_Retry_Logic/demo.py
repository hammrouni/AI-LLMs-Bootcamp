"""
02 - Retry Logic Demo
=====================
Learn how to retry failed API calls intelligently using exponential backoff.

HOW TO RUN:
    pip install httpx python-dotenv tenacity
    python demo.py

For real Mistral API examples, set MISTRAL_API_KEY in .env
"""

import os
import time
import random
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()

MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"


# ============================================================
# PART 1: Naive Retry — The Wrong Way
# ============================================================
def naive_retry_example():
    """Shows naive retry — retries immediately with no delay."""
    print("=== Naive Retry (The Wrong Way) ===\n")

    attempt_count = 0

    for attempt in range(3):
        attempt_count += 1
        print(f"  Attempt {attempt_count}...")
        try:
            # Simulating a failure for the first 2 attempts
            if attempt < 2:
                raise ConnectionError("Simulated transient error")
            print("  ✓ Succeeded on attempt 3\n")
            break
        except ConnectionError as e:
            print(f"  ✗ Failed: {e} — retrying immediately (BAD!)")

    print("Problem: immediately hammering the server when it's struggling.\n")


# ============================================================
# PART 2: Manual Exponential Backoff
# ============================================================
def exponential_backoff_retry(func, max_attempts: int = 3, base_delay: float = 1.0):
    """
    Retry a function with exponential backoff.
    wait = base_delay * (2 ^ attempt) + random jitter
    """
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                print(f"  ✗ All {max_attempts} attempts failed. Giving up.")
                raise

            # Exponential wait + jitter
            wait = base_delay * (2 ** attempt) + random.uniform(0, 0.5)
            print(f"  ✗ Attempt {attempt + 1} failed: {e}")
            print(f"    Waiting {wait:.1f}s before retry...")
            time.sleep(wait)

    return None


def show_manual_backoff():
    """Demonstrate manual exponential backoff."""
    print("=== Manual Exponential Backoff ===\n")

    call_count = [0]  # use list so inner function can mutate it

    def flaky_function():
        call_count[0] += 1
        if call_count[0] < 3:
            raise ConnectionError(f"Simulated error on attempt {call_count[0]}")
        return "Success!"

    try:
        result = exponential_backoff_retry(flaky_function, max_attempts=4, base_delay=0.3)
        print(f"  ✓ Got result: {result}\n")
    except Exception as e:
        print(f"  Final error: {e}\n")


# ============================================================
# PART 3: Async Retry with httpx
# ============================================================
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


async def call_with_retry(
    url: str,
    headers: dict,
    payload: dict,
    max_attempts: int = 3,
    base_delay: float = 1.0,
) -> dict | None:
    """
    Async API caller with exponential backoff retry.
    Only retries transient errors (429, 5xx, timeouts).
    Immediately fails on permanent errors (401, 400, 404).
    """
    for attempt in range(max_attempts):
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(url, headers=headers, json=payload)

                # Permanent errors — don't retry
                if response.status_code in (400, 401, 403, 404, 422):
                    print(f"  [ERROR] HTTP {response.status_code} — permanent error, not retrying.")
                    return None

                # Transient errors — retry
                if response.status_code in RETRYABLE_STATUS_CODES:
                    raise httpx.HTTPStatusError(
                        f"Retryable error {response.status_code}",
                        request=response.request,
                        response=response,
                    )

                response.raise_for_status()
                return response.json()

        except httpx.TimeoutException:
            error_msg = "Request timed out"
        except httpx.ConnectError:
            error_msg = "Connection failed"
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}"

        if attempt == max_attempts - 1:
            print(f"  [ERROR] All {max_attempts} attempts failed. Last error: {error_msg}")
            return None

        wait = base_delay * (2 ** attempt) + random.uniform(0, 0.5)
        print(f"  [RETRY] Attempt {attempt + 1} failed ({error_msg}). Retrying in {wait:.1f}s...")
        await asyncio.sleep(wait)

    return None


# ============================================================
# PART 4: Simulate Transient Failures
# ============================================================
async def simulate_transient_failure():
    """Simulate an API that fails twice then succeeds."""
    print("=== Simulating Transient Failure ===\n")

    fail_count = [0]

    async def flaky_api_call():
        fail_count[0] += 1
        if fail_count[0] <= 2:
            # simulate a 503 from a busy server
            await asyncio.sleep(0.1)
            raise httpx.ConnectError("Simulated network blip")
        # third time works — Nour's chatbot finally gets its answer
        return {"answer": "La Tunisie compte 24 gouvernorats."}

    for attempt in range(3):
        try:
            result = await flaky_api_call()
            print(f"  ✓ Succeeded on attempt {attempt + 1}: {result}\n")
            break
        except httpx.ConnectError as e:
            wait = 0.3 * (2 ** attempt)
            print(f"  ✗ Attempt {attempt + 1} failed: {e} — waiting {wait:.1f}s")
            await asyncio.sleep(wait)


# ============================================================
# PART 5: Using tenacity (optional library approach)
# ============================================================
def show_tenacity_approach():
    """Show how tenacity makes retry logic declarative."""
    print("=== tenacity Library Approach ===\n")

    print("Instead of writing retry loops manually, tenacity lets you use decorators:\n")
    print("""
    from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(httpx.HTTPStatusError)
    )
    async def call_mistral(prompt: str) -> str:
        response = await client.post(MISTRAL_API_URL, ...)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    # tenacity handles the retry loop, backoff, and give-up logic automatically
    result = await call_mistral("What is the medina of Tunis?")
    """)

    try:
        import tenacity
        print("  tenacity is installed — you can use it now.")
    except ImportError:
        print("  Install with: pip install tenacity")
    print()


# ============================================================
# PART 6: Real Mistral Call with Retry
# ============================================================
async def call_mistral_with_retry(prompt: str) -> str | None:
    """Call Mistral API with retry logic."""
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("  [SKIPPED] Set MISTRAL_API_KEY in .env to run this section.\n")
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "mistral-small-latest",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 150,
    }

    print(f"  Prompt: {prompt}")
    result = await call_with_retry(MISTRAL_API_URL, headers, payload, max_attempts=3)

    if result:
        reply = result["choices"][0]["message"]["content"]
        print(f"  Mistral: {reply}")
        return reply

    return None


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    naive_retry_example()
    show_manual_backoff()

    asyncio.run(simulate_transient_failure())

    show_tenacity_approach()

    print("=== Real Mistral Call with Retry ===\n")
    asyncio.run(call_mistral_with_retry("Quelle est la plus ancienne ville de Tunisie ?"))

    print("\n--- Key Takeaways ---")
    print("1. Never retry immediately — use exponential backoff (wait doubles each time)")
    print("2. Add jitter (random delay) to avoid thundering herd problem")
    print("3. Only retry TRANSIENT errors: 429, 500, 503, timeouts, connection errors")
    print("4. NEVER retry permanent errors: 400, 401, 403, 404 (retrying won't help)")
    print("5. Always set a max_attempts limit — don't retry forever")
    print("6. tenacity library makes retry logic clean and declarative")
