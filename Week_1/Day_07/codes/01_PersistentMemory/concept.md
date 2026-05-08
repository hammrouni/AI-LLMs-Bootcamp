# 01 - Persistent Memory (Building on Day 06's RealChatbot)

---

## What We Had in Day 06

In **Day 06's RealChatbot**, conversation history was stored **in-memory** only:

```python
# Day 06: In-memory buffer
buffer = ConversationBuffer(max_size=50)
buffer.add_message("user", "I love red shirts")
buffer.add_message("assistant", "Got it, you like red!")
# When the chatbot closes → data is GONE
```

---

## What is Persistent Memory?

**Persistent Memory** means saving conversation data to a database (or file) so it survives after the chatbot closes. The next time the user talks to the chatbot, it remembers everything from before.

Think of it like a journal:
- You write down everything you and a friend discuss
- The journal stays on a shelf after the conversation ends
- Months later, you pick it up and remember exactly what was said
- Your friend comes back and says "remember when we talked about...?"—you flip through the journal and find it

A chatbot without persistent memory forgets everything. With it, memories last forever.

---

## What is the Problem?

### Everything Disappears When the Chatbot Closes

In-memory buffers (like in Day 06) only exist while the chatbot is running. Close the chatbot, restart it, and all history is gone.

```
Session 1: User: "I love red shirts"
          AI: "Got it, you like red!"

[Chatbot closes and restarts]

Session 2: User: "Do you remember what I said?"
          AI: "No, I have no record of our previous conversation"
```

Users feel like the chatbot doesn't know them.

---

## What is the Solution? Persistent Storage!

**Persistent Memory** saves all messages to a database. Every API call reads from the database, not just from memory. This way:
1. Conversations survive restarts
2. Users feel understood across sessions
3. You can analyze conversation history
4. You have a legal record of what was said

---

## How It Works in Python

### Key words to know:

| Keyword / Concept | What it means |
|---|---|
| `database` | Permanent storage (SQLite, PostgreSQL, MongoDB) |
| `schema` | The structure: tables, columns, types |
| `CRUD` | Create, Read, Update, Delete operations |
| `query` | Asking the database for data |
| `transaction` | A group of operations that all succeed or all fail |

### The Golden Rule:
- **Write to the database immediately after each exchange.** Don't wait; don't batch. One message = one write.

### Basic Usage

```python
# What this example shows: storing and retrieving messages from SQLite

import sqlite3

class PersistentChatHistory:
    def __init__(self, db_path="chat_history.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        # Create table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                conversation_id TEXT,
                role TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def save_message(self, conversation_id, role, content):
        # Insert a message
        self.cursor.execute('''
            INSERT INTO messages (conversation_id, role, content)
            VALUES (?, ?, ?)
        ''', (conversation_id, role, content))
        self.conn.commit()

    def get_conversation(self, conversation_id):
        # Retrieve all messages in a conversation
        self.cursor.execute('''
            SELECT role, content FROM messages
            WHERE conversation_id = ?
            ORDER BY id ASC
        ''', (conversation_id,))
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

# Example usage
db = PersistentChatHistory()
db.save_message("user_123", "user", "Hi, my name is Bilel")
db.save_message("user_123", "assistant", "Nice to meet you, Bilel!")

history = db.get_conversation("user_123")
for role, content in history:
    print(f"{role}: {content}")
```

### How to Choose

| Option | When to use | When NOT to use |
|--------|------------|----------------|
| SQLite | Single-server, simple schema, < 1 million messages | Distributed systems, complex queries |
| PostgreSQL | Production, many concurrent users, complex queries | Prototypes, over-engineering |
| MongoDB | Flexible schema, large documents, easy scaling | Simple relational data |

---

## BAD vs GOOD

```python
# BAD — forgetting to save, conversation is lost
def chat_without_persistence(user_message):
    buffer.add_message("user", user_message)
    response = mistral.call(buffer.get_history())
    buffer.add_message("assistant", response)
    return response  # Only in memory!

# GOOD — saving immediately to database
def chat_with_persistence(user_id, user_message):
    db.save_message(user_id, "user", user_message)
    history = db.get_conversation(user_id)
    response = mistral.call(history)
    db.save_message(user_id, "assistant", response)
    return response  # Saved forever!
```

---

## Why This Matters for AI Apps

Real apps must persist:
- **Customer support:** Bilel's issue from Monday must be visible to agent on Thursday
- **Personalized learning:** Student's progress over weeks, not reset each day
- **Sales pipeline:** Track what Yasmine wants across multiple conversations over a month
- **Compliance:** Legal requirement to keep records for audit

Without persistence: data loss, poor UX, legal risk.
With it: continuity, personalization, compliance.

---

## Database Schema Patterns

```python
# Pattern 1: Simple conversations table
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY,
    user_id TEXT,
    started_at DATETIME,
    last_message DATETIME,
    status TEXT  -- 'active', 'closed'
);

CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER,
    role TEXT,  -- 'user' or 'assistant'
    content TEXT,
    timestamp DATETIME,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

# Pattern 2: Include metadata
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER,
    user_id TEXT,
    role TEXT,
    content TEXT,
    tokens INTEGER,  -- track API costs
    timestamp DATETIME,
    metadata JSON  -- flexible extra data
);
```
