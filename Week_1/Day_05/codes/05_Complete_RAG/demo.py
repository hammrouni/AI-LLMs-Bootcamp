"""
Demo: Complete RAG Pipeline
Assembling all steps into a complete RAG system
"""

import os
import sys
from pathlib import Path
from llama_index.core import VectorStoreIndex, Settings, SimpleDirectoryReader
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.embeddings.mistralai import MistralAIEmbedding
from llama_index.llms.mistralai import MistralAI
from dotenv import load_dotenv

# Load environment variables
project_root = Path(__file__).parent.parent
load_dotenv(project_root / ".env")

api_key = os.getenv("MISTRAL_API_KEY")

# Configure models globally so every VectorStoreIndex and query_engine
# in this file automatically uses Mistral without explicit arguments.
# embed_model handles document → vector conversion.
# llm handles retrieved context → natural-language answer.
Settings.embed_model = MistralAIEmbedding(model_name="mistral-embed", api_key=api_key)
Settings.llm = MistralAI(model="mistral-small-latest", api_key=api_key)

docs_dir = project_root / "sample_documents"

# file_metadata maps each filename to a category so downstream code can filter
# and cite documents by topic instead of showing raw file paths.
FILE_CATEGORIES = {
    "tunisia_geography.txt": "geography",
    "tunisian_cuisine.txt":  "food",
    "tech_sector.txt":       "technology",
    "mistral_ai.txt":        "ai-technology",
    "rag_systems.txt":       "ai-systems",
}

KNOWLEDGE_BASE = SimpleDirectoryReader(
    input_files=[str(docs_dir / f) for f in FILE_CATEGORIES],
    file_metadata=lambda path: {"category": FILE_CATEGORIES.get(Path(path).name, "unknown")},
).load_data()


def example_1_load_documents():
    """Example 1: Loading documents"""
    print("\n" + "="*60)
    print("Step 1: Loading Documents")
    print("="*60)

    # In a real system these documents would come from a database, SharePoint,
    # PDFs, web scraping, etc. Here they are hardcoded for demo simplicity.
    # The category metadata will appear in source citations at query time.
    print(f"\n✓ Loaded {len(KNOWLEDGE_BASE)} documents about Tunisia and Technology")
    for i, doc in enumerate(KNOWLEDGE_BASE, 1):
        text_preview = doc.text[:50] + "..." if len(doc.text) > 50 else doc.text
        print(f"  {i}. {doc.metadata.get('category', 'unknown')}: {text_preview}")


def example_2_parse_and_chunk():
    """Example 2: Chunking documents"""
    print("\n" + "="*60)
    print("Step 2: Chunking Documents")
    print("="*60)

    # chunk_overlap=128 means the last 128 tokens of each chunk are repeated
    # at the start of the next chunk. This ensures that a sentence spanning
    # a chunk boundary is fully present in at least one chunk.
    parser = SimpleNodeParser.from_defaults(chunk_size=512, chunk_overlap=128)
    nodes = parser.get_nodes_from_documents(KNOWLEDGE_BASE)

    print(f"\n✓ Split {len(KNOWLEDGE_BASE)} documents into {len(nodes)} chunks")
    avg_chunk_size = sum(len(n.text) for n in nodes) // len(nodes)
    print(f"  - Average chunk size: {avg_chunk_size} characters")

    print(f"\n📝 First 3 chunks:")
    for i, node in enumerate(nodes[:3], 1):
        preview = node.text[:60] + "..." if len(node.text) > 60 else node.text
        print(f"  {i}. {preview}")


def example_3_create_index():
    """Example 3: Creating the vector index with Mistral embeddings"""
    print("\n" + "="*60)
    print("Step 3: Creating the Vector Index with Mistral")
    print("="*60)

    parser = SimpleNodeParser.from_defaults(chunk_size=512)
    nodes = parser.get_nodes_from_documents(KNOWLEDGE_BASE)

    print("\n⏳ Creating embeddings with Mistral...")
    # VectorStoreIndex sends each node's text to mistral-embed and stores the
    # returned 1024-dim vector alongside the node. At query time the user's
    # question is also embedded and compared against these stored vectors using
    # cosine similarity to find the most relevant chunks.
    index = VectorStoreIndex(nodes, show_progress=False)
    print(f"\n✓ Index created with Mistral embeddings (1024 dimensions)")
    return index


