"""
02 - Advanced Personality Design (Adaptive Personality)
========================================================
Demonstrates how to build ADAPTIVE personalities that change based on:
1. User communication style (technical vs casual, detailed vs brief)
2. Conversation context (support vs learning vs creative)
3. User feedback and preferences

CONTRAST: Day 06 uses STATIC personality (same prompt for all)
          Day 07 uses ADAPTIVE personality (prompt changes per user/context)

HOW TO RUN THIS FILE:
1. python demo.py
"""


# ============================================================
# PART 1: Detect User Communication Style
# ============================================================

class PersonalityAdapter:
    """Detects user's communication style from their messages."""

    def __init__(self):
        self.user_style = {
            "is_technical": False,
            "prefers_detail": True,
            "likes_humor": False,
            "impatient": False,
        }
        self.conversation_context = None  # "support", "learning", "creative", etc

    def detect_style_from_message(self, user_message):
        """Analyze user message to infer communication style."""
        # Use substring check so plurals/compounds match (apis->api, databases->database)
        message_lower = user_message.lower()

        # Technical indicators
        technical_words = [
            "api", "database", "syntax", "algorithm", "function", "variable",
            "loop", "class", "method", "async", "framework", "stack",
            "json", "xml", "query", "sql", "performance", "optimization"
        ]
        self.user_style["is_technical"] = any(w in message_lower for w in technical_words)

        # Detail preference indicators
        detail_words = ["explain", "detailed", "step-by-step", "why", "elaborate",
                        "how does", "deep dive", "break down"]
        self.user_style["prefers_detail"] = any(w in message_lower for w in detail_words)

        # Humor indicators
        humor_words = ["lol", "haha", "funny", "joke"]
        self.user_style["likes_humor"] = any(w in message_lower for w in humor_words)

        # Impatience indicators
        impatient_words = ["quick", "asap", "hurry", "urgent", "fast"]
        self.user_style["impatient"] = any(w in message_lower for w in impatient_words)

    def detect_context(self, user_message):
        """Detect what type of conversation this is."""
        message_lower = user_message.lower()

        if any(word in message_lower for word in ["bug", "error", "issue", "problem", "crash"]):
            self.conversation_context = "support"
        elif any(word in message_lower for word in ["learn", "teach", "how", "beginner", "explain"]):
            self.conversation_context = "learning"
        elif any(word in message_lower for word in ["create", "design", "brainstorm", "idea", "imagine"]):
            self.conversation_context = "creative"
        else:
            self.conversation_context = "general"

    def get_style_summary(self):
        """Print detected style."""
        return (
            f"Technical: {self.user_style['is_technical']} | "
            f"Detail-oriented: {self.user_style['prefers_detail']} | "
            f"Likes humor: {self.user_style['likes_humor']} | "
            f"Impatient: {self.user_style['impatient']} | "
            f"Context: {self.conversation_context}"
        )


# ============================================================
# PART 2: Build Adaptive System Prompt
# ============================================================

def build_adaptive_system_prompt(adapter):
    """Generate system prompt that matches user's detected style."""

    base = "You are Ahmed, a Tunisian AI assistant."

    # Voice and tone based on technical level
    if adapter.user_style["is_technical"]:
        voice = "technical, precise, professional"
        language = "Use technical terminology accurately. Mention time complexity, patterns, best practices."
        examples = "Provide code examples when relevant."
    else:
        voice = "approachable, friendly, simple"
        language = "Explain in plain English. Avoid jargon. Use everyday analogies."
        examples = "Use real-world examples, not code."

    # Detail level
    if adapter.user_style["prefers_detail"]:
        detail = "Provide comprehensive explanations. Include background, examples, and edge cases."
        length = "Responses can be longer and thorough."
    else:
        detail = "Be concise. Get to the point."
        length = "Keep responses brief (1-2 paragraphs)."

    # Humor
    if adapter.user_style["likes_humor"]:
        humor = "Light humor is welcome. Make occasionally witty observations."
    else:
        humor = "Keep it professional. Avoid jokes."

    # Pace
    if adapter.user_style["impatient"]:
        pace = "Prioritize speed. Provide quick answers first, details on request."
    else:
        pace = "Take time to explain thoroughly."

    # Context-specific instructions
    context_instructions = {
        "support": "User has a problem. Be empathetic, diagnostic, solution-focused.",
        "learning": "User wants to learn. Be patient, encourage thinking, guide don't solve.",
        "creative": "User is brainstorming. Be enthusiastic, exploratory, unconventional.",
        "general": "Have a friendly conversation."
    }
    context_instr = context_instructions.get(adapter.conversation_context, "Be helpful.")

    prompt = f"""
{base}

Voice: {voice}
Tone: warm, helpful, professional

INSTRUCTIONS:
- {language}
- {examples}
- {detail} {length}
- {humor}
- {pace}
- {context_instr}

Constraints:
- Use Tunisian context when natural (Bilel, Yasmine, Sfax, Tunis)
- Never pretend to have capabilities you don't have
- If you're unsure, say so
""".strip()

    return prompt


# ============================================================
# PART 3: Compare Static vs Adaptive Personality
# ============================================================

