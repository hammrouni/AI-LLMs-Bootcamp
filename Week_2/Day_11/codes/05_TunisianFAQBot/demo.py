"""
05 - Tunisian FAQ Bot (Capstone) Demo
=====================================
Assembles a full hybrid-RAG FAQ bot for a fictional Tunisian software company,
exposing a single ask(question) method that returns an answer + source list.

HOW TO RUN THIS FILE:
1. pip install chromadb mistralai langchain-text-splitters rank-bm25 python-dotenv
2. Copy ../.env.example to ../.env and add your MISTRAL_API_KEY
3. python demo.py
"""

import os
import shutil
from dotenv import load_dotenv

load_dotenv()

DB_PATH = "./chroma_faq_capstone"


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
        "Khaled leads the engineering team, based in the Sousse office. Friday afternoons are no-meeting time."
    ),
    "contacts.txt": (
        "Support: support@mastersoft.tn (24h response). HR: hr@mastersoft.tn. "
        "CEO: Mehdi Trabelsi. Head of customer success: Yasmine Ben Ali."
    ),
}


SYSTEM_PROMPT = """You are the support assistant for MASTER Soft, a Tunisian software engineering company.

RULES:
- Answer ONLY using the provided context.
- Do not use outside knowledge.
- If the answer is not in the context, reply exactly: "I don't know based on the documents I have."
- Be concise (1-3 sentences).
- End every answer with citations in the form [source: filename].

LANGUAGE:
- Answer in the same language as the question (French, English, or Arabic).
"""


# ============================================================
# PART 1: The Problem — Individual Components Don't Answer
# ============================================================

def show_the_problem():
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("=== PART 1: THE PROBLEM (API key required) ===")
        print("Set MISTRAL_API_KEY in codes/.env to run this section.\n")
        return

    try:
        from mistralai.client import Mistral
    except ImportError:
        print("Run: pip install mistralai")
        return

    print("=== PART 1: Individual Components Don't Answer Questions ===\n")

    mistral = Mistral(api_key=api_key)
    question = "What's the refund window?"

    # Show that a plain LLM without our docs gets it wrong
    response = mistral.chat.complete(
        model="mistral-small-latest",
        messages=[{"role": "user", "content": f"{question} at MASTER Soft"}],
    )
    plain_answer = response.choices[0].message.content.strip()

    print(f"Question: {question}\n")
    print("-" * 60)
    print("Plain LLM (no retrieval, no grounding):")
    print("-" * 60)
    for line in plain_answer.split("\n"):
        print(f"  {line}")
    print("-" * 60)
    print("\nA real FAQ bot needs all components wired together:")
    print("  chunk -> vector + BM25 index -> hybrid retrieve -> grounded prompt -> answer")
    print("That's what the TunisianFAQBot capstone class does.\n")


# ============================================================
# PART 2: The Capstone Class (Architecture)
# ============================================================