def example_4_query_engine(index):
    """Example 4: Creating query engine"""
    print("\n" + "="*60)
    print("Step 4: Creating Query Engine")
    print("="*60)

    # query_engine = retriever + LLM synthesis in one call.
    # similarity_top_k=3 means: retrieve the 3 most similar chunks,
    # then send those 3 chunks as context to the LLM to generate the answer.
    # Increasing k gives the LLM more context but also more noise.
    query_engine = index.as_query_engine(similarity_top_k=3)

    print(f"\n✓ Query engine created")
    print(f"  - Embedding model: mistral-embed")
    print(f"  - LLM: mistral-small-latest")
    print(f"  - Similarity top-k: 3")

    return query_engine


def example_5_sample_queries(query_engine):
    """Example 5: Testing real queries"""
    print("\n" + "="*60)
    print("Step 5: Testing Queries")
    print("="*60)

    test_queries = [
        "What is Tunisia known for?",
        "Tell me about Mistral AI",
        "How does RAG improve LLM accuracy?",
        "What are famous Tunisian dishes?",
    ]

    print(f"\n🔍 Running {len(test_queries)} queries:")

    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        response = query_engine.query(query)
        # The LLM was instructed to answer using only the retrieved context.
        # If the answer is not in the knowledge base, it should say so.
        print(f"   Answer: {str(response)[:150]}...")
        if hasattr(response, 'source_nodes') and response.source_nodes:
            # source_nodes tells us exactly which documents were used —
            # essential for traceability and debugging hallucinations.
            sources = [n.metadata.get('category') for n in response.source_nodes]
            print(f"   Sources: {sources}")


def example_6_rag_workflow(index):
    """Example 6: Real RAG pipeline walkthrough"""
    print("\n" + "="*60)
    print("Step 6: RAG Pipeline Walkthrough")
    print("="*60)

    query = "What is Mistral AI?"
    print(f"\n1. User Query: '{query}'")

    # Step 1: embed the query using the same model used to embed the documents.
    # Using a different model here would break similarity — vectors must live
    # in the same embedding space to be comparable.
    retriever = index.as_retriever(similarity_top_k=3)
    nodes = retriever.retrieve(query)

    print(f"\n2. Embedding: converted to vector via mistral-embed")
    print(f"\n3. Vector Search: top {len(nodes)} results")
    for node in nodes:
        # Score > 0.8 = strong semantic match.
        # Score < 0.6 = weak match, likely not directly relevant.
        print(f"   - [{node.score:.3f}] {node.metadata.get('category')} | {node.text[:60]}...")

    print(f"\n4. Context passed to mistral-small-latest")
    query_engine = index.as_query_engine(similarity_top_k=3)
    response = query_engine.query(query)

    print(f"\n5. Final Answer:")
    print(f"   {str(response)[:300]}...")
    print(f"\n6. Sources used: {[n.metadata.get('category') for n in response.source_nodes]}")


def example_7_deployment_checklist():
    """Example 7: Production deployment checklist"""
    print("\n" + "="*60)
    print("Step 7: Production Deployment Checklist")
    print("="*60)

    checklist = [
        ("Documents loaded", True),
        ("Chunking configured", True),
        ("Embeddings computed (mistral-embed)", True),
        ("Vector store created", True),
        ("Query engine ready", True),
        ("LLM model configured (mistral-small-latest)", True),
        # These are the remaining gaps before going to production:
        ("Error handling added", False),      # wrap API calls in try/except with retries
        ("Monitoring set up", False),         # log latency, token usage, error rates
        ("Caching implemented", False),       # cache embeddings to avoid re-calling the API
        ("User testing completed", False),    # validate answer quality with real users
    ]

    print("\n📋 Production Readiness Checklist:")
    for task, done in checklist:
        symbol = "✅" if done else "❌"
        print(f"  {symbol} {task:<45} {'Done' if done else 'Pending'}")

    print("\n💡 Next Steps:")
    print("  1. Add logging and monitoring")
    print("  2. Implement caching for repeated queries")
    print("  3. Test with real users")
    print("  4. Deploy to production environment")


def main():
    """Run all examples"""
    print("\n🚀 Complete RAG Pipeline Demo - Tunisian Edition")
    print("="*60)

    try:
        example_1_load_documents()
        example_2_parse_and_chunk()
        index = example_3_create_index()
        query_engine = example_4_query_engine(index)
        example_5_sample_queries(query_engine)
        example_6_rag_workflow(index)
        example_7_deployment_checklist()

        print("\n" + "="*60)
        print("✅ RAG Pipeline Demo completed successfully!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
