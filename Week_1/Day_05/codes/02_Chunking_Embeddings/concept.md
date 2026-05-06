# 02 - Chunking & Embeddings

---

## 📦 Packages

**Requirements**: Python 3.11 or 3.12 (not 3.13+)

```bash
pip install llama-index llama-index-embeddings-mistralai python-dotenv
```

For Mistral embeddings support, also install:
```bash
pip install llama-index-embeddings-mistralai
```

---

## The Problem: Long Documents

Raw documents are **too big** to fit in a single context window:

- A 50-page PDF = 25,000+ tokens
- Mistral context limit = 32K (Mistral 7B) or 128K (Mistral Large)
- **Result**: lose important context, or waste tokens on irrelevant data

**Solution**: Split documents into smaller, overlapping chunks.

---

## Chunking Strategy

**Chunking** = dividing documents into fixed-size pieces with overlap.

```
Original Document (10,000 tokens)
        ↓
    Chunking (512 tokens per chunk, 20% overlap)
        ↓
    [Chunk 1: tokens 0-512]
    [Chunk 2: tokens 409-921]    ← 103 tokens overlap
    [Chunk 3: tokens 818-1330]
    ...
    [Chunk N: tokens 9500-10000]
```

**Why overlap?** Prevents context cutoff — a sentence split across chunks gets seen twice.

---

## Chunk Size Trade-offs

| Size | Pros | Cons |
|------|------|------|
| **256 tokens** | High precision, less noise | Loses context, many chunks |
| **512 tokens** (⭐ recommended) | Balance between precision & context | — |
| **1024 tokens** | More complete context | May include irrelevant text |
| **2048+ tokens** | Maximum context | Dilutes signal-to-noise |

**Rule of thumb**: 512 tokens (~2000 characters) with 20% overlap (100 tokens).

---

## What are Embeddings?

**Embedding** = converting text into a vector (list of numbers).

```python
text = "What is machine learning?"
embedding = [0.12, -0.45, 0.78, ..., 0.23]  # 1024 dimensions (Mistral)
```

**Key insight**: Similar texts → similar embeddings (close in vector space).

```
"Machine Learning" → [0.12, -0.45, 0.78, ...]
"ML"                → [0.11, -0.46, 0.77, ...]  ← very close (high cosine similarity)

"Machine Learning" → [0.12, -0.45, 0.78, ...]
"Pizza"             → [-0.89, 0.22, -0.34, ...] ← very far (low cosine similarity)
```

---

## Embedding Models

| Model | Dimensions | Cost | Speed | Quality | Use Case |
|-------|-----------|------|-------|---------|----------|
| **mistral-embed** | 1024 | 💰 cheap | ⚡ fast | ⭐⭐⭐⭐ | **Recommended** |
| **HuggingFace (open source)** | varies | free | varies | ⭐⭐⭐ | Privacy-first |

**Default**: Use `mistral-embed` — it's fast, cheap, and accurate.

---

## Chunking in LlamaIndex

```python
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core import Document

# Load documents
documents = [
    Document(text="Your long document text here..."),
    Document(text="Another document..."),
]

# Split into chunks
parser = SimpleNodeParser.from_defaults(
    chunk_size=512,           # tokens per chunk
    chunk_overlap=128,        # 25% overlap
)
nodes = parser.get_nodes_from_documents(documents)

# Result: list of Node objects (text + metadata)
for node in nodes:
    print(node.text)          # The chunk content
    print(node.metadata)      # Source info
```

---

## Computing Embeddings with Mistral

Mistral provides embeddings via the `mistral-embed` model.

```python
from llama_index.embeddings.mistralai import MistralAIEmbedding

embed_model = MistralAIEmbedding(
    api_key="your-mistral-api-key",
    model="mistral-embed"
)

# Embed a single chunk
embedding = embed_model.get_text_embedding("Some text here")
print(len(embedding))  # 1024 dimensions
```

**Note**: Mistral embeddings use the same vector format, making it easy to swap providers without changing code.

Embeddings are computed **lazily** — only when you create a VectorStoreIndex.

---

## Chunk Size Decision Tree

```
Question: How long are typical queries?
├─ Short (< 100 tokens)
│  └─ Use: 256-512 tokens (high precision)
├─ Medium (100-500 tokens)
│  └─ Use: 512 tokens ⭐ (balanced)
└─ Long (> 500 tokens)
   └─ Use: 1024 tokens (more context)

Question: How much data?
├─ < 10K documents
│  └─ Any size works
├─ 10K-100K documents
│  └─ Prefer 256-512 (faster retrieval)
└─ > 100K documents
   └─ Use 256 (minimize search latency)
```

---

## Key Takeaways

1. **Chunk size matters** — affects both retrieval relevance and speed
2. **Overlap prevents cutoff** — use 20-30% overlap
3. **Embeddings = semantic fingerprint** — texts are compared by meaning, not keywords
4. **Use Mistral embeddings by default** — best quality-to-cost ratio
