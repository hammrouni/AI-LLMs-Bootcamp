"""
05 - Prompt Comparison & Quality Evaluation Demo
=================================================
Learn how to systematically compare prompts, score their outputs,
and iterate toward better, more reliable AI responses.

HOW TO RUN:
    pip install openai python-dotenv
    python demo.py

Set MISTRAL_API_KEY in a .env file to run live API examples.
Get a free key at: https://console.mistral.ai
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# HELPER: Call Mistral API
# ============================================================
def call_mistral(
    user_message: str,
    system_prompt: str | None = None,
    max_tokens: int = 300,
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
        return response.choices[0].message.content.strip()

    except ImportError:
        print("  Install with: pip install openai")
        return None
    except Exception as e:
        print(f"  [ERROR] {e}")
        return None


# ============================================================
# SCORING FRAMEWORK
# ============================================================
@dataclass
class PromptScore:
    format_compliance: int   # 1-5: does output match the required format?
    completeness: int        # 1-5: did it answer everything asked?
    conciseness: int         # 1-5: appropriately short, no filler?
    usability: int           # 1-5: can the output be used directly in code/display?

    @property
    def total(self) -> int:
        return self.format_compliance + self.completeness + self.conciseness + self.usability

    @property
    def max_score(self) -> int:
        return 20

    def display(self, label: str):
        print(f"  [{label}] Score: {self.total}/{self.max_score}")
        print(f"    Format:       {self.format_compliance}/5")
        print(f"    Completeness: {self.completeness}/5")
        print(f"    Conciseness:  {self.conciseness}/5")
        print(f"    Usability:    {self.usability}/5")


# ============================================================
# PART 1: Weak Prompt vs Strong Prompt — Side by Side
# ============================================================
def weak_vs_strong_demo():
    """Compare a vague prompt vs a specific, well-structured prompt."""
    print("=== PART 1: Weak Prompt vs Strong Prompt ===\n")

    article = """Tunis startup Cerbere.ai raised 2 million TND in seed funding last week.
The company, founded by three engineers from ENSI, is building an AI-powered fraud detection
system for Tunisian banks. They plan to hire 15 engineers and launch their first product
by Q3 2025. CEO Bilel Hamdi said: 'Tunisian banks lose over 50 million TND per year to fraud.'"""

    weak_prompt = f"Summarize this:\n\n{article}"

    strong_prompt = f"""Summarize this startup news in exactly 3 bullet points.
Each bullet must follow this format: **[Category]** — one sentence fact.
Categories to use: Funding, Product, Plans.
Under 60 words total. No preamble, no conclusion.

Article:
{article}"""

    print(f"  WEAK prompt: 'Summarize this: [article]'\n")
    print(f"  STRONG prompt: specifies format, structure, length, categories\n")

    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("  [SIMULATED — set MISTRAL_API_KEY to see real responses]\n")

        weak_sim = ("Cerbere.ai, a Tunisian startup founded by three ENSI engineers, recently raised 2 million TND "
                    "in seed funding. The company develops AI-powered fraud detection for Tunisian banks and plans "
                    "to hire 15 engineers, launching their first product in Q3 2025. CEO Bilel Hamdi highlighted "
                    "that Tunisian banks lose over 50 million TND annually to fraud.")
        strong_sim = ("**Funding** — Tunis startup Cerbere.ai raised 2M TND in seed funding.\n"
                      "**Product** — They are building AI-powered fraud detection for Tunisian banks.\n"
                      "**Plans** — 15 new hires planned and product launch targeted for Q3 2025.")

        print(f"  WEAK output:\n  '{weak_sim}'\n")
        print(f"  STRONG output:\n  '{strong_sim}'\n")

        weak_score = PromptScore(format_compliance=2, completeness=4, conciseness=2, usability=2)
        strong_score = PromptScore(format_compliance=5, completeness=5, conciseness=5, usability=5)
        weak_score.display("Weak")
        print()
        strong_score.display("Strong")
        print(f"\n  Improvement: +{strong_score.total - weak_score.total} points\n")
        return

    print("  WEAK prompt response:")
    weak_result = call_mistral(weak_prompt, max_tokens=200)
    if weak_result:
        print(f"  '{weak_result}'\n")

    print("  STRONG prompt response:")
    strong_result = call_mistral(strong_prompt, max_tokens=150)
    if strong_result:
        print(f"  '{strong_result}'\n")


# ============================================================
# PART 2: Iterative Improvement — Version by Version
# ============================================================
def iterative_improvement_demo():
    """Show how to improve a prompt across 3 iterations."""
    print("=== PART 2: Iterative Prompt Improvement ===\n")

    task_input = "Yasmine is a 28-year-old data scientist who has been feeling burned out lately. She works 10-hour days, skips lunch, and hasn't taken a vacation in 2 years. She's considering quitting her job."

    versions = [
        (
            "v1 — Vague",
            "Give advice.",
            "No role, no format, no constraint — model can output anything",
        ),
        (
            "v2 — Added role + topic",
            "You are a career coach. Give advice to someone feeling burned out.",
            "Better: has role and topic, but still no format or length constraint",
        ),
        (
            "v3 — Fully specified",
            """You are an empathetic career coach.
