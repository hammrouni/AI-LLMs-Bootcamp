"""
03 - Text Chunking Demo
=======================
Compares naive fixed-size chunking with LangChain's RecursiveCharacterTextSplitter
on a Tunisian-themed sample document.

HOW TO RUN THIS FILE:
1. pip install langchain-text-splitters
2. python demo.py
"""

SAMPLE = """\
MASTER Soft is a software engineering company based in Tunis, with a satellite office in Sousse.

Our refund policy is generous. Customers on the Pro plan can request a refund within 14 days of purchase, no questions asked. To start a refund, contact Yasmine Ben Ali, the head of customer success. Refunds are processed within 5 business days back to the original payment method.

MASTER Soft builds three products: a CRM platform, a billing API, and a mobile app builder. The CRM platform is the company's flagship product, used by over 500 businesses across Tunisia.

Vacation policy: employees accrue 2 paid vacation days per month, totalling 24 days per year. Days roll over up to a cap of 30 days. Approval is needed at least one week in advance for vacations longer than 5 working days.

Working hours are 9:00 to 18:00 Monday to Friday, with a 1-hour lunch break that can be split. Remote work is allowed up to 2 days per week with manager approval. Khaled leads the engineering team, based in the Sousse office.
"""


# ============================================================
# PART 1: The Problem — Naive Fixed-Size Chunking
# ============================================================

def naive_split(text, size=200):
    return [text[i : i + size] for i in range(0, len(text), size)]


def show_the_problem():
    print("=== PART 1: Naive Fixed-Size Chunking ===\n")
    chunks = naive_split(SAMPLE, size=200)
    for i, c in enumerate(chunks):
        last_char = c[-1] if c else ""
        cut_word = c.split()[-1] if c.split() else ""
        preview = " ".join(c.split())[-60:]
        print(f"[chunk {i}] ({len(c):>3} chars) ends with: ...{preview}")
        if last_char.isalpha() and not c.endswith(" "):
            print(f"             -> likely cut mid-word: '{cut_word}'")
    print(f"\nTotal: {len(chunks)} chunks. Several are cut mid-word/mid-sentence.\n")


# ============================================================
# PART 2: The Solution — Recursive Splitter
# ============================================================

def show_the_solution():
    print("=== PART 2: RecursiveCharacterTextSplitter ===\n")

    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
    except ImportError:
        print("Run: pip install langchain-text-splitters")
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_text(SAMPLE)

    for i, c in enumerate(chunks):
        print(f"[chunk {i}] ({len(c)} chars) {c!r}")
    print(f"\nTotal: {len(chunks)} chunks. Each ends at a natural boundary.\n")


# ============================================================
# PART 3: Tuning chunk_size and chunk_overlap
# ============================================================

def real_world_example():
    print("=== PART 3: Effect of chunk_size and overlap ===\n")

    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
    except ImportError:
        print("Run: pip install langchain-text-splitters")
        return

    configs = [
        {"chunk_size": 100,  "chunk_overlap": 0},
        {"chunk_size": 300,  "chunk_overlap": 50},
        {"chunk_size": 600,  "chunk_overlap": 100},
        {"chunk_size": 1200, "chunk_overlap": 200},
    ]

    for cfg in configs:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=cfg["chunk_size"],
            chunk_overlap=cfg["chunk_overlap"],
        )
        chunks = splitter.split_text(SAMPLE)
        avg_len = sum(len(c) for c in chunks) / max(len(chunks), 1)
        print(
            f"size={cfg['chunk_size']:>4} overlap={cfg['chunk_overlap']:>3} "
            f"-> {len(chunks):>2} chunks, avg length {avg_len:.0f} chars"
        )

    print("\nTry chunk_size=300 first; tune up for long technical docs.\n")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    show_the_problem()
    show_the_solution()
    real_world_example()

    print("--- Key Takeaways ---")
    print("1. Naive fixed-size chunking cuts words and sentences -> bad retrieval.")
    print("2. RecursiveCharacterTextSplitter respects natural boundaries.")
    print("3. Defaults: chunk_size 300-500, chunk_overlap 50-100.")
    print("4. Smaller for FAQs, larger for legal/technical text.")
    print("5. Measure recall on your data; chunk size is not one-size-fits-all.")
