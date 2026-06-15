"""
02 - Document Preparation Demo
==============================
Shows how to load TXT, PDF, and DOCX, and clean common noise
(page numbers, headers, hyphen line breaks, whitespace).

HOW TO RUN THIS FILE:
1. pip install pypdf python-docx reportlab
2. python generate_sample_docs.py   (creates sample_docs/*)
3. python demo.py
"""

import os
import re

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "sample_docs")


SAMPLE_RAW_TEXT = """\
MASTER Soft — Internal — Confidential
Page 1 / 3

Welcome to the MASTER Soft employee hand-
book. This document explains our company poli-
cies for our Tunis and Sousse offices.

MASTER Soft — Internal — Confidential
Page 2 / 3

Refund policy: Customers can request a re-
fund within 14 days of purchase, no questions
asked. Contact Yasmine in customer service.

MASTER Soft — Internal — Confidential
Page 3 / 3

Vacation:    Employees    accrue
2 days per month, totalling 24 days/year.
"""


# ============================================================
# PART 1: The Problem — Raw Extracted Text
# ============================================================

def show_the_problem():
    print("=== PART 1: Raw, Messy Document Text ===\n")
    print(SAMPLE_RAW_TEXT)
    print("\nIssues visible above:")
    print("  - Page numbers ('Page 1 / 3')")
    print("  - Repeated headers ('MASTER Soft — Internal — Confidential')")
    print("  - Hyphenated line breaks ('hand-\\nbook')")
    print("  - Inconsistent whitespace")
    print("Feeding this to a chunker = noisy retrieval.\n")


# ============================================================
# PART 2: The Solution — A Cleaning Pipeline
# ============================================================

def clean_text(raw: str) -> str:
    text = raw

    # 1. Remove page numbers
    text = re.sub(r"Page\s*\d+\s*/\s*\d+", "", text)

    # 2. Remove repeated headers
    text = re.sub(r"MASTER Soft.*?Confidential", "", text)

    # 3. Repair hyphen line breaks ("re-\nfund" -> "refund")
    text = re.sub(r"-\n", "", text)

    # 4. Collapse whitespace (but keep paragraph breaks)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n\n", text)

    return text.strip()


def show_the_solution():
    print("=== PART 2: After the Cleaning Pipeline ===\n")
    cleaned = clean_text(SAMPLE_RAW_TEXT)
    print(cleaned)
    print("\nNow it's ready to be chunked and embedded.\n")


# ============================================================
# PART 3: Real Loaders for PDF, DOCX, and TXT
# ============================================================

def load_pdf(path):
    from pypdf import PdfReader

    reader = PdfReader(path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        pages.append({"page": i + 1, "text": clean_text(text)})
    return pages


def load_docx(path):
    from docx import Document

    doc = Document(path)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    full_text = "\n\n".join(paragraphs)
    return clean_text(full_text)


def load_txt(path):
    with open(path, encoding="utf-8") as f:
        return clean_text(f.read())


def real_world_example():
    print("=== PART 3: Real Loaders (PDF, DOCX, TXT) ===\n")

    if not os.path.isdir(SAMPLE_DIR):
        print(f"Sample files not found in {SAMPLE_DIR}")
        print("Run: python generate_sample_docs.py\n")
        return

    try:
        print("PDF (handbook.pdf):")
        for page in load_pdf(os.path.join(SAMPLE_DIR, "handbook.pdf")):
            print(f"  [page {page['page']}] {page['text']!r}")
    except ImportError:
        print("Run: pip install pypdf")

    try:
        print("\nDOCX (policies.docx):")
        print(f"  {load_docx(os.path.join(SAMPLE_DIR, 'policies.docx'))!r}")
    except ImportError:
        print("Run: pip install python-docx")

    print("\nTXT (notes.txt):")
    print(f"  {load_txt(os.path.join(SAMPLE_DIR, 'notes.txt'))!r}")

    print("\nKey habit: always run clean_text() before chunking.\n")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    show_the_problem()
    show_the_solution()
    real_world_example()

    print("--- Key Takeaways ---")
    print("1. PDF/DOCX extractors return raw, noisy text.")
    print("2. Strip page numbers, headers, footers before chunking.")
    print("3. Fix hyphen line breaks and whitespace.")
    print("4. Keep source metadata: filename + page for every chunk.")
    print("5. Skipping cleanup is the #1 RAG quality killer.")
