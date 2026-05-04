# 04 - JSON Output (Structured Output)

---

## 📦 Packages

```bash
pip install openai python-dotenv pydantic
```

---

## The Problem with Unstructured Output

By default, an LLM returns **plain text**. That's fine for a chatbot that displays text, but terrible for an application that needs to **process the data**.

```python
# You ask the AI: "Extract the name, price, and category from this product description."
# The AI responds:
response = "The product is an olive oil. It costs 18 TND and belongs to the Food category."

# How do you get the price? String parsing? regex? This is fragile and brittle.
```

What you WANT:
```json
{
  "name": "Olive Oil",
  "price": 18,
  "category": "Food"
}
```

Now you can do `data["price"]` reliably — no parsing guesswork.

---

## Three Approaches to Get JSON

### Approach 1: Ask for JSON in the Prompt (simplest)

Just tell the model to output JSON in your user message or system prompt.

```python
prompt = """
Extract product info from this description and return ONLY a JSON object.
No explanation, no extra text — just the JSON.

Description: "Fresh olive oil from Sfax, 500ml, costs 18 TND, category: Food"

Return this exact structure:
{"name": "...", "price": ..., "category": "..."}
"""
```

**Pros:** Simple, works everywhere
**Cons:** Model might still add text before/after the JSON; you need to parse and clean

---

### Approach 2: JSON Mode (API-level enforcement)

Some APIs have a `response_format` parameter that forces JSON output at the API level.

```python
response = client.chat.completions.create(
    model="mistral-small-latest",
    messages=[...],
    response_format={"type": "json_object"},  # forces JSON output
)
```

**Pros:** Guaranteed valid JSON — no cleanup needed
**Cons:** Not all models/APIs support it; you still define the structure in the prompt

---

### Approach 3: Instructor Library (cleanest — seen in Day 01)

The `instructor` library wraps the OpenAI SDK and uses Pydantic models to enforce a schema:

```python
import instructor
from pydantic import BaseModel
from openai import OpenAI

class Product(BaseModel):
    name: str
    price: float
    category: str

client = instructor.from_openai(OpenAI(...))
product = client.chat.completions.create(
    model="mistral-small-latest",
    messages=[{"role": "user", "content": "..."}],
    response_model=Product,  # model MUST match this schema
)

print(product.name)   # type-safe!
print(product.price)  # validated!
```

**Pros:** Type-safe, auto-validated, retries on schema violations
**Cons:** Extra dependency, slightly more setup

---

## Designing a Good JSON Schema in Your Prompt

Tell the model EXACTLY what structure you expect. Be explicit:

```
Return ONLY a JSON object with this exact structure:
{
  "name": "string — product name",
  "price": "number — price in TND, no currency symbol",
  "category": "string — one of: Food, Handicraft, Cosmetics, Clothing",
  "in_stock": "boolean — true or false"
}

No markdown code blocks. No extra text. Only the JSON object.
```

Key rules:
1. Say what each field should contain (type + constraint)
2. For enums, list the valid values
3. Say "ONLY the JSON" explicitly — models love to add explanations
4. Say "No markdown code blocks" — models often wrap JSON in ```json ... ```

---

## Parsing and Validating JSON

Once you have the JSON string, parse and validate it:

```python
import json
from pydantic import BaseModel, ValidationError

class Product(BaseModel):
    name: str
    price: float
    category: str

raw_json = response_text  # e.g., '{"name": "Olive Oil", "price": 18, "category": "Food"}'

try:
    data = json.loads(raw_json)         # parse string → dict
    product = Product(**data)           # validate with Pydantic
    print(product.name, product.price)  # use safely
except json.JSONDecodeError:
    print("Model returned invalid JSON!")
except ValidationError as e:
    print(f"Schema mismatch: {e}")
```

---

## Cleaning Dirty JSON Output

Models sometimes wrap JSON in markdown:

```
```json
{"name": "Olive Oil", "price": 18}
```
```

Clean it before parsing:

```python
import re

def extract_json(text: str) -> str:
    """Strip markdown code blocks if present."""
    # Remove ```json ... ``` or ``` ... ``` wrappers
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        return match.group(1).strip()
    return text.strip()
```
