# 01 - LangChain & LLM Setup

---

## 📦 Packages

```bash
pip install langchain langchain-openai python-dotenv
```

---

## What is LangChain?

**LangChain** is a framework for building applications powered by Large Language Models.

Think of it as a **toolbox** — instead of writing all the plumbing yourself (HTTP calls, message formatting, prompt management, memory, etc.), LangChain provides ready-made components you can snap together.

Without LangChain:
```python
# You manage everything yourself:
import httpx
headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
payload = {"model": "...", "messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]}
response = httpx.post(url, headers=headers, json=payload)
text = response.json()["choices"][0]["message"]["content"]
```

With LangChain:
```python
# LangChain handles the plumbing:
from langchain_openai.chat_models.base import BaseChatOpenAI
llm = BaseChatOpenAI(model="mistral-small-latest", base_url="https://api.mistral.ai/v1")
response = llm.invoke("What is the capital of Tunisia?")
print(response.content)
```

Same result. Much less code to manage.

---

## Why Use LangChain?

| Without LangChain | With LangChain |
|---|---|
| Write HTTP calls manually | `llm.invoke()` handles it |
| Format message dicts by hand | `ChatPromptTemplate` structures prompts |
| Manage conversation history in lists | Built-in memory components |
| Wire multiple steps together manually | Chain them with `\|` (pipe) |
| Reimplement retry/parsing logic | Pre-built output parsers |

LangChain shines when you need to:
- Build **multi-step pipelines** (prompt → LLM → parse → transform → next LLM)
- Add **memory** to conversations
- Connect LLMs to **external tools** (search, databases, APIs)
- Build **agents** that decide what to do next

---

## LangChain's Core Components

```
┌─────────────────────────────────────────────┐
│              LangChain App                  │
│                                             │
│  [Prompt Template]  → formats the input     │
│         ↓                                   │
│    [LLM / Chat Model]  → calls the API      │
│         ↓                                   │
│   [Output Parser]  → extracts the result    │
│         ↓                                   │
│     [Memory]  → stores conversation history │
│         ↓                                   │
│     [Tools]  → external actions (optional)  │
└─────────────────────────────────────────────┘
```

We'll cover each component across Days 4 and 5.

---

## Chat Models vs LLMs in LangChain

LangChain has two types of model wrappers:

| Type | Class | Input | Output |
|---|---|---|---|
| **Chat Model** | `ChatOpenAI`, `ChatAnthropic` | List of messages | AIMessage |
| **LLM** | `OpenAI` (raw) | Plain string | Plain string |

**Always use Chat Models** — they support system prompts, conversation history, and are what all modern APIs use.

---

## Connecting LangChain to Mistral

Mistral's API is **OpenAI-compatible** — it uses the same message format. Use `BaseChatOpenAI` (not `ChatOpenAI`) and point it at Mistral's endpoint:

```python
from langchain_openai.chat_models.base import BaseChatOpenAI

llm = BaseChatOpenAI(
    model="mistral-small-latest",
    api_key="your-mistral-key",
    base_url="https://api.mistral.ai/v1",
    temperature=0.7,      # 0 = deterministic, 1 = creative
    max_tokens=500,
)
```

> **Why `BaseChatOpenAI` and not `ChatOpenAI`?**
> In `langchain-openai` ≥ 1.x, `ChatOpenAI` renames `max_tokens` → `max_completion_tokens` in the request payload (for OpenAI o-series models). Mistral rejects that field with a 422 error.
> `BaseChatOpenAI` is the parent class — it sends `max_tokens` as-is, which is what Mistral (and most OpenAI-compatible APIs) expect.

---

## The AIMessage Response Object

When you call `llm.invoke()`, you get back an `AIMessage` object — not a plain string:

```python
response = llm.invoke("Hello!")

print(response)           # AIMessage(content='Hello!', ...)
print(response.content)   # 'Hello!' ← the actual text
print(response.usage_metadata)  # token counts
```

To get plain text, either use `response.content` or attach an output parser (covered in `03_Chains`).

---

## Packages

```bash
pip install langchain langchain-openai python-dotenv
```

- `langchain` — core framework
- `langchain-openai` — `ChatOpenAI` class (works with Mistral too)
- `python-dotenv` — load API keys from `.env`
