"""
01 - Chain of Thought (CoT) Demo
==================================
See how asking the AI to "think step by step" dramatically improves accuracy
on reasoning tasks — and when it's not worth the extra tokens.

HOW TO RUN:
    pip install openai python-dotenv
    python demo.py

Set MISTRAL_API_KEY in a .env file to run live API examples.
Get a free key at: https://console.mistral.ai
"""

import os
import time
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# HELPER: Call Mistral API
# ============================================================
def call_mistral(
    user_message: str,
    system_prompt: str | None = None,
    max_tokens: int = 400,
) -> str | None:
    """Call Mistral via OpenAI-compatible SDK. Returns None if no API key."""
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        return None

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url="https://api.mistral.ai/v1")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model="mistral-small-latest",
            messages=messages,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    except ImportError:
        print("  Install with: pip install openai")
        return None
    except Exception as e:
        print(f"  [ERROR] {e}")
        return None


# ============================================================
# PART 1: The Problem — Direct Answers Can Be Wrong
# ============================================================
def show_the_problem():
    """Demonstrate why direct answers fail on reasoning tasks."""
    print("=== PART 1: The Problem with Direct Answers ===\n")

    print("Consider this problem:")
    problem = "A bookstore sells 3 types of books. Fiction costs 12 TND, science costs 18 TND, and history costs 15 TND. Yasmine buys 2 fiction, 1 science, and 3 history books. She pays with a 100 TND bill. How much change does she get?"

    print(f"  Problem: {problem}\n")

    print("  WITHOUT Chain of Thought (direct answer):")
    print("  Prompt: 'Answer: [number] TND'")
    print()
    print("  The model might output: '19 TND' — and you have NO IDEA if it's right")
    print("  You can't verify it. You can't spot where it went wrong.")
    print()
    print("  WITH Chain of Thought:")
    print("  Prompt: 'Think step by step, then give the answer.'")
    print()
    print("  The model outputs:")
    print("    Step 1: Fiction: 2 × 12 = 24 TND")
    print("    Step 2: Science: 1 × 18 = 18 TND")
    print("    Step 3: History: 3 × 15 = 45 TND")
    print("    Step 4: Total: 24 + 18 + 45 = 87 TND")
    print("    Step 5: Change: 100 - 87 = 13 TND")
    print("    Answer: 13 TND")
    print()
    print("  Now you can CHECK each step. If step 3 were wrong, you'd catch it.\n")


# ============================================================
# PART 2: Zero-Shot CoT — Just Add "Think Step by Step"
# ============================================================
def zero_shot_cot_demo():
    """Show how a simple phrase activates step-by-step reasoning."""
    print("=== PART 2: Zero-Shot CoT — The Magic Phrase ===\n")

    problem = "If a train leaves Tunis at 08:00 and travels to Sousse at 90 km/h, and the distance is 135 km, what time does it arrive?"

    prompt_direct = f"{problem} Give only the arrival time."
    prompt_cot = f"{problem} Think step by step, then state the arrival time."

    print("  Same problem, two different prompts:\n")
    print(f"  DIRECT PROMPT:\n  '{prompt_direct}'\n")
    print(f"  COT PROMPT:\n  '{prompt_cot}'\n")

    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("  [SIMULATED — set MISTRAL_API_KEY to see real responses]\n")
        print("  DIRECT answer: '09:30'  ← you have to trust it blindly\n")
        print("  COT answer:")
        print("    Step 1: Time = Distance / Speed = 135 / 90 = 1.5 hours")
        print("    Step 2: 1.5 hours = 1 hour 30 minutes")
        print("    Step 3: Departure 08:00 + 1h30min = 09:30")
        print("    The train arrives at 09:30.\n")
        return

    print("  Calling Mistral — DIRECT prompt:")
    direct_answer = call_mistral(prompt_direct, max_tokens=50)
    if direct_answer:
        print(f"  {direct_answer}\n")

    print("  Calling Mistral — CoT prompt:")
    cot_answer = call_mistral(prompt_cot, max_tokens=200)
    if cot_answer:
        print(f"  {cot_answer}\n")


# ============================================================
# PART 3: Few-Shot CoT — Examples with Reasoning
# ============================================================
def few_shot_cot_demo():
    """Provide examples that include reasoning to set the pattern."""
    print("=== PART 3: Few-Shot CoT — Teaching the Reasoning Format ===\n")

    few_shot_prompt = """Solve each problem by showing your work clearly.

Example 1:
Q: Mehdi earns 800 TND/month and saves 15% of his salary. How much does he save per year?
A: Monthly savings = 800 × 0.15 = 120 TND. Annual savings = 120 × 12 = 1,440 TND. Mehdi saves 1,440 TND per year.

Example 2:
Q: A recipe makes 4 servings and needs 300g of semolina. How much semolina for 10 servings?
A: Per serving = 300 / 4 = 75g. For 10 servings = 75 × 10 = 750g. You need 750g of semolina.

Now solve:
Q: A café in the medina sells 45 coffees on Monday, 62 on Tuesday, and 38 on Wednesday. The café earns 2.5 TND per coffee. How much did the café earn in total over the 3 days?
A:"""

    print("  Prompt shows 2 examples with clear reasoning, then asks a new question.")
    print("  The model learns the format (show work → state answer) from examples.\n")

    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("  [SIMULATED — set MISTRAL_API_KEY to see real responses]\n")
        print("  Mistral's answer:")
        print("    Total coffees = 45 + 62 + 38 = 145 coffees.")
        print("    Total earnings = 145 × 2.5 = 362.5 TND.")
        print("    The café earned 362.5 TND over the 3 days.\n")
        return

    answer = call_mistral(few_shot_prompt, max_tokens=200)
    if answer:
        print(f"  Mistral: {answer}\n")


