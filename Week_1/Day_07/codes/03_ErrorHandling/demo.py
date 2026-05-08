"""
04 - Error Handling Demo
========================
Demonstrates handling common chatbot errors gracefully.

HOW TO RUN THIS FILE:
1. python demo.py
"""

import random


# ============================================================
# PART 1: API Error Handling
# ============================================================

def show_api_error_handling():
    """Demonstrate handling API errors."""
    print("=== PART 1: API Error Handling ===\n")

    class APIClient:
        def __init__(self, failure_rate=0.3):
            self.failure_rate = failure_rate

        def call(self, messages):
            if random.random() < self.failure_rate:
                error_type = random.choice(["timeout", "rate_limit", "server_error"])
                if error_type == "timeout":
                    raise TimeoutError("API request timed out after 30 seconds")
                elif error_type == "rate_limit":
                    raise RuntimeError("Rate limit exceeded: 100 requests/minute")
                else:
                    raise RuntimeError("API Server Error 500")
            return f"Response to: {messages[-1]}"

    client = APIClient(failure_rate=0.5)

    def safe_api_call(messages, retries=2):
        """Call API with error handling and retry logic."""
        for attempt in range(retries):
            try:
                response = client.call(messages)
                return response
            except TimeoutError:
                if attempt < retries - 1:
                    print(f"  Timeout, retrying (attempt {attempt + 1}/{retries})...")
                else:
                    return "I'm taking longer than usual to respond. Please try again."
            except RuntimeError as e:
                if "Rate limit" in str(e):
                    return "I'm getting too many requests. Please wait a moment and try again."
                else:
                    return f"Service temporarily unavailable. Error: {str(e)[:30]}"

    # Simulate requests
    for i in range(4):
        print(f"Request {i + 1}:")
        response = safe_api_call([{"role": "user", "content": "Hello"}])
        print(f"  {response}\n")


# ============================================================
# PART 2: Input Validation
# ============================================================

def show_input_validation():
    """Demonstrate validating user input."""
    print("=== PART 2: Input Validation ===\n")

    class InputValidator:
        MIN_LENGTH = 1
        MAX_LENGTH = 500
        BANNED_WORDS = ["spam", "badword"]

        @staticmethod
        def validate(user_input):
            """Validate input, return (is_valid, error_message)."""
            # Check empty
            if not user_input or not user_input.strip():
                return False, "Message cannot be empty."

            # Check length
            if len(user_input) < InputValidator.MIN_LENGTH:
                return False, "Message too short."
            if len(user_input) > InputValidator.MAX_LENGTH:
                return False, f"Message too long (max {InputValidator.MAX_LENGTH} chars)."

            # Check banned words
            for word in InputValidator.BANNED_WORDS:
                if word in user_input.lower():
                    return False, "Message contains inappropriate content."

            return True, "OK"

    test_inputs = [
        "",
        "Hi",
        "This is a spam message",
        "Normal question about Python",
        "x" * 600,
    ]

    for user_input in test_inputs:
        is_valid, message = InputValidator.validate(user_input)
        status = "[OK]" if is_valid else "[X]"
        preview = user_input[:30] + ("..." if len(user_input) > 30 else "")
        print(f"{status} '{preview}' -> {message}")

    print()


# ============================================================
# PART 3: Database Error Handling
# ============================================================

def show_database_error_handling():
    """Demonstrate handling database errors."""
    print("=== PART 3: Database Error Handling ===\n")

    class ChatHistory:
        def __init__(self, simulate_errors=False):
            self.simulate_errors = simulate_errors
            self.data = {}

        def save_message(self, user_id, message):
            """Save message with error handling."""
            try:
                if self.simulate_errors and random.random() < 0.3:
                    raise RuntimeError("Database connection lost")
                self.data[user_id] = message
                return True
            except RuntimeError as e:
                print(f"    [X] Save failed: {e}")
                return False

        def get_history(self, user_id):
            """Retrieve history with fallback."""
            try:
                if self.simulate_errors and random.random() < 0.2:
                    raise RuntimeError("Query timeout")
                return self.data.get(user_id, [])
            except RuntimeError:
                print(f"    [X] Retrieval failed, using empty history")
                return []

    db = ChatHistory(simulate_errors=True)

    print("Attempting to save messages with simulated errors:\n")
    for i in range(3):
        success = db.save_message("user_1", f"Message {i + 1}")
        status = "[OK] Saved" if success else "[X] Failed"
        print(f"  {status}\n")


# ============================================================
# PART 4: Graceful Degradation
# ============================================================

def show_graceful_degradation():
    """Demonstrate reducing features when errors occur."""
    print("=== PART 4: Graceful Degradation ===\n")

    class RobustChatbot:
        def __init__(self):
            self.features_available = {
                "basic_chat": True,
                "context_extraction": True,
                "persistence": True,
                "analytics": True,
            }

        def disable_feature(self, feature):
            self.features_available[feature] = False
            print(f"  [!] {feature} disabled due to error")

        def chat(self, user_input):
            try:
                # Try full-featured response
                if all(self.features_available.values()):
                    return "Full response with all features"

                # Degrade gracefully
                response = "Response with limited features:"
                if self.features_available["basic_chat"]:
                    response += " [chat works]"
                if self.features_available["context_extraction"]:
                    response += " [context works]"
                return response

            except Exception as e:
                return "Emergency mode: Basic chat only"

    bot = RobustChatbot()

    print("Normal operation:")
    print(f"  {bot.chat('hello')}\n")

    print("After persistence failure:")
    bot.disable_feature("persistence")
    print(f"  {bot.chat('hello')}\n")

    print("After API failure:")
    bot.disable_feature("context_extraction")
    print(f"  {bot.chat('hello')}\n")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    show_api_error_handling()
    show_input_validation()
    show_database_error_handling()
    show_graceful_degradation()

    print("--- Key Takeaways ---")
    print("1. Always wrap API calls in try-except")
    print("2. Validate user input before processing")
    print("3. Catch database errors and use fallbacks")
    print("4. Implement retry logic with exponential backoff")
    print("5. Degrade gracefully - keep core features working")