class TunisianFAQBot:
    def __init__(self, mistral, corpus: dict, chunk_size=300, chunk_overlap=50):
        import chromadb
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from rank_bm25 import BM25Okapi

        if os.path.exists(DB_PATH):
            shutil.rmtree(DB_PATH)
        self.mistral = mistral
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        self.client = chromadb.PersistentClient(path=DB_PATH)
        self.collection = self.client.get_or_create_collection("faq")

        # Index
        all_chunks = []
        all_sources = []
        for source, text in corpus.items():
            chunks = self.splitter.split_text(text)
            all_chunks.extend(chunks)
            all_sources.extend([source] * len(chunks))

        if all_chunks:
            vectors = [
                d.embedding
                for d in self.mistral.embeddings.create(
                    model="mistral-embed", inputs=all_chunks
                ).data
            ]
            self.collection.add(
                documents=all_chunks,
                embeddings=vectors,
                metadatas=[{"source": s} for s in all_sources],
                ids=[f"chunk_{i}" for i in range(len(all_chunks))],
            )

        self.all_chunks = all_chunks
        self.all_sources = all_sources
        self.bm25 = BM25Okapi([c.lower().split() for c in all_chunks])

    def _vector_topk(self, query, k):
        q_vec = self.mistral.embeddings.create(
            model="mistral-embed", inputs=[query]
        ).data[0].embedding
        res = self.collection.query(query_embeddings=[q_vec], n_results=k)
        ids = [int(i.split("_")[1]) for i in res["ids"][0]]
        return ids

    def _bm25_topk(self, query, k):
        scores = self.bm25.get_scores(query.lower().split())
        return sorted(range(len(scores)), key=lambda i: -scores[i])[:k]

    def _rrf(self, rankings, k_const=60, top_k=3):
        score = {}
        for ranking in rankings:
            for rank, doc_id in enumerate(ranking, start=1):
                score[doc_id] = score.get(doc_id, 0) + 1.0 / (k_const + rank)
        return [d for d, _ in sorted(score.items(), key=lambda x: -x[1])[:top_k]]

    def ask(self, question: str, k=3) -> dict:
        vec_ids = self._vector_topk(question, k=10)
        bm_ids = self._bm25_topk(question, k=10)
        final_ids = self._rrf([vec_ids, bm_ids], top_k=k)

        chunks = [self.all_chunks[i] for i in final_ids]
        sources = [self.all_sources[i] for i in final_ids]

        context = "\n\n".join(f"[{s}] {c}" for s, c in zip(sources, chunks))
        response = self.mistral.chat.complete(
            model="mistral-small-latest",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"Context:\n{context}\n\nQuestion: {question}"},
            ],
        )
        answer = response.choices[0].message.content.strip()

        return {"answer": answer, "sources": list(dict.fromkeys(sources)), "raw_question": question}


_bot = None


def _get_bot():
    global _bot
    if _bot is not None:
        return _bot

    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        return None

    from mistralai.client import Mistral
    mistral = Mistral(api_key=api_key)
    _bot = TunisianFAQBot(mistral, CORPUS)
    return _bot


def show_the_solution():
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("=== PART 2: BOT SINGLE QUERY (API key required) ===")
        print("Set MISTRAL_API_KEY in codes/.env to run this section.\n")
        return

    try:
        from mistralai.client import Mistral  # noqa: F401
    except ImportError:
        print("Run: pip install mistralai chromadb langchain-text-splitters rank-bm25")
        return

    print("=== PART 2: TunisianFAQBot — Single Query Demo ===\n")

    bot = _get_bot()

    question = "What's the refund window?"
    result = bot.ask(question, k=3)

    print(f"bot.ask(\"{question}\")\n")
    print("-" * 60)
    print(f"  answer:  {result['answer']}")
    print(f"  sources: {result['sources']}")
    print("-" * 60)
    print("\nOne class, one ask() call. All internals (chunker, vector DB,")
    print("BM25, RRF, grounded prompt) are hidden behind the interface.\n")


# ============================================================
# PART 3: Real Bot In Action
# ============================================================

def real_world_example():
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("=== PART 3: REAL BOT (API key required) ===")
        print("Set MISTRAL_API_KEY in codes/.env to run this section.\n")
        return

    try:
        from mistralai.client import Mistral  # noqa: F401
    except ImportError:
        print("Run: pip install mistralai chromadb langchain-text-splitters rank-bm25")
        return

    print("=== PART 3: Tunisian FAQ Bot In Action ===\n")

    bot = _get_bot()

    questions = [
        "What's the refund window at MASTER Soft?",
        "What products does MASTER Soft build?",
        "How many vacation days do employees get per year?",
        "Who is the CEO?",
        "Quels sont vos horaires d'ouverture ?",       # French
        "How do I contact HR?",
        "What is the capital of France?",              # not in corpus
    ]

    for q in questions:
        result = bot.ask(q, k=3)
        print(f"Q: {result['raw_question']}")
        print(f"A: {result['answer']}")
        print(f"   sources: {result['sources']}\n")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    show_the_problem()
    show_the_solution()
    real_world_example()

    print("--- Key Takeaways ---")
    print("1. The capstone exposes one method: ask(question) -> {answer, sources, ...}.")
    print("2. Hybrid retrieval (vector + BM25) catches both meaning and acronyms.")
    print("3. The grounded system prompt enforces 'use only the context'.")
    print("4. Citations come from retriever metadata, not from the LLM.")
    print("5. Same blueprint = telecom support, bank FAQ, HR assistant, etc.")
