"""
04 - JSON Output (Structured Output) Demo
==========================================
Learn how to force AI responses into JSON format so your code can
process the data reliably instead of parsing plain text.

HOW TO RUN:
    pip install openai python-dotenv pydantic
    python demo.py

Set MISTRAL_API_KEY in a .env file to run live API examples.
Get a free key at: https://console.mistral.ai
"""

import os
import json
import re
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# HELPER: Call Mistral API
# ============================================================
def call_mistral(
    user_message: str,
    system_prompt: str | None = None,
    max_tokens: int = 300,
    json_mode: bool = False,
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

        kwargs: dict = {
            "model": "mistral-small-latest",
            "messages": messages,
            "max_tokens": max_tokens,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = client.chat.completions.create(**kwargs)
        return response.choices[0].message.content.strip()

    except ImportError:
        print("  Install with: pip install openai")
        return None
    except Exception as e:
        print(f"  [ERROR] {e}")
        return None


# ============================================================
# HELPER: Clean JSON output (strip markdown wrappers)
# ============================================================
def extract_json(text: str) -> str:
    """Remove ```json ... ``` or ``` ... ``` wrappers if present."""
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        return match.group(1).strip()
    return text.strip()


# ============================================================
# PART 1: The Problem — Unstructured Output Breaks Code
# ============================================================
def show_the_problem():
    """Why plain text AI output is bad for code."""
    print("=== PART 1: The Problem with Unstructured Output ===\n")

    print("  You ask the AI: 'What is the price of olive oil?'")
    print("  AI says: 'The olive oil from Sfax costs about 18 TND per 500ml bottle.'\n")
    print("  Now how do you get the price as a number in your code?")
    print()
    print("  Option A: String parsing (FRAGILE):")
    bad_response = "The olive oil from Sfax costs about 18 TND per 500ml bottle."
    print(f"    text = '{bad_response}'")
    print("    price = float(text.split('costs about ')[1].split(' TND')[0])  # BREAKS easily!")
    print()

    # Show how this breaks
    try:
        price = float(bad_response.split("costs about ")[1].split(" TND")[0])
        print(f"    Got: {price}  ← works this time, but any phrasing change breaks it\n")
    except Exception:
        print("    CRASHED — string parsing is fragile!\n")

    print("  Option B: Ask for JSON (RELIABLE):")
    print("    {'product': 'Olive Oil', 'price': 18, 'unit': '500ml'}")
    print("    price = data['price']  ← always works, type-safe, predictable\n")


# ============================================================
# PART 2: Approach 1 — Ask for JSON in the Prompt
# ============================================================
def prompt_json_approach():
    """Simply ask for JSON in the prompt."""
    print("=== PART 2: Approach 1 — Ask for JSON in the Prompt ===\n")

    description = "Fresh organic olive oil from Sfax, 500ml bottle, selling at 18 TND. Category: Food."

    prompt = f"""Extract product info from this description.
Return ONLY a JSON object with this structure — no extra text, no markdown:
{{"name": "string", "price_tnd": number, "volume_ml": number, "category": "string"}}

Description: {description}"""

    print(f"  Input: '{description}'\n")
    print(f"  Prompt includes the exact JSON schema we want.\n")

    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("  [SIMULATED — set MISTRAL_API_KEY to see real responses]\n")
        simulated = '{"name": "Olive Oil", "price_tnd": 18, "volume_ml": 500, "category": "Food"}'
        print(f"  Raw response: {simulated}")
        try:
            data = json.loads(simulated)
            print(f"\n  Parsed successfully!")
            print(f"  Name: {data['name']}")
            print(f"  Price: {data['price_tnd']} TND")
            print(f"  Volume: {data['volume_ml']}ml")
            print(f"  Category: {data['category']}\n")
        except Exception as e:
            print(f"  Parse error: {e}\n")
        return

    raw = call_mistral(prompt, max_tokens=150)
    if not raw:
        return

    print(f"  Raw response: {raw}")
    clean = extract_json(raw)
    try:
        data = json.loads(clean)
        print(f"\n  Parsed successfully!")
        print(f"  Name: {data.get('name')}")
        print(f"  Price: {data.get('price_tnd')} TND")
        print(f"  Volume: {data.get('volume_ml')}ml")
        print(f"  Category: {data.get('category')}\n")
    except json.JSONDecodeError as e:
        print(f"  Parse error: {e}")
        print(f"  Tip: Model may have added text — use extract_json() to clean\n")


# ============================================================
# PART 3: Approach 2 — JSON Mode (API-Level Enforcement)
# ============================================================
def json_mode_approach():
    """Use response_format=json_object for guaranteed valid JSON."""
    print("=== PART 3: Approach 2 — JSON Mode (API-Level Enforcement) ===\n")

    print("  With json_mode=True, the API GUARANTEES valid JSON output.")
    print("  You still define the schema in the prompt — but no cleanup needed.\n")

    system = "You are a data extraction assistant. Always respond with valid JSON."
    prompt = """Extract info from this text and return JSON with keys:
"person", "city", "profession", "age"

Text: "Yasmine Ben Salem, a 29-year-old architect, has been working in Tunis for 5 years." """

    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("  [SIMULATED — set MISTRAL_API_KEY to see real responses]\n")
        simulated = '{"person": "Yasmine Ben Salem", "city": "Tunis", "profession": "Architect", "age": 29}'
        print(f"  Response (guaranteed JSON): {simulated}")
        data = json.loads(simulated)
        print(f"  person: {data['person']}, age: {data['age']}, city: {data['city']}\n")
        return

    raw = call_mistral(prompt, system_prompt=system, max_tokens=150, json_mode=True)
    if not raw:
        return

    print(f"  Response (guaranteed JSON): {raw}")
    try:
        data = json.loads(raw)
        print(f"  person: {data.get('person')}, age: {data.get('age')}, city: {data.get('city')}\n")
    except json.JSONDecodeError as e:
        print(f"  Unexpected parse error: {e}\n")


# ============================================================
# PART 4: Pydantic Validation — Catching Schema Mismatches
# ============================================================
def pydantic_validation():
    """Use Pydantic to validate that the JSON matches your schema."""
    print("=== PART 4: Pydantic Validation — Catching Schema Violations ===\n")

    try:
        from pydantic import BaseModel, ValidationError
    except ImportError:
        print("  Install with: pip install pydantic\n")
        return

    class Product(BaseModel):
        name: str
        price_tnd: float
        category: str
        in_stock: bool

    print("  Pydantic model: Product(name, price_tnd, category, in_stock)\n")

    # Good JSON
    good_json = '{"name": "Harissa Paste", "price_tnd": 4.5, "category": "Food", "in_stock": true}'
    # Bad JSON — wrong types
    bad_json = '{"name": "Harissa Paste", "price_tnd": "cheap", "category": "Food"}'

    test_cases = [
        ("Valid JSON", good_json),
        ("Invalid JSON (wrong types + missing field)", bad_json),
    ]

    for label, raw_json in test_cases:
        print(f"  Testing: {label}")
        print(f"  Input: {raw_json}")
        try:
            data = json.loads(raw_json)
            product = Product(**data)
            print(f"  ✓ Valid! name={product.name}, price={product.price_tnd} TND, in_stock={product.in_stock}\n")
        except json.JSONDecodeError as e:
            print(f"  ✗ Invalid JSON: {e}\n")
        except ValidationError as e:
            errors = e.errors()
            for err in errors:
                print(f"  ✗ Schema error — field '{err['loc'][0]}': {err['msg']}")
            print()


# ============================================================
# PART 5: Real Pipeline — Extract + Validate in One Flow
# ============================================================
def full_pipeline_demo():
    """Complete pipeline: prompt → JSON → validate → use."""
    print("=== PART 5: Full Pipeline — Extract, Parse, Validate, Use ===\n")

    try:
        from pydantic import BaseModel, ValidationError

        class EventInfo(BaseModel):
            event_name: str
            location: str
            date: str
            ticket_price_tnd: float | None

    except ImportError:
        print("  Install with: pip install pydantic\n")
        return

    descriptions = [
        "The Carthage International Festival will take place at the Roman Theatre of Carthage on July 15th, 2025. Tickets start at 25 TND.",
        "Free outdoor jazz concert at Belvedere Park, Tunis, this Saturday August 3rd.",
    ]

    system = "You are a data extraction assistant. Always respond with valid JSON only."

    for desc in descriptions:
        print(f"  Input: '{desc}'\n")

        prompt = f"""Extract event info from this text.
Return ONLY JSON with this structure (no markdown, no extra text):
{{"event_name": "string", "location": "string", "date": "string", "ticket_price_tnd": number or null}}

Text: {desc}"""

        api_key = os.environ.get("MISTRAL_API_KEY")
        if not api_key:
            if "Carthage" in desc:
                raw = '{"event_name": "Carthage International Festival", "location": "Roman Theatre of Carthage", "date": "July 15, 2025", "ticket_price_tnd": 25}'
            else:
                raw = '{"event_name": "Outdoor Jazz Concert", "location": "Belvedere Park, Tunis", "date": "August 3", "ticket_price_tnd": null}'
        else:
            raw = call_mistral(prompt, system_prompt=system, max_tokens=150, json_mode=True)

        if not raw:
            continue

        clean = extract_json(raw)
        try:
            data = json.loads(clean)
            event = EventInfo(**data)
            price_str = f"{event.ticket_price_tnd} TND" if event.ticket_price_tnd else "FREE"
            print(f"  ✓ {event.event_name}")
            print(f"    Location: {event.location}")
            print(f"    Date: {event.date}")
            print(f"    Tickets: {price_str}\n")
        except (json.JSONDecodeError, ValidationError) as e:
            print(f"  ✗ Failed to parse: {e}\n")

    if not os.environ.get("MISTRAL_API_KEY"):
        print("  [SIMULATED — set MISTRAL_API_KEY to see real responses]\n")


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    show_the_problem()
    prompt_json_approach()
    json_mode_approach()
    pydantic_validation()
    full_pipeline_demo()

    print("--- Key Takeaways ---")
    print("1. Plain text output is fragile for code — always prefer structured JSON")
    print("2. Approach 1: Ask for JSON in the prompt — simple, but add extract_json() cleanup")
    print("3. Approach 2: json_mode=True — API-guaranteed valid JSON, no cleanup needed")
    print("4. Say 'ONLY JSON, no markdown, no extra text' to avoid ```json ... ``` wrappers")
    print("5. Pydantic validates the schema — catches type mismatches and missing fields")
    print("6. Full pipeline: prompt → raw text → extract_json() → json.loads() → Pydantic")
