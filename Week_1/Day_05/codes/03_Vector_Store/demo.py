"""
Demo: Vector Store
Storing and retrieving vectors from a database
"""

import os
import sys
from pathlib import Path
from llama_index.core import VectorStoreIndex, Settings, SimpleDirectoryReader
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core.storage import StorageContext
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.embeddings.mistralai import MistralAIEmbedding
from dotenv import load_dotenv

# Load environment variables
project_root = Path(__file__).parent.parent
load_dotenv(project_root / ".env")

docs_dir = Path(__file__).parent.parent / "sample_documents"
SAMPLE_DOCS = SimpleDirectoryReader(
    input_files=[
        str(docs_dir / "web_development.txt"),
        str(docs_dir / "software_engineering.txt"),
        str(docs_dir / "data_systems.txt"),
    ]
).load_data()


def example_1_simple_vector_store():
    """Example 1: Create a simple vector store"""
    print("\n" + "="*60)
    print("Example 1: Creating a Simple Vector Store")
    print("="*60)

    parser = SimpleNodeParser.from_defaults(chunk_size=256)
    nodes = parser.get_nodes_from_documents(SAMPLE_DOCS)

    # SimpleVectorStore keeps vectors in a Python dict in RAM.
    # It uses brute-force cosine similarity — compares the query vector
    # against every stored vector one by one. Fine for small collections
    # (< 10K nodes), but too slow for production-scale data.
    vector_store = SimpleVectorStore()

    print(f"\n✓ Created vector store in memory")
    print(f"  - Number of nodes: {len(nodes)}")

    for i, node in enumerate(nodes[:2]):
        text_preview = node.text[:60] + "..." if len(node.text) > 60 else node.text
        print(f"\nNode #{i+1}:")
        # node_id is the key used to look up the full text and metadata
        # after the vector store returns a nearest-neighbor result.
        print(f"  - ID: {node.node_id[:20]}...")
        print(f"  - Text: {text_preview}")
        print(f"  - Source: {node.metadata}")


def example_2_index_storage_context():
    """Example 2: Storage context"""
    print("\n" + "="*60)
    print("Example 2: Storage Context")
    print("="*60)

    parser = SimpleNodeParser.from_defaults(chunk_size=256)
    nodes = parser.get_nodes_from_documents(SAMPLE_DOCS)

    vector_store = SimpleVectorStore()

    # StorageContext is the container that holds all storage backends together:
    # the vector store (for embeddings), the doc store (for raw text), and the
    # index store (for index metadata). Passing it explicitly lets you swap
    # backends — e.g. replace SimpleVectorStore with Chroma — without changing
    # any other code.
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store
    )

    print(f"\n✓ Created storage context")
    print(f"  - Vector store type: {type(vector_store).__name__}")
    print(f"  - Number of nodes ready: {len(nodes)}")

    if nodes:
        example_node = nodes[0]
        print(f"\n📊 Information about first node:")
        print(f"  - ID: {example_node.node_id[:25]}...")
        print(f"  - Text size: {len(example_node.text)} characters")
        print(f"  - Metadata: {example_node.metadata}")


def example_3_vector_search():
    """Example 3: Real vector search using Mistral embeddings"""
    print("\n" + "="*60)
    print("Example 3: Real Vector Search with Mistral Embeddings")
    print("="*60)

    api_key = os.getenv("MISTRAL_API_KEY")

    # Set the embedding model on Settings so VectorStoreIndex uses it
    # automatically when building the index and when embedding queries.
    # Both must use the same model — otherwise the query vector and the
    # document vectors live in different spaces and similarity scores
    # become meaningless.
    Settings.embed_model = MistralAIEmbedding(
        model_name="mistral-embed",
        api_key=api_key
    )

    # from_documents chunks, embeds, and stores all documents in one call.
    # Internally it: parses → embeds each node → inserts into the vector store.
    index = VectorStoreIndex.from_documents(SAMPLE_DOCS)

    # as_retriever returns chunks only — no LLM call, no answer synthesis.
    # Useful when you want to inspect what was retrieved before deciding
    # whether to send it to an LLM.
    retriever = index.as_retriever(similarity_top_k=2)

    queries = ["What is web development?", "How is data stored?"]

    for query in queries:
        print(f"\n🔍 Query: '{query}'")
        results = retriever.retrieve(query)
        for i, node in enumerate(results, 1):
            print(f"  Result #{i}:")
            print(f"    - Source: {node.metadata.get('source')}")
            # Cosine similarity score: 1.0 = perfect match, 0.0 = unrelated.
            # Scores above ~0.75 indicate a strong semantic match.
            print(f"    - Score:  {node.score:.4f}")
            print(f"    - Text:   {node.text[:80]}...")


