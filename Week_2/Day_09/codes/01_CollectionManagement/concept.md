# 01 - Collection Management

---

## 📦 Packages

```bash
pip install chromadb python-dotenv
```

---

## What is a Collection?

A **collection** is a named container of documents that share the same embedding model and the same purpose. Like a table in SQL: it has a name, a structure (vector dimension), and rules about what goes in.

Think of a Tunisian supermarket like Carrefour Tunis:
- Aisle 1: bakery items (bread, msemen, baguettes)
- Aisle 2: dairy (laban, yoghurt, cheese)
- Aisle 3: cleaning products

You don't put the laban next to the floor cleaner. Same idea: you don't put recipe embeddings next to user-profile embeddings. Each collection has its own purpose.

---

## What is the Problem?

### Mixing different data types in one collection breaks search

Yasmine builds a Tunisian recipe app and decides to keep everything in one collection: recipes, users, restaurant reviews, even comments. After a month, every search returns garbage:

```
Query: "spicy fish couscous"
Result 1: "Yasmine, age 27, lives in Tunis"     ← user profile, not a recipe
Result 2: "Great service at Café Plaza"          ← review, not a recipe
Result 3: actual recipe somewhere down the list
```

Why? Different content types live in different regions of the vector space, but they're all in the same haystack. Filters help, but starting with separate collections is cleaner and faster.

---

## What is the Solution? Multiple Collections!

**One collection per data type.** Each collection holds documents that answer the same kind of question. Query the right collection for the question you're asking.

```
recipes_collection          → "what dish is similar to X?"
users_collection            → "find similar customers"
restaurant_reviews_collection → "what do people say about Y?"
```

Bonus: smaller collections = faster searches. A collection with 5k recipes is way faster to search than a soup of 50k mixed items.

---

## How It Works in Python

### Key words to know:

| Keyword / Concept | What it means |
|---|---|
| `client` | The Chroma client object |
| `create_collection` | Make a new collection (errors if it exists) |
| `get_collection` | Open an existing one (errors if missing) |
| `get_or_create_collection` | Safest — opens or creates |
| `list_collections` | List all collection names in the client |
| `delete_collection` | Remove permanently |
| `collection.count()` | Number of documents inside |

### The Golden Rule:
- **Decide the schema before you start adding documents.** Once a collection has data, changing the embedding model or dimension means rebuilding it from scratch.

### Basic Usage

```python
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")

# Idempotent — safe to call on every startup
recipes = client.get_or_create_collection(name="recipes")
users   = client.get_or_create_collection(name="users")
reviews = client.get_or_create_collection(name="restaurant_reviews")

# List everything you have
for c in client.list_collections():
    print(f"{c.name}: {c.count()} docs")

# Get rid of a collection that's gone stale
client.delete_collection("old_test_collection")
```

### How to Choose

| Pattern | When to use | When NOT to use |
|--------|------------|----------------|
| One huge collection + filters | < 100 docs, prototyping only | Anything real |
| One collection per data type | The default — always start here | When data is truly heterogeneous and tiny |
| Per-tenant collections | Multi-tenant SaaS (one per customer) | Single-tenant apps |

### BAD vs GOOD

```python
# BAD — one mega collection
collection = client.get_or_create_collection("everything")
collection.add(documents=["Recipe", "User profile", "Review"], ids=["1", "2", "3"])

# GOOD — separate, named collections
recipes_col  = client.get_or_create_collection("recipes")
users_col    = client.get_or_create_collection("users")
reviews_col  = client.get_or_create_collection("reviews")
```

---

## Why This Matters for AI Apps

Real apps deal with multiple kinds of content:
- A Tunisian delivery app (Jumia-style) has products, customer reviews, restaurant menus, and support tickets — four collections, four search experiences.
- A school platform has lecture notes, student questions, and teacher feedback — three collections.
- A bank chatbot has FAQ entries, transaction descriptions, and policy documents — three collections.

Separating by collection keeps each search experience focused, fast, and easy to debug.
