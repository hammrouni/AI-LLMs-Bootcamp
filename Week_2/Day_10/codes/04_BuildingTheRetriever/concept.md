# 04 - Building the Retriever

---

## 📦 Packages

```bash
pip install chromadb mistralai langchain-text-splitters python-dotenv
```

---

## What is a Retriever?

A **retriever** is the component that, given a question, returns the top-k most relevant chunks from your corpus. It's the bridge between "raw documents" and "LLM context".

Think of the librarian in the Tunis National Library:
- You arrive with a question
- She doesn't read every book — she goes to the right shelf, picks 3 books, opens to the relevant pages, hands them to you
- The librarian is the retriever; the shelves are the vector DB; the pages are the chunks

A retriever wraps: chunking + embedding + vector DB query, exposed as a single `.search(query, k)` method.

---

## What is the Problem?

### A "retriever" scattered across 5 files is unmaintainable

The naive way: each script handles its own chunking, embedding, and storage. After a month:
- Chunk size is `300` in some places and `500` in others
- One script uses `mistral-embed`, another uses an old `text-embedding-ada-002`
- Each query re-embeds the entire corpus
- No tests, no metrics

You can't reason about retrieval quality if retrieval is duct-taped together.

---

## What is the Solution? Wrap It In a Class!

Encapsulate everything in a `Retriever` object:

```python
class Retriever:
    def __init__(self, persist_path, mistral_client, chunk_size=400):
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection("docs")
        self.mistral = mistral_client
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=80)

    def add_document(self, text, source):
        chunks = self.splitter.split_text(text)
        vectors = self._embed(chunks)
        ids = [f"{source}_{i}" for i in range(len(chunks))]
        metadatas = [{"source": source, "chunk": i} for i in range(len(chunks))]
        self.collection.add(documents=chunks, embeddings=vectors, ids=ids, metadatas=metadatas)

    def search(self, query, k=3):
        q_vec = self._embed([query])[0]
        return self.collection.query(query_embeddings=[q_vec], n_results=k)
```

One class. One contract. Easy to test, easy to swap pieces (try a different chunk size? change one constant).

---

## How It Works in Python

### Architecture Outline

| Method | What it does |
|---|---|
| `add_document(text, source)` | Chunk + embed + store with metadata |
| `search(query, k)` | Embed query + vector search top-k chunks |
| `count()` | How many chunks are indexed |
| `clear()` | Delete the collection (useful for tests) |

### The Golden Rule:
- **The retriever owns the embedding model and the chunking strategy.** No code outside the retriever should touch either — that way, changing them is a one-line change.

### BAD vs GOOD

```python
# BAD — embedding scattered across the codebase
def index_pdf(path):
    text = load_pdf(path)
    chunks = text.split("\n\n")
    vecs = mistral.embeddings.create(model="mistral-embed", inputs=chunks).data
    chroma.add(documents=chunks, embeddings=[v.embedding for v in vecs])

def index_docx(path):
    text = load_docx(path)
    chunks = naive_split(text, 1000)  # different chunk size from index_pdf!
    vecs = mistral.embeddings.create(model="mistral-tiny", inputs=chunks).data  # different model!

# GOOD — single retriever handles it all consistently
retriever = Retriever("./chroma_db", mistral, chunk_size=400)
retriever.add_document(load_pdf("handbook.pdf"),   source="handbook.pdf")
retriever.add_document(load_docx("policies.docx"), source="policies.docx")
```

---

## Why This Matters for AI Apps

A clean retriever class is the difference between a science project and a product:
- Easy to swap from Chroma to Qdrant (change one method)
- Easy to A/B test chunk sizes (change a constructor arg)
- Easy to add re-ranking later (override `search`)
- Easy to test (unit-test each method)

Tomorrow we plug an LLM on top. If the retriever is a clean object, that's 10 lines of code. If retrieval logic is sprawled out, it's a refactor.

```
Refactor cost when retrieval is duct-taped: 2 days.
Refactor cost when retrieval is a clean class: 10 minutes.
```
