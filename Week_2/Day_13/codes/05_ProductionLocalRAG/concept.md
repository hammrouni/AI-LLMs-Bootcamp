# 05 - Production Local RAG (Capstone)

---

## Packages

```bash
pip install ollama chromadb langchain-text-splitters
```

---

## What is This Capstone?

A **production-grade offline RAG**: same architecture as Day 12 capstone, but with:
- Quantized models (concept 02)
- Response caching for repeat questions (~10x speedup on cache hit)
- Latency monitoring with TTFT + total time (concept 04)
- Streaming output (UX win)

This is what you'd actually deploy in a Tunisian bank or hospital where local + fast + measurable is non-negotiable.

---

## What is the Problem?

### "Offline" alone isn't enough — it has to be fast and reliable

The Day 12 capstone works, but:
- Same question repeated 50 times = LLM called 50 times = wasted compute
- No idea if it's slow or fast
- No way to debug a regression after changing the chunker
- Default model (`mistral`) might be FP16-ish — Q4 is faster

Production needs caching, monitoring, and tuned model selection.

---

## What is the Solution? Add the Three Missing Layers!

```
+-----------------------------------------+
|       Streaming response                |  <- UX
+-----------------------------------------+
|       LLM (quantized Mistral 7B)        |  <- Speed
+-----------------------------------------+
|       Response cache (LRU)              |  <- Repeat-question speedup
+-----------------------------------------+
|       Retriever (Chroma + Ollama)       |  <- Day 12
+-----------------------------------------+
|       Latency metrics                   |  <- Observability
+-----------------------------------------+
```

Each layer is 20–40 lines of code. Together they turn a demo into a deployable system.

---

## How It Works in Python

### Architecture

| Layer | Responsibility |
|---|---|
| Cache | Look up question (normalized) -> return cached answer instantly |
| Retriever | Embed + search top-k |
| LLM call | Run with strict prompt + stream |
| Metrics | TTFT, total time, cache-hit ratio |

### The ProductionRAG Class (from demo.py)

```python
import os, time, shutil, statistics
import ollama, chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter

class ProductionRAG:
    def __init__(self, chat_model, embed_model, corpus):
        self.ollama = ollama
        self.chat_model = chat_model
        self.embed_model = embed_model

        # Create persistent vector store
        if os.path.exists(DB_PATH):
            shutil.rmtree(DB_PATH)
        self.chroma = chromadb.PersistentClient(path=DB_PATH)
        self.collection = self.chroma.get_or_create_collection("docs")
        splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)

        # Index corpus
        for source, text in corpus.items():
            chunks = splitter.split_text(text)
            if not chunks:
                continue
            vectors = [self._embed(c) for c in chunks]
            self.collection.add(
                documents=chunks,
                embeddings=vectors,
                metadatas=[{"source": source} for _ in chunks],
                ids=[f"{source}::{i}" for i in range(len(chunks))],
            )

        self.cache = {}
        self.metrics = {"hits": 0, "misses": 0, "ttft_ms": [], "total_s": []}

    def _embed(self, text: str):
        return self.ollama.embeddings(model=self.embed_model, prompt=text)["embedding"]
```

### The ask() Method — Cache + Retrieve + Stream (from demo.py)

