# 04 - Pydantic (The Data Validator)

---

## What Does an AI Model Actually Return?

When you ask an AI model a question, what do you get back?

**You get a STRING. Plain text.**

```python
response = "The user's name is Yasmine, she is 30 years old, from Tunisia."
```

That's it. Just text. One long string.

**The Problem:**
- You can't do `response.name` — it's not an object, it's a string
- You don't know if the data is valid (what if the AI said "age: thirty" instead of 30?)
- You can't enforce structure — the AI might return anything
- Bugs are everywhere because you're parsing raw strings manually

---

## What is the Problem Without Pydantic?

Imagine you want to extract user info from AI output:

```python
# The AI returns this text:
ai_output = '{"name": "Yasmine", "age": "thirty", "email": "not-an-email"}'

# Without Pydantic — you parse it yourself
import json
data = json.loads(ai_output)
age = int(data["age"])  # CRASH! "thirty" is not an integer
email = data["email"]   # Invalid email but no error — silent bug
```

Problems:
- Wrong data types silently cause bugs
- Invalid data (bad email, negative age) gets through
- You write lots of manual validation code
- Error messages are confusing

---

## What is the Solution? Pydantic!

**Pydantic** lets you define WHAT your data should look like (a schema), and it automatically:
- Validates the data (is the age actually a number?)
- Converts types (turns "30" string into 30 integer)
- Gives clear error messages when data is wrong
- Turns raw data into a proper Python object with attributes

---

## What is a Schema?

A **schema** is a blueprint that describes the shape of your data.

Real world example:
- A form at the doctor's office is a schema
- It says: "Name (text), Age (number), Date of birth (date)"
- If you write "abc" in the age field, they reject it

In Python, a Pydantic schema is a class that says:
- "name must be a string"
- "age must be an integer"
- "email must look like an email"

---

## How to Define a Data Schema with Pydantic

```python
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    name: str          # must be text
    age: int           # must be a whole number
    email: str         # must be text (use EmailStr for email validation)
    is_active: bool = True  # optional, defaults to True
```

That's it! Now Pydantic enforces all those rules automatically.

---

## Why Pydantic + AI = Perfect Match

AI outputs text. Pydantic validates and structures that text into real Python objects.

```
AI Output (raw text) → Pydantic → Clean Python Object
   "name: Yasmine"    →  magic  →  user.name = "Yasmine"
   "age: 30"          →  magic  →  user.age = 30  (integer!)
```

You stop writing parsing code and start using clean data immediately.

---

## Installation

```bash
pip install pydantic
pip install pydantic[email]  # for email validation
```