# ============================================================
# PART 4: CoT for Logic / Classification Tasks
# ============================================================
def cot_for_classification():
    """CoT improves complex classification, not just math."""
    print("=== PART 4: CoT for Complex Classification ===\n")

    text = "This product arrived late, the packaging was damaged, but the item itself works perfectly and customer support was responsive."

    prompt_direct = f'Classify this review as Positive, Negative, or Mixed: "{text}"'
    prompt_cot = f'Classify this review as Positive, Negative, or Mixed. Think through each aspect mentioned before giving your final classification.\n\nReview: "{text}"'

    print("  Review:", text)
    print()

    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("  [SIMULATED — set MISTRAL_API_KEY to see real responses]\n")
        print("  DIRECT: 'Mixed'  ← correct but we don't know why\n")
        print("  COT answer:")
        print("    - Delivery: negative (arrived late)")
        print("    - Packaging: negative (damaged)")
        print("    - Product quality: positive (works perfectly)")
        print("    - Customer support: positive (responsive)")
        print("    The review has both positive and negative aspects.")
        print("    Classification: Mixed\n")
        return

    print("  DIRECT prompt:")
    direct = call_mistral(prompt_direct, max_tokens=20)
    if direct:
        print(f"  {direct}\n")

    print("  COT prompt:")
    cot = call_mistral(prompt_cot, max_tokens=200)
    if cot:
        print(f"  {cot}\n")


# ============================================================
# PART 5: When NOT to Use CoT — Wasted Tokens
# ============================================================
def when_not_to_use_cot():
    """Some tasks don't benefit from CoT — it just wastes tokens."""
    print("=== PART 5: When NOT to Use CoT ===\n")

    simple_tasks = [
        ("What is the capital of Tunisia?", "Tunis"),
        ("Translate 'bonjour' to English.", "Hello"),
        ("What color is the sky?", "Blue"),
    ]

    print("  For simple factual questions, CoT adds NO value:\n")
    for question, expected in simple_tasks:
        print(f"  Q: {question}")
        print(f"  Direct answer: '{expected}'  ← perfect, done")
        print(f"  With CoT: 'Let me think... The capital of Tunisia is... Tunisia has a capital city... it is Tunis.' ← WASTE")
        print()

    print("  Rule: If you'd answer instantly without thinking, skip CoT.")
    print("  CoT is worth it only when the problem needs real reasoning.\n")


# ============================================================
# PART 6: Measuring CoT Impact (Token Cost)
# ============================================================
def measure_cot_cost():
    """Show the token tradeoff between CoT and direct answers."""
    print("=== PART 6: The Token Cost of CoT ===\n")

    print("  Approximate token counts for the bookstore problem from Part 1:\n")
    print("  ┌─────────────────────┬────────────────┬───────────────┐")
    print("  │ Approach            │ Response tokens│ Accuracy      │")
    print("  ├─────────────────────┼────────────────┼───────────────┤")
    print("  │ Direct answer       │ ~5 tokens      │ ~60-70%       │")
    print("  │ Zero-Shot CoT       │ ~80-120 tokens │ ~85-95%       │")
    print("  │ Few-Shot CoT        │ ~100-150 tokens│ ~90-98%       │")
    print("  └─────────────────────┴────────────────┴───────────────┘\n")
    print("  CoT uses ~15-30x more tokens — but accuracy jumps significantly.")
    print("  For a 2.5 TND math mistake, spending 0.001 TND extra on tokens is worth it.\n")


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    show_the_problem()
    zero_shot_cot_demo()
    few_shot_cot_demo()
    cot_for_classification()
    when_not_to_use_cot()
    measure_cot_cost()

    print("--- Key Takeaways ---")
    print("1. CoT = ask the model to show its reasoning before the final answer")
    print("2. Zero-Shot CoT: just add 'Think step by step' — no examples needed")
    print("3. Few-Shot CoT: give examples WITH reasoning to set the format")
    print("4. CoT helps most with: math, logic, multi-step reasoning, classification")
    print("5. Skip CoT for simple factual questions — it wastes tokens with no benefit")
    print("6. Bonus: CoT responses are auditable — you can spot where the model went wrong")