```python
    @staticmethod
    def _cache_key(question: str) -> str:
        return " ".join(question.lower().split())

    def ask(self, question: str, k=3, stream_to_stdout=False) -> dict:
        key = self._cache_key(question)

        # Cache check
        if key in self.cache:
            self.metrics["hits"] += 1
            cached = self.cache[key]
            if stream_to_stdout:
                print(cached["answer"], end="", flush=True)
            return cached
        self.metrics["misses"] += 1

        # Retrieve
        q_vec = self._embed(question)
        res = self.collection.query(query_embeddings=[q_vec], n_results=k)
        chunks = res["documents"][0]
        sources = [m["source"] for m in res["metadatas"][0]]
        context = "\n\n".join(f"[{s}] {c}" for s, c in zip(sources, chunks))

        # Generate (streaming) with metrics
        start = time.perf_counter()
        first_token_time = None
        answer_parts = []
        for chunk in self.ollama.chat(
            model=self.chat_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"Context:\n{context}\n\nQuestion: {question}"},
            ],
            stream=True,
            options={"num_predict": 200, "temperature": 0.2},
        ):
            txt = chunk["message"]["content"]
            if first_token_time is None and txt:
                first_token_time = time.perf_counter()
            if txt:
                answer_parts.append(txt)
                if stream_to_stdout:
                    print(txt, end="", flush=True)
        end = time.perf_counter()

        answer = "".join(answer_parts).strip()
        total = end - start
        ttft_ms = (first_token_time - start) * 1000 if first_token_time else total * 1000

        self.metrics["ttft_ms"].append(ttft_ms)
        self.metrics["total_s"].append(total)

        result = {"answer": answer, "sources": list(dict.fromkeys(sources)), "ttft_ms": ttft_ms, "total_s": total}
        self.cache[key] = result
        return result
```

### The report() Method — p50 Latencies (from demo.py)

```python
    def report(self):
        total = self.metrics["hits"] + self.metrics["misses"]
        hit_ratio = self.metrics["hits"] / total if total else 0
        ttft_p50 = statistics.median(self.metrics["ttft_ms"]) if self.metrics["ttft_ms"] else 0
        tot_p50  = statistics.median(self.metrics["total_s"])  if self.metrics["total_s"]  else 0
        return {
            "cache_hit_ratio": hit_ratio,
            "ttft_p50_ms":     ttft_p50,
            "total_p50_s":     tot_p50,
            "questions":       total,
        }
```

### Running With Repeat Questions (from demo.py)

```python
rag = ProductionRAG(chat_model, embed_model, CORPUS)

questions = [
    "What's the refund window?",
    "What products does MASTER Soft build?",
    "How many vacation days per year?",
    "What's the refund window?",              # repeat -> cache hit
    "What products does MASTER Soft build?",  # repeat -> cache hit
]

for q in questions:
    print(f"Q: {q}")
    print("A: ", end="", flush=True)
    result = rag.ask(q, stream_to_stdout=True)
    print(f"   [TTFT {result['ttft_ms']:.0f} ms, total {result['total_s']:.2f}s]")

rep = rag.report()
print(f"Cache hit ratio: {rep['cache_hit_ratio']:.1%}")
print(f"TTFT p50:        {rep['ttft_p50_ms']:.0f} ms")
print(f"Total p50:       {rep['total_p50_s']:.2f} s")
```

### The Golden Rule:
- **Make caching opt-out, not opt-in.** Most repeat questions are the same — caching is a free win.

### BAD vs GOOD

```python
# BAD — re-run LLM every time, no metrics
def ask(q):
    return llm(retrieve(q))

# GOOD — cached + measured + streaming
def ask(q):
    key = normalize(q)
    if key in cache: return cache[key]
    ...
    cache[key] = answer
    log_metric(ttft, total)
    return answer
```

---

## Why This Matters for AI Apps

For Tunisian institutions deploying local RAG, the capstone is the *minimum* to actually ship:
- A bank's helpdesk handles ~70% repeat questions — caching is huge
- Hospitals need latency under 2s for triage assistants — quantization + GPU
- Government legal-document assistants need reliability — metrics + alerting

```
Naive offline RAG:       8s avg per query, 100% LLM calls, no insight
Productionized:          1.2s avg, 60% cached, p95 = 4s, metrics logged
```

After Day 13 you have what most "AI consultants" in the region don't: a measured, tuned, deployable local-RAG stack ready for a real customer.

Tomorrow we'll add the missing piece: how to measure not just *speed* but *answer quality* with proper evaluation metrics.
