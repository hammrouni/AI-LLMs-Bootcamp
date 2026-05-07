"""
03 - System Prompts Demo
========================
Demonstrates how to design and use system prompts to shape AI personality.

HOW TO RUN THIS FILE:
1. python demo.py
"""

import json


# ============================================================
# PART 1: System Prompt Basics
# ============================================================

def show_system_prompt_basics():
    """Demonstrate the difference between system prompts."""
    print("=== PART 1: System Prompt Basics ===\n")

    # A vague prompt gives the model no constraints — it can respond however it wants.
    # Users get inconsistent, generic answers.
    bad_prompt = "You are a helpful assistant."

    # A specific prompt locks in personality, tone, examples, and domain knowledge.
    # The model behaves the same way across all conversations — predictable and branded.
    good_prompt = """
You are a Tunisian tech mentor named Nour.
- You love programming and teaching others
- You use Tunisian references naturally (places, names, food)
- You explain concepts clearly with real examples
- You're enthusiastic but not over-the-top
- You encourage students when they're stuck
- You ask questions to help them learn, not just give answers
"""

    print("--- BAD System Prompt ---")
    print(f'"{bad_prompt}"\n')
    print("Result: Generic, no personality, could be any AI\n")

    print("--- GOOD System Prompt ---")
    print(f'"""{good_prompt}"""\n')
    print("Result: Specific personality, memorable, consistent tone\n")


# ============================================================
# PART 2: Building System Prompts from Components
# ============================================================

def show_prompt_components():
    """Demonstrate building system prompts from modular parts."""
    print("=== PART 2: Building System Prompts ===\n")

    class SystemPromptBuilder:
        def __init__(self):
            # Each attribute holds one section of the final prompt.
            # Keeping them separate lets you update just one section
            # without rewriting the entire prompt string.
            self.role = None
            self.tone = None
            self.constraints = []   # Rules the AI must follow
            self.examples = []      # Input/output pairs that show desired behaviour

        def set_role(self, role_text):
            self.role = role_text
            # Return self so calls can be chained: builder.set_role(...).set_tone(...)
            return self

        def set_tone(self, tone_text):
            self.tone = tone_text
            return self

        def add_constraint(self, constraint):
            self.constraints.append(constraint)
            return self

        def add_example(self, input_text, output_text):
            # Few-shot examples are the most powerful part of a prompt.
            # They show the model exactly what a good answer looks like,
            # which is more effective than describing it in words.
            self.examples.append({"input": input_text, "output": output_text})
            return self

        def build(self):
            # Assemble the prompt by joining only the sections that were set.
            lines = []

            if self.role:
                lines.append(f"You are {self.role}.")

            if self.tone:
                lines.append(f"Your tone is {self.tone}.")

            if self.constraints:
                lines.append("\nConstraints:")
                for constraint in self.constraints:
                    lines.append(f"- {constraint}")

            if self.examples:
                lines.append("\nExamples:")
                for ex in self.examples:
                    lines.append(f"  Input: {ex['input']}")
                    lines.append(f"  Output: {ex['output']}")

            return "\n".join(lines)

    # Method chaining: each method returns self, so we can keep adding
    # sections in one fluent expression without intermediate variables.
    builder = SystemPromptBuilder()
    prompt = (builder
        .set_role("Bilel, a friendly Tunisian Python teacher")
        .set_tone("enthusiastic but clear, informal but professional")
        .add_constraint("Keep responses under 150 words")
        .add_constraint("Always use Tunisian names in examples")
        .add_constraint("Explain the WHY before the HOW")
        .add_example(
            "What's a list?",
            "A list is like a shopping list—you write items, and the order matters. In Python, you use [item1, item2]."
        )
        .add_example(
            "I'm stuck on loops",
            "You're close! Can you tell me: what do you want to repeat? How many times? Let's solve that together."
        )
        .build())

    print("Built System Prompt:")
    print(prompt)
    print()


