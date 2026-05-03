"""
05 - Logging Demo
=================
Learn how to add proper logging to your AI app — so you can debug, monitor, and audit it.

HOW TO RUN:
    pip install httpx python-dotenv
    python demo.py

This demo creates a file called "ai_requests.log" in the same folder.
Get a free Mistral API key at: https://console.mistral.ai
"""

import os
import time
import json
import logging
import asyncio
import httpx
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

load_dotenv()

MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"


# ============================================================
# PART 1: Basic Logging Setup
# ============================================================
def setup_basic_logging():
    """Show the simplest possible logging setup."""
    print("=== Basic Logging Setup ===\n")

    # The simplest setup — logs to terminal
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    logger = logging.getLogger("demo")

    logger.debug("This is a DEBUG message — for developers only")
    logger.info("This is an INFO message — normal operation")
    logger.warning("This is a WARNING — something unexpected but not fatal")
    logger.error("This is an ERROR — something failed")

    print()


# ============================================================
# PART 2: Logging to Both Terminal and File
# ============================================================
def setup_production_logging(log_file: str = "ai_requests.log") -> logging.Logger:
    """
    Production-ready logging: writes to terminal AND a rotating log file.
    Returns a logger that the rest of the app will use.
    """
    logger = logging.getLogger("ai_app")
    logger.setLevel(logging.DEBUG)

    # Avoid adding duplicate handlers if called multiple times
    if logger.handlers:
        return logger

    log_format = logging.Formatter(
        "%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Terminal handler — INFO and above only (don't clutter terminal with DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    # File handler — DEBUG and above (full details in file)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=1_000_000,   # 1 MB per file
        backupCount=3,        # keep 3 rotated files
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    return logger


# ============================================================
# PART 3: Logging Around API Calls
# ============================================================
async def call_mistral_with_logging(
    prompt: str,
    api_key: str,
    logger: logging.Logger,
    max_tokens: int = 200,
) -> str | None:
    """
    Make a Mistral API call with structured logging at every step.
    Shows the exact events you should log in a real AI app.
    """
    prompt_preview = prompt[:60] + "..." if len(prompt) > 60 else prompt

    logger.info(f"API call started | prompt_len={len(prompt)} | model=mistral-small-latest")
    logger.debug(f"Full prompt: '{prompt}'")

    start_time = time.monotonic()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "mistral-small-latest",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(MISTRAL_API_URL, headers=headers, json=payload)
            response.raise_for_status()

        data = response.json()
        usage = data.get("usage", {})
        reply = data["choices"][0]["message"]["content"]
        duration = time.monotonic() - start_time

        logger.info(
            f"API call succeeded | "
            f"prompt_tokens={usage.get('prompt_tokens', '?')} | "
            f"completion_tokens={usage.get('completion_tokens', '?')} | "
            f"total_tokens={usage.get('total_tokens', '?')} | "
            f"duration={duration:.2f}s"
        )
        logger.debug(f"Response: '{reply[:100]}...'")
        return reply

    except httpx.TimeoutException:
        duration = time.monotonic() - start_time
        logger.error(f"API call timed out after {duration:.2f}s | prompt='{prompt_preview}'")
        return None

    except httpx.ConnectError:
        logger.error("API call failed: cannot connect to server. Check internet connection.")
        return None

    except httpx.HTTPStatusError as e:
        duration = time.monotonic() - start_time
        status = e.response.status_code
        if status == 429:
            logger.warning(f"Rate limited (429) | duration={duration:.2f}s | consider adding retry logic")
        elif status == 401:
            logger.error("Unauthorized (401) | check your MISTRAL_API_KEY")
        elif status >= 500:
            logger.error(f"Server error ({status}) | duration={duration:.2f}s | retry later")
        else:
            logger.error(f"HTTP error {status} | duration={duration:.2f}s | {e.response.text[:100]}")
        return None

    except (KeyError, IndexError) as e:
        logger.error(f"Unexpected response format: {e} | raw={data}")
        return None


# ============================================================
# PART 4: Log Level Demo — What Gets Shown at Each Level
# ============================================================
def show_log_levels():
    """Show how log levels filter output."""
    print("\n=== Log Level Filtering ===\n")

    levels = [
        ("DEBUG",    logging.DEBUG),
        ("INFO",     logging.INFO),
        ("WARNING",  logging.WARNING),
        ("ERROR",    logging.ERROR),
    ]

    messages = [
        (logging.DEBUG,   "debug",   "Processing token 1 of 47"),
        (logging.INFO,    "info",    "Request completed in 1.2s"),
        (logging.WARNING, "warning", "Rate limited, waiting 2s"),
        (logging.ERROR,   "error",   "API returned 500"),
    ]

    for level_name, level_value in levels:
        shown = [name for lvl, name, _ in messages if lvl >= level_value]
        hidden = [name for lvl, name, _ in messages if lvl < level_value]
        print(f"  level={level_name:<10} shows: {shown}  |  hides: {hidden}")

    print()
    print("  In production: use INFO (see normal ops + all problems)")
    print("  In development: use DEBUG (see everything)\n")


# ============================================================
# PART 5: Structured Logging (JSON format)
# ============================================================
class JSONFormatter(logging.Formatter):
    """Emit log records as JSON — easier to search and analyze."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "time": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Include extra fields if any were passed
        for key in ("model", "tokens", "duration", "prompt_len"):
            if hasattr(record, key):
                log_entry[key] = getattr(record, key)
        return json.dumps(log_entry, ensure_ascii=False)


def show_structured_logging():
    """Show JSON structured logging output."""
    print("=== Structured (JSON) Logging ===\n")

    json_logger = logging.getLogger("structured_demo")
    json_logger.setLevel(logging.DEBUG)

    if not json_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        json_logger.addHandler(handler)
        json_logger.propagate = False

    # Normal log
    json_logger.info("Yasmine a envoyé une question")

    # Log with extra context fields
    json_logger.info(
        "Réponse Mistral reçue",
        extra={"model": "mistral-small", "tokens": 73, "duration": 1.24, "prompt_len": 42}
    )
    json_logger.error("Requête échouée — Mehdi doit vérifier sa clé API", extra={"duration": 30.0})

    print("\n  JSON logs are easy to filter:")
    print("  jq '.[] | select(.tokens > 100)' ai_requests.log   # find expensive calls")
    print("  jq '.[] | select(.level == \"ERROR\")' ai_requests.log  # find all errors\n")


# ============================================================
# MAIN
# ============================================================
async def main():
    setup_basic_logging()
    show_log_levels()
    show_structured_logging()

    # Setup the production logger — writes to ai_requests.log
    logger = setup_production_logging("ai_requests.log")
    logger.info("=== Starting AI App Session ===")

    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        logger.warning("MISTRAL_API_KEY not set — skipping live API calls")
        print("  Set MISTRAL_API_KEY in .env to test live logging.\n")
    else:
        print("\n=== Live API Calls With Logging ===\n")

        prompts = [
            "Sfax est connue pour quoi ? Réponds en une phrase.",
            "Quel est l'ingrédient principal du harissa tunisien ?",
            "En une phrase, qu'est-ce que le musée du Bardo ?",
        ]

        for prompt in prompts:
            reply = await call_mistral_with_logging(prompt, api_key, logger)
            if reply:
                print(f"  → {reply[:100]}\n")
            await asyncio.sleep(1)  # be polite to the rate limit

    logger.info("=== Session ended ===")
    print("  Logs written to: ai_requests.log\n")


if __name__ == "__main__":
    asyncio.run(main())

    print("--- Key Takeaways ---")
    print("1. Use logging module, not print() — it has levels, formatting, and file output")
    print("2. Log 5 events per API call: started, succeeded, timed out, rate limited, failed")
    print("3. Never log API keys, full prompts (if sensitive), or personal user data")
    print("4. Use RotatingFileHandler to cap log file size automatically")
    print("5. INFO level for terminal, DEBUG level for files — full detail without clutter")
    print("6. Structured (JSON) logs are easier to search and analyze at scale")
