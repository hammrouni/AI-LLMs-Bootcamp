"""
04 - Building the Retriever Demo
================================
Wraps chunking + embedding + vector storage into a single Retriever class,
indexes a small Tunisian corpus, and runs queries.

HOW TO RUN THIS FILE:
1. pip install chromadb mistralai langchain-text-splitters python-dotenv
2. Copy ../.env.example to ../.env and add your MISTRAL_API_KEY
3. python demo.py
"""

import os
import shutil
from dotenv import load_dotenv

load_dotenv()

DB_PATH = "./chroma_retriever_demo"


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


# ============================================================
# PART 1: The Problem — Duct-Taped Retrieval
# ============================================================

def show_the_problem():
    print("=== PART 1: The Duct-Taped Retrieval Anti-Pattern ===\n")
    print("Without a clean Retriever class:")
    print("  - One script chunks at 300, another at 800.")
    print("  - One uses mistral-embed, another uses an older model.")
    print("  - Adding a new doc means re-implementing the pipeline.")
    print("  - Tests are impossible because logic is scattered.\n")
    print("Solution: wrap it all in a class.\n")


# ============================================================
# PART 2: The Retriever Class
# ============================================================

class Retriever:
    def __init__(self, persist_path, mistral_client, chunk_size=300, chunk_overlap=50):
        import chromadb
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        if os.path.exists(persist_path):
            shutil.rmtree(persist_path)
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection("docs")
        self.mistral = mistral_client
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

    def _embed(self, texts):
        import time
        from mistralai.client.errors import SDKError

        for attempt in range(5):
            try:
                return [
                    d.embedding
                    for d in self.mistral.embeddings.create(model="mistral-embed", inputs=texts).data
                ]
            except SDKError as e:
                if "429" not in str(e) or attempt == 4:
                    raise
                time.sleep(2 ** attempt)  # 1, 2, 4, 8, 16 seconds

    def add_document(self, text, source):
        chunks = self.splitter.split_text(text)
        if not chunks:
            return 0
        vectors = self._embed(chunks)
        self.collection.add(
            documents=chunks,
            embeddings=vectors,
            metadatas=[{"source": source, "chunk_index": i} for i in range(len(chunks))],
            ids=[f"{source}::{i}" for i in range(len(chunks))],
        )
        return len(chunks)

    def search(self, query, k=3):
        q_vec = self._embed([query])[0]
        return self.collection.query(query_embeddings=[q_vec], n_results=k)

    def count(self):
        return self.collection.count()


def show_the_solution():
    print("=== PART 2: The Retriever Class (Walkthrough) ===\n")
    print("class Retriever:")
    print("    __init__(persist_path, mistral_client, chunk_size, chunk_overlap)")
    print("    add_document(text, source) -> chunks + embeds + stores")
    print("    search(query, k) -> top-k chunks from the vector DB")
    print("    count() -> number of chunks indexed")
    print()
    print("One class, one contract. Replace embedding model or DB in one place.\n")


# ============================================================
# PART 3: Real Retriever Over the Tunisian Corpus
# ============================================================

def real_world_example():
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("=== PART 3: REAL RETRIEVER (API key required) ===")
        print("Set MISTRAL_API_KEY in codes/.env to run this section.\n")
        return

    try:
        from mistralai.client import Mistral
    except ImportError:
        print("Run: pip install mistralai")
        return

    print("=== PART 3: Indexing and Querying the Corpus ===\n")

    mistral = Mistral(api_key=api_key)
    retriever = Retriever(DB_PATH, mistral, chunk_size=300, chunk_overlap=50)

    total = 0
    for source, text in CORPUS.items():
        n = retriever.add_document(text, source)
        total += n
        print(f"  indexed {n} chunks from {source}")
    print(f"Total chunks indexed: {total}\n")

    questions = [
        "What's the refund window?",
        "What products does MASTER Soft build?",
        "How many vacation days do I get per year?",
        "Is remote work allowed?",
    ]

    for q in questions:
        results = retriever.search(q, k=2)
        print(f"Q: {q}")
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            print(f"  [{meta['source']}] dist={dist:.4f} | {doc[:90]}")
        print()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    show_the_problem()
    show_the_solution()
    real_world_example()

    print("--- Key Takeaways ---")
    print("1. Wrap chunking + embedding + storage in a Retriever class.")
    print("2. Single source of truth for chunk size and embedding model.")
    print("3. add_document() and search() are the only public methods you need.")
    print("4. Source metadata (filename) lets you cite the answer later.")
    print("5. Tomorrow: plug an LLM on top of this retriever -> full RAG.")