Read the situation and give practical advice in exactly 3 numbered steps.
Each step: one short sentence (under 20 words).
Tone: supportive and actionable, not generic platitudes.
End with one clarifying question for the person.""",
            "Best: role, format, length, tone, ending requirement — all specified",
        ),
    ]

    print(f"  Situation: '{task_input[:80]}...'\n")

    api_key = os.environ.get("MISTRAL_API_KEY")
    simulated = {
        "v1 — Vague": "It sounds like Yasmine is going through a tough time. Burnout is serious and she should take care of herself. Maybe she should talk to someone or take a break. It's important to find work-life balance.",
        "v2 — Added role + topic": "As a career coach, I'd first recommend that Yasmine immediately schedule some time off — even a long weekend makes a difference. She should also look at setting firmer boundaries around her working hours. The question of quitting deserves more reflection before acting.",
        "v3 — Fully specified": "1. Block one full weekend off this week — no laptop, no email.\n2. Set a hard stop time for work each day, starting tomorrow.\n3. Write down what specifically drains you most before deciding to quit.\n\nWhat part of your job still gives you energy, even a little?",
    }

    for version_name, system, description in versions:
        print(f"  [{version_name}]")
        print(f"  Description: {description}")

        if not api_key:
            output = simulated.get(version_name, "...")
        else:
            output = call_mistral(task_input, system_prompt=system, max_tokens=200)

        if output:
            preview = output[:120] + "..." if len(output) > 120 else output
            print(f"  Output: '{preview}'\n")

    if not api_key:
        print("  [SIMULATED — set MISTRAL_API_KEY to see real responses]\n")

    print("  Observation: v1 is generic, v2 is better but unstructured, v3 is immediately usable.\n")


# ============================================================
# PART 3: A/B Testing — Same Input, Multiple Prompt Variants
# ============================================================
def ab_testing_demo():
    """Run multiple prompt variants on the same inputs and compare."""
    print("=== PART 3: A/B Testing Prompt Variants ===\n")

    test_messages = [
        "My order hasn't arrived and it's been 2 weeks!",
        "I'd like to know if you offer discounts for bulk orders.",
        "Your website crashed when I was trying to checkout.",
    ]

    prompt_a = """You are a customer service agent.
Respond to the customer message."""

    prompt_b = """You are a friendly and empathetic customer service agent for an e-commerce company.
