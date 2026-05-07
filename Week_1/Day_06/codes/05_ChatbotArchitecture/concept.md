# 05 - Chatbot Architecture

---

## What is Chatbot Architecture?

**Chatbot Architecture** is the complete design of how all pieces fit together: conversation buffers, context management, system prompts, and multi-turn handling. It's the blueprint for a working chatbot.

Think of it like designing a restaurant:
- The concept (system prompt) is your restaurant's identity: "We're a Tunisian bistro, warm and friendly"
- The kitchen (buffer) keeps orders and prepares them: no lost orders, no confusion
- The host (context manager) remembers regulars: "Ah, Bilel! The usual, yes?"
- The waiter (multi-turn) knows the conversation flow: takes order → suggests wine → brings food → asks about dessert
- Together, they create a coherent experience

Chatbot architecture connects everything into one working system.

---

## What is the Problem?

### Building a Chatbot is Chaotic Without a Plan

If you just glue components together without thinking, you get:
- Memory leaks (history grows forever)
- Forgotten context (AI asks the same question twice)
- No personality (generic responses)
- Broken state (conversation loops)
- No recovery (one error crashes everything)

---

## What is the Solution? A Clear Architecture!

**A good architecture defines:**
1. How messages flow (input → buffer → context → API → response)
2. How state is tracked (what information is saved and where)
3. How errors are handled (graceful degradation, fallbacks)
4. How to extend it (add new features cleanly)
5. How to test it (mock components independently)

---

## How It Works in Python

### Key words to know:

| Keyword / Concept | What it means |
|---|---|
| `component` | A single piece (buffer, context manager, API handler) |
| `orchestrator` | The piece that coordinates all components |
| `state` | What the chatbot knows and remembers |
| `pipeline` | The sequence of steps: input → process → output |
| `error_boundary` | Where errors are caught and handled |

### The Golden Rule:
- **Each component does ONE thing well.** Buffer = storage, context = extraction, API = calling. Don't mix responsibilities.

### The 4 Components + 1 Orchestrator

These are the exact classes built in `demo.py` and carried forward into `06_RealChatbot`:

```python
class ConversationBuffer:
    """Stores all messages in order (Day 2)."""
    def add_message(self, role, content): ...
    def get_history(self): ...              # Returns list of dicts
    def get_as_message_objects(self): ...   # Returns LangChain message objects

class ContextManager:
    """Extracts key facts from each message (Day 3)."""
    def extract_from_message(self, message): ...  # Called on every user turn
    def get_summary(self): ...                     # Returns a formatted string

class SystemPromptManager:
    """Defines chatbot personality and behavior (Day 4)."""
    def get_system_prompt(self): ...          # Builds the prompt string on demand
    def set_personality(self, role, tone): ... # Changes personality mid-session

class LangChainBridge:
    """Handles real API calls via LangChain (Day 6)."""
    def invoke(self, history, user_input): ...  # Calls Mistral or returns simulation
    def is_live(self): ...                       # True if API key is set

class CompleteChatbot:
    """Coordinates all components — the orchestrator."""
    def chat(self, user_input): ...          # Main pipeline
    def show_conversation(self): ...
    def show_context(self): ...
    def reset(self): ...
    def change_personality(self, role, tone): ...
```

---

## The Pipeline (Step by Step)

Inside `CompleteChatbot.chat()`:

```python
def chat(self, user_input):
    # Step 1: Validate — reject empty input before it reaches the API
    if not user_input or not user_input.strip():
        return "Please enter a message."

    # Step 2: Store in buffer (ConversationBuffer)
    self.buffer.add_message("user", user_input)

    # Step 3: Extract context (ContextManager)
    self.context.extract_from_message(user_input)

    # Step 4: Build history for LangChain
    # [:-1] skips the user message we just added because LangChain
    # injects it separately via the "{user_input}" template slot
    history = self.buffer.get_as_message_objects()[:-1]

    # Step 5: Call API (LangChainBridge)
    response = self.bridge.invoke(history, user_input)

    # Step 6: Store assistant response in buffer
    self.buffer.add_message("assistant", response)

    # Step 7: Track turn count
    self.turn_count += 1

    return response
```

---

## BAD vs GOOD Architecture

```python
# BAD — everything mixed together, hard to debug or extend
class ChatbotBad:
    def chat(self, user_input):
        self.history.append(user_input)
        summary = ""            # Context extraction forgotten
        response = self.api.call(self.history)  # No error handling
        self.history.append(response)
        return response

# GOOD — clear separation of concerns (matches demo.py)
class CompleteChatbot:
    def __init__(self, name, api_key):
        self.buffer = ConversationBuffer()        # ONE job: store messages
        self.context = ContextManager()           # ONE job: extract facts
        self.prompt_mgr = SystemPromptManager()   # ONE job: define personality
        self.bridge = LangChainBridge(            # ONE job: call the API
            system_prompt=self.prompt_mgr.get_system_prompt(),
            api_key=api_key
        )

    def chat(self, user_input):
        try:
            self.buffer.add_message("user", user_input)
            self.context.extract_from_message(user_input)
            history = self.buffer.get_as_message_objects()[:-1]
            response = self.bridge.invoke(history, user_input)
            self.buffer.add_message("assistant", response)
            return response
        except Exception as e:
            return f"Error: {str(e)}"
```

---

## Why This Matters for AI Apps

Every chatbot bigger than a prototype needs architecture:
- **Support chatbot:** Handle 1000s of concurrent conversations, each with different context
- **Sales bot:** Track customer journey across multiple turns, preferences, history
- **Learning bot:** Remember student progress, adapt difficulty, personalize explanations
- **Personal assistant:** Work across devices, remember long-term preferences, handle errors gracefully

Without architecture: system becomes unmaintainable, impossible to debug, can't be extended.  
With it: teammates understand the codebase, bugs are isolated, new features plug in cleanly.

---

## Typical Chatbot Components

```
┌─────────────┐
│  User Input │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│   Validation     │ (Is input valid? Empty check)
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ ConversationBuffer│ (Store in history — Day 2)
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ ContextManager   │ (Extract name, topic, preferences — Day 3)
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│SystemPromptManager│ (Build system prompt — Day 4)
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ LangChainBridge  │ (Call Mistral via LangChain — Day 6)
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│   Response       │ (Return to user)
└──────────────────┘
```

> **Note:** This simulation version (`05_ChatbotArchitecture`) replaces `LangChainBridge` with `_simulate_api_call()`. The full real implementation is in `06_RealChatbot/demo.py`.
