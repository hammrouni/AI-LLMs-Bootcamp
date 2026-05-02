"""
04 - Pydantic Demo
==================
This file shows how Pydantic validates data and turns
raw text/dictionaries into proper Python objects.

HOW TO RUN:
    pip install pydantic
    python demo.py
"""

from pydantic import BaseModel, ValidationError, field_validator
from typing import Optional, List
from datetime import datetime


# ============================================================
# PART 1: The Problem Without Pydantic
# ============================================================
def without_pydantic():
    """This is what you have to do WITHOUT Pydantic — messy and error-prone."""
    print("=== WITHOUT Pydantic (the old painful way) ===\n")

    # Imagine this came from an AI model or a JSON API
    raw_data = {
        "name": "Yasmine",
        "age": "30",          # Problem: it's a STRING not a number!
        "email": "not-valid", # Problem: this isn't a real email!
        "score": -50          # Problem: scores shouldn't be negative!
    }

    # You have to manually validate EVERYTHING
    name = raw_data.get("name")
    if not name or not isinstance(name, str):
        print("Error: name is invalid")
        return

    try:
        age = int(raw_data.get("age", 0))  # Manually convert string to int
    except ValueError:
        print("Error: age must be a number")
        return

    if age < 0 or age > 150:
        print("Error: age out of range")
        return

    email = raw_data.get("email", "")
    if "@" not in email:  # Very basic email check (not even good)
        print(f"Warning: '{email}' doesn't look like a valid email")

    # ... and you still don't have a proper object!
    # You have separate variables floating around
    print(f"Name: {name}")
    print(f"Age: {age}")
    print("This is a lot of code for something simple!\n")


# ============================================================
# PART 2: Defining a Schema with Pydantic
# ============================================================
# A BaseModel is your schema blueprint.
# You just define the fields and their types.

class User(BaseModel):
    name: str              # Must be text
    age: int               # Must be a whole number
    email: str             # Must be text
    is_active: bool = True # Optional — defaults to True if not provided
    score: float = 0.0     # Optional — defaults to 0.0


