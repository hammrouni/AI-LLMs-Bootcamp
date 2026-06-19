"""
05 - Offline RAG (Capstone) Demo
================================
A full RAG pipeline that runs 100% locally using Ollama for embeddings and
generation. ChromaDB persists vectors on disk. No internet required.

HOW TO RUN THIS FILE:
1. ollama serve (in another terminal)
2. ollama pull mistral
3. ollama pull nomic-embed-text
4. pip install ollama chromadb langchain-text-splitters
5. python demo.py
"""

import os
import shutil

DB_PATH = "./chroma_offline_rag"

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
- If unknown, reply exactly: "I don't know based on the documents I have."
- Be concise (1-3 sentences).
- End with citations like [source: filename].
"""


def model_available(target):
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
        if target in name:
            return name
    return None


# ============================================================
# PART 1: Problem — Cloud-Only RAG Doesn't Fit Every Deploy
# ============================================================

def show_the_problem():
    print("=" * 60)
    print("  PART 1: When Cloud RAG Isn't Allowed")
    print("=" * 60)
    print()
    print("  Day 11's capstone calls Mistral cloud APIs.")
    print("  Many Tunisian orgs can't send data to the cloud:")
    print()
    print("    - Bank:     BCT data-residency rules")
    print("    - Hospital: patient confidentiality")
    print("    - Ministry: state-data sovereignty")
    print()
    print("  Offline RAG keeps every byte local while keeping")
    print("  the same UX and pipeline architecture.")
    print("-" * 60)
    print()


# ============================================================
# PART 2: Solution — Same Pipeline, Local Backends
# ============================================================

def show_the_solution():
    print("=" * 60)
    print("  PART 2: Provider Abstraction")
    print("=" * 60)
    print()
    print("  The trick: two thin wrapper functions hide the backend.")
    print()
    print("    def embed(text)    -> vector list   # Ollama or Mistral")
    print("    def generate(msgs) -> str           # Ollama or Mistral")
    print()
    print("  Plug Ollama for offline, Mistral for cloud.")
    print("  The RAG pipeline doesn't care which one is behind them.")
    print("-" * 60)
    print()


# ============================================================
# PART 3: End-to-End Offline RAG
# ============================================================

def real_world_example():
    try:
        import ollama
        import chromadb
        from langchain_text_splitters import RecursiveCharacterTextSplitter
    except ImportError:
        print("Run: pip install ollama chromadb langchain-text-splitters")
        return

    chat_model = model_available("llama3") or model_available("mistral") or model_available("phi3")
    embed_model = model_available("nomic-embed-text")

    if not chat_model:
        print("Pull a chat model first: ollama pull mistral")
        return
    if not embed_model:
        print("Pull an embedding model first: ollama pull nomic-embed-text")
        return

    print("=" * 60)
    print("  PART 3: Offline RAG In Action")
    print("=" * 60)
    print()
    print("  Full pipeline: embed docs -> store in ChromaDB ->")
    print("  query with question -> generate answer with LLM.")
    print("  Everything runs on localhost, no internet needed.")
    print()
    print(f"  Chat model:  {chat_model}")
    print(f"  Embed model: {embed_model}")
    print()

    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)
    chroma = chromadb.PersistentClient(path=DB_PATH)
    collection = chroma.get_or_create_collection("docs")

    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)

    def embed(text: str):
        return ollama.embeddings(model=embed_model, prompt=text)["embedding"]

    # Index
    for source, text in CORPUS.items():
        chunks = splitter.split_text(text)
        if not chunks:
            continue
        vectors = [embed(c) for c in chunks]
        collection.add(
            documents=chunks,
            embeddings=vectors,
            metadatas=[{"source": source} for _ in chunks],
            ids=[f"{source}::{i}" for i in range(len(chunks))],
        )
    print(f"  Indexed {collection.count()} chunks locally.")
    print()
    print("-" * 40)
    print("  Q&A — asking 5 questions against the corpus")
    print("-" * 40)
    print()

    def ask(question: str, k=3) -> str:
        q_vec = embed(question)
        res = collection.query(query_embeddings=[q_vec], n_results=k)
        chunks = res["documents"][0]
        sources = [m["source"] for m in res["metadatas"][0]]
        context = "\n\n".join(f"[{s}] {c}" for s, c in zip(sources, chunks))

        resp = ollama.chat(
            model=chat_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"Context:\n{context}\n\nQuestion: {question}"},
            ],
            options={"num_predict": 200, "temperature": 0.2},
        )
        return resp["message"]["content"].strip()

    questions = [
        "What's the refund window?",
        "What products does MASTER Soft build?",
        "How many vacation days per year?",
        "Who leads the engineering team?",
        "What is the speed of light?",  # not in corpus
    ]
    for i, q in enumerate(questions, 1):
        note = "  (not in corpus — should refuse)" if q == "What is the speed of light?" else ""
        print(f"  [{i}] Q: {q}{note}")
        print(f"      A: {ask(q)}")
        print()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    show_the_problem()
    show_the_solution()
    real_world_example()

    print("=" * 60)
    print("  KEY TAKEAWAYS")
    print("=" * 60)
    print("  1. Same RAG architecture — only LLM/embedding backends swap")
    print("  2. nomic-embed-text + 7B chat model = full RAG on a laptop")
    print("  3. Provider abstraction makes cloud/local a one-line swap")
    print("  4. Offline RAG unlocks regulated deployments (bank/hospital)")
    print("  5. Next: optimize local inference — quantization, GPU, throughput")
    print("=" * 60)
