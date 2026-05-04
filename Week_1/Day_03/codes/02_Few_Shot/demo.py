"""
02 - Few-Shot Learning Demo
============================
See how providing examples (shots) before your real question
dramatically improves the format, consistency, and accuracy of AI responses.

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
    max_tokens: int = 100,
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
# PART 1: 0-Shot vs 1-Shot vs 3-Shot — Sentiment Classification
# ============================================================
def shot_comparison_demo():
    """Compare 0-shot, 1-shot, and 3-shot for the same classification task."""
    print("=== PART 1: 0-Shot vs 1-Shot vs 3-Shot ===\n")

    new_review = "The couscous was decent but I had to wait forever for a table."
    print(f"  Target review: '{new_review}'\n")

    # 0-Shot
    prompt_0shot = f"""Classify this review as Positive, Negative, or Neutral.

Review: "{new_review}"
Classification:"""

    # 1-Shot
    prompt_1shot = f"""Classify reviews as Positive, Negative, or Neutral.

Review: "The tagine was excellent and the service was fast!"
Classification: Positive

Review: "{new_review}"
Classification:"""

    # 3-Shot
    prompt_3shot = f"""Classify reviews as Positive, Negative, or Neutral.

Review: "The tagine was excellent and the service was fast!"
Classification: Positive

Review: "Cold food, rude staff, would not return."
Classification: Negative

Review: "Prices are fair, food is okay, nothing memorable."
Classification: Neutral

Review: "{new_review}"
Classification:"""

    prompts = [
        ("0-Shot (no examples)", prompt_0shot),
        ("1-Shot (one example)", prompt_1shot),
        ("3-Shot (three examples)", prompt_3shot),
    ]

    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("  [SIMULATED — set MISTRAL_API_KEY to see real responses]\n")
        print("  0-Shot: 'Mixed'               ← inconsistent label, not in our set!")
        print("  1-Shot: 'Neutral'              ← uses our format now")
        print("  3-Shot: 'Neutral'              ← consistent, sees all three categories\n")
        return

    for label, prompt in prompts:
        print(f"  {label}:")
        result = call_mistral(prompt, max_tokens=20)
        if result:
            result_line = result.split("\n")[0]
            print(f"  Answer: {result_line}\n")


# ============================================================
# PART 2: Few-Shot for Format Transformation
# ============================================================
def format_transformation_demo():
    """Use few-shot to teach a specific output format."""
    print("=== PART 2: Few-Shot for Format Transformation ===\n")

    print("  Task: Convert free-text person descriptions into a consistent format.\n")

    prompt = """Convert each person description into the format: LASTNAME, Firstname (Age) — Role

Description: "Ahmed Ben Ali is 25 years old and works as a Software Engineer."
Formatted: BEN ALI, Ahmed (25) — Software Engineer

Description: "Fatima Zahra is 31, she's a doctor at the Tunis clinic."
Formatted: ZAHRA, Fatima (31) — Doctor

Description: "Karim Mansour, 28 years old, data scientist at a startup in Carthage."
Formatted: MANSOUR, Karim (28) — Data Scientist

Description: "Nour El Houda is 22 and just started her career as a graphic designer."
Formatted:"""

    print("  Giving the model 3 format examples, then asking for a new transformation.\n")

    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("  [SIMULATED — set MISTRAL_API_KEY to see real responses]\n")
        print("  Without examples: 'Nour El Houda, 22, Graphic Designer' ← wrong format")
        print("  With 3-shot:      'EL HOUDA, Nour (22) — Graphic Designer' ← perfect!\n")
        return

    print("  Without examples (0-shot):")
    zero_shot = call_mistral(
        'Convert to format "LASTNAME, Firstname (Age) — Role": "Nour El Houda is 22 and just started her career as a graphic designer."',
        max_tokens=50,
    )
    if zero_shot:
        print(f"  {zero_shot}\n")

    print("  With 3-shot examples:")
    few_shot = call_mistral(prompt, max_tokens=50)
    if few_shot:
        print(f"  {few_shot}\n")


# ============================================================
# PART 3: Few-Shot for Style Transfer
# ============================================================
def style_transfer_demo():
    """Teach the model a style via examples."""
    print("=== PART 3: Few-Shot for Style Transfer ===\n")

    print("  Task: Rewrite formal business messages in a friendly, casual Slack style.\n")

    prompt = """Rewrite formal messages in a casual, friendly Slack tone. Keep it short.

Formal: "We regret to inform you that the scheduled meeting has been postponed to Thursday."
Casual: "Hey team! Quick heads up — the meeting is moving to Thursday. 👍"

Formal: "Please be advised that your access credentials will expire within 24 hours."
Casual: "Reminder: your login expires tomorrow — renew it when you get a sec!"

Formal: "We are pleased to confirm receipt of your application and will be in touch shortly."
Casual: "Got your application! We'll get back to you soon. Thanks for applying! 🎉"