class Product(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None  # Optional — can be None
    tags: List[str] = []               # Optional list, defaults to empty


def basic_pydantic_demo():
    """Create Pydantic models and access them like Python objects."""
    print("=== Basic Pydantic Model ===\n")

    # Create a User object — Pydantic validates automatically
    user = User(
        name="Yasmine",
        age=30,
        email="yasmine@example.tn",
        score=95.5
    )

    # Now you have a REAL Python object with attributes!
    print(f"Name: {user.name}")         # Attribute access
    print(f"Age: {user.age}")           # Already an integer
    print(f"Email: {user.email}")
    print(f"Active: {user.is_active}")  # Default value was used
    print(f"Score: {user.score}")
    print(f"Type of age: {type(user.age)}")  # <class 'int'>

    # Convert back to dictionary
    print(f"\nAs dict: {user.model_dump()}")

    # Convert to JSON string
    print(f"As JSON: {user.model_dump_json()}")


# ============================================================
# PART 3: Automatic Type Conversion
# ============================================================
def type_conversion_demo():
    """Pydantic automatically converts types when possible."""
    print("\n=== Automatic Type Conversion ===\n")

    # Notice: age is a STRING "30" but our schema says int
    # Pydantic will automatically convert it!
    user = User(
        name="Mehdi",
        age="30",           # String "30" → automatically becomes int 30
        email="mehdi@test.tn",
        is_active="true"    # String "true" → automatically becomes bool True
    )

    print(f"We passed age as string '30', got: {user.age} (type: {type(user.age).__name__})")
    print(f"We passed is_active as string 'true', got: {user.is_active} (type: {type(user.is_active).__name__})")
    print("Pydantic did the conversion automatically!")


# ============================================================
# PART 4: Validation Errors
# ============================================================
def validation_error_demo():
    """Pydantic catches invalid data and gives clear error messages."""
    print("\n=== Validation Errors ===\n")

    # Try to create a User with invalid data
    try:
        bad_user = User(
            name="Karim",
            age="not-a-number",  # Can't convert "not-a-number" to int!
            email="karim@test.tn"
        )
    except ValidationError as e:
        print("Caught a validation error!")
        print(f"Error details:\n{e}\n")

    # Missing required field
    try:
        incomplete_user = User(
            age=25
            # Missing 'name' and 'email' — both required!
        )
    except ValidationError as e:
        print("Caught missing fields error!")
        print(f"Error details:\n{e}\n")


# ============================================================
# PART 5: Custom Validators
# ============================================================
class StrictUser(BaseModel):
    name: str
    age: int
    email: str

    @field_validator("age")
    @classmethod
    def age_must_be_positive(cls, value):
        """Custom rule: age must be between 0 and 120."""
        if value < 0 or value > 120:
            raise ValueError(f"Age {value} is not realistic (must be 0-120)")
        return value

    @field_validator("email")
    @classmethod
    def email_must_have_at(cls, value):
        """Custom rule: email must contain @."""
        if "@" not in value:
            raise ValueError(f"'{value}' is not a valid email address")
        return value.lower()  # Also normalize to lowercase


def custom_validator_demo():
    """Show custom validation rules."""
    print("=== Custom Validators ===\n")

    # Valid data
    user = StrictUser(name="Nour", age=25, email="Nour@EXAMPLE.TN")
    print(f"Email normalized: {user.email}")  # dana@example.com (lowercased!)

    # Invalid age
    try:
        StrictUser(name="Amira", age=200, email="amira@test.tn")
    except ValidationError as e:
        print(f"\nAge validation caught: {e.errors()[0]['msg']}")

    # Invalid email
    try:
        StrictUser(name="Sami", age=30, email="not-an-email")
    except ValidationError as e:
        print(f"Email validation caught: {e.errors()[0]['msg']}")


# ============================================================
# PART 6: Nested Models (models inside models)
# ============================================================
class Address(BaseModel):
    street: str
    city: str
    country: str


class UserWithAddress(BaseModel):
    name: str
    age: int
    address: Address  # Nested model!


def nested_model_demo():
    """Models can contain other models."""
    print("\n=== Nested Models ===\n")

    user = UserWithAddress(
        name="Mariem",
        age=28,
        address={           # Pass a dict — Pydantic creates Address automatically
            "street": "Avenue Habib Bourguiba",
            "city": "Tunis",
            "country": "Tunisia"
        }
    )

    print(f"User: {user.name}")
    print(f"City: {user.address.city}")    # Nested attribute access!
    print(f"Country: {user.address.country}")
    print(f"Full object: {user.model_dump()}")


# ============================================================
# PART 7: Parsing AI Output (the real use case!)
# ============================================================
class ExtractedPersonInfo(BaseModel):
    """Schema for what we want to extract from AI output."""
    first_name: str
    last_name: str
    age: int
    job_title: str
    company: Optional[str] = None


def parse_ai_output_demo():
    """Simulate parsing structured data from an AI response."""
    print("\n=== Parsing AI Output ===\n")

    # Imagine this JSON came from an AI model (via Instructor — next lesson!)
    ai_returned_json = {
        "first_name": "Hamza",
        "last_name": "Trabelsi",
        "age": "35",           # AI returned a string, Pydantic converts it
        "job_title": "Software Engineer",
        "company": "TechCorp"
    }

    # Parse it into a proper Python object
    person = ExtractedPersonInfo.model_validate(ai_returned_json)

    print(f"Extracted name: {person.first_name} {person.last_name}")
    print(f"Age (as int): {person.age}")
    print(f"Job: {person.job_title} at {person.company}")
    print("\nNow you have a clean Python object — no manual parsing!")


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    without_pydantic()
    basic_pydantic_demo()
    type_conversion_demo()
    validation_error_demo()
    custom_validator_demo()
    nested_model_demo()
    parse_ai_output_demo()

    print("\n--- Key Takeaways ---")
    print("1. class MyModel(BaseModel)  = define your schema")
    print("2. field: type               = declare a required field")
    print("3. field: type = default     = declare an optional field")
    print("4. Pydantic auto-converts types (str '30' → int 30)")
    print("5. ValidationError           = clear error when data is wrong")
    print("6. model.model_dump()        = convert to dictionary")
    print("7. Model.model_validate(dict) = parse a dict into a model")
