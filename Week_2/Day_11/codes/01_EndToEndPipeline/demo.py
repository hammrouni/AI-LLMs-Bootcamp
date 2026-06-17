"""
01 - End-to-End RAG Pipeline Demo
=================================
Builds a Retriever + RAGPipeline class over a small Tunisian-themed knowledge
base, then runs a few user questions end-to-end.

HOW TO RUN THIS FILE:
1. pip install chromadb mistralai langchain-text-splitters python-dotenv
2. Copy ../.env.example to ../.env and add your MISTRAL_API_KEY
3. python demo.py
"""

import os
import shutil
from dotenv import load_dotenv

load_dotenv()

DB_PATH = "./chroma_rag_pipeline"


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
# PART 1: The Problem — LLM Without Context Hallucinates
# ============================================================

def show_the_problem():
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("=== PART 1: LLM WITHOUT CONTEXT (API key required) ===")
        print("Set MISTRAL_API_KEY in codes/.env to run this section.\n")
        return

    try:
        from mistralai.client import Mistral
    except ImportError:
        print("Run: pip install mistralai")
        return

    print("=== PART 1: LLM Without Context Hallucinates ===\n")

    question = "What's the refund window?"
    client = Mistral(api_key=api_key)
    response = client.chat.complete(
        model="mistral-small-latest",
        messages=[{"role": "user", "content": question}],
    )
    answer_no_rag = response.choices[0].message.content.strip()

    print(f"Question: {question}\n")
    print("-" * 60)
    print("LLM (no context):")
    print("-" * 60)
    for line in answer_no_rag.split("\n"):
        print(f"  {line}")
    print("-" * 60)
    print("\nReality (from the handbook): 14 days, no questions asked, Pro plan only.")
    print("Without context, the LLM guesses or admits it doesn't know.\n")


# ============================================================
# PART 2: The Solution — Retriever + LLM = Grounded Answer
# ============================================================

def show_the_solution():
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("=== PART 2: RAG PIPELINE (API key required) ===")
        print("Set MISTRAL_API_KEY in codes/.env to run this section.\n")
        return

    try:
        from mistralai.client import Mistral
    except ImportError:
        print("Run: pip install mistralai")
        return

    print("=== PART 2: RAG Pipeline Step by Step ===\n")

    client = Mistral(api_key=api_key)
    question = "What's the refund window?"

    # Step 1: embed + retrieve relevant chunks
    print("Step 1: Retrieve relevant chunks via embeddings\n")
    all_texts = list(CORPUS.values())
    all_sources = list(CORPUS.keys())
    vectors = [
        d.embedding
        for d in client.embeddings.create(model="mistral-embed", inputs=all_texts).data
    ]
    q_vec = client.embeddings.create(model="mistral-embed", inputs=[question]).data[0].embedding

    from math import sqrt

    def cosine(a, b):
        dot = sum(x * y for x, y in zip(a, b))
        na = sqrt(sum(x * x for x in a))
        nb = sqrt(sum(y * y for y in b))
        return dot / (na * nb)

    scored = sorted(
        zip(all_sources, all_texts, [cosine(q_vec, v) for v in vectors]),
        key=lambda x: -x[2],
    )
    top_sources = [s for s, _, _ in scored[:3]]
    top_chunks = [c for _, c, _ in scored[:3]]

    print("-" * 60)
    print("Retrieved chunks:")
    print("-" * 60)
    for src, chunk in zip(top_sources, top_chunks):
        print(f"  [{src}] {chunk[:80]}...")
    print("-" * 60)

    # Step 2: build the grounded prompt
    print("\nStep 2: Build a grounded prompt with system + user messages\n")
    context = "\n\n".join(f"[{s}] {c}" for s, c in zip(top_sources, top_chunks))
    system_prompt = (
        "Answer ONLY using the provided context. "
        "If unknown, say 'I don't know'. "
        "After the answer, list sources as [source: filename]."
    )
    print("-" * 60)
    print("Prompt:")
    print("-" * 60)
    print(f"  SYSTEM: {system_prompt}")
    print(f"  USER:   Context:\\n[refunds.txt] ...\\n\\nQuestion: {question}")
    print("-" * 60)

    # Step 3: LLM generates the grounded answer
    print("\nStep 3: LLM answers from the context\n")
    response = client.chat.complete(
        model="mistral-small-latest",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
    )
    answer = response.choices[0].message.content.strip()

    print("-" * 60)
    print("Grounded answer:")
    print("-" * 60)
    for line in answer.split("\n"):
        print(f"  {line}")
    print("-" * 60)

    print("\nThat's the full pipeline: retrieve -> prompt -> generate -> answer.")
    print("The RAGPipeline class wraps all 3 steps behind one ask() call.\n")


