"""
03 - System Prompts Demo
=========================
See how the system prompt completely changes AI behavior — same user question,
totally different answers depending on the role, constraints, and format you set.

HOW TO RUN:
    pip install openai python-dotenv
    python demo.py

Set MISTRAL_API_KEY in a .env file to run live API examples.
Get a free key at: https://console.mistral.ai
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# HELPER: Call Mistral API
# ============================================================
def call_mistral(
    user_message: str,
    system_prompt: str | None = None,
    max_tokens: int = 200,
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
# PART 1: No System Prompt vs With System Prompt
# ============================================================
def baseline_vs_system_prompt():
    """Show the dramatic difference a system prompt makes."""
    print("=== PART 1: No System Prompt vs With System Prompt ===\n")

    question = "How do I fix this error: 'list index out of range'?"

    system_tutor = """You are a Python tutor for beginners.
Explain errors in simple, encouraging language. Use analogies.
After explaining the cause, always show a short code example of the fix.
Keep your response under 150 words."""

    print(f"  User question: '{question}'\n")

    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("  [SIMULATED — set MISTRAL_API_KEY to see real responses]\n")
        print("  WITHOUT system prompt:")
        print("    'IndexError: list index out of range occurs when you try to access")
        print("     an index that doesn't exist in the list. Check your list length...'")
        print("    ← Generic, technical, no code example, no encouragement\n")
        print("  WITH system prompt (Python Tutor):")
        print("    'Great question! Think of a list like seats in a bus. If the bus has")
        print("     5 seats (0 to 4), asking for seat 10 causes this error! Here's a fix:\n")
        print("     my_list = [1, 2, 3]")
        print("     if len(my_list) > 0:  # check before accessing")
        print("         print(my_list[0])")
        print("    ← Friendly, analogy, concrete example - perfect for beginners!\n")
        return

    print("  WITHOUT system prompt:")
    result_no_system = call_mistral(question)
    if result_no_system:
        print(f"  {result_no_system}\n")

    print("  WITH 'Python Tutor' system prompt:")
    result_with_system = call_mistral(question, system_prompt=system_tutor)
    if result_with_system:
        print(f"  {result_with_system}\n")


# ============================================================
# PART 2: Same Question, Four Different Personas
# ============================================================
def persona_comparison():
    """Same question answered by 4 different AI personas."""
    print("=== PART 2: One Question, Four Personas ===\n")

    question = "What should I eat to stay healthy?"

    personas = [
        (
            "Nutritionist",
            """You are a certified nutritionist.
Give evidence-based dietary advice. Be specific and practical.
Format: 3-4 bullet points, max 120 words total.""",
        ),
        (
            "Personal Trainer",
            """You are an energetic personal trainer and fitness coach.
Focus on nutrition for performance and energy. Be motivating!
Keep it punchy — under 80 words.""",
        ),
        (
            "Grandmother",
            """You are a warm, traditional Tunisian grandmother who loves to cook.
Give advice based on traditional home cooking wisdom.
Be loving and reference real Tunisian foods. Under 100 words.""",
        ),
        (
            "Budget Chef",
            """You are a budget-conscious chef who helps people eat well for less money.
Focus on affordable, nutritious foods. Give practical shopping tips.
Under 100 words.""",
        ),
    ]

    print(f"  Question: '{question}'\n")

    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("  [SIMULATED — set MISTRAL_API_KEY to see real responses]\n")
        print("  Nutritionist: '• Prioritize vegetables and legumes • Choose whole grains over refined carbs • Limit processed foods and added sugar • Include healthy fats like olive oil'\n")
        print("  Personal Trainer: 'Fuel your gains! Load up on protein (eggs, chicken, legumes), complex carbs for energy, and don't skip healthy fats. Hydrate! Your body is a machine — feed it right! 💪'\n")
        print("  Grandmother: 'Yemmi, eat your couscous with vegetables! Fresh bread, olive oil, harissa, some lablabi in winter. Drink mint tea. Don't skip breakfast, habibti!'\n")
        print("  Budget Chef: 'Lentils, chickpeas, and eggs are your best friends — cheap, filling, and nutritious. Buy seasonal vegetables at the market. A bag of oats costs 2 TND and lasts a week!'\n")
        return

    for name, system in personas:
        print(f"  [{name}]:")
        result = call_mistral(question, system_prompt=system, max_tokens=150)
        if result:
            print(f"  {result}\n")


# ============================================================
# PART 3: Constraints — What the AI Must NOT Do
# ============================================================
def constraints_demo():
    """Show how constraints protect your app from unwanted behavior."""
    print("=== PART 3: Constraints — Restricting the AI ===\n")

    system_customer_service = """You are a customer service agent for TunisAir.

Your job: help customers with bookings, flight info, and baggage questions.

Constraints:
- ONLY answer questions about TunisAir. Never discuss competitors.
- If asked about competitors, respond: "I can only assist with TunisAir services."
- Never make up flight schedules or prices — say "Please check tunisair.com for current info."
- Always end your response by asking if there's anything else you can help with.

