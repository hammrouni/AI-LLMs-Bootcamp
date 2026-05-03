"""
04 - Token Usage & Cost Tracking Demo
======================================
Learn how to read token counts from API responses and track your spending.

HOW TO RUN:
    pip install httpx python-dotenv
    python demo.py

Get a free Mistral API key at: https://console.mistral.ai
Set MISTRAL_API_KEY in your .env file.
"""

import os
import asyncio
import httpx
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()

MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

# Mistral pricing (USD per 1M tokens — check current pricing)
MISTRAL_SMALL_INPUT_PRICE  = 0.20   # $ per 1M prompt tokens
MISTRAL_SMALL_OUTPUT_PRICE = 0.60   # $ per 1M completion tokens


# ============================================================
# PART 1: What Tokens Are (Simulated)
# ============================================================
def explain_tokens():
    """Explain tokens with concrete examples."""
    print("=== What Are Tokens? ===\n")

    examples = [
        ("Hello", 1),
        ("Hello world", 2),
        ("unbelievable", 4),
        ("What is the capital of Tunisia?", 8),
        ("Carthage was founded in 814 BC near modern-day Tunis.", 13),
    ]

    print("  Text → approximate token count:")
    for text, approx_tokens in examples:
        print(f"  '{text}' → ~{approx_tokens} tokens")

    print()
    print("  Rule of thumb: 1 token ≈ 4 characters ≈ 0.75 words")
    print("  Arabic/Chinese text uses MORE tokens per word than English.\n")


# ============================================================
# PART 2: The TokenTracker Class
# ============================================================
@dataclass
class RequestRecord:
    """Stores usage info for a single API call."""
    prompt: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    response_preview: str


@dataclass
class TokenTracker:
    """Tracks token usage and estimated cost across multiple API calls."""
    model: str = "mistral-small-latest"
    input_price_per_million: float = MISTRAL_SMALL_INPUT_PRICE
    output_price_per_million: float = MISTRAL_SMALL_OUTPUT_PRICE
    requests: list = field(default_factory=list)
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0

    def track(self, prompt: str, usage: dict, response_text: str):
        """Record token usage from an API response's 'usage' field."""
        prompt_tokens      = usage.get("prompt_tokens", 0)
        completion_tokens  = usage.get("completion_tokens", 0)
        total_tokens       = usage.get("total_tokens", prompt_tokens + completion_tokens)

        self.total_prompt_tokens     += prompt_tokens
        self.total_completion_tokens += completion_tokens

        record = RequestRecord(
            prompt=prompt[:60] + "..." if len(prompt) > 60 else prompt,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            response_preview=response_text[:80] + "..." if len(response_text) > 80 else response_text,
        )
        self.requests.append(record)
        return record

    @property
    def total_tokens(self) -> int:
        return self.total_prompt_tokens + self.total_completion_tokens

    @property
    def estimated_cost_usd(self) -> float:
        return (
            self.total_prompt_tokens     / 1_000_000 * self.input_price_per_million +
            self.total_completion_tokens / 1_000_000 * self.output_price_per_million
        )

    def print_summary(self):
        """Print a usage summary for the session."""
        print("\n=== Token Usage Summary ===\n")
        print(f"  Total requests:       {len(self.requests)}")
        print(f"  Prompt tokens:        {self.total_prompt_tokens:,}")
        print(f"  Completion tokens:    {self.total_completion_tokens:,}")
        print(f"  Total tokens:         {self.total_tokens:,}")
        print(f"  Estimated cost:       ${self.estimated_cost_usd:.6f}")
        print(f"  Cost per request:     ${self.estimated_cost_usd / max(len(self.requests), 1):.6f}")

        print("\n  Per-request breakdown:")
        for i, r in enumerate(self.requests, 1):
            print(f"  [{i}] '{r.prompt}'")
            print(f"      {r.prompt_tokens}p + {r.completion_tokens}c = {r.total_tokens} tokens")

        print()


