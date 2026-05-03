# 05 - Logging

---

## 📦 Packages

```bash
pip install httpx python-dotenv
```

> `logging` est un module **intégré à Python** — pas besoin de l'installer.

---

## Why Logging?

When your AI app runs in production, you can't stare at the terminal.

You need **logs** — a permanent record of what happened, when, and why — so you can:
- Debug problems after they happen ("what went wrong at 3am?")
- Monitor performance ("are my API calls getting slower?")
- Track errors ("how often does Mistral return a 429?")
- Audit usage ("who asked what, and when?")

`print()` is for development. **Logging** is for production.

---

## Python's Built-in `logging` Module

Python ships with a `logging` module — no install needed.

### Log Levels (from least to most severe)

| Level | Number | When to use |
|---|---|---|
| `DEBUG` | 10 | Detailed info for developers — every step, every variable |
| `INFO` | 20 | Normal operation — "request started", "response received" |
| `WARNING` | 30 | Something unexpected but not fatal — "rate limited, retrying" |
| `ERROR` | 40 | A request failed — "API returned 500" |
| `CRITICAL` | 50 | The whole app is broken — "database is down" |

**Rule:** In production, set the level to `INFO`. In development, use `DEBUG`.

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.debug("Detailed debug info")     # only shown if level=DEBUG
logger.info("Request started")          # shown at INFO and above
logger.warning("Rate limited")          # shown at WARNING and above
logger.error("API returned 500")        # always shown
logger.critical("App is crashing!")     # always shown
```

---

## Logging to a File

By default, logs go to the terminal. For production, write them to a file:

```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("app.log"),   # write to file
        logging.StreamHandler()           # also print to terminal
    ]
)
```

Now `app.log` has a permanent record of everything that happened.

---

## What to Log in an AI App

**Log these events:**
```
INFO  — Request started (with prompt length, model used)
INFO  — Response received (with token count, duration)
WARNING — Retry attempt (with attempt number, wait time)
ERROR — Request failed after all retries
ERROR — Unexpected response format
WARNING — High token usage (budget alert)
```

**Don't log these:**
```
- The full prompt text (may contain sensitive user data)
- API keys (NEVER log credentials)
- Personal user information
```

---

## Structured Logging

For apps with many logs, plain text is hard to search. **Structured logging** emits JSON instead:

```
Plain text:
  2026-01-15 10:23:45 [INFO] Request succeeded: 73 tokens in 1.2s

Structured JSON:
  {"time": "2026-01-15T10:23:45", "level": "INFO", "tokens": 73, "duration": 1.2, "model": "mistral-small"}
```

With structured logs you can filter: `jq '.[] | select(.tokens > 500)'` to find expensive requests.

---

## Log Rotation

If your app runs forever, log files grow forever.

Use `RotatingFileHandler` to cap file size:
```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    "app.log",
    maxBytes=1_000_000,    # 1 MB max per file
    backupCount=5          # keep 5 old files
)
```

When `app.log` hits 1MB, it becomes `app.log.1`, and a new `app.log` starts.

---

## The Pattern: One Logger Per Module

Create one logger per file using `__name__`:

```python
# In api_client.py
logger = logging.getLogger(__name__)  # logger named "api_client"

# In main.py
logger = logging.getLogger(__name__)  # logger named "__main__"
```

This lets you see which module generated each log line, and control logging per module.
