"""
05 - Chatbot Architecture Demo (Capstone)
==========================================
Complete working chatbot integrating buffer, context, prompts, and multi-turn.

HOW TO RUN THIS FILE:
1. pip install python-dotenv
2. Copy .env.example to .env and add your MISTRAL_API_KEY
3. python demo.py
"""

import os
from collections import deque
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# COMPONENT 1: Conversation Buffer
# ============================================================

class ConversationBuffer:
    """Stores all messages in chronological order."""

    def __init__(self, max_size=50):
        # deque with maxlen automatically drops the oldest message when full,
        # so memory usage stays constant no matter how long the chat runs.
        self.history = deque(maxlen=max_size)

    def add_message(self, role, content):
        # Each message is a dict with "role" and "content" —
        # the exact format expected by LLM APIs.
        self.history.append({"role": role, "content": content})

    def get_history(self):
        # Return a plain list so callers can index, iterate, and serialize it.
        return list(self.history)

    def format_for_api(self):
        # Explicitly pick only "role" and "content" — strips any extra fields
        # (like timestamps) that would break the API's strict message schema.
        return [{"role": msg["role"], "content": msg["content"]} for msg in self.history]

    def __len__(self):
        return len(self.history)


# ============================================================
# COMPONENT 2: Context Manager
# ============================================================

class ContextManager:
    """Extracts and tracks key facts from conversation."""

    def __init__(self):
        self.entities = {}    # Structured facts: {"user_name": "Bilel"}
        self.decisions = []   # Raw messages where the user expressed intent

    def extract_from_message(self, message):
        """Simple extraction: look for key patterns."""
        content = message.lower()

        # Extract name by finding "my name is" and taking the next word.
        if "my name is" in content:
            words = content.split()
            idx = words.index("is")
            if idx + 1 < len(words):
                # .capitalize() fixes casing: "bilel" → "Bilel"
                self.entities['user_name'] = words[idx + 1].capitalize()

        # Capture any message where the user states a preference or need.
        # We store the full message so no intent is lost in translation.
        if any(word in content for word in ["want", "need", "prefer", "choose"]):
            self.decisions.append(message)

    def get_summary(self):
        """Return extracted context as a summary."""
        summary = []
        if self.entities:
            summary.append("Known facts: " + ", ".join(f"{k}={v}" for k, v in self.entities.items()))
        if len(self.decisions) > 0:
            summary.append(f"User has made {len(self.decisions)} decision(s)")
        # Return empty string (not None) so callers can safely check `if summary`.
        return "\n".join(summary) if summary else ""


# ============================================================
# COMPONENT 3: System Prompt Manager
# ============================================================

class SystemPromptManager:
    """Manages chatbot personality and behavior."""

    def __init__(self, role="friendly assistant", tone="warm", constraints=None):
        self.role = role
        self.tone = tone
        # Use `or []` instead of a mutable default argument — mutable defaults
        # in Python are shared across all instances, which causes subtle bugs.
        self.constraints = constraints or []

    def get_system_prompt(self):
        # Build the system prompt string on demand.
        # Doing this lazily (rather than storing it) means changes to role/tone
        # are reflected the next time get_system_prompt() is called.
        prompt = f"You are a {self.role}.\n"
        prompt += f"Your tone is {self.tone}.\n"
        if self.constraints:
            prompt += "Constraints:\n"
            for constraint in self.constraints:
                prompt += f"- {constraint}\n"
        return prompt

    def set_personality(self, role, tone):
        # Allow changing personality mid-session.
        # The next call to get_system_prompt() will reflect the new values.
        self.role = role
        self.tone = tone


# ============================================================
# COMPONENT 4: Message Builder
# ============================================================

