# 02 - Similarity Metrics

---

## 📦 Packages

```bash
pip install numpy
```

---

## What is a Similarity Metric?

A **similarity metric** is a formula that takes two vectors and returns a single number telling you how close they are. Higher = more similar. Lower = less similar (or the other way around depending on the metric).

Think of it like comparing two restaurants in Tunis:
- Two cafés in La Marsa get a high similarity score (same neighborhood, same vibe)
- A café in La Marsa vs. a fish market in Sfax gets a low score (different things, different places)
- The *formula* you use to compute that score is the similarity metric

In a vector database, the metric is what decides which document gets returned first when a user asks a question.

---

## What is the Problem?

### Not all "distance" formulas are good for text

You have a 1024-dimensional embedding. Now what? "Distance" in 1024 dimensions is not intuitive. Different formulas give different rankings — and some of them are *wrong* for text:

```
Query vector  Q = [0.5, 0.2, ...]
Doc vector A: tiny magnitude, same direction as Q
Doc vector B: huge magnitude, completely different direction

Euclidean distance: says A and Q are far (because magnitudes differ)
Cosine similarity:  says A and Q are very similar (same direction = same meaning)
```

For text, **direction** matters more than **magnitude** — pick the wrong metric and your search returns garbage.

---

## What is the Solution? Cosine Similarity!

**Cosine similarity** measures the angle between two vectors and ignores their length. It's the standard for text embeddings because text meaning is encoded in the *direction* of the vector, not how big the vector is.

Formula:
```
cosine_similarity(A, B) = (A · B) / (|A| × |B|)
```

- Result = **1** → vectors point in the same direction (very similar)
- Result = **0** → vectors are perpendicular (unrelated)
- Result = **-1** → vectors point opposite ways (opposite meaning, rare for embeddings)

---

## How It Works in Python

### Key words to know:

| Keyword / Concept | What it means |
|---|---|
| `dot product` | Element-wise multiply, then sum: `A·B = Σ aᵢ × bᵢ` |
| `norm` (`\|A\|`) | The length of the vector: `sqrt(Σ aᵢ²)` |
| `cosine similarity` | `dot / (norm_A × norm_B)` — range [-1, 1] |
| `euclidean distance` | Straight-line distance: `sqrt(Σ (aᵢ - bᵢ)²)` |
| `dot product (raw)` | Just the dot — fast, but sensitive to magnitude |

### The Golden Rule:
- **Use cosine similarity for text embeddings.** Mistral embeddings are normalized in a way that makes cosine and dot product equivalent, but cosine is the safe default for any provider.

### Basic Usage

```python
import numpy as np

def cosine_similarity(a, b):
    """Compute cosine similarity between two vectors."""
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Example with toy 3-dim vectors
v_couscous_tunis = [0.9, 0.1, 0.2]
v_couscous_sfax  = [0.85, 0.15, 0.25]
v_motorbike      = [0.1, 0.9, 0.8]

print(cosine_similarity(v_couscous_tunis, v_couscous_sfax))  # ~0.99 (same topic)
print(cosine_similarity(v_couscous_tunis, v_motorbike))      # ~0.35 (different)
```

### How to Choose

| Metric | When to use | When NOT to use |
|--------|------------|----------------|
| Cosine similarity | Text embeddings, semantic search | Sparse vectors with magnitude meaning |
| Dot product | When vectors are already normalized (faster) | Vectors of different magnitudes |
| Euclidean distance | Geographic data, image pixels | Text — magnitudes can mislead |

### BAD vs GOOD

```python
# BAD — using euclidean for text embeddings
from numpy.linalg import norm
distance = norm(np.array(query) - np.array(doc))   # punishes long docs

# GOOD — cosine ignores length, captures meaning
similarity = np.dot(query, doc) / (norm(query) * norm(doc))
```

---

## Why This Matters for AI Apps

When building AI apps you need to rank documents by relevance:
- "Show me Tunisian recipes similar to this one"
- "Which past support tickets are like Mehdi's new one?"
- "Find products in our shop that match this image caption"

With the wrong metric: irrelevant top results, users lose trust.
With cosine similarity: the most semantically related items rise to the top.

```
Query: "spicy fish stew"
  cosine top 1:  "Tajine de mérou pimenté de Sfax"   ✓
  euclidean top 1: random short doc that happens to be small  ✗
```