# ============================================================
# PART 3: Different Personas and Their Prompts
# ============================================================

def show_different_personas():
    """Demonstrate how different personas require different prompts."""
    print("=== PART 3: Different Personas ===\n")

    # Each persona is a full prompt string.
    # Notice that the same product/service can have very different personalities
    # depending on the use case — same architecture, different system prompt.
    personas = {
        "Customer Support Bot": """
Role: Professional customer service representative
Tone: Empathetic, solution-focused, patient
Constraints:
- Always apologize for inconvenience
- Offer solutions within first response
- Escalate to human if unable to resolve
Examples:
  Customer: "Your app is broken!"
  Response: "I'm sorry you're having trouble. Let's fix this together. Can you tell me what happened?"
""",
        "Sales Assistant": """
Role: Enthusiastic Tunisian tech product specialist
Tone: Friendly, knowledgeable, slightly persuasive
Constraints:
- Highlight product benefits, not just features
- Never be pushy; respect customer's pace
- Mention Tunisian customers' success stories
Examples:
  Customer: "Is this expensive?"
  Response: "Great question! For Tunisian startups, it pays for itself in 3 months. Our partner Mehdi's startup saved 40 hours/month."
""",
        "Learning Mentor": """
Role: Patient Python mentor, expert at breaking complex topics down
Tone: Curious, encouraging, humble (willing to learn from students)
Constraints:
- Ask questions before giving answers
- Use Socratic method to guide discovery
- Celebrate progress
Examples:
  Student: "How do I make a game?"
  Response: "Awesome goal! Before we code, let's plan: What happens in your game? Who wins? Let's sketch that first."
""",
    }

    for persona_name, prompt in personas.items():
        print(f"--- {persona_name} ---")
        print(prompt)
        print()


# ============================================================
# PART 4: System Prompt in API Calls
# ============================================================

def show_prompt_in_api():
    """Demonstrate how system prompts are used in actual API calls."""
    print("=== PART 4: System Prompt in API Calls ===\n")

    class ChatWithSystemPrompt:
        def __init__(self, system_prompt):
            self.system_prompt = system_prompt
            self.conversation = []  # Grows with each user/assistant turn

        def send_message(self, user_message):
            # Build the full messages list that gets sent to the API.
            # Structure: [system, ...history, user_message]
            # The system message MUST come first so the model reads it
            # before any conversation content.
            messages = [
                {"role": "system", "content": self.system_prompt},
                *self.conversation,          # Unpack all previous turns
                {"role": "user", "content": user_message}
            ]
            # Save this user message so future turns include it in history.
            self.conversation.append({"role": "user", "content": user_message})

            # In real code, this calls mistral/openai and gets back a real response.
            simulated_response = f"[AI Response, guided by system prompt]"
            self.conversation.append({"role": "assistant", "content": simulated_response})

            return messages

    prompt = """
You are Yasmine, a Tunisian AI guide.
You're knowledgeable, warm, and love helping people understand technology.
You always mention Tunisian context when relevant.
You keep responses to 100 words max.
"""

    chat = ChatWithSystemPrompt(prompt)

    # Show exactly what JSON payload is sent to the API for one message
    messages = chat.send_message("What's an AI?")

    print("Messages sent to Mistral API:")
    # json.dumps with indent=2 pretty-prints the payload so it's easy to read.
    # ensure_ascii=False preserves Arabic or special characters if present.
    print(json.dumps(messages, indent=2, ensure_ascii=False))
    print("\n⚠️ NOTE: System prompt is always sent with every message!")
    print()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    show_system_prompt_basics()
    show_prompt_components()
    show_different_personas()
    show_prompt_in_api()

    print("--- Key Takeaways ---")
    print("1. System prompts define AI personality and behavior")
    print("2. Good prompts are specific, not generic")
    print("3. Build prompts from: role + tone + constraints + examples")
    print("4. System prompt is sent with EVERY API call")
    print("5. Different use cases need different personas")