class MessageBuilder:
    """Builds the complete message list for API calls."""

    def __init__(self, system_prompt):
        self.system_prompt = system_prompt

    def build(self, buffer, include_context=None):
        """Build messages: system + context + history."""
        # System message is always first — the model reads it before anything else.
        messages = [{"role": "system", "content": self.system_prompt}]

        # If there is extracted context (names, decisions), inject it as a
        # second system message. This keeps it separate from user messages
        # so the model can distinguish "known facts" from "what the user said".
        if include_context:
            messages.append({
                "role": "system",
                "content": f"Context:\n{include_context}"
            })

        # Append the full conversation history after the system messages.
        # format_for_api() returns only {role, content} dicts — no extra fields.
        messages.extend(buffer.format_for_api())
        return messages


# ============================================================
# COMPONENT 5: Main Chatbot Orchestrator
# ============================================================

class CompleteChatbot:
    """Complete chatbot integrating all components."""

    def __init__(self, name="Ramy"):
        self.name = name
        # Each component is created independently — they don't know about each other.
        # The orchestrator (this class) is the only place that connects them.
        self.buffer = ConversationBuffer(max_size=50)
        self.context = ContextManager()
        self.prompt_mgr = SystemPromptManager(
            role=f"{name}, a friendly Tunisian AI assistant",
            tone="warm, helpful, mentions Tunisian context when relevant",
            constraints=[
                "Keep responses under 150 words",
                "Use Tunisian names naturally: Bilel, Yasmine, Mehdi",
                "Reference Tunisian places: Tunis, Sfax, Djerba, Sousse",
            ]
        )
        # Build the message builder once with the current system prompt.
        self.message_builder = MessageBuilder(self.prompt_mgr.get_system_prompt())
        self.turn_count = 0

    def process_user_input(self, user_input):
        """Main pipeline: input → buffer → context → output."""
        # Step 1: Validate — never send an empty message to the API
        if not user_input or not user_input.strip():
            return "Please enter a message."

        # Step 2: Store the user message in the buffer BEFORE calling the API,
        # so the full history (including this message) is available if needed.
        self.buffer.add_message("user", user_input)

        # Step 3: Extract entities/decisions from what the user said.
        # This runs on every turn so context builds up passively.
        self.context.extract_from_message(user_input)

        # Step 4: Build the final message list: system + context + history.
        # This is what gets sent to the API.
        context_summary = self.context.get_summary()
        messages = self.message_builder.build(self.buffer, context_summary)

        # Step 5: Call the API (simulated here; real code calls Mistral).
        response = self._simulate_api_call(user_input)

        # Step 6: Store the assistant's response so the next turn includes it.
        self.buffer.add_message("assistant", response)

        # Step 7: Track turns for analytics and display.
        self.turn_count += 1

        return response

    def _simulate_api_call(self, user_input):
        """Simulate what Mistral would respond."""
        # In real implementation, pass `messages` to mistral.Completions.create()
        # and return response.choices[0].message.content
        return f"[{self.name} simulates response to: {user_input[:40]}...]"

    def get_conversation_summary(self):
        """Return conversation for display."""
        lines = [f"\n=== {self.name}'s Conversation (Turn {self.turn_count}) ===\n"]
        for msg in self.buffer.get_history():
            lines.append(f"{msg['role'].upper()}: {msg['content']}")
        return "\n".join(lines)

    def reset(self):
        """Clear conversation for a fresh start."""
        # Re-create buffer and context from scratch rather than calling .clear()
        # so any subclass overrides of their constructors are respected.
        self.buffer = ConversationBuffer()
        self.context = ContextManager()
        self.turn_count = 0


# ============================================================
# PART 1: Basic Chatbot Demo
# ============================================================

def show_basic_chatbot():
    """Demonstrate the complete chatbot in action."""
    print("=== PART 1: Complete Chatbot Demo ===\n")

    chatbot = CompleteChatbot(name="Nour")

    print(f"Chatbot: {chatbot.name}")
    print(f"Personality: {chatbot.prompt_mgr.role}")
    print(f"Tone: {chatbot.prompt_mgr.tone}\n")

    # Run through a four-turn conversation — each turn builds on the last.
    user_messages = [
        "Hi, my name is Bilel",
        "I'm from Tunis and work in tech",
        "Can you help me learn Python?",
        "What's a list in Python?",
    ]

    for user_msg in user_messages:
        print(f"User: {user_msg}")
        response = chatbot.process_user_input(user_msg)
        print(f"Nour: {response}\n")

    print(chatbot.get_conversation_summary())
    print()