Formal: "Your request for additional resources has been approved pending budget confirmation."
Casual:"""

    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("  [SIMULATED — set MISTRAL_API_KEY to see real responses]\n")
        print("  Mistral (with 3-shot style examples):")
        print("  'Great news — your resource request got approved! Just waiting on budget sign-off. 🙌'\n")
        return

    result = call_mistral(prompt, max_tokens=80)
    if result:
        print(f"  Mistral: {result}\n")


# ============================================================
# PART 4: Choosing Good Examples — Quality vs Quantity
# ============================================================
def example_quality_demo():
    """Show that bad examples hurt performance."""
    print("=== PART 4: Example Quality Matters ===\n")

    # Genuinely ambiguous: "experimental menu replaced classics" is positive (innovation)
    # or negative (lost favorites) depending entirely on framing context.
    review_to_classify = "The new chef's experimental menu has replaced all the classic dishes."

    # Bad: 5 all-positive examples about menu innovation — strongly biases toward Positive
    bad_prompt = f"""Classify restaurant reviews as Positive or Negative.

Review: "The new seasonal menu is a breath of fresh air — chef's creativity really shines!"
Classification: Positive

Review: "Loved the bold new flavors, every dish was a pleasant surprise!"
Classification: Positive

Review: "The chef's innovative approach made this the best dining experience of the year."
Classification: Positive

Review: "New dishes, new vibe — the kitchen is firing on all cylinders!"
Classification: Positive

Review: "The revamped menu showed real culinary ambition, we were blown away."
Classification: Positive

Review: "{review_to_classify}"
Classification:"""

    # Good: balanced — positives praise innovation, negatives criticize losing classics
    good_prompt = f"""Classify restaurant reviews as Positive or Negative.

Review: "The new seasonal menu is a breath of fresh air — chef's creativity really shines!"
Classification: Positive

Review: "They changed the menu and removed our favorite dishes — very disappointing."
Classification: Negative

Review: "Loved the bold new flavors, every dish was a pleasant surprise!"
Classification: Positive

Review: "The 'experimental' dishes were pretentious and too expensive for what they were."
Classification: Negative

Review: "New dishes, new vibe — the kitchen is firing on all cylinders!"
Classification: Positive

Review: "{review_to_classify}"
Classification:"""

    print(f"  Test review: '{review_to_classify}'\n")
    print("  BAD prompt: 5 examples, ALL Positive (menu innovation) → biases toward Positive")
    print("  GOOD prompt: 5 examples, balanced — negatives specifically criticize replacing classics\n")
    print("  Why binary (Positive/Negative only)? Removing 'Neutral' forces the model to")
    print("  choose a side, making the bias effect visible.\n")

    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("  [SIMULATED — set MISTRAL_API_KEY to see real responses]\n")
        print("  BAD  examples → model says: 'Positive'  ← biased! innovation framing wins")
        print("  GOOD examples → model says: 'Negative'  ← correct: classics replaced = loss\n")
        return

    print("  With BAD examples:")
    bad_result = call_mistral(bad_prompt, max_tokens=20)
    if bad_result:
        print(f"  Answer: {bad_result.split(chr(10))[0]}\n")

    print("  With GOOD examples:")
    good_result = call_mistral(good_prompt, max_tokens=20)
    if good_result:
        print(f"  Answer: {good_result.split(chr(10))[0]}\n")


# ============================================================
# PART 5: Few-Shot for Extracting Structured Data
# ============================================================
def structured_extraction_demo():
    """Use few-shot to extract data in a consistent structure."""
    print("=== PART 5: Few-Shot for Data Extraction ===\n")

    print("  Task: Extract product info from unstructured descriptions.\n")

    prompt = """Extract product info from descriptions. Use format: Name | Price (TND) | Category

Description: "Fresh organic olive oil from Sfax, 500ml bottle, selling at 18 dinars."
Extracted: Olive Oil (500ml) | 18 | Food

Description: "Traditional handwoven Berber carpet, 2x3 meters, available for 450 TND."
Extracted: Berber Carpet (2x3m) | 450 | Handicraft

Description: "Jasmine perfume made in Nabeul, 30ml, priced at 25 dinars."
Extracted: Jasmine Perfume (30ml) | 25 | Cosmetics

Description: "Authentic Tunisian harissa paste, 200g jar, costs 4.5 TND at the market."
Extracted:"""

    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("  [SIMULATED — set MISTRAL_API_KEY to see real responses]\n")
        print("  0-Shot: 'Harissa 200g - 4.5 TND'  ← inconsistent format")
        print("  3-Shot: 'Harissa Paste (200g) | 4.5 | Food'  ← matches our format perfectly!\n")
        return

    print("  With 3-shot examples:")
    result = call_mistral(prompt, max_tokens=50)
    if result:
        print(f"  Extracted: {result.split(chr(10))[0]}\n")


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    shot_comparison_demo()
    format_transformation_demo()
    style_transfer_demo()
    example_quality_demo()
    structured_extraction_demo()

    print("--- Key Takeaways ---")
    print("1. Few-shot = give examples before your real task — no model training needed")
    print("2. 0-shot works for well-known tasks; few-shot helps with custom formats/behaviors")
    print("3. Consistency is critical — use the exact same format in every example")
    print("4. Balance your examples — cover all categories you want the model to output")
    print("5. Bad examples are worse than no examples — they bias the model's output")
    print("6. 2-5 examples is usually enough; more examples = more tokens, diminishing returns")
