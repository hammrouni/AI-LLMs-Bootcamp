# 03 - System Prompts

---

## What is a System Prompt?

A **System Prompt** is an instruction you give to an AI at the start of a conversation that defines its personality, behavior, and constraints. It's like a character sheet for the AI.

Think of it like hiring a waiter:
- You tell the waiter: "Be friendly, suggest the house special, don't let customers leave angry"
- The waiter's behavior follows these rules all night
- Different instructions produce different service (friendly vs formal, pushy vs subtle)
- The waiter becomes what you instruct them to be

A system prompt shapes how the AI acts in every response.

---

## What is the Problem?

### AI Has No Personality Without Direction

Without a system prompt, the AI is generic and uncommitted. It won't take a position, won't be fun, won't have a consistent tone. Every response feels like reading documentation.

```
User: "What's a good restaurant?"
AI: "That depends on several factors including cuisine preference, budget, location, dietary restrictions, party size, ambiance preference, and occasion."
```

The AI is correct but boring, unhelpful, and doesn't sound like anything.

---

## What is the Solution? A Good System Prompt!

**A strong system prompt:**
1. Defines the AI's role ("You are a Tunisian food expert")
2. Sets its tone ("Friendly and enthusiastic")
3. Explains constraints ("Keep responses under 100 words")
4. Gives examples of how to behave

With a good prompt, the same AI becomes useful and memorable.

---

## How It Works in Python

### Key words to know:

| Keyword / Concept | What it means |
|---|---|
| `role` | What the AI pretends to be (expert, assistant, comedian) |
| `tone` | How it sounds (formal, casual, technical, fun) |
| `constraint` | Rules it must follow (max length, no profanity) |
| `system_message` | The prompt sent to the AI at conversation start |
| `instruction` | A specific behavior directive |

### The Golden Rule:
- **System prompt is sent once at the start, but it shapes all responses.** Make it clear, specific, and memorable.

### Basic Usage

```python
# What this example shows: defining a system prompt that shapes AI personality
system_prompt = """
You are Ramy, a friendly Tunisian travel guide.
- You love your country and recommend places enthusiastically
- You speak English but often mention Tunisian place names: Tunis, Sfax, Djerba
- You give practical advice: costs, opening hours, best times to visit
- Keep responses friendly and personal, not formal
- If asked about Tunis specifically, you become extra enthusiastic
"""

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "Where should I visit in Tunisia?"}
]

response = mistral.call(messages)
# Response will be warm, Tunisian-focused, practical
```

### How to Choose

| Type | When to use | When NOT to use |
|------|------------|----------------|
| Expert role | Q&A, learning, support | Open-ended creative chat |
| Persona | Customer service, branding | Technical tasks |
| Instruction-heavy | Complex requirements, specific format | Simple tasks |

---

## BAD vs GOOD

```python
# BAD — vague system prompt, AI is unfocused
system_bad = "You are a helpful assistant."

# GOOD — specific role, tone, and behavior
system_good = """
You are a Tunisian tech mentor helping students learn.
- Focus on practical, runnable code examples
- Use Tunisian names in examples: Bilel, Yasmine, Nour
- Explain the WHY before the HOW
- Keep enthusiasm high; make learning fun
- If stuck, encourage them with: "You're close! Try..."
"""
```

---

## Why This Matters for AI Apps

Every serious AI app needs a strong system prompt:
- **Customer support:** Define how formal/friendly the bot should be
- **Sales chatbot:** Define what to push, what to avoid, how to handle objections
- **Learning app:** Define teaching style (Socratic, step-by-step, visual, etc)
- **Content creation:** Define voice, style, brand personality

Without a system prompt: AI outputs feel generic, users don't connect, brand identity is lost.
With a great one: AI becomes an extension of your brand, users remember and like it.

---

## System Prompt Patterns

```python
# Pattern 1: Role-based
ROLE_PROMPT = """
You are [specific role].
You [characteristic 1].
You [characteristic 2].
You always [behavior 1].
You never [behavior 2].
"""

# Pattern 2: Instruction-based
INSTRUCTION_PROMPT = """
Instructions:
1. When user asks about X, respond with Y
2. If no context, ask for clarification
3. Always cite sources
4. Keep responses under 200 words
"""

# Pattern 3: Example-based
EXAMPLE_PROMPT = """
You respond like this:
Example input: "What should I eat?"
Example output: "In Tunis, try [specific dish]. It's [description]."
"""
```
