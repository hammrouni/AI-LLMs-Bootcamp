# 05 - Complete RAG Pipeline

---

## 📦 Packages

**Requirements**: Python 3.11 or 3.12 (not 3.13+)

```bash
pip install llama-index llama-index-readers-file llama-index-embeddings-mistralai llama-index-llms-mistralai python-dotenv
```

---

## The Complete RAG System

RAG = **Retrieval Augmented Generation**. A four-stage pipeline:

```
┌──────────────────────────────────────────────────────┐
│ STAGE 1: INDEXING (one-time)                         │
├──────────────────────────────────────────────────────┤
│ Load documents                                       │
│    ↓                                                 │
│ Split into chunks (512 tokens, 20% overlap)         │
│    ↓                                                 │
│ Compute embeddings (Mistral)                        │
│    ↓                                                 │
│ Store in vector database                            │
└──────────────────────────────────────────────────────┘
                      ↓ (once)
┌──────────────────────────────────────────────────────┐
│ STAGE 2-4: QUERY TIME (repeated)                     │
├──────────────────────────────────────────────────────┤
│ User asks: "What is RAG?"                            │
│    ↓                                                 │
│ [RETRIEVAL] Search vector store → top-k chunks      │
│    ↓                                                 │
│ [CONTEXT] Format chunks + original query            │
│    ↓                                                 │
│ [GENERATION] LLM answers with context               │
│    ↓                                                 │
│ Response: "RAG is... [cites sources]"               │
└──────────────────────────────────────────────────────┘
```

---

## Building RAG in LlamaIndex

### Minimal (5 lines)

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

documents = SimpleDirectoryReader("../sample_documents").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

response = query_engine.query("What is machine learning?")
print(response)
```

### Production-Ready with Mistral (more control)

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.embeddings.mistralai import MistralAIEmbedding
from llama_index.llms.mistralai import MistralAI
import os

# 1. Load documents
documents = SimpleDirectoryReader("../sample_documents").load_data()

# 2. Parse & chunk
parser = SimpleNodeParser.from_defaults(chunk_size=512, chunk_overlap=128)
nodes = parser.get_nodes_from_documents(documents)

# 3. Setup Mistral embeddings
embed_model = MistralAIEmbedding(
    api_key=os.getenv("MISTRAL_API_KEY"),
    model="mistral-embed"
)

# 4. Create index
index = VectorStoreIndex(nodes, embed_model=embed_model)

# 5. Create query engine with Mistral Large
llm = MistralAI(
    api_key=os.getenv("MISTRAL_API_KEY"),
    model="mistral-large-latest",
    temperature=0.0
)
query_engine = index.as_query_engine(llm=llm, similarity_top_k=5)

# 6. Query
response = query_engine.query("Your question here")
print(f"Answer: {response.response}")
for i, node in enumerate(response.source_nodes, 1):
    print(f"\nSource {i} (score: {node.score:.2f}):")
    print(f"  {node.text[:100]}...")
```

---

## RAG Workflow Step-by-Step

### Step 1: Indexing (happens once)

```python
# Your knowledge base
documents = [
    Document(text="Python is a programming language..."),
    Document(text="Machine Learning is a subset of AI..."),
    # ... more documents
]

# Automatic indexing
index = VectorStoreIndex.from_documents(
    documents,
    embed_model=MistralAIEmbedding(model_name="mistral-embed"),
    show_progress=True
)

# Save for later
index.storage_context.persist(persist_dir="./storage")
```

### Step 2: Querying (happens many times)

```python
# Load from disk
from llama_index.core import StorageContext, load_index_from_storage
storage_context = StorageContext.from_defaults(persist_dir="./storage")
index = load_index_from_storage(storage_context)

# Create engine
query_engine = index.as_query_engine(similarity_top_k=5)

# User asks
response = query_engine.query("How do I start with ML?")
```

---

## Why RAG Beats Raw LLMs

| Problem | Raw LLM | RAG |
|---------|---------|-----|
| **Hallucination** | "CEO is John" (wrong) | "CEO is Jane" (from docs) |
| **Old knowledge** | Cutoff in April 2024 | Can include docs from today |
| **Domain docs** | No access to your PDFs | Searches your PDFs |
| **Citations** | Can't prove source | "See page 3 of contract" |
| **Control** | Can't control content | You decide what's searchable |

---

## Common RAG Issues & Fixes

| Issue | Symptom | Cause | Fix |
|-------|---------|-------|-----|
| **Bad retrieval** | "I don't know" responses | Wrong chunks retrieved | Reduce `chunk_size` or use re-ranking |
| **Irrelevant context** | Noisy, verbose answers | Too many chunks (`top_k=20`) | Reduce to `top_k=5` |
| **Slow queries** | > 5 seconds per query | Embedding or LLM latency | Use faster model or cache |
| **Missing context** | LLM says "not found" | Chunks too small | Increase `chunk_size` |
| **Token overflow** | Context too long | Many retrieved chunks | Limit `top_k` or chunk size |

---

## Evaluation: Is Your RAG Working?

### Retrieval Quality

```python
# Ask a test question
response = query_engine.query("What is Python?")

# Check 1: Did we retrieve relevant docs?
for node in response.source_nodes:
    if "Python" in node.text:
        print("✓ Relevant chunk found")
    else:
        print("✗ Irrelevant chunk")

# Check 2: High similarity score?
if response.source_nodes[0].score > 0.7:
    print("✓ Top result is very similar")
else:
    print("✗ Low confidence in top result")

# Check 3: Enough chunks?
if len(response.source_nodes) >= 3:
    print("✓ Multiple sources")
else:
    print("✗ Only single source (may miss context)")
```

### Generation Quality

- Read response: Does it answer the question?
- Check citations: Does it reference sources?
- Test edge cases: What if query has no match?

---

## Deployment Checklist

- [ ] Documents loaded and indexed
- [ ] Embeddings computed (API key working)
- [ ] Vector store persisted
- [ ] Query engine tested with 5+ real questions
- [ ] Retrieval quality acceptable (top-k results relevant)
- [ ] LLM responses factual and cite sources
- [ ] Error handling for edge cases
- [ ] Monitoring/logging in place
- [ ] System tested with actual users
- [ ] Fallback plan for API failures

---

## Next Steps

- **Evaluation**: Build metrics to measure RAG quality (NDCG, MRR, etc.)
- **Optimization**: Add re-ranking, query expansion, hybrid search
- **Scaling**: Move from local vector store to Pinecone
- **Feedback loop**: User feedback → retrain embeddings/re-index
- **Monitoring**: Track latency, error rates, user satisfaction