# ============================================================
# PART 3: Real End-to-End RAG
# ============================================================

class SimpleRetriever:
    def __init__(self, mistral, chunk_size=300):
        import chromadb
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        if os.path.exists(DB_PATH):
            shutil.rmtree(DB_PATH)
        self.client = chromadb.PersistentClient(path=DB_PATH)
        self.collection = self.client.get_or_create_collection("docs")
        self.mistral = mistral
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=50)

    def _embed(self, texts):
        return [
            d.embedding
            for d in self.mistral.embeddings.create(model="mistral-embed", inputs=texts).data
        ]

    def index(self, corpus: dict):
        for source, text in corpus.items():
            chunks = self.splitter.split_text(text)
            if not chunks:
                continue
            vectors = self._embed(chunks)
            self.collection.add(
                documents=chunks,
                embeddings=vectors,
                metadatas=[{"source": source} for _ in chunks],
                ids=[f"{source}::{i}" for i in range(len(chunks))],
            )

    def search(self, query, k=3):
        q_vec = self._embed([query])[0]
        return self.collection.query(query_embeddings=[q_vec], n_results=k)


class RAGPipeline:
    def __init__(self, retriever, mistral, model="mistral-small-latest"):
        self.retriever = retriever
        self.client = mistral
        self.model = model
        self.system_prompt = (
            "You are a helpful assistant for MASTER Soft. "
            "Answer ONLY using the provided context. "
            "If the answer is not in the context, say 'I don't know based on the documents I have.' "
            "End the answer with citations in the form [source: filename]."
        )

    def ask(self, question, k=3):
        results = self.retriever.search(question, k=k)
        chunks = results["documents"][0]
        sources = [m["source"] for m in results["metadatas"][0]]
        context = "\n\n".join(f"[{s}] {c}" for s, c in zip(sources, chunks))

        response = self.client.chat.complete(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user",   "content": f"Context:\n{context}\n\nQuestion: {question}"},
            ],
        )
        return response.choices[0].message.content.strip()


def real_world_example():
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("=== PART 3: REAL RAG (API key required) ===")
        print("Set MISTRAL_API_KEY in codes/.env to run this section.\n")
        return

    try:
        from mistralai.client import Mistral
    except ImportError:
        print("Run: pip install mistralai")
        return

    print("=== PART 3: Real End-to-End RAG ===\n")

    mistral = Mistral(api_key=api_key)
    retriever = SimpleRetriever(mistral)
    retriever.index(CORPUS)
    pipeline = RAGPipeline(retriever, mistral)

    questions = [
        "What's the refund window?",
        "What products does MASTER Soft build?",
        "How many vacation days per year?",
        "What is the speed of light?",  # not in corpus
    ]

    for q in questions:
        print(f"Q: {q}")
        print(f"A: {pipeline.ask(q, k=3)}\n")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    show_the_problem()
    show_the_solution()
    real_world_example()

    print("--- Key Takeaways ---")
    print("1. End-to-end RAG = retriever + LLM wrapped in one ask() method.")
    print("2. The pipeline owns the system prompt and prompt template.")
    print("3. Grounded prompts force the LLM to quote, not invent.")
    print("4. Citations [source: filename] are trust gold for users.")
    print("5. Every surface (chatbot, API, Slack bot) calls pipeline.ask() — 1 line.")
