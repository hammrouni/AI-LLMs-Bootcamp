# 01 - Error Handling

---

## 📦 Packages

```bash
pip install httpx python-dotenv
```

---

## What is an API Error?

When your Python code calls an AI API, many things can go wrong:

- **Your internet cuts out** — the request never reaches the server
- **The server is overloaded** — it returns an error code instead of a response
- **Your API key is wrong** — the server refuses to answer you
- **You sent bad data** — the server tells you your request is malformed
- **You hit your rate limit** — you sent too many requests too fast

If you don't handle these errors, your entire program CRASHES and the user sees nothing but a scary error message.

---

## HTTP Status Codes — The Server's Language

When a server responds, it always includes a **status code** — a number that tells you what happened.

| Code | Meaning | What it means for you |
|---|---|---|
| `200` | OK | Everything worked |
| `400` | Bad Request | YOU sent something wrong |
| `401` | Unauthorized | Your API key is missing or wrong |
| `403` | Forbidden | You don't have permission |
| `404` | Not Found | That URL doesn't exist |
| `422` | Unprocessable Entity | Your data format is wrong |
| `429` | Too Many Requests | You hit the rate limit — SLOW DOWN |
| `500` | Internal Server Error | The server broke — not your fault |
| `503` | Service Unavailable | Server is overloaded — try again later |

---

## Types of Errors in Python

### 1. Network Errors (before reaching the server)
```
ConnectError    — could not reach the server at all
TimeoutException — server took too long to respond
```

### 2. HTTP Errors (server responded but with an error)
```
401 Unauthorized   — bad API key
429 Too Many Requests — rate limited
500 Server Error   — server crashed
```

### 3. Data Errors (server responded but data is wrong)
```
KeyError      — the key you expected isn't in the response
ValueError    — the data is in the wrong format
```

---

## The try/except Pattern

Python handles errors with `try/except`:

```python
try:
    # code that might fail
    response = client.get(url)
except SpecificError:
    # what to do when that specific thing fails
    print("That specific thing failed")
except AnotherError:
    # handle another type of failure
    print("Something else went wrong")
finally:
    # this runs no matter what (success OR failure)
    print("Done (success or failure)")
```

**Golden rule:** Always catch the MOST SPECIFIC error first, then more general ones.

---

## Why Specific Error Handling Matters

```python
# BAD — swallows ALL errors, you can't tell what went wrong
try:
    call_api()
except Exception:
    print("Something went wrong")  # useless!

# GOOD — each error type gets its own response
try:
    call_api()
except httpx.TimeoutException:
    print("Request timed out — try again")
except httpx.ConnectError:
    print("No internet connection")
except APIError as e:
    if e.status_code == 429:
        print("Rate limited — wait before retrying")
    elif e.status_code == 401:
        print("Check your API key")
```

---

## The Context: Why This Matters for AI Apps

AI API calls are especially error-prone because:
- They take a long time (2-30 seconds) — more time for things to fail
- They cost money — a crash loop could rack up charges
- Rate limits are strict — Mistral free tier = 1 request/second

A production AI app **must** handle errors gracefully, or users will see crashes constantly.
