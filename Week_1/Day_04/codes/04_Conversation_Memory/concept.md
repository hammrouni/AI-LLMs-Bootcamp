# 04 - Conversation Memory

---

## 📦 Packages

```bash
pip install langchain langchain-openai python-dotenv
```

---

## The Problem: AI Has No Memory by Default

Every call to an LLM is **stateless** — it has no idea what you said before.

```
You:  "My name is Yasmine."
AI:   "Nice to meet you, Yasmine!"

You:  "What's my name?"
AI:   "I don't know your name."  ← forgot immediately
```

The model doesn't store anything between calls. Each API request starts completely fresh.

---

## The Solution: Send the History Yourself

The fix is simple: **include the full conversation history in every request**.

```
Request 1:
  [System: "You are a helpful assistant."]
  [Human: "My name is Yasmine."]
  → AI: "Nice to meet you, Yasmine!"

Request 2:
  [System: "You are a helpful assistant."]
  [Human: "My name is Yasmine."]     ← include past messages
  [AI: "Nice to meet you, Yasmine!"] ← include past response
  [Human: "What's my name?"]          ← new question
  → AI: "Your name is Yasmine!"  ✓
```

You are not "giving the model memory" — you are **sending the entire conversation as context** on every request.

---

## How LangChain Handles This

LangChain uses `MessagesPlaceholder` in the prompt template to inject history, and you maintain a list of messages that grows with each turn.

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

# Template with a slot for history
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    MessagesPlaceholder("chat_history"),   # ← history goes here
    ("human", "{user_input}"),
])

# Your running history list
chat_history = []

# Turn 1
response = chain.invoke({"chat_history": chat_history, "user_input": "My name is Yasmine."})
chat_history.append(HumanMessage("My name is Yasmine."))
chat_history.append(AIMessage(response))

# Turn 2 — history is now included automatically
response = chain.invoke({"chat_history": chat_history, "user_input": "What's my name?"})
# → "Your name is Yasmine!"
```

---

## The Growing Context Window Problem

Every turn adds more tokens to the context. After 50 turns, you might be sending thousands of tokens of history — slow and expensive.

Three strategies to manage this:

### 1. Buffer (last N messages)
Keep only the last N turns:
```python
MAX_TURNS = 10
if len(chat_history) > MAX_TURNS * 2:
    chat_history = chat_history[-(MAX_TURNS * 2):]
```
**Simple.** May forget early important info.

### 2. Summary Memory
Summarize old history with the LLM:
```
Old: 10 turns about Python, data science, and career plans
Summary: "User is Yasmine, a data scientist interested in Python and AI career growth."
```
**Efficient.** Loses some detail.

### 3. Hybrid (Summary + Recent Buffer)
Keep a summary of old turns + the last N turns verbatim.
**Best quality.** More complex to implement.

---

## Token Cost of Memory

```
Turn 1:  prompt (50 tokens) + response (100 tokens) = 150 tokens
Turn 2:  prompt (50) + turn-1 (150) + response (100) = 300 tokens
Turn 3:  prompt (50) + turn-1 (150) + turn-2 (300) + response (100) = 600 tokens
...
Turn 10: potentially 3,000+ tokens just for history
```

For a free Mistral API key with rate limits, long conversations get expensive fast. Buffer memory at 5-10 turns is a practical default.

---

## Old LangChain Memory vs Modern Approach

**Old way (deprecated):**
```python
from langchain.memory import ConversationBufferMemory  # ← deprecated
memory = ConversationBufferMemory(return_messages=True)
chain = ConversationChain(llm=llm, memory=memory)
```

**Modern way (LCEL — what we use):**
```python
chat_history = []  # you manage the list
chain = prompt | llm | StrOutputParser()

# Each turn:
response = chain.invoke({"chat_history": chat_history, "user_input": msg})
chat_history.append(HumanMessage(msg))
chat_history.append(AIMessage(response))
```

The modern approach is **explicit** — you see exactly what's being sent to the model. No magic, no hidden state.
