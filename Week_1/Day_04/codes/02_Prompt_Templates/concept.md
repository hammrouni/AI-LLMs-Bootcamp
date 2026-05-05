# 02 - Prompt Templates

---

## 📦 Packages

```bash
pip install langchain langchain-openai python-dotenv
```

---

## What is a Prompt Template?

A **Prompt Template** is a reusable prompt with **variables** that get filled in at runtime.

Instead of hardcoding prompts:
```python
# BAD — you have to rewrite the whole prompt every time
prompt = "Translate 'bonjour' from French to Spanish."
prompt = "Translate 'merci' from French to Spanish."
prompt = "Translate 'bonjour' from French to Arabic."
```

You define a template once:
```python
# GOOD — one template, unlimited uses
template = "Translate '{word}' from {source_language} to {target_language}."
# Fill it: word="bonjour", source_language="French", target_language="Spanish"
```

---

## Why Use Templates?

1. **Reusability** — write the prompt once, use it 1000 times with different data
2. **Consistency** — all calls use the same structure, no typos or drift
3. **Separation of concerns** — prompt logic is separate from data
4. **Easy testing** — test different values without rewriting the prompt
5. **Pipeline compatibility** — templates plug directly into LangChain chains

---

## Two Types of Templates

### 1. `PromptTemplate` — for simple text prompts (no system/user split)
```python
from langchain_core.prompts import PromptTemplate

template = PromptTemplate.from_template(
    "Write a {length} summary of this text: {text}"
)
filled = template.format(length="one-sentence", text="Carthage was...")
# → "Write a one-sentence summary of this text: Carthage was..."
```

### 2. `ChatPromptTemplate` — for chat models (system + user messages)
```python
from langchain_core.prompts import ChatPromptTemplate

template = ChatPromptTemplate.from_messages([
    ("system", "You are a {role}. Respond in {language}."),
    ("human",  "{user_question}"),
])
messages = template.format_messages(
    role="history expert",
    language="English",
    user_question="Tell me about Carthage."
)
```

**Always use `ChatPromptTemplate`** with modern chat models like Mistral/GPT-4.

---

## Variable Syntax

Variables use double curly braces: `{variable_name}`

```python
ChatPromptTemplate.from_messages([
    ("system", "You are a {role}. Be {tone}."),
    ("human", "Question about {topic}: {question}"),
])
# Variables: role, tone, topic, question
```

LangChain auto-detects all `{variable}` placeholders — you don't need to declare them.

---

## `from_messages` vs `from_template`

```python
# from_messages: full control over each message type
ChatPromptTemplate.from_messages([
    ("system", "You are an expert in {domain}."),
    ("human", "{question}"),
])

# from_template: shortcut — creates a single HumanMessage
ChatPromptTemplate.from_template("Answer this: {question}")
# Same as: from_messages([("human", "Answer this: {question}")])
```

Use `from_messages` when you need a system prompt or multi-turn structure.

---

## Partial Templates — Pre-fill Some Variables

You can fix some variables ahead of time and leave others for later:

```python
base_template = ChatPromptTemplate.from_messages([
    ("system", "You are a {role} assistant. Respond in {language}."),
    ("human", "{question}"),
])

# Pre-fill role and language — these are fixed for this app
french_assistant = base_template.partial(role="customer service", language="French")

# Later, only need to provide the user's question
messages = french_assistant.format_messages(question="Où est mon colis?")
```

