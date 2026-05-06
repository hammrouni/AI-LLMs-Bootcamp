# 📅 Day 5: RAG & LlamaIndex 🚀

## ⚠️ IMPORTANT: Python Version Requirements

**Use Python 3.11 or 3.12 — NOT 3.13+**

LlamaIndex and most ML packages do not yet support Python 3.13.

### Why not Python 3.13?
- **LlamaIndex** requires `Python <3.12`
- **NumPy, PyTorch, TensorFlow** have limited 3.13 support
- **Industry standard**: ML community uses Python 3.11/3.12
- **Stability**: 3.13 released Sept 2024, ecosystem still catching up

---

# RAG — Retrieval Augmented Generation

Augment your LLM with real documents for accurate, factual answers.

---

## 🎯 Today's Goal

Learn **RAG (Retrieval Augmented Generation)** — a technique to make AI answer correctly using YOUR documents instead of hallucinating.

**The Problem**: LLMs are like humans who read one book — they make up answers from imagination.

**The Solution**: Give them your real documents (PDFs, text, data), index them with embeddings, and tell the LLM "answer based on THESE documents" — accurate and verified.

---

## 📚 Key Concepts

- **RAG Pipeline**: Load docs → split → embed → store → retrieve → generate
- **Document Loading**: Load PDFs, TXTs, or data files in organized way
- **Chunking**: Split long documents into small chunks (with overlap) for accurate embeddings
- **Embeddings**: Convert text to vectors (numbers) — the "fingerprint" of text
- **Vector Store**: Save vectors in smart database (Pinecone, Weaviate, sqlite-vec)
- **Query Engine**: User asks question → find closest chunks → pass to LLM with context
- **LlamaIndex**: Framework that simplifies all these steps with simple API

---

## 🛠️ Setup Instructions

### Step 1: Create Virtual Environment with Python 3.11 or 3.12

```bash
# Check if Python 3.11 is available
py -3.11 --version

# Create new venv with Python 3.11
py -3.11 -m venv bootcamp

# Activate venv
bootcamp\Scripts\activate     # Windows
source bootcamp/bin/activate  # Mac/Linux
```

### Step 2: Install Dependencies

```bash
# Base packages
pip install llama-index llama-index-readers-file python-dotenv

# Optional: For Mistral embeddings
pip install llama-index-embeddings-mistralai llama-index-llms-mistralai
```

### Step 3: Configure API Keys

```bash
# Copy .env template
copy codes\.env.example codes\.env

# Edit codes\.env and add:
# MISTRAL_API_KEY=your_key_from_console.mistral.ai
# (Optional) OPENAI_API_KEY=your_openai_key_for_embeddings
```

### Step 4: Run Demos

```bash
cd codes\01_Document_Loading
python demo.py
```

---

## 📖 Your Learning Path

**Follow this order** (each depends on the previous):

1. **01_Document_Loading** → Learn to load documents with metadata
2. **02_Chunking_Embeddings** → Split docs and create vector representations
3. **03_Vector_Store** → Store vectors for fast retrieval
4. **04_Query_Engine** → Search and rank relevant documents
5. **05_Complete_RAG** → Tie everything together into a working system

Each folder has:
- **concept.md** — Understand the concepts (read first)
- **demo.py** — See it in action (run second)

---

## 💾 Deliverables

By the end of Day 5, you should have:

✅ `01_Document_Loading` — Load documents and manage metadata
✅ `02_Chunking_Embeddings` — Split text and compute embeddings
✅ `03_Vector_Store` — Store and persist vectors
✅ `04_Query_Engine` — Build search with different top-k values
✅ `05_Complete_RAG` — Complete pipeline from documents to LLM answers

---

## 🔗 Related Days

- **Previous**: [Day 4 - LangChain Fundamentals](../Day_04/README.md)
- **Next**: [Day 6 - Smart Chatbot](../Day_06/README.md)

---

## 💡 Tips & Tricks

- **Mistral embeddings** are OpenAI-compatible — easy to swap providers
- **Chunk size matters**: 512 tokens is the sweet spot (balance precision vs context)
- **20% overlap** prevents context cutoff between chunks
- **Vector similarity** (cosine similarity) is 0-1, where 1 = identical meaning
- **Mistral-embed** produces 1024 dimensions (vs OpenAI's 1536)
- **No API key?** All demos work in demo mode showing the workflow
- **Start simple** with SimpleVectorStore, upgrade to Pinecone for production

---

## 🐛 Troubleshooting

**ModuleNotFoundError: No module named 'llama_index'**
→ Run: `pip install llama-index`

**Python 3.13 compatibility error**
→ Use Python 3.11 or 3.12: `py -3.11 -m venv bootcamp`

**API Key errors**
→ Check `.env` file has correct key format (no spaces, no quotes)

**Embedding service unavailable**
→ Demos work without API keys — shows what would happen with real API

---

## 📚 Resources

- [LlamaIndex Documentation](https://docs.llamaindex.ai/)
- [RAG Concepts](https://docs.llamaindex.ai/en/stable/getting_started/concepts/)
- [Mistral API Docs](https://docs.mistral.ai/)
- [Vector Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)

---

## 🚀 Next Steps After Day 5

1. Use real documents (your PDFs, company docs, research papers)
2. Experiment with different chunk sizes
3. Try Pinecone for cloud-based vector storage
4. Add reranking for better search quality
5. Build a chatbot on top of your RAG system (Day 6)

Good luck! 🎓
