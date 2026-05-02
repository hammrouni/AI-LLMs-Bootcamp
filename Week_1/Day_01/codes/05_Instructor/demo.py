"""
05 - Instructor Demo
====================
Instructor forces LLMs to return perfectly structured data
that maps directly to your Pydantic models.

HOW TO RUN:
    pip install instructor "mistralai>=1.0.0,<2.0.0" python-dotenv
    (mistralai v2 conflicts with instructor 1.x — must use mistralai v1)
    Copy your .env file from 03_HTTPX or create one with MISTRAL_API_KEY=your_key

    You need a Mistral API key (free tier at https://console.mistral.ai):
    Set MISTRAL_API_KEY=your-key-here in your .env file

    python demo.py

NOTE: Part 1 and Part 2 show the PROBLEM and SOLUTION conceptually
      using simulated data (no API key needed).
      Part 3+ require a real Mistral API key.
"""

import os
import json
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# PART 1: The Problem — Raw AI Output is Just Text
# ============================================================
def show_the_problem():
    """Demonstrate why raw AI output is hard to work with."""
    print("=== THE PROBLEM: Raw AI Output ===\n")

    # This is what an AI model actually returns — just a string!
    raw_ai_response = """
    Based on the resume, the candidate is Bilel, aged 32,
    who has been working as a Senior Software Engineer at X
    for the past 4 years. His skills include Python, JavaScript,
    and machine learning. He is available for full-time roles.
    """

    print("AI returned this raw text:")
    print(raw_ai_response)

    print("Now how do you get 'name' from this? Parse it manually?")
    print("What if the AI says 'age thirty-two' next time instead of '32'?")
    print("This is FRAGILE and requires lots of manual code.\n")


# ============================================================
# PART 2: The Solution — Define a Schema, Get Objects Back
# ============================================================

# Step 1: Define what you WANT to get back (using Pydantic)
class CandidateProfile(BaseModel):
    full_name: str
    age: int
    current_job_title: str
    current_company: str
    years_of_experience: int
    skills: List[str]
    available_for_hire: bool


def show_the_solution():
    """Demonstrate how Instructor gives you clean objects."""
    print("=== THE SOLUTION: Structured Output ===\n")

    print("You define a schema (what you want):")
    print("""
    class CandidateProfile(BaseModel):
        full_name: str
        age: int
        current_job_title: str
        current_company: str
        years_of_experience: int
        skills: List[str]
        available_for_hire: bool
    """)

    # This is what Instructor would return (simulated without API key)
    simulated_result = CandidateProfile(
        full_name="Bilel",
        age=32,
        current_job_title="Senior Software Engineer",
        current_company="X",
        years_of_experience=4,
        skills=["Python", "JavaScript", "Machine Learning"],
        available_for_hire=True
    )

    print("With Instructor, you get back a clean Python object:")
    print(f"  Name: {simulated_result.full_name}")
    print(f"  Age: {simulated_result.age} (integer, not a string!)")
    print(f"  Job: {simulated_result.current_job_title}")
    print(f"  Company: {simulated_result.current_company}")
    print(f"  Skills: {simulated_result.skills} (a real Python list!)")
    print(f"  Available: {simulated_result.available_for_hire} (a real bool!)")
    print("\nNo manual parsing. No fragile string matching. Just clean data.")


# ============================================================
# PART 3: Real Instructor Usage (requires Mistral API key)
# ============================================================

# --- Define schemas for different use cases ---

class PersonInfo(BaseModel):
    """Extract basic info about a person."""
    name: str
    age: Optional[int] = None
    occupation: Optional[str] = None
    location: Optional[str] = None


class SentimentAnalysis(BaseModel):
    """Analyze the sentiment of a piece of text."""
    sentiment: str          # "positive", "negative", or "neutral"
    confidence: float       # 0.0 to 1.0
    key_emotions: List[str] # e.g., ["happy", "excited"]
    summary: str            # One sentence explanation


class CalendarEvent(BaseModel):
    """Extract a calendar event from natural language."""
    title: str
    date: str               # In YYYY-MM-DD format
    time: Optional[str] = None
    location: Optional[str] = None
    participants: List[str] = []
    duration_minutes: Optional[int] = None


