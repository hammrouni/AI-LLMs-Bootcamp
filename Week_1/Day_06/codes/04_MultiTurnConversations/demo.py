"""
04 - Multi-Turn Conversations Demo
===================================
Demonstrates managing multi-turn conversations with proper context tracking.

HOW TO RUN THIS FILE:
1. python demo.py
"""

from datetime import datetime


# ============================================================
# PART 1: Simple Multi-Turn Chat
# ============================================================

def show_simple_multiturn():
    """Demonstrate basic multi-turn conversation tracking."""
    print("=== PART 1: Simple Multi-Turn Chat ===\n")

    class SimpleChatSession:
        def __init__(self, system_prompt):
            self.system_prompt = system_prompt
            self.messages = []   # Grows by 2 messages each turn (user + assistant)
            self.turn_count = 0

        def send_message(self, user_input):
            self.turn_count += 1

            # Build the FULL context for this API call.
            # [system, prev_turn_1_user, prev_turn_1_ai, prev_turn_2_user, prev_turn_2_ai, ..., new_user]
            # This is the core of multi-turn: the AI sees the entire conversation,
            # not just the latest message. Without this, every reply would start fresh.
            context = [
                {"role": "system", "content": self.system_prompt},
                *self.messages,                              # All previous turns
                {"role": "user", "content": user_input}     # The new question
            ]

            # Simulate API response (in real code, pass `context` to Mistral)
            simulated_response = f"[Turn {self.turn_count} Response] Processing: '{user_input[:30]}...'"

            # Append BOTH the user message AND the AI response to history.
            # If you forget to store the AI response, it won't be included
            # in the next turn's context and the AI will lose track of what it said.
            self.messages.append({"role": "user", "content": user_input})
            self.messages.append({"role": "assistant", "content": simulated_response})

            return simulated_response

        def print_conversation(self):
            print("\n--- Conversation So Far ---")
            for msg in self.messages:
                role = msg['role'].upper()
                content = msg['content']
                print(f"{role}: {content}")

    system = "You are a helpful assistant helping Bilel learn Python."
    chat = SimpleChatSession(system)

    print("Turn 1:")
    resp1 = chat.send_message("What's a loop?")
    print(f"  User: What's a loop?")
    print(f"  AI: {resp1}")

    print("\nTurn 2:")
    resp2 = chat.send_message("Can I use it to repeat code?")
    print(f"  User: Can I use it to repeat code?")
    print(f"  AI: {resp2}")

    print("\nTurn 3:")
    resp3 = chat.send_message("Give me an example")
    print(f"  User: Give me an example")
    print(f"  AI: {resp3}")

    # By Turn 3, the context list sent to the API has 7 messages:
    # 1 system + 2 user/ai pairs from Turns 1&2 + 1 new user message.
    chat.print_conversation()
    print()


# ============================================================
# PART 2: Multi-Turn with State Tracking
# ============================================================

def show_stateful_multiturn():
    """Demonstrate multi-turn with decision tracking."""
    print("=== PART 2: Multi-Turn with State Tracking ===\n")

    class StatefulChat:
        def __init__(self):
            # State holds everything we've learned about this conversation session.
            # This is separate from the message history — state is structured,
            # history is raw text. Together they give the full picture.
            self.state = {
                "user_name": None,
                "needs": [],
                "preferences": {},
                "decision_made": False,
                "messages": [],
            }

        def extract_decision(self, response_text):
            # Scan the AI's response for decision signals.
            # In production you'd use NLP or regex; here we check a keyword.
            if "decided" in response_text.lower():
                self.state['decision_made'] = True

        def send_message(self, user_input, extract_key=None, extract_value=None):
            # Optionally update state with a pre-extracted fact.
            # The caller decides what to extract; the chat session just stores it.
            # This keeps extraction logic outside the session class (separation of concerns).
            if extract_key:
                self.state[extract_key] = extract_value

            self.state['messages'].append({"role": "user", "content": user_input})

            # Simulated response — a real implementation would call the API here
            # and pass the full messages list + state summary.
            response = f"[AI understands state: {list(self.state.keys())}]"
            self.state['messages'].append({"role": "assistant", "content": response})

            self.extract_decision(response)
            return response

        def print_state(self):
            print("\n--- Current State ---")
            for key, value in self.state.items():
                # Skip messages — they're already in the history; too verbose here.
                if key != 'messages':
                    print(f"{key}: {value}")

    chat = StatefulChat()

    print("Simulating product purchase conversation...\n")

    # Each call extracts one fact from the user message and stores it in state.
    # Notice we pass extract_key/extract_value explicitly — real apps would
    # use a regex or NLP pipeline to do this automatically.
    chat.send_message("Hi, I'm Yasmine looking for a laptop", extract_key="user_name", extract_value="Yasmine")
    print("✓ Extracted: user_name = Yasmine")

    chat.send_message("I need something powerful for video editing", extract_key="needs", extract_value="video editing")
    print("✓ Extracted: need = video editing")

    chat.send_message("Under $1500", extract_key="preferences", extract_value={"budget": 1500})
    print("✓ Extracted: budget = $1500")

    chat.print_state()
    print()