Rules:
- Acknowledge the customer's issue first (1 sentence).
- Offer a concrete next step (1 sentence).
- End with a reassurance (1 sentence).
Total: exactly 3 sentences. Professional and warm tone."""

    print("  Testing two prompt variants on 3 customer messages.\n")
    print("  Prompt A: generic instruction (no format, no tone, no structure)")
    print("  Prompt B: specific instruction (format, tone, structure, length)\n")

    api_key = os.environ.get("MISTRAL_API_KEY")

    simulated_a = [
        "I apologize for the delay. Please check your tracking information and contact us if you need more help.",
        "Yes, we do offer discounts for bulk orders. Please reach out to our sales team for more details.",
        "We're sorry to hear about this issue. Please try again or contact our technical support team.",
    ]
    simulated_b = [
        "I completely understand how frustrating a 2-week delay is, and I sincerely apologize. I'm escalating your order to our fulfillment team right now to investigate immediately. You will receive a full update by email within 24 hours — we will make this right.",
        "Thank you for considering bulk ordering with us! I'm connecting you with our B2B sales specialist who can discuss our volume discount tiers. You can expect a call within one business day, and we look forward to partnering with you.",
        "I'm so sorry the checkout crash caused you trouble — that should never happen. Our technical team has been notified and is investigating the issue right now. Please try again in 30 minutes, and if the problem persists, I'll personally process your order for you.",
    ]

    for i, message in enumerate(test_messages):
        print(f"  Message {i + 1}: '{message}'")

        if not api_key:
            result_a = simulated_a[i]
            result_b = simulated_b[i]
        else:
            result_a = call_mistral(message, system_prompt=prompt_a, max_tokens=100) or ""
            result_b = call_mistral(message, system_prompt=prompt_b, max_tokens=150) or ""

        print(f"  Prompt A: '{result_a[:90]}{'...' if len(result_a) > 90 else ''}'")
        print(f"  Prompt B: '{result_b[:90]}{'...' if len(result_b) > 90 else ''}'")
        print()

    if not api_key:
        print("  [SIMULATED — set MISTRAL_API_KEY to see real responses]\n")

    print("  Result: Prompt B consistently gives structured, empathetic, 3-sentence responses.\n")


# ============================================================
# PART 4: Common Failure Patterns — How to Diagnose Bad Prompts
# ============================================================
def failure_patterns_demo():
    """Show common AI output failures and what caused them."""
    print("=== PART 4: Common Prompt Failure Patterns ===\n")

    failures = [
        (
            "Output too long / no length control",
            "Explain machine learning.",
            "Add: 'Explain in exactly 2 sentences, for a 10-year-old.'",
        ),
        (
            "Wrong format (prose instead of list)",
            "What are the benefits of open source?",
            "Add: 'List exactly 4 benefits as bullet points. No prose.'",
        ),
        (
            "Off-topic / no scope constraint",
            "As a customer service agent, help this user.",
            "Add constraints: 'Only answer questions about our product. If asked about competitors, say: I can only help with our products.'",
        ),
        (
            "Inconsistent output structure",
            "Extract the key info from this text.",
            "Add: 'Return ONLY this JSON: {\"name\": ..., \"date\": ..., \"amount\": ...}'",
        ),
    ]

    for failure_name, bad_prompt_fragment, fix in failures:
        print(f"  Problem: {failure_name}")
        print(f"  Weak prompt: '{bad_prompt_fragment}'")
        print(f"  Fix: {fix}")
        print()


# ============================================================
# PART 5: The Prompt Improvement Checklist
# ============================================================
def improvement_checklist():
    """A practical checklist to run every prompt through before production."""
    print("=== PART 5: Prompt Quality Checklist ===\n")

    checklist = [
        ("Role defined?", "Is there a 'You are a ...' persona?"),
        ("Task is specific?", "Does the prompt say exactly what to do — not just 'help'?"),
        ("Format specified?", "Bullet points? JSON? Number of sentences? Markdown?"),
        ("Length bounded?", "Is there a word/sentence/token limit?"),
        ("Constraints set?", "What should the model NOT do? What's out of scope?"),
        ("Edge cases covered?", "What if the input is empty, off-topic, or ambiguous?"),
        ("Output testable?", "Can you check if the output is correct programmatically?"),
        ("Audience specified?", "Is the tone/complexity appropriate for the end user?"),
    ]

    print("  Run every production prompt through this checklist:\n")
    for i, (check, question) in enumerate(checklist, 1):
        print(f"  {i}. ✅ {check}")
        print(f"     → {question}")
    print()
    print("  A prompt that passes all 8 checks is production-ready.")
    print("  A prompt that fails 3+ is a bug waiting to happen.\n")


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    weak_vs_strong_demo()
    iterative_improvement_demo()
    ab_testing_demo()
    failure_patterns_demo()
    improvement_checklist()

    print("--- Key Takeaways ---")
    print("1. Prompt engineering is iterative — test, score, improve one weakness at a time")
    print("2. Score on 4 axes: format compliance, completeness, conciseness, usability")
    print("3. A/B test on the SAME inputs — never compare prompts across different inputs")
    print("4. Most common weaknesses: no format, no length limit, no constraints, no role")
    print("5. A strong prompt specifies: role + task + format + length + constraints")
    print("6. Use the 8-point checklist before shipping any prompt to production")
