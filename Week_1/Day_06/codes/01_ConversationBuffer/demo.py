"""
01 - Conversation Buffer Demo
==============================
Demonstrates how to build a simple conversation buffer that stores messages.

HOW TO RUN THIS FILE:
1. python demo.py
"""

from collections import deque
from datetime import datetime


# ============================================================
# PART 1: Basic Conversation Buffer
# ============================================================

def show_basic_buffer():
    """Demonstrate a simple buffer storing user and assistant messages."""
    print("=== PART 1: Basic Conversation Buffer ===\n")

    class ConversationBuffer:
        def __init__(self, max_size=20):
            # deque (double-ended queue) is used instead of a list because
            # maxlen automatically drops the oldest message when the buffer is full.
            # With a plain list you'd need to manually call .pop(0) — slower and error-prone.
            self.history = deque(maxlen=max_size)
            self.created_at = datetime.now()

        def add_message(self, role, content):
            # Every message is a dict with "role" and "content" — this is the
            # exact format expected by LLM APIs (OpenAI, Mistral, etc.).
            self.history.append({"role": role, "content": content})

        def get_history(self):
            # Convert deque to list so callers can index, slice, or serialize it.
            return list(self.history)

        def format_for_display(self):
            # Build a human-readable transcript: "USER: ...\nASSISTANT: ...\n"
            text = ""
            for msg in self.history:
                text += f"{msg['role'].upper()}: {msg['content']}\n"
            return text

    # Create a buffer that holds at most 20 messages
    buffer = ConversationBuffer()

    print("Adding messages to buffer...")
    buffer.add_message("user", "My name is Bilel")
    buffer.add_message("assistant", "Nice to meet you, Bilel!")
    buffer.add_message("user", "I'm from Tunis")
    buffer.add_message("assistant", "Tunis is beautiful! What do you do there?")
    buffer.add_message("user", "I work in tech")

    print("\n--- Conversation History ---")
    print(buffer.format_for_display())

    print(f"Total messages: {len(buffer.get_history())}")
    print(f"Buffer created at: {buffer.created_at.strftime('%H:%M:%S')}\n")


# ============================================================
# PART 2: Buffer with Lookup & Search
# ============================================================

def show_buffer_with_search():
    """Demonstrate searching through conversation history."""
    print("=== PART 2: Buffer with Lookup & Search ===\n")

    class SearchableBuffer:
        def __init__(self):
            # maxlen=50: in real chatbots you cap history to control API costs.
            # Each message sent to the API costs tokens; older messages cost money
            # without adding much value once the conversation moves forward.
            self.history = deque(maxlen=50)

        def add_message(self, role, content):
            # Store a timestamp so we can later filter by time if needed.
            self.history.append({"role": role, "content": content, "timestamp": datetime.now()})

        def search(self, keyword):
            # Case-insensitive search: .lower() on both sides ensures
            # "Python" and "python" both match a query for "python".
            results = [msg for msg in self.history if keyword.lower() in msg['content'].lower()]
            return results

        def get_by_role(self, role):
            # Useful for analytics: "What did the user ask?" vs "What did the AI answer?"
            return [msg for msg in self.history if msg['role'] == role]

        def last_n_messages(self, n):
            # Negative slicing gets the last N items from the list.
            # Useful when you only want recent context, not the full history.
            return list(self.history)[-n:]

    buffer = SearchableBuffer()

    # Add a realistic multi-turn Python help conversation
    messages = [
        ("user", "Hi, I need help with Python"),
        ("assistant", "Sure! What's your Python question?"),
        ("user", "How do I use lists?"),
        ("assistant", "Lists are ordered collections. You use [] to create them."),
        ("user", "Can I add items to a list?"),
        ("assistant", "Yes, use .append() to add items"),
        ("user", "What about dictionaries?"),
        ("assistant", "Dictionaries use {key: value} syntax")
    ]

    for role, content in messages:
        buffer.add_message(role, content)

    print("--- Search for 'Python' ---")
    python_msgs = buffer.search("Python")
    for msg in python_msgs:
        print(f"{msg['role'].upper()}: {msg['content']}")

    print("\n--- All User Messages ---")
    user_msgs = buffer.get_by_role("user")
    for msg in user_msgs:
        print(f"  • {msg['content']}")

    print("\n--- Last 3 Messages ---")
    recent = buffer.last_n_messages(3)
    for msg in recent:
        print(f"{msg['role'].upper()}: {msg['content']}")

    print()


# ============================================================
# PART 3: Buffer with Token Estimation (for API calls)
# ============================================================

def show_buffer_with_tokens():
    """Demonstrate estimating tokens in conversation."""
    print("=== PART 3: Buffer with Token Estimation ===\n")

    class TokenAwareBuffer:
        def __init__(self, max_tokens=2000):
            # maxlen=100 caps the raw message count;
            # max_tokens caps the total *size* of those messages in tokens.
            # Both limits are needed: 100 short messages < 100 long messages.
            self.history = deque(maxlen=100)
            self.max_tokens = max_tokens

        def add_message(self, role, content):
            self.history.append({"role": role, "content": content})

        def estimate_tokens(self, text):
            # Rule of thumb: 1 token ≈ 4 characters for English text.
            # The actual tokenizer splits on subwords, but this is accurate
            # enough for budget estimation without importing a full tokenizer.
            return len(text) // 4

        def get_total_tokens(self):
            # Sum token estimates across every message in the buffer.
            total = 0
            for msg in self.history:
                total += self.estimate_tokens(msg['content'])
            return total

        def get_history_within_limit(self):
            # We want to keep the MOST RECENT messages, not the oldest,
            # because recent context is more relevant to the current question.
            # Strategy: iterate backwards, fill up to max_tokens, then reverse.
            messages = []
            total_tokens = 0

            # reversed() iterates from newest to oldest without copying the deque.
            for msg in reversed(list(self.history)):
                msg_tokens = self.estimate_tokens(msg['content'])
                if total_tokens + msg_tokens <= self.max_tokens:
                    # Insert at position 0 to restore chronological order.
                    messages.insert(0, msg)
                    total_tokens += msg_tokens
                else:
                    # Once we exceed the token limit, stop — remaining older
                    # messages would push us over budget.
                    break

            return messages, total_tokens

    buffer = TokenAwareBuffer(max_tokens=500)

    # Use repeated strings to simulate long messages that stress the token limit.
    long_messages = [
        ("user", "Tell me about machine learning. " * 10),
        ("assistant", "Machine learning is a subset of artificial intelligence. " * 8),
        ("user", "How do neural networks work? " * 15),
        ("assistant", "Neural networks are inspired by biological neurons. " * 10),
    ]

    for role, content in long_messages:
        buffer.add_message(role, content)

    print(f"Max tokens allowed: {buffer.max_tokens}")
    print(f"Total tokens in full history: {buffer.get_total_tokens()}")

    limited_history, tokens_used = buffer.get_history_within_limit()
    print(f"Tokens used in limited history: {tokens_used}")
    print(f"Messages in limited history: {len(limited_history)}")
    print(f"Dropped oldest {len(buffer.history) - len(limited_history)} message(s)\n")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    show_basic_buffer()
    show_buffer_with_search()
    show_buffer_with_tokens()

    print("--- Key Takeaways ---")
    print("1. Buffers store conversation history in chronological order")
    print("2. Always send full history to AI, never assume it remembers")
    print("3. Buffers can have max sizes to prevent unbounded memory growth")
    print("4. You can search, filter, and extract specific messages")
    print("5. For API calls, estimate tokens to stay within limits")