def compare_static_vs_adaptive():
    """Show the difference between Day 06 (static) and Day 07 (adaptive)."""
    print("=" * 70)
    print("COMPARISON: Static vs Adaptive Personality")
    print("=" * 70)

    # Static system prompt (Day 06 style)
    static_prompt = """
You are Ahmed, a friendly Tunisian AI assistant.
You're warm, helpful, and encouraging.
Keep responses concise.
"""

    print("\n--- DAY 06: STATIC PERSONALITY ---")
    print("Same prompt for ALL users:")
    print(static_prompt)

    # Adaptive examples
    print("\n--- DAY 07: ADAPTIVE PERSONALITY ---")

    test_messages = [
        # Technical + Detail-oriented → technical voice, thorough response
        "Explain the algorithm step-by-step, including time complexity and edge cases",
        # Casual + Humor → simple, playful tone
        "lol my code crashed again haha, why does python hate me?",
        # Impatient + Technical → technical but concise, skip preamble
        "quick fix asap - my sql query is broken and it's urgent!",
        # Non-technical + Support → empathetic, plain language
        "I have an error and I don't understand what's wrong, can you help me?",
        # Creative + Detail → enthusiastic, exploratory, thorough
        "I want to brainstorm and design a new app idea step-by-step",
        # Technical + Learning → patient but technical
        "teach me how database queries work and why they're slow sometimes",
    ]

    adapter = PersonalityAdapter()

    for msg in test_messages:
        print(f"\nUser: '{msg}'")
        adapter.detect_style_from_message(msg)
        adapter.detect_context(msg)
        print(f"   Style detected: {adapter.get_style_summary()}")

        adaptive_prompt = build_adaptive_system_prompt(adapter)
        print(f"   Adapted prompt snippet:")
        # Show first 3 lines of adapted prompt
        for line in adaptive_prompt.split('\n')[:4]:
            if line.strip():
                print(f"   > {line}")
        print()


# ============================================================
# PART 4: Interactive Personality Adaptation
# ============================================================

def demonstrate_personality_learning():
    """Show how personality adapts based on user feedback."""
    print("=" * 70)
    print("PERSONALITY LEARNING: Adapt Based on Feedback")
    print("=" * 70)

    adapter = PersonalityAdapter()

    interactions = [
        ("What's a list in Python?", "too_simple"),      # User found it too simple
        ("How do lists work internally?", "good"),        # User was satisfied
        ("Explain hash maps", "too_technical"),           # User found it too technical
        ("ELI5 hash maps", "good"),                       # User was satisfied
    ]

    print("\nLearning pattern: User gives feedback after each response\n")

    for turn, (message, feedback) in enumerate(interactions, 1):
        adapter.detect_style_from_message(message)

        print(f"Turn {turn}: User says '{message}'")
        print(f"  Initial style: {adapter.get_style_summary()}")

        if feedback == "too_simple":
            # Increase technical level
            adapter.user_style["is_technical"] = True
            print(f"  Feedback: 'too simple' -> Adjusting to more technical")
        elif feedback == "too_technical":
            # Decrease technical level
            adapter.user_style["is_technical"] = False
            print(f"  Feedback: 'too technical' -> Adjusting to simpler")
        elif feedback == "good":
            print(f"  Feedback: 'good' -> Personality is working!")

        print()


# ============================================================
# PART 5: Multi-Context Personality
# ============================================================

def show_multi_context_example():
    """Demonstrate different personalities for different contexts."""
    print("=" * 70)
    print("MULTI-CONTEXT: Different Personalities for Different Jobs")
    print("=" * 70)

    contexts = {
        "support": {
            "message": "I'm getting a permission denied error",
            "personality": "Empathetic, diagnostic, solution-focused"
        },
        "learning": {
            "message": "Teach me about recursion",
            "personality": "Patient, encouraging, use examples"
        },
        "creative": {
            "message": "Help me design a todo app",
            "personality": "Enthusiastic, exploratory, collaborative"
        },
    }

    adapter = PersonalityAdapter()

    for context, info in contexts.items():
        print(f"\n[{context.upper()}]")
        print(f"  User: {info['message']}")

        adapter.detect_context(info['message'])
        adapter.detect_style_from_message(info['message'])

        prompt = build_adaptive_system_prompt(adapter)
        print(f"  Personality: {info['personality']}")
        print(f"  Context detected: {adapter.conversation_context}")
        print()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("\n")
    print("ADVANCED PERSONALITY DESIGN - ADAPTIVE")
    print("=" * 70)

    compare_static_vs_adaptive()

    print("\n")
    demonstrate_personality_learning()

    print("\n")
    show_multi_context_example()

    print("\n" + "=" * 70)
    print("KEY DIFFERENCES: Day 06 -> Day 07")
    print("=" * 70)
    print("""
DAY 06 (Static Personality):
  [+] One system prompt for all users
  [+] Simple: "You are Ahmed, friendly assistant"
  [-] Doesn't adapt to user's needs
  [-] Same personality for support, learning, creative work

DAY 07 (Adaptive Personality):
  [+] Analyzes user's message to detect communication style
  [+] Generates prompt that matches user's technical level
  [+] Adjusts based on conversation context (support vs learning)
  [+] Learns from user feedback over time
  [+] Better user satisfaction, higher retention

PRACTICAL IMPACT:
  - Technical users get technical responses
  - Beginners get simple explanations
  - Support users get empathy
  - Learners get patience
  - Same bot, optimized for each user
""")
