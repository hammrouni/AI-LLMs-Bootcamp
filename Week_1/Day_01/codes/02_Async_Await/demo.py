"""
02 - Async / Await Demo
========================
This file demonstrates the difference between synchronous (blocking)
and asynchronous (non-blocking) code.

HOW TO RUN:
    python demo.py
"""

import asyncio
import time


# ============================================================
# PART 1: The Synchronous (BLOCKING) problem
# ============================================================
# In sync code, each step must FINISH before the next one starts.
# While waiting, the program is completely frozen.

def fake_api_call_sync(name: str, wait_seconds: float) -> str:
    """Simulates a slow API call using time.sleep (BLOCKING)."""
    print(f"  [SYNC] Starting call: {name}")
    time.sleep(wait_seconds)  # Program is FROZEN here — does nothing
    print(f"  [SYNC] Finished call: {name}")
    return f"Result from {name}"


def run_sync_example():
    """Run all API calls one by one — SLOW."""
    print("\n=== SYNCHRONOUS (Blocking) ===")
    print("All calls run one by one. The program freezes between each.\n")
    start = time.time()

    # These run ONE AFTER ANOTHER — even though they could run together
    result1 = fake_api_call_sync("AI Model", wait_seconds=2)
    result2 = fake_api_call_sync("Database", wait_seconds=1)
    result3 = fake_api_call_sync("Weather API", wait_seconds=1.5)

    total = time.time() - start
    print(f"\nTotal time: {total:.1f} seconds")
    print("(Should be ~4.5 seconds — we waited for EACH one)")


# ============================================================
# PART 2: The Asynchronous (NON-BLOCKING) solution
# ============================================================
# With async, we START all the calls and then WAIT for ALL of them
# at the same time. The program never freezes.

async def fake_api_call_async(name: str, wait_seconds: float) -> str:
    """Simulates a slow API call using asyncio.sleep (NON-BLOCKING).

    The key difference:
    - time.sleep()  → freezes the WHOLE program
    - asyncio.sleep() → pauses only THIS function, others keep running
    """
    print(f"  [ASYNC] Starting call: {name}")
    await asyncio.sleep(wait_seconds)  # PAUSE here, but others can run!
    print(f"  [ASYNC] Finished call: {name}")
    return f"Result from {name}"


async def run_async_example():
    """Run all API calls at the same time — FAST."""
    print("\n=== ASYNCHRONOUS (Non-Blocking) ===")
    print("All calls start at the same time. We wait for all together.\n")
    start = time.time()

    # asyncio.gather() starts ALL tasks at the same time
    # and waits for ALL of them to finish
    results = await asyncio.gather(
        fake_api_call_async("AI Model", wait_seconds=2),
        fake_api_call_async("Database", wait_seconds=1),
        fake_api_call_async("Weather API", wait_seconds=1.5),
    )

    total = time.time() - start
    print(f"\nTotal time: {total:.1f} seconds")
    print("(Should be ~2 seconds — the slowest one, not the sum!)")
    print("Results:", results)


# ============================================================
# PART 3: Simple async function example
# ============================================================
# This is the most basic async pattern — what you will use
# when calling AI APIs like OpenAI or Anthropic.

async def ask_ai(question: str) -> str:
    """Simulates calling an AI API asynchronously."""
    print(f"\nSending to AI: '{question}'")
    print("Waiting for AI response... (non-blocking)")

    await asyncio.sleep(2)  # Simulates 2-second AI response time

    answer = f"AI answer to: {question}"
    print(f"Got response: '{answer}'")
    return answer


async def main_chatbot():
    """A simple async chatbot simulation."""
    print("\n=== Simple Async AI Call ===")

    # The 'await' keyword means:
    # "Start this, and come back when it's done — but don't block others"
    response = await ask_ai("What is Python?")
    print(f"Final answer: {response}")


# ============================================================
# PART 4: Key syntax patterns
# ============================================================

# PATTERN 1: Define an async function
async def my_async_function():
    return "I am async"

# PATTERN 2: Await another async function inside async function
async def caller():
    result = await my_async_function()  # wait for it
    return result

# PATTERN 3: Run the top-level async function
# asyncio.run() is ALWAYS the entry point — you call it once, at the top level
# asyncio.run(caller())


# ============================================================
# MAIN — Run all examples
# ============================================================
if __name__ == "__main__":
    # Run the SYNCHRONOUS example (slow)
    run_sync_example()

    # Run the ASYNCHRONOUS example (fast)
    # asyncio.run() is how you start any async program
    asyncio.run(run_async_example())

    # Run the simple chatbot example
    asyncio.run(main_chatbot())

    print("\n--- Key Takeaways ---")
    print("1. async def  = this function can be paused without blocking")
    print("2. await      = pause here and wait, but let others run")
    print("3. asyncio.run() = the starting point for any async program")
    print("4. asyncio.gather() = run multiple async tasks at the same time")
