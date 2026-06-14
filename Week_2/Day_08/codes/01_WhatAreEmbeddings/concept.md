# 01 - What Are Embeddings

---

## 📦 Packages

```bash
pip install mistralai numpy python-dotenv
```

---

## What is an Embedding?

An **embedding** is a list of numbers (a vector) that represents the *meaning* of a piece of text. Two pieces of text with similar meaning end up close to each other in this number space, even if they don't share the same words.

Think of it like a map of a city:
- Every shop in Tunis has GPS coordinates (latitude, longitude)
- Two shops near each other have close coordinates
- A bakery in La Marsa and a bakery in Carthage are both bakeries — their coordinates are close because they're in the same neighborhood
- A bakery in Sfax has totally different coordinates because it's far away

An embedding does the same thing — but instead of 2 coordinates, it uses 512, 768, or 1024 numbers, and instead of geography, it maps *meaning*.

---

## What is the Problem?

### Keyword search fails when words differ but meaning is the same

If Bilel searches for "couscous au poisson" in a recipe app and the recipe is titled "كسكسي بالحوت", a normal text search returns zero results. Same dish, different language, zero match.

```
User query:  "couscous au poisson"
DB recipe:   "كسكسي بالحوت"

Keyword match: 0% — no shared characters
Reality:       100% — same meaning
```

Traditional databases only know exact string matching. They have no idea that "couscous", "كسكسي", and "kouskousi" all mean the same thing.

---

## What is the Solution? Embeddings!

**Embeddings** convert text into vectors of numbers where the *meaning* is encoded into the numbers themselves. Now "couscous au poisson" and "كسكسي بالحوت" produce vectors that are very close to each other — because the underlying meaning is the same.

Once you have vectors instead of strings, you compare by *distance*. Close vectors = similar meaning. Far vectors = different meaning. Language, spelling, and word order stop mattering.

---

## How It Works in Python

### Key words to know:

| Keyword / Concept | What it means |
|---|---|
| `vector` | A list of numbers like `[0.12, -0.84, 0.33, ...]` |
| `dimensions` | The length of the vector — Mistral uses 1024 |
| `embedding model` | The AI that converts text → vector |
| `vector space` | The N-dimensional space where vectors live |
| `proximity` | How close two vectors are (= how similar their meaning is) |

### The Golden Rule:
- **You must use the same embedding model for the query and the documents.** If you embed documents with `mistral-embed` but queries with another model, the vectors live in different spaces and comparisons are meaningless.

### Basic Usage

```python
# Convert text to a vector with Mistral
from mistralai.client import Mistral
import os

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

# Embed a single text
response = client.embeddings.create(
    model="mistral-embed",
    inputs=["Yasmine loves harissa from Nabeul"]
)

vector = response.data[0].embedding
print(f"Length: {len(vector)}")       # 1024
print(f"First 5 numbers: {vector[:5]}")
```

### BAD vs GOOD

```python
# BAD — embedding one text per API call (slow + costly)
for sentence in sentences:
    response = client.embeddings.create(model="mistral-embed", inputs=[sentence])

# GOOD — batch embedding in a single call
response = client.embeddings.create(model="mistral-embed", inputs=sentences)
vectors = [d.embedding for d in response.data]
```

---

## Why This Matters for AI Apps

When building AI apps, you often need to:
- Find documents related to a user question (RAG)
- Group similar tickets in a customer support tool
- Recommend products based on what a customer browsed
- Cluster reviews of Tunisian restaurants by topic

With **keyword search**: misses synonyms, misses translations, misses paraphrases — frustrating users.
With **embeddings**: finds anything that *means* the same thing — even across Arabic, French, and English.

```
Query "akel taw el-mghreb" (Tunisian darija)
  → embedding finds "dinner restaurants near sunset" (English)
  → because the meaning is the same
```
