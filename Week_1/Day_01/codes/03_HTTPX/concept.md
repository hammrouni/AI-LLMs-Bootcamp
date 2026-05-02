# 03 - HTTPX (The Async Networking Pro)

---

## What is HTTP?

**HTTP** is the language computers use to talk to each other over the internet.

When your browser opens google.com:
1. It sends an HTTP **request**: "Give me google.com"
2. Google's server sends back an HTTP **response**: here's the HTML page

When your Python code asks Mistral AI "What are the best beaches in Tunisia?", it does the exact same thing — but with Python code instead of a browser.

---

## What is `requests`?

`requests` is the most famous Python library for making HTTP calls. It's been around since 2011 and is very simple.

```python
import requests
response = requests.get("https://api.mistral.ai/v1/...")
```

**Problem:** `requests` is **synchronous only**. It BLOCKS your program while waiting. It has no async support.

---

## What is HTTPX?

**HTTPX** is the modern replacement for `requests`. It does everything `requests` does, PLUS:

- Supports **async/await** natively
- Faster
- HTTP/2 support
- Type hints built in
- Used by FastAPI, modern AI frameworks

Think of `requests` as a flip phone — it works but it's old.
Think of `httpx` as a smartphone — same calls, way more powerful.

---

## requests vs HTTPX

| Feature | requests | httpx |
|---|---|---|
| Synchronous (normal) | YES | YES |
| Asynchronous (async) | NO | YES |
| HTTP/2 | NO | YES |
| Modern type hints | NO | YES |
| AI framework compatible | Limited | YES |
| Install | `pip install requests` | `pip install httpx` |

---

## Why HTTPX for AI Development?

Imagine a Tunisia travel chatbot that calls the Mistral AI API:
- The AI takes 3-10 seconds to respond
- With `requests`: your entire app freezes — no one can ask about Tunis, Sousse, or Djerba while waiting
- With `httpx` async: your app keeps running, handles multiple users at once, stays responsive

In 2026, if you're building production AI apps, **always use HTTPX**.

---

## Installation

```bash
pip install httpx python-dotenv
```

---

## Example: Parsing an AI Response

When Mistral replies, you get back a string. You can store and use it like any Python variable:

```python
response = "The user's name is Yasmine, she is 30 years old, from Tunisia."
```

From there, you can display it, parse it, or pass it to the next part of your app.
