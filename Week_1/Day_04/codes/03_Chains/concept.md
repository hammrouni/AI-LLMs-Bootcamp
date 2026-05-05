# 03 - Chains (LCEL — LangChain Expression Language)

---

## 📦 Packages

```bash
pip install langchain langchain-openai python-dotenv
```

---

## What is a Chain?

A **chain** is a sequence of steps where the output of one step becomes the input of the next.

```
User Input → [Step 1: Format Prompt] → [Step 2: Call LLM] → [Step 3: Parse Output] → Result
```

Instead of writing this manually every time:
```python
messages = template.format_messages(question=user_input)
response = llm.invoke(messages)
text = response.content
```

A chain does it in one call:
```python
chain = template | llm | output_parser
result = chain.invoke({"question": user_input})
```

---

## LCEL — The Pipe Operator `|`

**LCEL (LangChain Expression Language)** uses the `|` (pipe) operator to connect components — exactly like Unix pipes.

```python
chain = prompt | llm | parser
```

This reads left to right:
1. `prompt` — format the input into messages
2. `llm` — send messages to the AI, get AIMessage back
3. `parser` — extract plain text from AIMessage

Each component's output becomes the next component's input.

---

## The Three Core Components

### 1. `ChatPromptTemplate` — formats input
```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "{question}"),
])
# Input: dict with keys matching the template variables
# Output: list of formatted messages
```

### 2. `BaseChatOpenAI` — calls the LLM
```python
from langchain_openai.chat_models.base import BaseChatOpenAI

llm = BaseChatOpenAI(model="mistral-small-latest", ...)
# Input: list of messages
# Output: AIMessage object
```

### 3. `StrOutputParser` — extracts plain text
```python
from langchain_core.output_parsers import StrOutputParser

parser = StrOutputParser()
# Input: AIMessage
# Output: plain string (message.content)
```

### Put it together:
```python
chain = prompt | llm | StrOutputParser()
result = chain.invoke({"question": "What is Python?"})
print(result)  # "Python is a programming language..."
```

---

## `invoke` vs `stream` vs `batch`

Every LCEL chain supports three execution modes:

| Method | What it does | When to use |
|---|---|---|
| `chain.invoke(input)` | Run once, wait for full response | Most common — simple calls |
| `chain.stream(input)` | Stream tokens as they arrive | Chat UIs — live typing effect |
| `chain.batch([i1, i2, i3])` | Run multiple inputs in parallel | Batch processing |

```python
# invoke — one shot
result = chain.invoke({"question": "Hello"})

# stream — token by token
for chunk in chain.stream({"question": "Tell me a story"}):
    print(chunk, end="", flush=True)

# batch — many at once
results = chain.batch([
    {"question": "Question 1"},
    {"question": "Question 2"},
    {"question": "Question 3"},
])
```

---

## `RunnablePassthrough` — Pass Input Unchanged

Sometimes you want to pass the original input through to the next step alongside the transformed data.

```python
from langchain_core.runnables import RunnablePassthrough

# Useful for: passing original text alongside a summary
chain = {
    "original": RunnablePassthrough(),   # pass input unchanged
    "summary": prompt | llm | parser,    # also run the chain
}
```

---

## Multi-Step Chains

You can chain more than 3 steps. Each step's output feeds the next:

```python
# Step 1: Translate input to English
translate_chain = translate_prompt | llm | StrOutputParser()

# Step 2: Summarize the English text
summarize_chain = summarize_prompt | llm | StrOutputParser()

# Full pipeline: translate → summarize
full_chain = translate_chain | summarize_chain
```

---

## Why LCEL Over the Old LangChain?

In older LangChain (< v0.1), you used `LLMChain`:
```python
# OLD — deprecated
from langchain.chains import LLMChain
chain = LLMChain(llm=llm, prompt=prompt)
```

LCEL (`|`) replaced this because it is:
- **More composable** — any component can be piped to any other
- **Streaming-native** — `stream()` works on any chain automatically
- **Debuggable** — each step is inspectable
- **Async-ready** — `ainvoke()`, `astream()` work without extra setup

Always use LCEL (`|`) in new code.
