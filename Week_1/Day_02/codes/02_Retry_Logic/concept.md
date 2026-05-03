# 02 - Retry Logic

---

## 📦 Packages

```bash
pip install httpx python-dotenv tenacity
```

> `tenacity` est optionnel — utilisé dans la Partie 5 seulement. Les Parties 1-4 n'ont besoin que de `httpx`.

---

## Why Retry?

AI APIs fail sometimes. Not because of your code — but because:

- The internet had a blip for 200ms
- The server was briefly overloaded
- You hit your rate limit (too many requests/minute)
- The server had a momentary 500 error

These are **transient errors** — temporary problems that fix themselves in seconds.

If you just fail immediately on these, you create a bad user experience. The right answer is to **try again** — but intelligently.

---

## Naive Retry — The Wrong Way

```python
# BAD: retry immediately in a tight loop
for attempt in range(3):
    try:
        result = call_api()
        break
    except Exception:
        continue  # tries again IMMEDIATELY — hammers the server!
```

Problems:
1. You hammer the server with requests when it's already struggling
2. If you're rate-limited, retrying immediately makes it worse
3. You waste compute and money on rapid failures

---

## Exponential Backoff — The Right Way

**Exponential backoff** means: wait longer after each failure.

```
Attempt 1 fails → wait 1 second
Attempt 2 fails → wait 2 seconds
Attempt 3 fails → wait 4 seconds
Attempt 4 fails → wait 8 seconds
Give up after max attempts
```

The wait time doubles each time: `wait = base * (2 ^ attempt)`

### Why Exponential?

If 100 clients all hit the server at once and all retry immediately, they ALL fail again at once. They all retry again... and again. This is called a **thundering herd**.

With exponential backoff:
- First retry is quick (maybe it was just a blip)
- Later retries give the server real time to recover
- Clients spread out their retries naturally

---

## Jitter — Adding Randomness

Even with exponential backoff, if 100 clients all start at the same time, they all retry at the same intervals.

**Jitter** adds a random amount to the wait time so retries are spread out:

```
Without jitter: all retry at exactly t=1s, t=2s, t=4s
With jitter:    retry at t=0.8s, t=1.3s, t=2.1s, t=3.7s (random spread)
```

```python
import random

wait = (2 ** attempt) + random.uniform(0, 1)  # add 0-1 second of randomness
```

---

## What to Retry vs What NOT to Retry

Not all errors deserve a retry. Some errors are permanent:

| Error | Retry? | Why |
|---|---|---|
| `500 Server Error` | ✅ Yes | Temporary server problem |
| `503 Service Unavailable` | ✅ Yes | Server overloaded, will recover |
| `429 Too Many Requests` | ✅ Yes | Rate limited, wait and try again |
| `408 Timeout` | ✅ Yes | Network blip |
| `401 Unauthorized` | ❌ No | Your key is wrong — retrying won't fix it |
| `400 Bad Request` | ❌ No | YOUR data is wrong — retrying sends the same bad data |
| `404 Not Found` | ❌ No | That URL doesn't exist — retrying is pointless |

**Rule:** Only retry errors that are temporary (server-side or network). Never retry errors caused by your own code or credentials.

---

## The tenacity Library

Python's `tenacity` library makes retry logic clean and declarative:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
def call_api():
    ...  # tenacity handles all the retry logic for you
```

You can also write it manually with a loop — which is important to understand before using a library.
