# 02 - Async / Await

---

## What is an API Call?

An **API** (Application Programming Interface) is a way for your program to talk to another program — usually over the internet.

Real example:
- You build a chatbot
- Your Python code sends a question to OpenAI's servers: "What is the capital of France?"
- OpenAI's servers process it and send back: "Paris"
- Your Python code receives the answer and shows it to the user

That round trip — send request, wait, receive response — is called an **API call**.

The problem? That trip takes TIME. Sometimes 1 second. Sometimes 5 seconds. Sometimes 30 seconds for a long answer.

---

## What is the Problem?

### The Blocking Problem

By default, Python is **synchronous** — it does ONE thing at a time, in order.

```
Step 1: Send request to AI        ← starts
Step 2: WAIT... WAIT... WAIT...   ← your program is FROZEN here (2-5 seconds)
Step 3: Get response              ← only now does it continue
Step 4: Do the next thing
```

While your program waits in Step 2, it does NOTHING else.

Imagine a restaurant where the waiter:
1. Takes your order
2. Goes to the kitchen
3. STANDS there doing nothing waiting for your food
4. Brings it back
5. ONLY THEN takes the next table's order

That waiter is blocking. The restaurant is slow. Everyone waits.

---

## What is the Solution? Async / Await!

**Async/Await** lets your program do OTHER things while waiting for slow operations.

The smart waiter:
1. Takes your order
2. Goes to the kitchen and LEAVES the ticket
3. Goes to take the NEXT table's order (doesn't stand and wait)
4. When the kitchen yells "ORDER READY!", comes back and delivers

This is **non-blocking** — your program keeps running while waiting.

---

## How It Works in Python

### Key words to know:

| Keyword | What it means |
|---|---|
| `async def` | This function CAN pause and wait without blocking |
| `await` | "Pause HERE and wait for this to finish, but let others run" |
| `asyncio` | The Python library that manages all of this |

### The Golden Rule:
- `await` can ONLY be used inside an `async def` function
- To run an async function, you need `asyncio.run()` or another async function

---

## Why This Matters for AI Apps

When building AI apps, you often need to:
- Call the AI API (slow — 2-10 seconds)
- Call a database
- Call another API for weather/news/etc.

With sync code: do them ONE BY ONE = slow
With async code: do them ALL AT ONCE = fast

```
Sync:   [AI call 3s] → [DB call 1s] → [API call 2s]  = 6 seconds total
Async:  [AI call 3s]
        [DB call 1s]       (all running at the same time)
        [API call 2s]
        = 3 seconds total (just the slowest one)
```
