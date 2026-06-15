"""
05 - Retrieval Quality (Capstone) Demo
======================================
Builds a tiny Tunisian corpus + an eval set, runs the retriever, and computes
recall@k and MRR. Then runs an ablation on chunk_size to show the metric moving.

HOW TO RUN THIS FILE:
1. pip install chromadb mistralai langchain-text-splitters python-dotenv
2. Copy ../.env.example to ../.env and add your MISTRAL_API_KEY
3. python demo.py
"""

import os
import shutil
from dotenv import load_dotenv

load_dotenv()


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


# Each correct_sources entry must match a source filename key in CORPUS.
EVAL_SET = [
    {"question": "What's the refund window?",                "correct_sources": {"refunds.txt"}},
    {"question": "How are refunds processed?",               "correct_sources": {"refunds.txt"}},
    {"question": "What products does MASTER Soft build?",    "correct_sources": {"products.txt"}},
    {"question": "How many businesses use the CRM platform?", "correct_sources": {"products.txt"}},
    {"question": "How many vacation days per year?",         "correct_sources": {"vacation.txt"}},
    {"question": "Do I need approval for long vacations?",   "correct_sources": {"vacation.txt"}},
    {"question": "What are your working hours?",             "correct_sources": {"hours.txt"}},
    {"question": "Is remote work allowed?",                  "correct_sources": {"hours.txt"}},
    {"question": "When was MASTER Soft founded?",            "correct_sources": {"company.txt"}},
    {"question": "How many employees does MASTER Soft have?", "correct_sources": {"company.txt"}},
]


# ============================================================
# PART 1: Problem — Eyeballing Is Unreliable
# ============================================================

def show_the_problem():
    print("=== PART 1: 'Looks Good' Is Not a Metric ===\n")
    print("Without eval you cannot answer:")
    print("  - Did chunk_size=400 just make retrieval better or worse?")
    print("  - Is my recall above 80% across all our FAQ topics?")
    print("  - Should we ship?")
    print()


# ============================================================
# PART 2: Eval Pipeline (Simulated — No API Needed)
# ============================================================

def show_the_solution():
    print("=== PART 2: Eval Pipeline (Walkthrough) ===\n")
    print("Step 1: Build a small eval set of (question, correct_source).")
    print("Step 2: For each question, ask the retriever for top-k chunks.")
    print("Step 3: Check whether any chunk comes from the correct source.")
    print("Step 4: Aggregate hits -> recall@k. Track first-hit rank -> MRR.")
    print()
    print("Example eval set entries:")
    for e in EVAL_SET[:3]:
        sources = ", ".join(sorted(e["correct_sources"]))
        print(f"  Q: \"{e['question']}\"  expected: {sources}")
    print()


# ============================================================
# PART 3: Real End-to-End Eval (Two Chunk Sizes)
# ============================================================

def embed_with_retry(mistral, texts):
    """Embed a batch of texts, retrying with backoff on 429 rate limits."""
    import time
    from mistralai.client.errors import SDKError

    for attempt in range(5):
        try:
            return [
                d.embedding
                for d in mistral.embeddings.create(model="mistral-embed", inputs=texts).data
            ]
        except SDKError as e:
            if "429" not in str(e) or attempt == 4:
                raise
            time.sleep(2 ** attempt)  # 1, 2, 4, 8, 16 seconds


class SimpleRetriever:
    def __init__(self, persist_path, mistral, chunk_size, chunk_overlap=50):
        import chromadb
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        if os.path.exists(persist_path):
            shutil.rmtree(persist_path)
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection("docs")
        self.mistral = mistral
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

    def index(self, corpus: dict):
        # Split everything first, then embed all chunks in ONE batched call
        # (one API request per chunk_size instead of one per document).
        all_chunks, all_sources = [], []
        for source, text in corpus.items():
            for chunk in self.splitter.split_text(text):
                all_chunks.append(chunk)
                all_sources.append(source)

        if not all_chunks:
            return

        vectors = embed_with_retry(self.mistral, all_chunks)
        counts = {}
        ids = []
        for source in all_sources:
            counts[source] = counts.get(source, 0)
            ids.append(f"{source}::{counts[source]}")
            counts[source] += 1

        self.collection.add(
            documents=all_chunks,
            embeddings=vectors,
            metadatas=[{"source": s} for s in all_sources],
            ids=ids,
        )

    def search_by_vector(self, q_vec, k=5):
        return self.collection.query(query_embeddings=[q_vec], n_results=k)


def evaluate(retriever, eval_set, query_vectors, k=5):
    hits = 0
    mrr_sum = 0.0
    for item in eval_set:
        results = retriever.search_by_vector(query_vectors[item["question"]], k=k)
        sources = [m["source"] for m in results["metadatas"][0]]
        rank = next(
            (r for r, s in enumerate(sources, start=1) if s in item["correct_sources"]),
            None,
        )
        if rank:
            hits += 1
            mrr_sum += 1.0 / rank
    return {"recall@k": hits / len(eval_set), "MRR": mrr_sum / len(eval_set), "k": k}


def real_world_example():
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("=== PART 3: REAL EVAL (API key required) ===")
        print("Set MISTRAL_API_KEY in codes/.env to run this section.\n")
        return

    try:
        from mistralai.client import Mistral
    except ImportError:
        print("Run: pip install mistralai")
        return

    print("=== PART 3: Real Eval — chunk_size Ablation ===\n")
    mistral = Mistral(api_key=api_key)

    # Query embeddings don't depend on chunk_size, so compute them once
    # and reuse across every ablation config (fewer API calls overall).
    questions = [item["question"] for item in EVAL_SET]
    question_vectors = dict(zip(questions, embed_with_retry(mistral, questions)))

    for cs in [150, 300, 600]:
        ret = SimpleRetriever(f"./chroma_eval_cs{cs}", mistral, chunk_size=cs)
        ret.index(CORPUS)
        scores = evaluate(ret, EVAL_SET, question_vectors, k=3)
        print(f"chunk_size={cs:>3}  recall@{scores['k']}={scores['recall@k']:.2f}  MRR={scores['MRR']:.2f}")

    print("\nPick the chunk_size with the best trade-off of recall and MRR.\n")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    show_the_problem()
    show_the_solution()
    real_world_example()

    print("--- Key Takeaways ---")
    print("1. Retrieval quality must be measured, not eyeballed.")
    print("2. recall@k and MRR are the two basic metrics.")
    print("3. A 20-50 question eval set is enough to start.")
    print("4. Ablate one knob at a time (chunk_size, embedding model, k).")
    print("5. Tomorrow: plug an LLM on top -> measure full-RAG answer quality.")
