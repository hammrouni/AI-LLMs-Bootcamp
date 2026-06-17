"""
02 - Prompt Templates Demo
==========================
Compares a sloppy prompt vs a strict grounding prompt on the same context,
and shows the difference in hallucination behavior.

HOW TO RUN THIS FILE:
1. pip install mistralai python-dotenv
2. Copy ../.env.example to ../.env and add your MISTRAL_API_KEY
3. python demo.py
"""

import os
from dotenv import load_dotenv

load_dotenv()


CONTEXT_CHUNKS = [
    ("refunds.txt", (
        "Our refund policy is generous. Customers on the Pro plan can request a refund "
        "within 14 days of purchase, no questions asked. To start a refund, contact "
        "Yasmine Ben Ali, the head of customer success. Refunds are processed within 5 "
        "business days back to the original payment method."
    )),
    ("products.txt", (
        "MASTER Soft builds three products: a CRM platform, a billing API, and a mobile "
        "app builder. The CRM platform is the company's flagship product, used by over "
        "500 businesses across Tunisia."
    )),
    ("hours.txt", (
        "Working hours are 9:00 to 18:00 Monday to Friday, with a 1-hour lunch break that can "
        "be split. Remote work is allowed up to 2 days per week with manager approval. "
        "Khaled leads the engineering team, based in the Sousse office."
    )),
]


SLOPPY_PROMPT_USER = """Answer this question: {question}

Here is some context:
{context}
"""

STRICT_SYSTEM = """You are a helpful assistant for MASTER Soft.

RULES:
- Answer ONLY using the provided context.
- Do not use outside knowledge, even if you think you know the answer.
- If the answer is not in the context, reply exactly: "I don't know based on the documents I have."
- Be concise (1–3 sentences).
- End every answer with citations in the format [source: filename].

LANGUAGE:
- Answer in the same language as the question.
"""

STRICT_USER = """Context:
{context}

Question: {question}"""


def format_context(chunks):
    return "\n\n".join(f"[{src}] {text}" for src, text in chunks)


# ============================================================
# PART 1: The Problem — Sloppy Prompt Hallucinates
# ============================================================

def show_the_problem():
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("=== PART 1: SLOPPY PROMPT (API key required) ===")
        print("Set MISTRAL_API_KEY in codes/.env to run this section.\n")
        return

    try:
        from mistralai.client import Mistral
    except ImportError:
        print("Run: pip install mistralai")
        return

    print("=== PART 1: Sloppy Prompt = Hallucinations ===\n")

    client = Mistral(api_key=api_key)
    context = format_context(CONTEXT_CHUNKS)

    questions = [
        "What's the refund window for Pro plan customers?",     # in context
        "What's the SLA for the billing API?",                 # NOT in context -> hallucination
    ]

    print("Prompt template (no system message, no grounding rule):")
    print("-" * 60)
    print(SLOPPY_PROMPT_USER.strip())
    print("-" * 60)

    for q in questions:
        response = client.chat.complete(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": SLOPPY_PROMPT_USER.format(question=q, context=context)}],
        )
        answer = response.choices[0].message.content.strip()

        print(f"\nQ: {q}")
        print("-" * 60)
        for line in answer.split("\n"):
            print(f"  {line}")
        print("-" * 60)

    print("\nNo grounding rule -> LLM invents answers not in the context.\n")


# ============================================================
# PART 2: The Solution — Strict Grounding Prompt
# ============================================================

def show_the_solution():
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("=== PART 2: STRICT PROMPT (API key required) ===")
        print("Set MISTRAL_API_KEY in codes/.env to run this section.\n")
        return

    try:
        from mistralai.client import Mistral
    except ImportError:
        print("Run: pip install mistralai")
        return

    print("=== PART 2: Strict Grounding Prompt ===\n")

    client = Mistral(api_key=api_key)
    context = format_context(CONTEXT_CHUNKS)

    questions = [
        "What's the refund window?",                           # in context -> correct answer
        "What about returns for damaged goods?",               # NOT in context -> "I don't know"
    ]

    print("Strict prompt (system message with grounding rules):")
    print("-" * 60)
    print(STRICT_SYSTEM.strip())
    print("-" * 60)

    for q in questions:
        response = client.chat.complete(
            model="mistral-small-latest",
            messages=[
                {"role": "system", "content": STRICT_SYSTEM},
                {"role": "user",   "content": STRICT_USER.format(question=q, context=context)},
            ],
        )
        answer = response.choices[0].message.content.strip()

        print(f"\nQ: {q}")
        print("-" * 60)
        for line in answer.split("\n"):
            print(f"  {line}")
        print("-" * 60)

    print("\nWith grounding -> correct when in context, 'I don't know' when missing.\n")


# ============================================================
# PART 3: Side-by-Side Comparison — Sloppy vs Strict
# ============================================================

def real_world_example():
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("=== PART 3: SIDE-BY-SIDE (API key required) ===")
        print("Set MISTRAL_API_KEY in codes/.env to run this section.\n")
        return

    try:
        from mistralai.client import Mistral
    except ImportError:
        print("Run: pip install mistralai")
        return

    print("=== PART 3: Sloppy vs Strict — Side by Side ===\n")

    client = Mistral(api_key=api_key)
    context = format_context(CONTEXT_CHUNKS)

    questions = [
        "What's the refund window for Pro plan customers?",    # in context
        "What's the SLA for the billing API?",                 # NOT in context
        "Does MASTER Soft offer phone support?",               # NOT in context
    ]

    for q in questions:
        sloppy = client.chat.complete(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": SLOPPY_PROMPT_USER.format(question=q, context=context)}],
        ).choices[0].message.content.strip()

        strict = client.chat.complete(
            model="mistral-small-latest",
            messages=[
                {"role": "system", "content": STRICT_SYSTEM},
                {"role": "user",   "content": STRICT_USER.format(question=q, context=context)},
            ],
        ).choices[0].message.content.strip()

        print(f"Q: {q}")
        print(f"  SLOPPY: {sloppy}")
        print(f"  STRICT: {strict}")
        print()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    show_the_problem()
    show_the_solution()
    real_world_example()

    print("--- Key Takeaways ---")
    print("1. The grounding rule belongs in the system message.")
    print("2. Always include a fallback: 'I don't know based on the documents I have.'")
    print("3. Require citations in a fixed format like [source: filename].")
    print("4. Bound the answer length to keep responses focused.")
    print("5. Match the language of the question — works for FR / EN / AR.")
