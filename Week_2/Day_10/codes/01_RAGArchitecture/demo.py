"""
01 - RAG Architecture Demo
==========================
Walks through a minimal RAG pipeline in code so the student can see every step:
chunk -> embed -> retrieve -> generate.

HOW TO RUN THIS FILE:
1. pip install mistralai python-dotenv
2. Copy ../.env.example to ../.env and add your MISTRAL_API_KEY (optional for PART 3)
3. python demo.py
"""

import os
from dotenv import load_dotenv

load_dotenv()


# A tiny "knowledge base" — pretend these are pages from a software company's internal handbook
KNOWLEDGE_BASE = [
    "Our company is called MASTER Soft, a software engineering company based in Tunis with a satellite office in Sousse.",
    "Employees accrue 2 paid vacation days per month, totalling 24 days per year, capped at 30.",
    "Customers on the Pro plan get a refund within 14 days of purchase, no questions asked.",
    "Working hours are 9:00 to 18:00 Monday to Friday, Tunis time.",
    "Our main products are a CRM platform, a billing API, and a mobile app builder.",
    "Yasmine Ben Ali is the head of customer success.",
    "Khaled leads the engineering team, based in the Sousse office.",
]


# ============================================================
# PART 1: The Problem — LLM Without Context Hallucinates
# ============================================================

def show_the_problem():
    print("=== PART 1: Why a Plain LLM Hallucinates ===\n")

    question = "Who leads the engineering team at MASTER Soft?"

    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print(f"Question: {question}")
        print("LLM (no context): [skipped — set MISTRAL_API_KEY to run this for real]")
        print("\nReality (from the handbook): Khaled leads engineering, based in the Sousse office.")
        print("Without context, the LLM has nothing to go on but guess a name.\n")
        return

    try:
        from mistralai.client import Mistral
    except ImportError:
        print("Run: pip install mistralai")
        return

    client = Mistral(api_key=api_key)
    response = client.chat.complete(
        model="mistral-small-latest",
        messages=[{"role": "user", "content": question}],
    )
    llm_answer_no_rag = response.choices[0].message.content.strip()

    print(f"Question: {question}")
    print(f"LLM (no context): '{llm_answer_no_rag}'")
    print("\nReality (from the handbook): Khaled leads engineering, based in the Sousse office.")
    print("'MASTER Soft' doesn't exist outside this demo, so the LLM either")
    print("makes up a name or admits it doesn't know — either way, it never saw the handbook.\n")


# ============================================================
# PART 2: The Solution — RAG Step by Step
# ============================================================

def show_the_solution():
    print("=== PART 2: RAG Step by Step (Simulated Retrieval) ===\n")

    question = "Who leads the engineering team at MASTER Soft?"

    # Step 1: naive "retrieval" — keyword score
    print("Step 1: Retrieve relevant chunks (here: naive keyword score)")
    scores = [(c, sum(w in c.lower() for w in question.lower().split())) for c in KNOWLEDGE_BASE]
    scores.sort(key=lambda x: -x[1])
    top_chunks = [c for c, s in scores[:2]]
    for c in top_chunks:
        print(f"  - {c}")

    # Step 2: build the prompt with context
    print("\nStep 2: Build a grounded prompt")
    context = "\n".join(top_chunks)
    prompt = (
        f"Answer using ONLY the context below. Say 'I don't know' if missing.\n\n"
        f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    )
    print(prompt)

    # Step 3: simulated answer
    print("\nStep 3: LLM answers from the context (simulated):")
    print("  'Khaled leads the engineering team, based in the Sousse office.'\n")


# ============================================================
# PART 3: Real RAG With Mistral
# ============================================================

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

    print("=== PART 3: Real RAG With Mistral ===\n")

    client = Mistral(api_key=api_key)

    # Use Mistral embeddings for retrieval
    chunk_vectors = client.embeddings.create(
        model="mistral-embed", inputs=KNOWLEDGE_BASE
    ).data

    def cosine(a, b):
        from math import sqrt
        dot = sum(x * y for x, y in zip(a, b))
        na = sqrt(sum(x * x for x in a))
        nb = sqrt(sum(y * y for y in b))
        return dot / (na * nb)

    def retrieve(question, k=2):
        q_vec = client.embeddings.create(
            model="mistral-embed", inputs=[question]
        ).data[0].embedding
        scored = [
            (KNOWLEDGE_BASE[i], cosine(q_vec, cv.embedding))
            for i, cv in enumerate(chunk_vectors)
        ]
        scored.sort(key=lambda x: -x[1])
        return scored[:k]

    questions = [
        "What is the refund policy at MASTER Soft?",
        "Who leads engineering, and where are they based?",
        "What products does MASTER Soft build?",
        "What's the meaning of life?",  # not in knowledge base
    ]

    for q in questions:
        top = retrieve(q, k=2)
        context = "\n".join(c for c, _ in top)

        response = client.chat.complete(
            model="mistral-small-latest",
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Answer using ONLY the context. Say 'I don't know' if missing.\n\n"
                        f"Context:\n{context}\n\nQuestion: {q}\nAnswer:"
                    ),
                }
            ],
        )
        answer = response.choices[0].message.content.strip()
        print(f"Q: {q}")
        print(f"A: {answer}\n")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    show_the_problem()
    show_the_solution()
    real_world_example()

    print("--- Key Takeaways ---")
    print("1. RAG = retrieve relevant chunks, then generate an answer using them.")
    print("2. Without RAG, LLMs hallucinate on private/specific data.")
    print("3. The prompt template forces grounding: 'use only the context'.")
    print("4. Retrieval quality > prompt cleverness — focus there first.")
    print("5. Next concepts: documents -> clean -> chunk -> embed -> retriever.")
