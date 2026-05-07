# 02 - Context Management

---

## What is Context Management?

**Context Management** is the practice of extracting and organizing the relevant information from a conversation so the AI can use it to give accurate, personalized answers.

Think of it like a doctor's visit:
- The doctor doesn't just listen to your complaint; they review your medical history
- They pull out the relevant facts: "You mentioned diabetes last time, so we need to check your levels"
- They organize the facts into a mental model: "Patient has diabetes + high blood pressure + takes medication X"
- They use this context to make a diagnosis—not just guess

Context management is your AI's "pulling the file and reviewing it" before answering.

---

## What is the Problem?

### Losing Relevance Over Long Conversations

As conversations grow, the important facts get buried. If a conversation is 100 messages long, sending all 100 to the AI is inefficient. The AI wastes time reading irrelevant details.

```
User asks about product: "I want a red shirt, size M"
[20 messages of small talk later]
User: "Do you have that in stock?"
AI: "What product are you asking about?" ← Forgot the context!
```

---

## What is the Solution? Context Management!

**Context Management** automatically:
1. Identifies important facts (entities, decisions, preferences)
2. Organizes them into a summary
3. Updates the summary as new information arrives
4. Uses the summary (not raw history) for answering

Instead of sending 100 messages, send 10 messages + a summary. The AI focuses on what matters.

---

## How It Works in Python

### Key words to know:

| Keyword / Concept | What it means |
|---|---|
| `entity` | A named thing (person, product, topic) |
| `summary` | Compressed facts about the conversation |
| `extraction` | Pulling facts out of messages |
| `context_window` | The portion of history sent to AI |
| `memory_chain` | Linking context across multiple turns |

### The Golden Rule:
- **Keep context lean.** Only include facts the AI needs to answer the next question. Old small talk is noise.

### Basic Usage

```python
# What this example shows: extracting and organizing key facts from messages
class ContextManager:
    def __init__(self):
        self.entities = {}  # Store named things (people, products, etc)
        self.facts = []     # Store important facts

    def extract_fact(self, message, key, value):
        # key = "product_name", value = "Red Shirt"
        self.entities[key] = value
        self.facts.append(f"{key}: {value}")

    def get_context_summary(self):
        # Return only the important facts
        return "\n".join(self.facts)

# Example
ctx = ContextManager()
ctx.extract_fact("User wants red shirt", "product", "Red Shirt")
ctx.extract_fact("User wants size M", "size", "M")
ctx.extract_fact("User concerned about stock", "concern", "Availability")

print(ctx.get_context_summary())
# Output:
# product: Red Shirt
# size: M
# concern: Availability
```

### How to Choose

| Approach | When to use | When NOT to use |
|----------|------------|----------------|
| Manual extraction | Small, controlled conversations | Large, unpredictable user input |
| Regex patterns | Specific facts ("phone", "name") | Complex, varied language |
| AI extraction | Any natural language | Slow, expensive for every message |

---

## BAD vs GOOD

```python
# BAD — sending entire 50-message history every time
def chat_without_context(message, full_history):
    # Wasteful: AI reads all 50 messages
    return mistral.call(full_history)

# GOOD — sending summary + recent messages
def chat_with_context(message, history, context_manager):
    summary = context_manager.get_context_summary()
    recent = history[-5:]  # Last 5 messages
    combined = f"CONTEXT:\n{summary}\n\nRECENT:\n{recent}"
    return mistral.call(combined)
```

---

## Why This Matters for AI Apps

Real-world apps juggle multiple contexts:
- **Customer support:** AI handles 1000s of users; each needs their own history
- **Sales chatbot:** Bilel asks about blue shirts, then come back tomorrow; bot must remember the color preference
- **Learning app:** Student learns about loops, then functions; context includes loop knowledge

With no context management: API costs explode (sending 1000 messages per user), AI gets confused, user experience degrades.
With context management: Costs drop, AI stays focused, users feel understood.

---

## Quick Reference Patterns

```python
# Pattern 1: Extract specific named entities
import re

def extract_entities(text):
    names = re.findall(r"My name is (\w+)", text)
    products = re.findall(r"interested in (\w+)", text)
    return {"names": names, "products": products}

# Pattern 2: Track user preferences
class PreferenceTracker:
    def __init__(self):
        self.preferences = {}

    def note_preference(self, key, value):
        self.preferences[key] = value

    def get_preference(self, key):
        return self.preferences.get(key)
```
