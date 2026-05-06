# 01 - Document Loading

---

## 📦 Packages

**Requirements**: Python 3.11 or 3.12 (not 3.13+)

```bash
# Create venv with Python 3.11 (if needed)
python -m venv bootcamp

# Activate
bootcamp\Scripts\activate  # Windows
source bootcamp/bin/activate  # Mac/Linux

# Install packages
pip install llama-index llama-index-readers-file python-dotenv
```

---

## The Foundation: Loading Documents

RAG starts here. Before embeddings, vectors, or search — you need to load documents.

A **Document** in LlamaIndex:

```python
from llama_index.core import Document

doc = Document(
    text="The actual content of the file...",
    metadata={
        "filename": "example.pdf",
        "page": 1,
        "source": "path/to/file",
        # Add custom metadata too:
        "category": "financial",
        "date": "2024-01-15"
    }
)
```

The `.text` is the content. The `.metadata` dict holds **anything useful for later** — source, page number, custom tags, etc.

---

## Document Loaders

**SimpleDirectoryReader** — the simplest way:

```python
from llama_index.readers.file import SimpleDirectoryReader

reader = SimpleDirectoryReader(input_dir="./documents")
documents = reader.load_data()

print(f"Loaded {len(documents)} documents")
for doc in documents:
    print(f"- {doc.metadata.get('file_name', 'unknown')}: {len(doc.text)} chars")
```

Automatically detects file types (PDF, TXT, MD, CSV, etc.) and loads them.

---

## Supported File Types

| Format | Reader | Notes |
|--------|--------|-------|
| `.pdf` | PDFReader | Extracts text + handles pagination |
| `.txt` | TextFileReader | Plain text |
| `.md` | MarkdownReader | Preserves markdown structure |
| `.csv` | CSVReader | Each row as a document |
| `.json` | JSONReader | Extracts specified fields |
| Web URLs | SimpleWebPageReader | HTTP GET + parsing |
| Databases | SQLReader | Query results as documents |

---

## Adding Metadata

Metadata is **crucial** for traceability:

```python
documents = reader.load_data()

# Add custom metadata
for doc in documents:
    filename = doc.metadata.get("file_name", "unknown")
    doc.metadata["custom_category"] = "training_material"
    doc.metadata["source_system"] = "legal_database"
```

Later, when you retrieve a chunk, metadata travels with it — enabling:
- **Citations**: "Source: legal_database, file: contract-v2.pdf, page 3"
- **Filtering**: "Only search documents with category=training_material"
- **Ranking**: "Boost results from recent files"

---

## Common Issues & Fixes

| Problem | Cause | Solution |
|---------|-------|----------|
| Memory error on large files | Single file > RAM | Use batch loading or chunk before parsing |
| Character encoding errors | Mixed encodings (UTF-8, Latin-1, etc.) | Specify `encoding="utf-8"` in reader |
| PDF images ignored | PDFs with scanned text | Use OCR reader (`PDFPlumberReader` + OCR) |
| No documents loaded | Wrong path or permissions | Check folder exists & has readable files |

---

## Manual Document Creation

Sometimes you skip file loading and create documents directly:

```python
from llama_index.core import Document

documents = [
    Document(
        text="Python is a versatile programming language...",
        metadata={"source": "wikipedia", "topic": "programming"}
    ),
    Document(
        text="Machine Learning is a subset of AI...",
        metadata={"source": "textbook", "chapter": 5}
    ),
]
```

Useful for:
- Testing (lightweight sample data)
- Combining multiple sources programmatically
- API responses (fetch from a service, wrap in Document)

---

## Best Practices

1. **Always set metadata** — future you will need it
2. **Use consistent keys** — decide on metadata schema upfront
3. **Handle errors gracefully** — corrupted files shouldn't crash the pipeline
4. **Load in batches** — don't load 10GB at once
5. **Preserve source info** — filename, URL, database table, etc.

---

## Next Steps

Once documents are loaded → chunk them → embed them → store them.

Each step builds on the previous one.
