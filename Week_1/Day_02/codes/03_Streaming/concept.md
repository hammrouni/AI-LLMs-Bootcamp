# 03 - Streaming

---

## 📦 Packages

```bash
pip install httpx python-dotenv openai
```

> `openai` est utilisé ici parce que Mistral est **compatible avec l'API OpenAI**.
> On pointe simplement le SDK OpenAI vers l'endpoint Mistral — même pattern que le Jour 01.

---

## The Problem With Normal API Calls

When you ask an AI for a long answer, the normal flow is:

```
You send request → AI thinks + writes the ENTIRE response → sends it all at once → you receive it
```

If the answer takes 10 seconds to generate, your user stares at a blank screen for 10 seconds.

Then all the text appears instantly at once. This feels like a slow, broken app.

---

## What is Streaming?

Streaming means: **the API sends you tokens (words) as soon as they are generated**, instead of waiting for the full response.

```
Normal:   [waiting 10 seconds............] → "The history of Carthage began in..."
Streaming: "The" → "history" → "of" → "Carthage" → "began" → "in" → ...
           (tokens appear as they're written, in real time)
```

You've seen this in ChatGPT — text appears word by word as the AI "types" it. That's streaming.

---

## Why Streaming Feels Better

| | Normal | Streaming |
|---|---|---|
| First response time | 10 seconds | ~0.3 seconds |
| User perception | "The app is frozen" | "The AI is actively working" |
| Can interrupt? | No — must wait | Yes — user can stop mid-generation |
| Memory needed | Full response in RAM | One token at a time |

Even if the TOTAL time is the same, streaming feels 10x faster because the user sees progress immediately.

---

## How Streaming Works (Technically)

The server sends back a special type of HTTP response called **Server-Sent Events (SSE)** or chunked transfer.

Instead of one big JSON response, you get many small chunks:

```
data: {"choices": [{"delta": {"content": "The"}}]}
data: {"choices": [{"delta": {"content": " history"}}]}
data: {"choices": [{"delta": {"content": " of"}}]}
...
data: [DONE]
```

Each `data:` line is one token (or a few tokens). Your code reads them one by one.

---

## Streaming with httpx (Manual Approach)

```python
async with httpx.AsyncClient() as client:
    async with client.stream("POST", url, headers=headers, json=payload) as response:
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                chunk = line[6:]  # remove "data: " prefix
                if chunk == "[DONE]":
                    break
                data = json.loads(chunk)
                token = data["choices"][0]["delta"].get("content", "")
                print(token, end="", flush=True)  # print without newline
```

---

## Streaming with the OpenAI SDK (Mistral-compatible)

Mistral uses the exact same API format as OpenAI. This means you can use the OpenAI Python SDK, just pointing it at Mistral's endpoint — the same pattern used in Day 01 with Instructor:

```python
from openai import AsyncOpenAI

# Point the OpenAI SDK at Mistral — works because Mistral is OpenAI-compatible
client = AsyncOpenAI(
    api_key=api_key,
    base_url="https://api.mistral.ai/v1"
)

async with client.chat.completions.stream(
    model="mistral-small-latest",
    messages=[{"role": "user", "content": "Décris la médina de Tunis"}]
) as stream:
    async for text in stream.text_stream:
        print(text, end="", flush=True)
```

This is cleaner than raw httpx — the SDK handles SSE parsing for you.

---

## When to Use Streaming

**Use streaming when:**
- You're building a chatbot or interactive app
- Responses might be long (more than a few sentences)
- User experience matters — you want the "typing" feel

**Skip streaming when:**
- You're processing responses in the background (no user is watching)
- You need the complete response before doing anything (e.g., parsing JSON)
- You're using `Instructor` for structured output (Instructor needs the full response)