# ============================================================
# PART 2: Multi-Chatbot Comparison
# ============================================================

def show_different_personalities():
    """Demonstrate changing chatbot personality."""
    print("=== PART 2: Different Personalities ===\n")

    # Two chatbots, same class, different system prompts.
    # This shows that personality is configuration, not code.

    # Personality 1: Formal Support Bot
    support_bot = CompleteChatbot("Support")
    support_bot.prompt_mgr.set_personality(
        "professional customer support representative",
        "formal, solution-focused, empathetic"
    )

    print("Support Bot Response:")
    resp1 = support_bot.process_user_input("I have an issue with my account")
    print(f"  {resp1}\n")

    # Personality 2: Learning Mentor
    mentor = CompleteChatbot("Mentor")
    mentor.prompt_mgr.set_personality(
        "patient Python learning mentor",
        "encouraging, curious, humble"
    )

    print("Mentor Response:")
    resp2 = mentor.process_user_input("I'm confused about loops")
    print(f"  {resp2}\n")


# ============================================================
# PART 3: Error Handling & Robustness
# ============================================================

def show_error_handling():
    """Demonstrate graceful error handling."""
    print("=== PART 3: Error Handling & Edge Cases ===\n")

    chatbot = CompleteChatbot()

    # Test a range of pathological inputs to verify the chatbot doesn't crash.
    test_cases = [
        ("", "Empty input"),
        ("   ", "Whitespace only"),
        ("x" * 1000, "Very long input"),  # Stress-test the buffer and API payload
        ("Normal question", "Normal input"),
    ]

    for user_input, description in test_cases:
        print(f"Test: {description}")
        try:
            response = chatbot.process_user_input(user_input)
            # Truncate long responses to 50 chars so the output stays readable.
            print(f"  ✓ Response: {response[:50]}...\n")
        except Exception as e:
            print(f"  ✗ Error: {e}\n")


# ============================================================
# PART 4: State Tracking
# ============================================================

def show_state_tracking():
    """Demonstrate how the chatbot tracks state."""
    print("=== PART 4: State Tracking ===\n")

    chatbot = CompleteChatbot()

    # Three messages that each trigger context extraction.
    messages = [
        "My name is Yasmine",         # → entities['user_name'] = "Yasmine"
        "I prefer red color",          # → decisions list grows
        "I want a large size",         # → decisions list grows again
    ]

    for msg in messages:
        chatbot.process_user_input(msg)

    print("--- Extracted Context ---")
    context = chatbot.context.get_summary()
    if context:
        print(context)
    else:
        print("No context extracted yet")

    print(f"\n--- Conversation State ---")
    print(f"Total turns: {chatbot.turn_count}")
    print(f"Messages stored: {len(chatbot.buffer)}")      # 6 = 3 user + 3 assistant
    print(f"Decisions tracked: {len(chatbot.context.decisions)}")  # 2 (prefer + want)
    print()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("CHATBOT ARCHITECTURE DEMO")
    print("Complete working example integrating all concepts")
    print("=" * 60 + "\n")

    show_basic_chatbot()
    show_different_personalities()
    show_error_handling()
    show_state_tracking()

    print("--- Key Takeaways ---")
    print("1. Separate concerns: buffer, context, prompts, API calls")
    print("2. Components work together via an orchestrator (main chatbot)")
    print("3. Pipeline: validate → buffer → context → build → API → respond")
    print("4. Each component can be tested independently")
    print("5. Personality is easy to change without rewriting logic")
    print("6. State is tracked at every turn for consistency")
    print("7. Error handling at component level ensures robustness")
