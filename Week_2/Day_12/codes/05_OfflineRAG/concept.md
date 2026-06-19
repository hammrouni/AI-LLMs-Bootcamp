# 05 - Offline RAG (Capstone)

---

## 📦 Packages

```bash
pip install ollama chromadb langchain-text-splitters
```

---

## What is Offline RAG?

**Offline RAG** is the Day 11 capstone — but without any cloud calls. Embeddings come from a local Ollama embedding model. Chat answers come from a local Ollama LLM. The vector DB is on disk. Internet can be off the whole time.

Think of a Tunisian municipal office that handles citizen requests:
- Cloud RAG: every citizen question sends data to a foreign company's servers
- Offline RAG: the same workflow, but the documents and the LLM live on a server in the building's basement
- Sovereignty, privacy, and zero ongoing cost

This is the architecture for any Tunisian institution that can't (or won't) send data abroad.

---

## What is the Problem?

### Day 11's FAQ bot still depends on Mistral's cloud API

The Day 11 capstone is great but uses:
- `mistral-embed` (cloud) for embeddings
- `mistral-small-latest` (cloud) for generation

That means:
- API key required
- Internet required
- Latency depends on the network
- Per-query cost forever
- Data leaves your country

For a bank in Tunis or a hospital in Sfax, those are non-starters.

---

## What is the Solution? Swap Cloud Calls for Ollama Calls!

The pipeline architecture stays the same. Only two function bodies change:

```python
# Cloud
def embed(text):
    return mistral.embeddings.create(model="mistral-embed", inputs=[text]).data[0].embedding

# Local (Ollama)
def embed(text):
    return ollama.embeddings(model="nomic-embed-text", prompt=text)["embedding"]
```

```python
# Cloud
def generate(messages):
    return mistral.chat.complete(model="mistral-small-latest", messages=messages).choices[0].message.content

# Local (Ollama)
def generate(messages):
    return ollama.chat(model="mistral", messages=messages)["message"]["content"]
```

That's it. Everything else (chunking, vector DB, prompts, citations) is unchanged.

---

## How It Works in Python

### Architecture Side By Side

| Step | Cloud (Day 11) | Offline (Day 12) |
|---|---|---|
| Chunk | LangChain splitter | LangChain splitter |
| Embed | `mistral-embed` | `nomic-embed-text` (Ollama) |
| Store | ChromaDB | ChromaDB |
| Retrieve | ChromaDB query | ChromaDB query |
| Prompt | Grounded system prompt | Grounded system prompt |
| Generate | `mistral-small-latest` | `mistral` (Ollama) |
| Total internet calls | many | **zero** |

### The Golden Rule:
- **Build an abstract `embed()` / `generate()` so you can swap providers in one line.** The RAG pipeline shouldn't know whether it's calling Ollama or Mistral.

### BAD vs GOOD

```python
# BAD — provider name hardcoded throughout the pipeline
def ask(q):
    vec = mistral.embeddings.create(...)
    ...
    answer = mistral.chat.complete(...)

# GOOD — abstract providers behind two small functions
def ask(q, embed_fn, generate_fn):
    vec = embed_fn(q)
    ...
    answer = generate_fn(...)
```

Run the same `ask()` with `embed_fn=ollama_embed, generate_fn=ollama_chat` for offline, or with Mistral cloud calls online.

---

## Why This Matters for AI Apps

Offline RAG unlocks deployments that cloud RAG can't reach:
- Tunisian Ministry of Finance — sensitive policy docs, no cloud allowed
- Hospital triage — patient records, GDPR/HIPAA-like rules
- School systems — kids' data, parental privacy concerns
- Conferences / demos — no Wi-Fi guaranteed
- Air-gapped corporate networks

The same code shape, the same Tunisian-flavored docs as in Day 10/11, but every byte of data stays on a server you own.

```
Cloud RAG cost  (100k queries/month): ~150 TND
Offline RAG cost (same workload):     ~0 TND (after a $400 server)
```

After Day 12 you can confidently say: "I can ship RAG for any Tunisian organization, even the ones that can't use cloud AI."
