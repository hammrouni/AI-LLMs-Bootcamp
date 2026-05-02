"""
03 - HTTPX Demo
===============
This file shows how to make HTTP requests using httpx,
both synchronously and asynchronously.

HOW TO RUN:
    pip install httpx python-dotenv
    python demo.py

We use https://httpbin.org — a free public testing API.
It just echoes back what you send, perfect for learning.

For the real Mistral AI example (Part 5), get a free API key at:
    https://console.mistral.ai
Then set: MISTRAL_API_KEY=your_key_here
"""

import asyncio
import os
import time

import httpx
from dotenv import load_dotenv

load_dotenv()  # loads .env file into os.environ


# ============================================================
# PART 1: Synchronous HTTPX (same as requests, but modern)
# ============================================================
# This works exactly like 'requests' — simple and blocking.
# Use this for simple scripts where speed doesn't matter.

def sync_get_example():
    """Make a simple GET request (synchronous)."""
    print("=== Sync GET Request ===")

    # httpx.get() sends a GET request and WAITS for the response
    url = "https://httpbin.org/get"

    try:
        response = httpx.get(url, timeout=10)

        print(f"Status code: {response.status_code}")  # 200 = success
        print(f"Response type: {type(response)}")

        # Parse the JSON response
        data = response.json()
        print(f"Your IP address: {data.get('origin', 'unknown')}")
        print(f"URL called: {data.get('url', 'unknown')}")

    except httpx.TimeoutException:
        print("Request timed out!")
    except httpx.ConnectError:
        print("Could not connect to server!")


def sync_post_example():
    """Send data with a POST request (synchronous)."""
    print("\n=== Sync POST Request ===")

    url = "https://httpbin.org/post"

    # This is how you send data to an API (like asking an AI about Tunisia)
    payload = {
        "message": "What is the capital of Tunisia?",
        "user_id": 42,
        "model": "mistral-small-latest"
    }

    response = httpx.post(url, json=payload, timeout=10)
    data = response.json()

    print(f"Status: {response.status_code}")
    print(f"Data we sent: {data.get('json')}")  # httpbin echoes it back


# ============================================================
# PART 2: Using a Client (better for multiple requests)
# ============================================================
# Instead of calling httpx.get() each time (which opens/closes a connection),
# use a Client to reuse the connection — faster and more efficient.

def sync_client_example():
    """Use httpx.Client for multiple requests."""
    print("\n=== Sync Client (reusable connection) ===")

    # 'with' statement automatically closes the client when done
    with httpx.Client(timeout=10) as client:
        # Make multiple requests with the same client
        r1 = client.get("https://httpbin.org/get")
        r2 = client.get("https://httpbin.org/headers")

        print(f"Request 1 status: {r1.status_code}")
        print(f"Request 2 status: {r2.status_code}")
        print("Both requests used the same connection!")


# ============================================================
# PART 3: Async HTTPX — The AI Development Way
# ============================================================
# This is what you'll use in real AI apps.
# While waiting for the AI response, your app handles other things.

async def async_get_example():
    """Make an async GET request."""
    print("\n=== Async GET Request ===")

    # httpx.AsyncClient is the async version of httpx.Client
    async with httpx.AsyncClient(timeout=10) as client:
        # 'await' means: make the request, but don't block everything else
        response = await client.get("https://httpbin.org/get")

        data = response.json()
        print(f"Status: {response.status_code}")
        print(f"Your IP: {data.get('origin', 'unknown')}")


async def async_multiple_requests():
    """Make multiple async requests at the SAME TIME."""
    print("\n=== Multiple Async Requests (Parallel) ===")
    start = time.time()

    async with httpx.AsyncClient(timeout=10) as client:
        # asyncio.gather() runs ALL requests at the same time
        # Instead of waiting for each one, they all run in parallel
        responses = await asyncio.gather(
            client.get("https://httpbin.org/delay/1"),  # 1 second delay
            client.get("https://httpbin.org/delay/1"),  # 1 second delay
            client.get("https://httpbin.org/delay/1"),  # 1 second delay
        )

    total = time.time() - start
    statuses = [r.status_code for r in responses]
    print(f"3 requests done in {total:.1f}s (not 3s!)")
    print(f"All statuses: {statuses}")


# ============================================================
# PART 4: Headers and Authentication
# ============================================================
# When calling AI APIs, you always need to send an API key
# in the request headers. This is how you do it.

async def async_with_headers():
    """Send headers with requests (like an API key)."""
    print("\n=== Request with Headers ===")

    headers = {
        "Authorization": "Bearer your-api-key-here",  # This is how AI APIs work
        "Content-Type": "application/json",
        "X-Custom-Header": "tunisia-bootcamp-demo"
    }

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(
            "https://httpbin.org/headers",
            headers=headers
        )
        data = response.json()
        print("Headers we sent:")
        for key, value in data.get("headers", {}).items():
            print(f"  {key}: {value}")


# ============================================================
# PART 5: Real Mistral AI API Call
# ============================================================
# Mistral AI offers a free tier — perfect for learning without cost.
# API docs: https://docs.mistral.ai/api/
# Get your free key: https://console.mistral.ai

MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

async def call_mistral_api(prompt: str, api_key: str) -> str:
    """
    Call the Mistral AI chat API.
    Uses the same HTTP pattern as all other AI APIs (OpenAI-compatible format).
    """
    print("\n=== Real Mistral AI API Call ===")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Mistral uses the same request format as OpenAI — easy to switch!
    payload = {
        "model": "mistral-small-latest",  # free tier model
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 256,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(MISTRAL_API_URL, headers=headers, json=payload)

        if response.status_code != 200:
            print(f"Error {response.status_code}: {response.text}")
            return ""

        data = response.json()
        reply = data["choices"][0]["message"]["content"]
        print(f"Prompt : {prompt}")
        print(f"Mistral: {reply}")

        # Example of what a typical Mistral response looks like:
        # response = "The user's name is Yasmine, she is 30 years old, from Tunisia."
        return reply


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=== HTTPX Demo ===\n")

    # Synchronous examples
    sync_get_example()
    sync_post_example()
    sync_client_example()

    # Async examples — need asyncio.run()
    asyncio.run(async_get_example())
    asyncio.run(async_multiple_requests())
    asyncio.run(async_with_headers())

    # Real Mistral AI call — reads from .env file
    mistral_key = os.environ.get("MISTRAL_API_KEY", "")
    if mistral_key:
        asyncio.run(call_mistral_api("Name 3 famous tourist cities in Tunisia and one thing to see in each.", mistral_key))
    else:
        print("\n[Skipping Mistral call — set mistral_key var to enable]")

    print("\n--- Key Takeaways ---")
    print("1. httpx.get()           = simple sync request (like requests)")
    print("2. httpx.Client          = reusable sync connection")
    print("3. httpx.AsyncClient     = reusable ASYNC connection (use this for AI)")
    print("4. await client.get()    = non-blocking request")
    print("5. asyncio.gather()      = multiple requests at the same time")
    print("6. Mistral API           = free tier, OpenAI-compatible format")