def real_instructor_examples():
    """
    Real Instructor examples — REQUIRES Mistral API key.

    This function shows 3 real-world use cases:
    1. Extract person info from text
    2. Sentiment analysis
    3. Extract calendar event
    """

    # Check for API key
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("\n=== REAL INSTRUCTOR USAGE (API key required) ===")
        print("Set your MISTRAL_API_KEY in your .env file to run this section.")
        print("Example code is shown below:\n")
        show_instructor_code_examples()
        return

    try:
        import instructor
        from openai import OpenAI
    except ImportError:
        print("Install packages: pip install instructor openai")
        return

    # Use Mistral's OpenAI-compatible endpoint — avoids mistralai SDK version issues
    client = instructor.from_openai(
        OpenAI(api_key=api_key, base_url="https://api.mistral.ai/v1")
    )

    print("\n=== REAL INSTRUCTOR USAGE ===\n")

    # --- Example 1: Extract person info ---
    print("--- Example 1: Extract Person Info ---")

    text = "Dr. Sonia, 45, is a renowned cardiologist based in Tunis."

    person = client.chat.completions.create(
        model="mistral-small-latest",
        response_model=PersonInfo,  # This is the Instructor magic! Tell it what to return
        messages=[
            {"role": "user", "content": f"Extract the person information from this text: {text}"}
        ]
    )

    print(f"Input text: '{text}'")
    print(f"Extracted name: {person.name}")
    print(f"Extracted age: {person.age}")
    print(f"Extracted job: {person.occupation}")
    print(f"Extracted location: {person.location}\n")

    # --- Example 2: Sentiment Analysis ---
    print("--- Example 2: Sentiment Analysis ---")

    review = "I absolutely love this product! It changed my life and I recommend it to everyone!"

    sentiment = client.chat.completions.create(
        model="mistral-small-latest",
        response_model=SentimentAnalysis,
        messages=[
            {"role": "user", "content": f"Analyze the sentiment of this review: {review}"}
        ]
    )

    print(f"Review: '{review}'")
    print(f"Sentiment: {sentiment.sentiment}")
    print(f"Confidence: {sentiment.confidence:.0%}")
    print(f"Emotions: {sentiment.key_emotions}")
    print(f"Summary: {sentiment.summary}\n")

    # --- Example 3: Calendar Event Extraction ---
    print("--- Example 3: Calendar Event Extraction ---")

    message = "Let's have a team lunch on Friday May 10th at noon at Dar Zarrouk. Yasmine, Mehdi, and Nour will join."

    event = client.chat.completions.create(
        model="mistral-small-latest",
        response_model=CalendarEvent,
        messages=[
            {"role": "user", "content": f"Extract the calendar event from: {message}"}
        ]
    )

    print(f"Message: '{message}'")
    print(f"Event title: {event.title}")
    print(f"Date: {event.date}")
    print(f"Time: {event.time}")
    print(f"Location: {event.location}")
    print(f"Participants: {event.participants}")


def show_instructor_code_examples():
    """Show the code patterns without running them."""

    print("Pattern 1: Basic setup")
    print("""
    import instructor
    from mistralai import Mistral   # requires mistralai v1 (not v2!)
    from pydantic import BaseModel

    client = instructor.from_mistral(Mistral(api_key="your-key"))
    """)

    print("Pattern 2: Get structured output")
    print("""
    class PersonInfo(BaseModel):
        name: str
        age: int
        job: str

    # response_model= is the Instructor magic
    person = client.chat.completions.create(
        model="mistral-small-latest",
        response_model=PersonInfo,   # <-- tell Instructor what type to return
        messages=[
            {"role": "user", "content": "Extract info from: Karim is 30, a developer"}
        ]
    )

    # You get a PersonInfo object back — not a string!
    print(person.name)  # "Karim"
    print(person.age)   # 30 (integer!)
    print(person.job)   # "developer"
    """)

    print("Pattern 3: Instructor with Anthropic (Claude)")
    print("""
    import instructor
    import anthropic

    client = instructor.from_anthropic(anthropic.Anthropic(api_key="your-key"))

    person = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        response_model=PersonInfo,
        messages=[
            {"role": "user", "content": "Extract: Yasmine, 28, data scientist"}
        ]
    )

    print(person.name)  # "Yasmine"
    """)


# ============================================================
# PART 4: How Instructor Works Under the Hood
# ============================================================
def explain_instructor_internals():
    """Explain what Instructor does behind the scenes."""
    print("\n=== How Instructor Works (Under the Hood) ===\n")

    print("Step 1: You define a Pydantic model")
    print("   class PersonInfo(BaseModel): ...")
    print()

    print("Step 2: Instructor converts it to a JSON Schema")
    from pydantic import BaseModel as BM
    class PersonInfo(BM):
        name: str
        age: int
    schema = PersonInfo.model_json_schema()
    print(f"   Pydantic schema: {json.dumps(schema, indent=4)}")
    print()

    print("Step 3: Instructor tells the AI to fill in this schema exactly")
    print("   (Uses Mistral's 'function calling' or 'tool use' feature)")
    print()

    print("Step 4: AI returns JSON that matches the schema")
    print('   {"name": "Yasmine", "age": 30}')
    print()

    print("Step 5: Instructor validates with Pydantic and gives you the object")
    print("   person.name → 'Yasmine'")
    print("   person.age  → 30")
    print()

    print("If validation fails, Instructor automatically RETRIES with the error")
    print("message, asking the AI to fix its output. You never see failures!")


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    show_the_problem()
    show_the_solution()
    explain_instructor_internals()
    real_instructor_examples()

    print("\n--- Key Takeaways ---")
    print("1. Instructor wraps AI clients (Mistral, Anthropic, etc.)")
    print("2. response_model=YourModel tells it what to return")
    print("3. You always get a Pydantic object — never raw text")
    print("4. Instructor automatically retries if AI output is invalid")
    print("5. Pydantic defines the SHAPE, Instructor ENFORCES it")