# ============================================================
# PART 3: Simulated Usage (no API key needed)
# ============================================================
def simulate_token_tracking():
    """Simulate token tracking without a real API key."""
    print("=== Simulated Token Tracking ===\n")

    tracker = TokenTracker()

    # Simulate 3 API calls with fake usage data
    fake_calls = [
        {
            "prompt": "What is the capital of Tunisia?",
            "usage": {"prompt_tokens": 9, "completion_tokens": 7, "total_tokens": 16},
            "response": "The capital of Tunisia is Tunis.",
        },
        {
            "prompt": "Name 5 ancient Carthaginian generals.",
            "usage": {"prompt_tokens": 10, "completion_tokens": 45, "total_tokens": 55},
            "response": "1. Hannibal Barca 2. Hasdrubal 3. Hamilcar Barca 4. Mago 5. Himilco",
        },
        {
            "prompt": "Write a detailed history of the Aghlabid dynasty in Tunisia.",
            "usage": {"prompt_tokens": 13, "completion_tokens": 320, "total_tokens": 333},
            "response": "The Aghlabid dynasty ruled Ifriqiya (modern Tunisia) from 800 to 909 AD...",
        },
    ]

    for call in fake_calls:
        record = tracker.track(call["prompt"], call["usage"], call["response"])
        print(f"  Prompt: '{record.prompt}'")
        print(f"  Tokens: {record.prompt_tokens} prompt + {record.completion_tokens} completion = {record.total_tokens} total\n")

    tracker.print_summary()


# ============================================================
# PART 4: Real API Call With Token Tracking
# ============================================================
async def call_mistral_tracked(
    prompt: str,
    api_key: str,
    tracker: TokenTracker,
    max_tokens: int = 200,
) -> str | None:
    """Make a real Mistral API call and record token usage."""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "mistral-small-latest",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(MISTRAL_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        reply = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})

        record = tracker.track(prompt, usage, reply)
        print(f"  Q: {prompt}")
        print(f"  A: {reply[:120]}...")
        print(f"     [{record.prompt_tokens}p + {record.completion_tokens}c = {record.total_tokens} tokens]\n")
        return reply

    except httpx.HTTPStatusError as e:
        print(f"  [ERROR] HTTP {e.response.status_code}: {e.response.text[:100]}\n")
        return None
    except Exception as e:
        print(f"  [ERROR] {e}\n")
        return None


async def run_live_tracking():
    """Run multiple tracked calls and print a summary."""
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("=== Live Token Tracking ===\n")
        print("  [SKIPPED] Set MISTRAL_API_KEY in .env to run live examples.\n")
        return

    print("=== Live Token Tracking (Real API) ===\n")

    tracker = TokenTracker()

    prompts = [
        ("Qu'est-ce que Carthage ?", 80),
        ("Cite les 3 plus grandes villes de Tunisie.", 60),
        ("En 4 phrases, décris le désert du Sahara tunisien.", 150),
    ]

    for prompt, max_tokens in prompts:
        await call_mistral_tracked(prompt, api_key, tracker, max_tokens)

    tracker.print_summary()

    # Show scale: what would 10,000 calls/day cost?
    avg_tokens = tracker.total_tokens / max(len(tracker.requests), 1)
    daily_cost = tracker.estimated_cost_usd / max(len(tracker.requests), 1) * 10_000
    print(f"  Scale estimate: 10,000 calls/day at {avg_tokens:.0f} avg tokens ≈ ${daily_cost:.2f}/day\n")


# ============================================================
# PART 5: Cost Comparison — Long vs Short Prompts
# ============================================================
def compare_prompt_costs():
    """Show how prompt length affects cost."""
    print("=== Prompt Cost Comparison ===\n")

    # Sami is building a chatbot — let's see how his prompt style affects cost
    prompts = [
        ("Short",   "Capitale de la Tunisie ?", 6),
        ("Medium",  "Quelle est la capitale de la Tunisie ?", 9),
        ("Verbose", "Bonjour ! Je suis Sami, étudiant tunisien. Pourriez-vous s'il vous plaît me dire aimablement quel est le nom de la capitale de la Tunisie, ce magnifique pays d'Afrique du Nord ?", 42),
    ]

    print(f"  {'Style':<10} {'Prompt (truncated)':<50} {'Tokens':>7} {'Cost':>12}")
    print("  " + "-" * 82)
    for style, prompt, tokens in prompts:
        cost = tokens / 1_000_000 * MISTRAL_SMALL_INPUT_PRICE
        display = (prompt[:46] + "...") if len(prompt) > 46 else prompt
        print(f"  {style:<10} {display:<50} {tokens:>7} ${cost:>10.8f}")

    print()
    print("  Takeaway: Sami's verbose prompt costs 7x more for the exact same question.\n")


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    explain_tokens()
    simulate_token_tracking()
    compare_prompt_costs()
    asyncio.run(run_live_tracking())

    print("--- Key Takeaways ---")
    print("1. Every API response includes a 'usage' field with prompt/completion token counts")
    print("2. Track tokens in a class to accumulate session totals and estimate cost")
    print("3. Cost = (prompt_tokens / 1M * input_price) + (completion_tokens / 1M * output_price)")
    print("4. Completion tokens cost more than prompt tokens — keep answers focused")
    print("5. Verbose prompts waste money — be concise and direct")
    print("6. Use max_tokens to prevent runaway generation and surprise costs")
