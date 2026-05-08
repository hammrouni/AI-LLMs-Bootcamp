# 04 - Production-Grade Error Handling (Building on Day 06)

---

## What You Had in Day 06

In **Day 06's RealChatbot**, there was basic error handling:
- If API fails or no key, it returns simulated response
- Graceful fallback, but not comprehensive

Day 07 adds **production-grade** error handling:
- Retry logic with exponential backoff
- Specific error types (timeouts vs rate limits vs auth errors)
- Detailed logging for debugging
- User-friendly error messages
- Transaction rollbacks for database failures
- Graceful degradation for different failure modes

---

## What is Production-Grade Error Handling?

**Error Handling** is planning for and gracefully managing things that go wrong: API failures, bad input, timeouts, database errors.

Without it, one error crashes the chatbot. With it, the chatbot keeps working and tells the user what happened.

---

## What is the Problem?

### Unhandled Errors Crash Everything

If the API times out and you don't handle it, the chatbot crashes and users lose everything.

---

## What is the Solution? Comprehensive Error Handling!

---

## How It Works in Python

### Key words to know:

| Keyword / Concept | What it means |
|---|---|
| `try-except` | Catch specific errors, handle gracefully |
| `exponential backoff` | Retry with increasing delays (1s, 2s, 4s, 8s...) |
| `finally` | Code that runs whether success or failure |
| `logging` | Record what happened for debugging |
| `fallback` | Default response when API fails |

### Basic Usage - Simple Error Handling

```python
# BAD — no error handling
response = mistral.call(messages)
return response

# GOOD — catches errors, returns fallback
try:
    response = mistral.call(messages)
    return response
except APITimeout:
    return "I'm thinking... (API is slow). Please ask again in a moment."
except APIError as e:
    return f"Sorry, I encountered an error: {str(e)[:50]}"
finally:
    # Always runs: cleanup, logging, etc
    logger.info(f"API call completed")
```

### Advanced Usage - Retry Logic with Exponential Backoff

```python
import time

def call_with_retry(messages, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = mistral.call(messages)
            logger.info(f"Success on attempt {attempt + 1}")
            return response
        except APIRateLimit:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 1s, 2s, 4s
                logger.warning(f"Rate limited. Retrying in {wait_time}s")
                time.sleep(wait_time)
            else:
                raise
        except APITimeout as e:
            logger.error(f"Timeout on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                raise
    
    return None  # Should not reach here
```

### BAD vs GOOD

```python
# BAD — crashes on error, data lost
def chat_unsafe(user_id, message):
    db.save_message(user_id, "user", message)
    response = mistral.call(get_history(user_id))  # No error handling!
    db.save_message(user_id, "assistant", response)
    return response

# GOOD — catches errors, saves state, logs for debugging
def chat_safe(user_id, message):
    try:
        db.save_message(user_id, "user", message)
        response = mistral.call(get_history(user_id))
        db.save_message(user_id, "assistant", response)
        return response
    except APIError as e:
        logger.error(f"API failed for user {user_id}: {e}")
        return "I had trouble processing that. Please try again."
    except DatabaseError as e:
        logger.critical(f"Database error for user {user_id}: {e}")
        return "System issue. Your message was saved. Please try again."
    except Exception as e:
        logger.critical(f"Unexpected error for user {user_id}: {e}")
        return "Something went wrong. Please contact support."
```

---

## Key Errors to Handle

1. **API errors** (timeout, rate limit, invalid key)
2. **Input errors** (empty, too long, invalid format)
3. **Database errors** (connection failed, query failed)
4. **Logic errors** (division by zero in calculations)

---

## Why This Matters for AI Apps

Good error handling:
- **Keeps chatbot running** (resilience)
- **Tells users what went wrong** (transparency)
- **Allows recovery** (user can retry, not stuck)
- **Prevents data loss** (save state before risky operations)
- **Makes debugging easier** (logs show what happened)

---
