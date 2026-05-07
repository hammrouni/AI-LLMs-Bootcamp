# 04 - Multi-Turn Conversations

---

## What is a Multi-Turn Conversation?

A **Multi-Turn Conversation** is an exchange where the user and AI take multiple turns, building on previous context. Each message depends on understanding what came before.

Think of it like a tennis rally:
- Player 1 serves
- Player 2 returns, knowing where the ball came from
- Player 1 sees the return and adjusts
- Back and forth, each shot depends on the previous one
- If you forgot the serve, you can't play the rally

Multi-turn conversations are real dialogue, not isolated Q&A.

---

## What is the Problem?

### Maintaining Consistency Across Turns

Each turn changes the context. If the AI doesn't track context properly, it forgets decisions, contradicts itself, or asks the same question twice.

```
Turn 1: User: "I want a red shirt"
        AI: "What size?"

Turn 2: User: "Medium"
        AI: "What color?" ← Forgot the red! Broken conversation.
```

---

## What is the Solution? Proper Multi-Turn Management!

**Multi-turn conversations require:**
1. Sending full history with each turn (or smart summaries)
2. Tracking what was decided and not re-asking
3. Advancing the conversation forward, not looping

The key: each turn builds on the last, making progress toward resolution.

---

## How It Works in Python

### Key words to know:

| Keyword / Concept | What it means |
|---|---|
| `turn` | One exchange (user message + AI response) |
| `context_carry-forward` | Information from previous turns used in new turns |
| `state_progression` | The conversation moves toward a goal, not circles |
| `history_management` | Keeping track of all turns for reference |
| `conflict_detection` | Catching when AI contradicts earlier turns |

### The Golden Rule:
- **Every turn must see all previous turns.** Never start a turn with less context than the previous one.

### Basic Usage

```python
# What this example shows: managing multi-turn state
class MultiTurnChat:
    def __init__(self, system_prompt):
        self.system_prompt = system_prompt
        self.turns = []  # List of (user, assistant) pairs

    def process_turn(self, user_message):
        # Build messages: system + all previous + new user message
        messages = [{"role": "system", "content": self.system_prompt}]
        for user_msg, assistant_msg in self.turns:
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": assistant_msg})
        messages.append({"role": "user", "content": user_message})

        # Call API
        assistant_response = mistral.call(messages)

        # Record the turn
        self.turns.append((user_message, assistant_response))
        return assistant_response

    def get_conversation_summary(self):
        text = "Conversation Summary:\n"
        for i, (user, assistant) in enumerate(self.turns, 1):
            text += f"Turn {i}:\n  User: {user}\n  AI: {assistant}\n"
        return text
```

### How to Choose

| Approach | When to use | When NOT to use |
|----------|------------|----------------|
| Stateless (send full history) | Any conversation, simple to debug | Long conversations (costs spiral) |
| Stateful (track on server) | Many users, long conversations | Complex to manage, harder to debug |
| Hybrid (smart summaries) | Production apps, balance cost/quality | Small projects |

---

## BAD vs GOOD

```python
# BAD — each turn starts fresh, AI forgets context
def bad_turn(user_message):
    # Only sends the new message!
    response = mistral.call(user_message)
    return response

# GOOD — each turn includes all previous context
def good_turn(user_message, chat_history):
    # Send system + full history + new message
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(chat_history)
    messages.append({"role": "user", "content": user_message})
    response = mistral.call(messages)
    return response
```

---

## Why This Matters for AI Apps

Almost every real app is multi-turn:
- **Chatbot:** Help Bilel debug a bug over 10 exchanges
- **Customer service:** Help Yasmine with an order across 5 turns (address, payment, shipping)
- **Learning:** Teach a concept in 3 turns (intro, example, practice)

Without proper multi-turn handling: AI forgets requirements, asks redundant questions, frustrates users.
With it: conversation flows naturally toward resolution.

---

## Multi-Turn Patterns

```python
# Pattern 1: Simple accumulation
def simple_chat(user_msg, history):
    history.append({"role": "user", "content": user_msg})
    response = api_call(history)
    history.append({"role": "assistant", "content": response})
    return response, history

# Pattern 2: Turn counting (for progress tracking)
def tracked_chat(user_msg, state):
    state['turn_count'] += 1
    state['messages'].append({"role": "user", "content": user_msg})
    response = api_call(state['messages'])
    state['messages'].append({"role": "assistant", "content": response})
    return response, state
```
