"""
01 - Persistent Memory Demo
============================
Demonstrates storing conversations in SQLite database.

HOW TO RUN THIS FILE:
1. python demo.py
(Creates chat_history.db in current directory)
"""

import sqlite3
import json
from datetime import datetime


# ============================================================
# PART 1: Simple SQLite Database for Messages
# ============================================================

def show_simple_persistence():
    """Demonstrate basic message persistence."""
    print("=== PART 1: Simple Persistent Storage ===\n")

    # File-based database — persists after script ends
    conn = sqlite3.connect("part1_messages.db")
    cursor = conn.cursor()

    # Drop and recreate for clean demo output
    cursor.execute("DROP TABLE IF EXISTS messages")
    cursor.execute('''
        CREATE TABLE messages (
            id INTEGER PRIMARY KEY,
            conversation_id TEXT,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Save some messages
    messages = [
        ("user_bilel", "user", "Hi, my name is Bilel"),
        ("user_bilel", "assistant", "Nice to meet you, Bilel from Tunis!"),
        ("user_bilel", "user", "Can you help me learn Python?"),
        ("user_bilel", "assistant", "Absolutely! What would you like to learn?"),
    ]

    for conv_id, role, content in messages:
        cursor.execute('''
            INSERT INTO messages (conversation_id, role, content)
            VALUES (?, ?, ?)
        ''', (conv_id, role, content))

    conn.commit()

    # Retrieve and display
    cursor.execute('''
        SELECT role, content, timestamp FROM messages
        WHERE conversation_id = ?
        ORDER BY id ASC
    ''', ("user_bilel",))

    print("Stored Conversation for user_bilel:")
    for role, content, timestamp in cursor.fetchall():
        print(f"  {role.upper()}: {content}")

    conn.close()
    print()


# ============================================================
# PART 2: Conversation-Based Database
# ============================================================

def show_conversation_structure():
    """Demonstrate organizing conversations with metadata."""
    print("=== PART 2: Conversation-Based Storage ===\n")

    conn = sqlite3.connect("part2_conversations.db")
    cursor = conn.cursor()

    # Drop and recreate for clean demo output
    cursor.execute("DROP TABLE IF EXISTS messages")
    cursor.execute("DROP TABLE IF EXISTS conversations")
    cursor.execute('''
        CREATE TABLE conversations (
            id INTEGER PRIMARY KEY,
            user_id TEXT,
            title TEXT,
            started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_message DATETIME,
            message_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active'
        )
    ''')

    # Create messages table with foreign key
    cursor.execute('''
        CREATE TABLE messages (
            id INTEGER PRIMARY KEY,
            conversation_id INTEGER,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
    ''')

    conn.commit()

    # Insert a conversation
    cursor.execute('''
        INSERT INTO conversations (user_id, title, last_message, message_count)
        VALUES (?, ?, ?, ?)
    ''', ("yasmine_123", "Python Learning", datetime.now(), 0))

    conv_id = cursor.lastrowid
    conn.commit()

    # Add messages to that conversation
    conv_messages = [
        ("user", "What's a list?"),
        ("assistant", "A list is an ordered collection of items."),
        ("user", "Can I add items to it?"),
        ("assistant", "Yes, use .append() method"),
    ]

    for role, content in conv_messages:
        cursor.execute('''
            INSERT INTO messages (conversation_id, role, content)
            VALUES (?, ?, ?)
        ''', (conv_id, role, content))

    # Update conversation metadata
    cursor.execute('''
        UPDATE conversations
        SET message_count = ?, last_message = ?
        WHERE id = ?
    ''', (len(conv_messages), datetime.now(), conv_id))

    conn.commit()

    # Display conversation with metadata
    cursor.execute('SELECT id, title, started_at, message_count FROM conversations WHERE user_id = ?',
                   ("yasmine_123",))

    print("Conversation Metadata:")
    for fetched_conv_id, title, started_at, msg_count in cursor.fetchall():
        print(f"  Conversation: {title}")
        print(f"  Started: {started_at}")
        print(f"  Messages: {msg_count}\n")

    # Get messages from conversation
    cursor.execute('SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY id ASC',
                   (fetched_conv_id,))

    print("  Messages:")
    for role, content in cursor.fetchall():
        print(f"    {role.upper()}: {content}")

    conn.close()
    print()


# ============================================================
# PART 3: Querying Conversation History
# ============================================================

def show_querying():
    """Demonstrate retrieving specific data from database."""
    print("=== PART 3: Querying Conversation History ===\n")

    conn = sqlite3.connect("part3_queries.db")
    cursor = conn.cursor()

    # Drop and recreate for clean demo output
    cursor.execute("DROP TABLE IF EXISTS messages")
    cursor.execute("DROP TABLE IF EXISTS conversations")
    cursor.execute('''CREATE TABLE conversations (
        id INTEGER PRIMARY KEY, user_id TEXT, created DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    cursor.execute('''CREATE TABLE messages (
        id INTEGER PRIMARY KEY, conversation_id INTEGER, role TEXT, content TEXT,
        created DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    # Insert test data: 3 conversations, 2 users
    users = [("bilel", "conv_1"), ("bilel", "conv_2"), ("yasmine", "conv_3")]
    for user_id, conv_title in users:
        cursor.execute('INSERT INTO conversations (user_id, created) VALUES (?, CURRENT_TIMESTAMP)',
                       (user_id,))
        conv_id = cursor.lastrowid

        # Add sample messages
        cursor.execute('''INSERT INTO messages (conversation_id, role, content, created)
                          VALUES (?, ?, ?, CURRENT_TIMESTAMP)''',
                       (conv_id, "user", f"Message from {user_id}"))
        cursor.execute('''INSERT INTO messages (conversation_id, role, content, created)
                          VALUES (?, ?, ?, CURRENT_TIMESTAMP)''',
                       (conv_id, "assistant", "Response"))

    conn.commit()

    # Query 1: Get all conversations for a user
    cursor.execute('''SELECT COUNT(*) FROM conversations WHERE user_id = ?''', ("bilel",))
    bilel_convs = cursor.fetchone()[0]
    print(f"Total conversations for Bilel: {bilel_convs}")

    # Query 2: Get user messages (not assistant)
    cursor.execute('''SELECT COUNT(*) FROM messages WHERE role = ?''', ("user",))
    user_messages = cursor.fetchone()[0]
    print(f"Total user messages: {user_messages}")

    # Query 3: Get recent conversation
    cursor.execute('''
        SELECT c.id, c.user_id, COUNT(m.id) as msg_count
        FROM conversations c
        LEFT JOIN messages m ON c.id = m.conversation_id
        GROUP BY c.id
        ORDER BY c.created DESC
        LIMIT 1
    ''')
    try:
        recent = cursor.fetchone()
        if recent:
            print(f"Most recent conversation ID: {recent[0]}, Messages: {recent[2]}")
    except Exception:
        print("Query completed")

    conn.close()
    print()


# ============================================================
# PART 4: Backup and Export
# ============================================================

def show_backup():
    """Demonstrate exporting conversation data."""
    print("=== PART 4: Backup & Export ===\n")

    conn = sqlite3.connect("part4_backup.db")
    cursor = conn.cursor()

    # Drop and recreate for clean demo output
    cursor.execute("DROP TABLE IF EXISTS messages")
    cursor.execute('''CREATE TABLE messages (
        id INTEGER PRIMARY KEY, conversation_id TEXT, role TEXT, content TEXT,
        created DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    messages = [
        ("conv_1", "user", "Hello"),
        ("conv_1", "assistant", "Hi there!"),
        ("conv_2", "user", "How are you?"),
        ("conv_2", "assistant", "I'm doing great!"),
    ]

    for conv_id, role, content in messages:
        cursor.execute('''INSERT INTO messages (conversation_id, role, content, created)
                          VALUES (?, ?, ?, CURRENT_TIMESTAMP)''',
                       (conv_id, role, content))

    conn.commit()

    # Export as JSON
    cursor.execute('SELECT conversation_id, role, content FROM messages')
    rows = cursor.fetchall()

    export_data = {}
    for conv_id, role, content in rows:
        if conv_id not in export_data:
            export_data[conv_id] = []
        export_data[conv_id].append({"role": role, "content": content})

    print("Exported as JSON:")
    print(json.dumps(export_data, indent=2))

    conn.close()
    print()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("PERSISTENT MEMORY DEMONSTRATION")
    print("=" * 60 + "\n")

    show_simple_persistence()
    show_conversation_structure()
    show_querying()
    show_backup()

    print("--- Key Takeaways ---")
    print("1. Use SQLite for local storage, PostgreSQL for production")
    print("2. Create tables: conversations + messages (with foreign key)")
    print("3. Save immediately after each exchange (no batching)")
    print("4. Query by user_id, conversation_id, date range")
    print("5. Export conversations to JSON for analysis or backup")
    print("6. Include metadata: timestamps, message count, status")