def example_4_document_statistics():
    """Example 4: Vector store statistics"""
    print("\n" + "="*60)
    print("Example 4: Vector Store Statistics")
    print("="*60)

    parser = SimpleNodeParser.from_defaults(chunk_size=256)
    nodes = parser.get_nodes_from_documents(SAMPLE_DOCS)

    total_chars = sum(len(node.text) for node in nodes)
    avg_chars = total_chars / len(nodes) if nodes else 0
    avg_words = sum(len(node.text.split()) for node in nodes) / len(nodes) if nodes else 0

    # These numbers help estimate embedding API cost:
    # Mistral charges per token (~4 chars/token), so total_chars / 4 ≈ total tokens.
    print(f"\n📊 Statistics:")
    print(f"  - Original documents: {len(SAMPLE_DOCS)}")
    print(f"  - Nodes after chunking: {len(nodes)}")
    print(f"  - Total characters: {total_chars}")
    print(f"  - Average characters per node: {avg_chars:.0f}")
    print(f"  - Average words per node: {avg_words:.0f}")

    from collections import Counter
    # Counter groups nodes by category so you can see if the index is
    # balanced — an uneven distribution can bias retrieval toward larger categories.
    topics = Counter(node.metadata.get("category") for node in nodes if node.metadata)

    print(f"\n📁 Distribution by topic:")
    for topic, count in topics.items():
        print(f"  - {topic}: {count} nodes")


def example_5_persistence():
    """Example 5: Save index to disk, reload it, and query without re-embedding"""
    print("\n" + "="*60)
    print("Example 5: Vector Store Persistence")
    print("="*60)

    from llama_index.core import load_index_from_storage

    persist_dir = Path(__file__).parent / "storage"

    # --- Step 1: build and save ---
    # Embeddings are computed here (API call). persist() writes them to disk so
    # the next run can skip this expensive step entirely.
    print("\n⏳ Building index and saving to disk...")
    index = VectorStoreIndex.from_documents(SAMPLE_DOCS, show_progress=False)
    index.storage_context.persist(persist_dir=str(persist_dir))
    print(f"✓ Index saved to: {persist_dir}")
    print(f"  Files: {[f.name for f in persist_dir.iterdir()]}")

    # --- Step 2: reload from disk (no API call) ---
    # StorageContext.from_defaults reads the JSON files written above and
    # reconstructs the vector store in memory — no embedding API needed.
    print("\n⏳ Reloading index from disk...")
    storage_context = StorageContext.from_defaults(persist_dir=str(persist_dir))
    loaded_index = load_index_from_storage(storage_context)
    print("✓ Index reloaded successfully")

    # --- Step 3: query the reloaded index ---
    # The retriever works identically whether the index was just built or loaded
    # from disk — the caller cannot tell the difference.
    retriever = loaded_index.as_retriever(similarity_top_k=1)
    result = retriever.retrieve("What is web development?")
    print(f"\n🔍 Query on reloaded index: 'What is web development?'")
    print(f"  - Source: {result[0].metadata.get('source')}")
    print(f"  - Score:  {result[0].score:.4f}")
    print(f"  - Text:   {result[0].text[:80]}...")

    print(f"\n✓ Files on disk (inspect them in your file explorer):")
    for f in sorted(persist_dir.iterdir()):
        print(f"  - {f.name}  ({f.stat().st_size} bytes)")


def main():
    """Run all examples"""
    print("\n🚀 Demo: Vector Store")
    print("="*60)

    try:
        example_1_simple_vector_store()
        example_2_index_storage_context()
        example_3_vector_search()
        example_4_document_statistics()
        example_5_persistence()

        print("\n" + "="*60)
        print("✅ All examples completed successfully!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
