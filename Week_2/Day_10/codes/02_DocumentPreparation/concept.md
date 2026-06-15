# 02 - Document Preparation

---

## 📦 Packages

```bash
pip install pypdf python-docx
```

---

## What is Document Preparation?

**Document preparation** is the step where you turn raw files (PDF, DOCX, HTML, TXT, scanned images) into clean plain text ready for chunking. It's the unglamorous, essential first step of any RAG pipeline.

Think of cooking a Tunisian couscous:
- Raw fish, raw vegetables, raw spices = you can't just put them in a bowl
- You wash, you peel, you chop, you season *before* anything goes into the pot
- The dish is only as good as the prep

Same with RAG: clean text in → clean answers out. Messy text in → garbage answers out.

---

## What is the Problem?

### Raw documents are messy

A typical Tunisian company handbook PDF has:
- Page numbers ("Page 12 / 87")
- Headers ("MASTER Soft — Internal — Confidential")
- Footers ("Last updated 2024-03-15")
- Tables of contents
- OCR artifacts ("Ø×Ù‚Ø¯" instead of "تقدم")
- Inconsistent line breaks mid-sentence

If you embed all that noise, your retriever will return chunks that look like:

```
"Page 12 / 87
MASTER Soft — Internal — Confidential

The refund policy is..."
```

The embedding picks up on "Page 12", which has nothing to do with refund policies. Retrieval degrades.

---

## What is the Solution? Clean Before You Chunk!

Pre-process every document:
1. **Extract text** (pypdf for PDF, python-docx for DOCX, plain read for TXT)
2. **Strip boilerplate** (headers, footers, page numbers, watermarks)
3. **Fix encoding** (UTF-8, normalize whitespace, fix mojibake)
4. **Reflow paragraphs** (join lines broken mid-sentence by the extractor)
5. **Tag metadata** (source filename, section, page range)

Then — and only then — chunk.

---

## How It Works in Python

### Key words to know:

| Keyword / Concept | What it means |
|---|---|
| `pypdf.PdfReader` | Read PDF pages as text |
| `docx.Document` | Read .docx paragraphs |
| `re.sub` | Strip patterns like page numbers |
| `normalize whitespace` | Collapse multiple spaces / newlines |
| `mojibake` | Wrong-encoding garbage (`Ã©` instead of `é`) |
| `source metadata` | Filename, page, section attached to each chunk |

### The Golden Rule:
- **One source = one extractor.** PDF needs pypdf. DOCX needs python-docx. HTML needs BeautifulSoup. Don't try to read all of them with `open()`.

### Basic Usage

```python
import re
from pypdf import PdfReader

def load_pdf(path):
    reader = PdfReader(path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        # Strip headers/footers — adapt the regex to your actual format
        text = re.sub(r"Page \d+ / \d+", "", text)
        text = re.sub(r"MASTER Soft.*?Confidential", "", text)
        # Normalize whitespace
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        pages.append({"page": i + 1, "text": text.strip()})
    return pages
```

```python
from docx import Document

def load_docx(path):
    doc = Document(path)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)
```

### Cleaning Checklist

| Issue | Fix |
|---|---|
| Page numbers `"Page X / Y"` | `re.sub(r"Page \d+ ?/? ?\d*", "", text)` |
| Repeated headers | Detect lines that appear on most pages, strip them |
| Hyphen line-breaks (`exam-\nple`) | `re.sub(r"-\n", "", text)` |
| Multiple spaces | `re.sub(r"\s+", " ", text)` |
| Wrong encoding | Re-decode with `bytes.decode("utf-8", errors="replace")` |

### BAD vs GOOD

```python
# BAD — feed the raw PDF text straight to chunking
raw = "".join(p.extract_text() for p in reader.pages)
chunks = simple_split(raw, 500)

# GOOD — clean, then chunk, and keep source metadata
pages = load_pdf("handbook.pdf")
chunks = []
for p in pages:
    for chunk in simple_split(p["text"], 500):
        chunks.append({"text": chunk, "source": "handbook.pdf", "page": p["page"]})
```

---

## Why This Matters for AI Apps

Every real RAG project starts with messy documents:
- A Tunisian bank chatbot: 200 PDFs of product fees, terms, and conditions
- A medical assistant: thousands of clinical protocols in DOCX
- A legal assistant: scanned contracts that need OCR before anything else

Skipping cleanup is the #1 reason RAG demos fail in production. The fancy embedding model can't save you if half the chunks are "Page 12 — Confidential".

```
Same docs, same model, just better cleaning:
Retrieval recall@5: 42% → 87%
```
