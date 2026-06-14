# 03 - ChromaDB Basics

---

## 📦 Packages

```bash
pip install chromadb mistralai python-dotenv
```

---

## What is ChromaDB?

**ChromaDB** is an open-source vector database that runs locally with a single `pip install`. You give it text + vectors, it stores them on disk, and lets you search by similarity in milliseconds.

Think of it like a notebook where you write down recipes:
- Each recipe has a title (id), the recipe text (document), and tags (metadata: "spicy", "Sfax", "fish")
- Instead of flipping through pages, you ask "find me something like this" and ChromaDB points to the right pages
- The notebook stays on your shelf — restart your laptop, the notebook is still there

ChromaDB is the "Hello World" of vector databases. Most teams start here, and many never need anything else.

---

## What is the Problem?

### Storing embeddings in memory dies when your script ends

After Day 8 concept 01, you can compute embeddings. But what do you do with them?

```python
embeddings = []
for doc in big_list_of_documents:
    embeddings.append(get_embedding(doc))   # 100k API calls, hours of time

# Script ends -> embeddings list is GONE
# Next run: re-compute everything from scratch
```

You need to:
1. Save embeddings to disk so you only compute them once
2. Search them fast (no looping through 100k vectors by hand)
3. Attach metadata (filename, date, author) so you can filter later

A plain list or a JSON file can't do this well. You need a database designed for vectors.

---

## What is the Solution? ChromaDB!

**ChromaDB** stores embeddings, documents, and metadata together, and lets you query by similarity with one line of code. Everything persists to a local folder. No server, no Docker, no config — just `import chromadb`.

```python
collection.add(documents=[...], embeddings=[...], ids=[...])
results = collection.query(query_embeddings=[...], n_results=5)
```

That's the whole API surface for 90% of use cases.

---

## How It Works in Python

### Key words to know:

| Keyword / Concept | What it means |
|---|---|
| `client` | The ChromaDB instance — `chromadb.PersistentClient(path="./chroma_db")` |
| `collection` | A named bucket of documents (like a table in SQL) |
| `id` | A unique string per document (e.g., `"recipe_001"`) |
| `document` | The original text (kept for display purposes) |
| `embedding` | The vector (provided by you, or computed by Chroma's default model) |
| `metadata` | Dict of filterable fields: `{"region": "Sfax", "spicy": True}` |
| `query` | Search call — returns top-k closest documents |

### The Golden Rule:
- **One collection = one type of data with one embedding model.** Don't mix recipes embedded with Mistral and product reviews embedded with OpenAI in the same collection.

### Basic Usage

```python
import chromadb

# 1. Create a persistent client (saves to disk)
client = chromadb.PersistentClient(path="./chroma_db")

# 2. Get or create a collection
collection = client.get_or_create_collection(name="tunisian_recipes")

# 3. Add documents (Chroma can embed them for you with the default model)
collection.add(
    documents=[
        "Couscous au poisson de Sfax avec harissa",
        "Brik à l'oeuf de Tunis",
        "Lablabi from La Goulette with cumin",
    ],
    metadatas=[
        {"region": "Sfax",  "type": "main"},
        {"region": "Tunis", "type": "starter"},
        {"region": "Tunis", "type": "soup"},
    ],
    ids=["recipe_1", "recipe_2", "recipe_3"],
)

# 4. Query by text — Chroma embeds the query automatically
results = collection.query(
    query_texts=["spicy fish dish"],
    n_results=2,
)

for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
    print(f"{meta['region']:>6} | {doc}")
```

### BAD vs GOOD

```python
# BAD — using an in-memory client (data disappears on restart)
client = chromadb.Client()

# GOOD — persistent client (survives restarts)
client = chromadb.PersistentClient(path="./chroma_db")
```

```python
# BAD — re-embedding every time you start the script
collection.add(documents=all_docs, ids=ids)   # runs every time

# GOOD — check first if data is already there
if collection.count() == 0:
    collection.add(documents=all_docs, ids=ids)
```

---

## Why This Matters for AI Apps

When building AI apps, you almost always need a vector store:
- A FAQ bot that searches past Q&A
- A search box on a Tunisian e-commerce site that understands "rouge" = "أحمر"
- A document Q&A app where Nour uploads PDFs and asks questions

With a plain Python list: re-embeds every restart, slow linear search, no metadata filtering.
With ChromaDB: persisted, indexed, filterable — production-ready in 10 lines of code.

```
Sync setup time: pip install chromadb -> ~5 seconds.
First query time on 10k docs: ~10 milliseconds.
```