Tone: Professional, friendly, concise."""

    questions = [
        "What's your baggage allowance for economy class?",
        "Is Nouvelair cheaper than TunisAir for domestic flights?",
        "When does the Tunis-Paris flight depart?",
    ]

    print("  System prompt sets up a TunisAir customer service agent with strict constraints.\n")

    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("  [SIMULATED — set MISTRAL_API_KEY to see real responses]\n")
        for q in questions:
            print(f"  User: '{q}'")
        print()
        print("  Agent: 'Economy class allows 23kg checked baggage and 10kg carry-on. Is there anything else I can help you with?'")
        print()
        print("  Agent: 'I can only assist with TunisAir services. Is there anything else I can help you with?'  ← constraint works!")
        print()
        print("  Agent: 'For current departure schedules, please check tunisair.com. Is there anything else I can help you with?'  ← doesn't make up info")
        print()
        return

    for question in questions:
        print(f"  User: '{question}'")
        result = call_mistral(question, system_prompt=system_customer_service, max_tokens=100)
        if result:
            print(f"  Agent: '{result}'\n")


# ============================================================
# PART 4: Format Control via System Prompt
# ============================================================
def format_control_demo():
    """Use the system prompt to enforce a specific output format."""
    print("=== PART 4: Format Control ===\n")

    question = "What are the benefits of learning Python?"

    format_variants = [
        (
            "Paragraph style",
            "You are a helpful assistant. Answer in 2-3 connected sentences. No lists.",
        ),
        (
            "Bullet list style",
            "You are a helpful assistant. Always answer in exactly 4 bullet points. No prose.",
        ),
        (
            "One-liner style",
            "You are a helpful assistant. Answer in exactly ONE sentence. Nothing more.",
        ),
    ]

    print(f"  Same question: '{question}'\n")

    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("  [SIMULATED — set MISTRAL_API_KEY to see real responses]\n")
        print("  Paragraph: 'Python is beginner-friendly, widely used in AI and data science, and has a massive ecosystem of libraries. It runs everywhere and has one of the strongest job markets of any language.'")
        print()
        print("  Bullets:\n  • Easy to learn with clean, readable syntax\n  • Dominant in AI, data science, and automation\n  • Huge library ecosystem (NumPy, pandas, TensorFlow)\n  • High demand and great salary potential")
        print()
        print("  One-liner: 'Python is the most versatile and beginner-friendly language for AI, automation, and web development.'")
        print()
        return

    for style_name, system in format_variants:
        print(f"  [{style_name}]:")
        result = call_mistral(question, system_prompt=system, max_tokens=120)
        if result:
            print(f"  {result}\n")


# ============================================================
# PART 5: Anatomy of a Well-Built System Prompt
# ============================================================
def show_system_prompt_anatomy():
    """Show the structure of a production-quality system prompt."""
    print("=== PART 5: Anatomy of a Production System Prompt ===\n")

    example_system_prompt = """You are Leila, an AI assistant for a Tunisian e-commerce platform specializing in artisan handicrafts.

YOUR ROLE:
Help customers discover, choose, and purchase authentic Tunisian artisan products.

WHAT YOU CAN DO:
- Answer questions about products, materials, and origins
- Help customers choose gifts based on their budget and preferences
- Explain Tunisian crafting traditions (pottery, weaving, leather, etc.)

WHAT YOU CANNOT DO:
- Make up prices or stock availability — direct to the website for live info
- Discuss products outside Tunisian handicrafts
- Offer discounts or promotions not listed on the site

TONE:
Warm, knowledgeable, and proud of Tunisian culture. Use occasional words in Arabic/Darija to add authenticity, but keep responses mostly in the user's language.

FORMAT:
- Keep responses under 150 words
- When recommending products, always explain WHY it fits the customer's needs
- End with a helpful follow-up question to guide them further"""

    print("  A well-structured system prompt covers:\n")
    print("  ✓ IDENTITY: Who the AI is (name, purpose)")
    print("  ✓ CAPABILITIES: What it can do")
    print("  ✓ CONSTRAINTS: What it cannot do")
    print("  ✓ TONE: How it communicates")
    print("  ✓ FORMAT: How responses are structured\n")
    print("  Example system prompt:")
    print("  " + "-" * 60)
    for line in example_system_prompt.strip().split("\n"):
        print(f"  {line}")
    print("  " + "-" * 60 + "\n")


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    baseline_vs_system_prompt()
    persona_comparison()
    constraints_demo()
    format_control_demo()
    show_system_prompt_anatomy()

    print("--- Key Takeaways ---")
    print("1. System prompt = job description for the AI — set it once, shapes all responses")
    print("2. Cover four pillars: Role, Task, Constraints, Format")
    print("3. Constraints protect your app — tell the AI what it CANNOT do")
    print("4. Same question → completely different answers with different system prompts")
    print("5. Be specific — vague instructions ('be helpful') have no effect")
    print("6. Test edge cases — what happens when users ask something off-topic?")