# ============================================================
# PART 3: Conversation Analytics
# ============================================================

def show_conversation_analytics():
    """Demonstrate analyzing multi-turn conversations."""
    print("=== PART 3: Conversation Analytics ===\n")

    class ConversationAnalyzer:
        def __init__(self):
            self.messages = []
            self.start_time = datetime.now()

        def add_turn(self, user_msg, assistant_msg):
            # Store both sides of each turn with timestamps.
            # Timestamps let you measure response time, session duration, etc.
            self.messages.append({
                "role": "user",
                "content": user_msg,
                "timestamp": datetime.now()
            })
            self.messages.append({
                "role": "assistant",
                "content": assistant_msg,
                "timestamp": datetime.now()
            })

        def get_statistics(self):
            # Split messages by role before computing stats.
            user_msgs = [m for m in self.messages if m['role'] == 'user']
            assistant_msgs = [m for m in self.messages if m['role'] == 'assistant']

            # Sum lengths then divide — avoids dividing by zero with the guard.
            total_user_length = sum(len(m['content']) for m in user_msgs)
            total_assistant_length = sum(len(m['content']) for m in assistant_msgs)

            return {
                "total_turns": len(user_msgs),           # One turn = one user message
                "total_messages": len(self.messages),    # Both sides combined
                "user_messages": len(user_msgs),
                "assistant_messages": len(assistant_msgs),
                # Integer division gives average chars per message
                "avg_user_length": total_user_length // len(user_msgs) if user_msgs else 0,
                "avg_assistant_length": total_assistant_length // len(assistant_msgs) if assistant_msgs else 0,
                "conversation_length": len(self.messages),
            }

        def print_stats(self):
            stats = self.get_statistics()
            print("--- Conversation Statistics ---")
            for key, value in stats.items():
                print(f"{key}: {value}")

    analyzer = ConversationAnalyzer()

    # Four turns of machine learning Q&A
    turns = [
        ("What's machine learning?", "Machine learning is when computers learn from data instead of explicit instructions."),
        ("Can you give an example?", "Sure! Email spam detection learns what spam looks like from examples."),
        ("How does it learn?", "It adjusts internal parameters to minimize errors on training data."),
        ("Is it hard to implement?", "There are libraries like Scikit-Learn that handle the complexity for you."),
    ]

    for user_msg, ai_msg in turns:
        analyzer.add_turn(user_msg, ai_msg)

    analyzer.print_stats()
    print()


# ============================================================
# PART 4: Turn-by-Turn Debugging
# ============================================================

def show_turn_debugging():
    """Demonstrate how to debug multi-turn conversations."""
    print("=== PART 4: Turn-by-Turn Debugging ===\n")

    class DebugChat:
        def __init__(self):
            self.messages = []   # Conversation history
            self.turn_logs = []  # Debug info for each turn (separate from history)

        def send_message_with_debug(self, user_message):
            # Build the payload we would send to the API — log it BEFORE calling,
            # so if the API call fails we still know what we tried to send.
            api_payload = [
                {"role": "system", "content": "You are a helpful assistant"},
                *self.messages,
                {"role": "user", "content": user_message}
            ]

            # Record the debug snapshot for this turn.
            # context_size tells us how many messages the AI sees at this turn —
            # it grows by 2 each turn (user + assistant), which means API cost grows too.
            self.turn_logs.append({
                "turn": len(self.messages) // 2 + 1,
                "user_input": user_message,
                "context_size": len(api_payload),          # Total messages sent to API
                "messages_in_history": len(self.messages), # How many were stored before this turn
            })

            # Simulate response
            response = f"Response to: {user_message[:30]}"

            # Append to history for future turns
            self.messages.append({"role": "user", "content": user_message})
            self.messages.append({"role": "assistant", "content": response})

            return response

        def print_debug_log(self):
            print("\n--- Turn-by-Turn Debug Log ---")
            for log in self.turn_logs:
                print(f"Turn {log['turn']}:")
                print(f"  User input: {log['user_input']}")
                # context_size grows: Turn 1 → 2 msgs, Turn 2 → 4 msgs, Turn 3 → 6 msgs
                print(f"  Context size (messages sent to API): {log['context_size']}")
                print(f"  Messages in history before this turn: {log['messages_in_history']}")

    chat = DebugChat()

    chat.send_message_with_debug("Hello")
    chat.send_message_with_debug("What's the weather?")
    chat.send_message_with_debug("In Tunis?")

    # The debug log shows context_size growing 1→3→5 (system + growing history).
    # This is why you need a bounded buffer — unbounded growth = unbounded API cost.
    chat.print_debug_log()
    print()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    show_simple_multiturn()
    show_stateful_multiturn()
    show_conversation_analytics()
    show_turn_debugging()

    print("--- Key Takeaways ---")
    print("1. Each turn must include ALL previous messages")
    print("2. Track conversation state: what was decided, what's pending")
    print("3. Analyze conversations: turns, length, effectiveness")
    print("4. Debug by logging what you send to the API at each turn")
    print("5. Multi-turn conversations are about progress, not circles")
