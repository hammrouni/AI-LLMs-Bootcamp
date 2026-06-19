"""
05 - Production Local RAG (Capstone) Demo
=========================================
A production-style local RAG: quantized Ollama model, response cache, streaming
output, and TTFT / tok/s metrics.

HOW TO RUN THIS FILE:
1. ollama serve
2. ollama pull mistral:7b-instruct-q4_K_M    (or any chat model)
3. ollama pull nomic-embed-text
4. pip install ollama chromadb langchain-text-splitters
5. python demo.py
"""

import os
import time
import shutil
import statistics

DB_PATH = "./chroma_prod_local_rag"


CORPUS = {
    "company.txt": (
        "MASTER Soft is a software engineering company based in Tunis, with a satellite "
        "office in Sousse. Founded in 2018, the company now has around 120 employees."
    ),
    "refunds.txt": (
        "Our refund policy is generous. Customers on the Pro plan can request a refund "
        "within 14 days of purchase, no questions asked. To start a refund, contact "
        "Yasmine Ben Ali, the head of customer success. Refunds are processed within 5 "
        "business days back to the original payment method."
    ),
    "products.txt": (
        "MASTER Soft builds three products: a CRM platform, a billing API, and a mobile "
        "app builder. The CRM platform is the company's flagship product, used by over "
        "500 businesses across Tunisia."
    ),
    "vacation.txt": (
        "Vacation policy: employees accrue 2 paid vacation days per month, totalling 24 days "
        "per year. Days roll over up to a cap of 30 days. Approval is needed at least one "
        "week in advance for vacations longer than 5 working days."
    ),
    "hours.txt": (
        "Working hours are 9:00 to 18:00 Monday to Friday, with a 1-hour lunch break that can "
        "be split. Remote work is allowed up to 2 days per week with manager approval. "
        "Khaled leads the engineering team, based in the Sousse office."
    ),
}

SYSTEM_PROMPT = """You are the support assistant for MASTER Soft.
RULES:
- Answer ONLY using the provided context.
- If unknown: "I don't know based on the documents I have."
- Be concise (1-3 sentences).
- End with citations like [source: filename].
"""


def pick_chat_model():
    try:
        import ollama
    except ImportError:
        return None
    try:
        info = ollama.list()
    except Exception:
        return None
    names = [m.get("name") or m.get("model") for m in info.get("models", [])]
    for cand in [
        "mistral:7b-instruct-q4_K_M",
        "mistral:latest",
        "mistral",
        "llama3",
        "phi3",
    ]:
        for n in names:
            if cand in n:
                return n
    return None


def pick_embed_model():
    try:
        import ollama
    except ImportError:
        return None
    try:
        info = ollama.list()
    except Exception:
        return None
    for m in info.get("models", []):
        name = m.get("name") or m.get("model")
        if "nomic-embed-text" in name:
            return name
    return None


# ============================================================
# PART 1: Problem — Demo vs Production
# ============================================================

def show_the_problem():
    print("=== PART 1: Demo Code vs Production Code ===\n")
    print("Yesterday's offline RAG works, but:")
    print("  - Repeat questions hit the LLM every time")
    print("  - No way to measure how fast it is")
    print("  - No streaming -> the answer arrives as one wall of text")
    print("  - Model selection isn't tuned for speed (Q4 quant)\n")


# ============================================================
# PART 2: Production RAG Class
# ============================================================

class ProductionRAG:
    def __init__(self, chat_model, embed_model, corpus):
        import ollama
        import chromadb
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        self.ollama = ollama
        self.chat_model = chat_model
        self.embed_model = embed_model

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

    @staticmethod
    def _cache_key(question: str) -> str:
        return " ".join(question.lower().split())

    def ask(self, question: str, k=3, stream_to_stdout=False) -> dict:
        key = self._cache_key(question)
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

        # Generate (streaming)
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
        if stream_to_stdout:
            print()

        answer = "".join(answer_parts).strip()
        total = end - start
        ttft_ms = (first_token_time - start) * 1000 if first_token_time else total * 1000

        self.metrics["ttft_ms"].append(ttft_ms)
        self.metrics["total_s"].append(total)

        result = {
            "answer": answer,
            "sources": list(dict.fromkeys(sources)),
            "ttft_ms": ttft_ms,
            "total_s": total,
        }
        self.cache[key] = result
        return result

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


def show_the_solution():
    print("=== PART 2: Production RAG Class (Walkthrough) ===\n")
    print("Layers added on top of Day 12 offline RAG:")
    print("  - response cache (normalize question -> answer dict)")
    print("  - streaming output (better UX)")
    print("  - per-call TTFT + total-time metrics")
    print("  - .report() returns p50 latencies and cache-hit ratio\n")


# ============================================================
# PART 3: Run It With Repeats
# ============================================================

def real_world_example():
    chat_model = pick_chat_model()
    embed_model = pick_embed_model()
    if not chat_model:
        print("=== PART 3: REAL DEMO ===")
        print("Pull a chat model: ollama pull mistral")
        return
    if not embed_model:
        print("=== PART 3: REAL DEMO ===")
        print("Pull an embed model: ollama pull nomic-embed-text")
        return

    print("=== PART 3: Production Local RAG In Action ===\n")
    print(f"Chat model:  {chat_model}")
    print(f"Embed model: {embed_model}\n")

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
        cached = "(cache hit)" if result["ttft_ms"] == rag.cache[rag._cache_key(q)]["ttft_ms"] and len(rag.metrics["ttft_ms"]) < len(questions) else ""
        print(f"   [TTFT {result['ttft_ms']:.0f} ms, total {result['total_s']:.2f}s] {cached}\n")

    print("--- Report ---")
    rep = rag.report()
    for k, v in rep.items():
        if isinstance(v, float):
            print(f"  {k:<18} {v:.3f}")
        else:
            print(f"  {k:<18} {v}")
    print()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    show_the_problem()
    show_the_solution()
    real_world_example()

    print("--- Key Takeaways ---")
    print("1. Quantized model (Q4_K_M) is the production default for local LLMs.")
    print("2. Response caching is a free 10x speedup on repeat questions.")
    print("3. Streaming + measuring TTFT makes the bot feel snappy.")
    print("4. Always log p50/p95 latency and cache-hit ratio.")
    print("5. Tomorrow: measure ANSWER QUALITY, not just speed.")
