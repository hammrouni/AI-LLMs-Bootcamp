"""
02 - Context Management Demo
=============================
Demonstrates how to extract, organize, and maintain context in conversations.

HOW TO RUN THIS FILE:
1. python demo.py
"""

import re
from typing import Dict, List


# ============================================================
# PART 1: Basic Context Extraction
# ============================================================

def show_basic_extraction():
    """Demonstrate extracting facts from messages."""
    print("=== PART 1: Basic Context Extraction ===\n")

    class SimpleContextManager:
        def __init__(self):
            # A simple dict to hold all extracted facts.
            # Keys are fact types ("user_name"), values are the extracted strings.
            self.context = {}

        def extract_from_message(self, message):
            # re.search finds the FIRST match anywhere in the string.
            # The r"..." raw string prevents Python from interpreting backslashes.
            # (\w+) is a capture group matching one or more word characters.

            # Match "My name is <word>" — e.g. "My name is Bilel" → "Bilel"
            name_match = re.search(r"My name is (\w+)", message, re.IGNORECASE)
            if name_match:
                # .group(1) returns the first capture group — the actual name word.
                self.context['user_name'] = name_match.group(1)

            # Match "from <word>" — e.g. "I'm from Tunis" → "Tunis"
            location_match = re.search(r"from (\w+)", message, re.IGNORECASE)
            if location_match:
                self.context['location'] = location_match.group(1)

            # Match "work(s) in <word>" — e.g. "I work in tech" → "tech"
            profession_match = re.search(r"work[s]? in (\w+)", message, re.IGNORECASE)
            if profession_match:
                self.context['profession'] = profession_match.group(1)

        def get_context(self):
            return self.context

        def format_summary(self):
            lines = []
            for key, value in self.context.items():
                lines.append(f"{key}: {value}")
            # Return "No context extracted yet" when nothing was found,
            # so callers never get an empty string back.
            return "\n".join(lines) if lines else "No context extracted yet"

    ctx = SimpleContextManager()

    messages = [
        "Hi, my name is Bilel and I'm from Tunis",
        "I work in tech and love AI"
    ]

    for msg in messages:
        print(f'Processing: "{msg}"')
        ctx.extract_from_message(msg)

    print("\n--- Extracted Context ---")
    print(ctx.format_summary())
    print()


# ============================================================
# PART 2: Entity Memory (Tracking Multiple Facts)
# ============================================================

def show_entity_memory():
    """Demonstrate tracking entities and their attributes."""
    print("=== PART 2: Entity Memory ===\n")

    class EntityMemory:
        def __init__(self):
            # Nested dict structure: {entity_type: {entity_name: {attribute: value}}}
            # Example: {"product": {"Red Shirt": {"size": "M", "price": "$25"}}}
            # This lets us store many different entities of different types
            # without mixing them up.
            self.entities = {}

        def add_entity(self, entity_type, name):
            # Initialise a nested dict for this type if it doesn't exist yet.
            if entity_type not in self.entities:
                self.entities[entity_type] = {}
            # Register the entity name with an empty attribute dict.
            self.entities[entity_type][name] = {}

        def set_attribute(self, entity_type, name, attribute, value):
            # Auto-create the entity if it wasn't added explicitly first.
            if entity_type not in self.entities:
                self.add_entity(entity_type, name)
            if name not in self.entities[entity_type]:
                self.entities[entity_type][name] = {}
            self.entities[entity_type][name][attribute] = value

        def get_entity_info(self, entity_type, name):
            # .get() with a default of {} avoids KeyError if the type/name doesn't exist.
            return self.entities.get(entity_type, {}).get(name, {})

        def format_all_entities(self):
            output = []
            for entity_type, entities in self.entities.items():
                output.append(f"\n{entity_type.upper()}:")
                for name, attrs in entities.items():
                    output.append(f"  {name}:")
                    for attr, val in attrs.items():
                        output.append(f"    - {attr}: {val}")
            return "\n".join(output)

    memory = EntityMemory()

    print("Simulating e-commerce conversation...\n")

    # Store product facts as they appear in the conversation
    memory.add_entity("product", "Red Shirt")
    memory.set_attribute("product", "Red Shirt", "size", "M")
    memory.set_attribute("product", "Red Shirt", "color", "Red")
    memory.set_attribute("product", "Red Shirt", "price", "$25")
    memory.set_attribute("product", "Red Shirt", "stock", "In Stock")

    # Store customer facts at the same time
    memory.add_entity("customer", "Yasmine")
    memory.set_attribute("customer", "Yasmine", "location", "Sfax")
    memory.set_attribute("customer", "Yasmine", "preference_color", "Red")
    memory.set_attribute("customer", "Yasmine", "size", "M")

    print("Customer asks: 'Do you have the red shirt in M?'")
    print("System extracts and remembers...\n")

    print(memory.format_all_entities())
    print()


# ============================================================
# PART 3: Conversation Summary (Compressing History)
# ============================================================

