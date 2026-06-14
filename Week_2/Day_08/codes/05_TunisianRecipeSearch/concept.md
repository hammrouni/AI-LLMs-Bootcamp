# 05 - Tunisian Recipe Search (Capstone)

---

## 📦 Packages

```bash
pip install chromadb mistralai python-dotenv
```

---

## What is This Capstone?

A **mini semantic-search engine** over a small dataset of Tunisian recipes. It ties together everything from concepts 01–04:
1. Take raw recipe text (concept 01)
2. Embed it with Mistral (concept 01)
3. Compare with cosine similarity (concept 02) — handled by the vector DB
4. Store and query through ChromaDB (concept 03) — or Qdrant from concept 04

A user types something in French, Arabic, English, or darija — the engine finds the closest matching recipes.

Think of it like the search bar on a Tunisian recipe site, except it understands *meaning*, not just exact words.

---

## What is the Problem?

### A recipe site can't ship a real search box with `LIKE '%query%'`

Hayet runs a Tunisian recipe site. Her current search uses SQL `LIKE`. Problems:
- User types "spicy fish" → 0 results (no recipe titled that way)
- User types "كسكسي" → misses every recipe in French
- User types "akel taw el-ftour" → no chance

She needs a search that understands meaning across languages. She needs embeddings.

---

## What is the Solution? End-to-End Semantic Search!

**Pipeline:**

```
[raw recipes] → [embed once] → [store in ChromaDB] → [user query] → [embed query] → [top-k results]
```

That's it. Every concept this day was a piece of this pipeline. Now we wire them together.

---

## How It Works in Python

### Architecture

| Step | Where the data lives | What runs |
|---|---|---|
| 1 | `RECIPES` list (in `demo.py`) | Defined at module load |
| 2 | Mistral API | `client.embeddings.create(...)` once |
| 3 | `./recipe_search_db/` | `collection.add(...)` once |
| 4 | Terminal | User types a query |
| 5 | Mistral API | Embed the query (1 call) |
| 6 | `./recipe_search_db/` | `collection.query(...)` returns top-k |
| 7 | Terminal | Print results |

### The Golden Rule:
- **Embed documents once, query embeddings every time.** Re-embedding the corpus on every run wastes API calls and money. Use `collection.count()` to detect "already indexed."

### Basic Usage

```python
def build_index(recipes, collection, mistral):
    """Embed and store recipes in ChromaDB (once)."""
    if collection.count() >= len(recipes):
        return  # already indexed

    texts = [r["text"] for r in recipes]
    embeddings = [
        d.embedding
        for d in mistral.embeddings.create(model="mistral-embed", inputs=texts).data
    ]
    collection.add(
        documents=texts,
        embeddings=embeddings,
        metadatas=[{"region": r["region"], "type": r["type"]} for r in recipes],
        ids=[r["id"] for r in recipes],
    )


def search(query, collection, mistral, k=3):
    """Embed query and return top-k recipes."""
    query_vec = mistral.embeddings.create(
        model="mistral-embed", inputs=[query]
    ).data[0].embedding

    return collection.query(query_embeddings=[query_vec], n_results=k)
```

### BAD vs GOOD

```python
# BAD — re-embedding every search
def search_bad(query, recipes):
    all_vecs = [embed(r["text"]) for r in recipes]  # re-embeds EVERYTHING
    q_vec = embed(query)
    return rank(q_vec, all_vecs)

# GOOD — embed corpus once, embed only the query each call
def search_good(query, collection):
    q_vec = embed(query)
    return collection.query(query_embeddings=[q_vec], n_results=3)
```

---

## Why This Matters for AI Apps

This is the exact pattern behind:
- E-commerce semantic search (Jumia-Tunisia style product search)
- FAQ bots (the retrieval step before the LLM answers)
- Recommendation systems ("recipes you might like")
- Document Q&A for legal, medical, internal company docs

Once you can build this pipeline, you can build a thousand AI-powered features.

```
Hayet's site, before: 30% of searches return zero results.
Hayet's site, after : 95% of searches return at least one relevant recipe.
```

The Day 8 concepts compose into a real, useful product. Tomorrow we make it bigger and smarter.