def show_conversation_summary():
    """Demonstrate creating summaries from long conversations."""
    print("=== PART 3: Conversation Summary ===\n")

    class ConversationSummarizer:
        def __init__(self):
            self.messages = []
            self.summary = None  # Will be populated by create_summary()

        def add_message(self, role, content):
            self.messages.append({"role": role, "content": content})

        def extract_key_facts(self):
            # Look for messages that contain action/intent words.
            # These are the messages most likely to contain decisions
            # that the AI should remember (preferences, requests, constraints).
            facts = []
            for msg in self.messages:
                content = msg['content']
                if any(word in content.lower() for word in ['want', 'need', 'prefer', 'ask', 'inquire']):
                    facts.append(content)
            return facts

        def create_summary(self):
            facts = self.extract_key_facts()
            if facts:
                # Truncate long facts to 60 chars to keep the summary compact.
                # The "..." signals to the reader that the original was longer.
                self.summary = "KEY FACTS:\n" + "\n".join(
                    [f"- {fact[:60]}..." if len(fact) > 60 else f"- {fact}" for fact in facts]
                )
            return self.summary

        def get_messages_for_api(self, include_recent=3):
            # Strategy: summary (compressed old context) + last N messages (fresh context).
            # This is cheaper than sending the full history while keeping quality high.
            context = ""
            if self.summary:
                context += self.summary + "\n\n"
            context += "RECENT MESSAGES:\n"
            # Negative index [-include_recent:] always gets the last N items safely,
            # even if there are fewer than N messages total.
            for msg in self.messages[-include_recent:]:
                context += f"{msg['role'].upper()}: {msg['content']}\n"
            return context

    summarizer = ConversationSummarizer()

    # Simulate a realistic e-commerce conversation
    conversation = [
        ("user", "Hi, I want to buy a laptop"),
        ("assistant", "What specs are you looking for?"),
        ("user", "I need something with 16GB RAM and SSD"),
        ("assistant", "Those are good specs for most work"),
        ("user", "What's the price range?"),
        ("assistant", "Laptops with those specs range from 2000DT to 3000DT"),
        ("user", "I prefer something under 1500DT"),
        ("assistant", "Let me show you options under 1500DT"),
        ("user", "Great! Which brand do you recommend?"),
        ("assistant", "Popular brands: Dell, Lenovo for that price range"),
    ]

    for role, content in conversation:
        summarizer.add_message(role, content)

    summary = summarizer.create_summary()
    print("Original conversation (10 messages)")
    print(f"Summary length: {len(summary)} characters\n")
    print(summary)
    print("\n--- What to Send to AI ---")
    # Only send the summary + 2 most recent messages, not all 10
    print(summarizer.get_messages_for_api(include_recent=2))
    print()


# ============================================================
# PART 4: Context State Machine
# ============================================================

def show_context_state_machine():
    """Demonstrate tracking conversation state and context changes."""
    print("=== PART 4: Conversation State ===\n")

    class ContextState:
        def __init__(self):
            # A state machine tracks WHERE in the conversation flow we are.
            # "greeting" → "problem_identification" → "solution_search" → "resolution"
            # Knowing the current state tells the AI what to do next.
            self.state = "greeting"
            self.context = {}        # All facts gathered so far
            self.state_history = []  # The path we took to get here (for debugging)

        def transition(self, new_state, context_update=None):
            # Save the current state before moving to the new one,
            # so we can see the full path: greeting → problem → solution → done
            self.state_history.append(self.state)
            self.state = new_state
            # Merge any new facts into the existing context dict.
            # dict.update() overwrites keys that already exist.
            if context_update:
                self.context.update(context_update)

        def get_state_info(self):
            return {
                "current_state": self.state,
                "context": self.context,
                "state_history": self.state_history,
            }

    state = ContextState()

    print("Customer service conversation flow:\n")

    # Walk through a customer service resolution flow step by step
    state.transition("greeting")
    print(f"1. State: {state.state}")

    state.transition("problem_identification", {"issue": "billing"})
    print(f"2. State: {state.state} | Context: {state.context}")

    state.transition("solution_search", {"account_id": "12345"})
    print(f"3. State: {state.state} | Context: {state.context}")

    state.transition("resolution", {"refund_issued": True})
    print(f"4. State: {state.state} | Context: {state.context}")

    print("\n--- Full State History ---")
    info = state.get_state_info()
    # Join history + current state with arrows to visualise the full path
    print(f"Transition path: {' → '.join(info['state_history'] + [info['current_state']])}")
    print()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    show_basic_extraction()
    show_entity_memory()
    show_conversation_summary()
    show_context_state_machine()

    print("--- Key Takeaways ---")
    print("1. Extract key facts from messages using patterns and rules")
    print("2. Organize facts into entities with attributes")
    print("3. Create summaries to compress long histories")
    print("4. Track conversation state to understand user intent")
    print("5. Send summary + recent messages, not entire history")
