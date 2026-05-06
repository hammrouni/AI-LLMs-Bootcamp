"""
Demo: Query Engine
Searching documents and retrieving relevant results
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

# Settings is a global config object that LlamaIndex reads whenever it needs
# to embed text or call an LLM — setting it once here means we never have to
# pass embed_model or llm manually into every index or query engine call.
Settings.embed_model = MistralAIEmbedding(model_name="mistral-embed", api_key=api_key)
Settings.llm = MistralAI(model="mistral-small-latest", api_key=api_key)

# Load documents from disk — files live in sample_documents/ alongside the other demos.
# Using SimpleDirectoryReader keeps content out of source code and makes it easy
# to update documents without touching the demo logic.
docs_dir = project_root / "sample_documents"
SAMPLE_FILES = [
    "tech_sector.txt",
    "mistral_ai.txt",
    "cloud_computing.txt",
    "programming_languages.txt",
    "devops.txt",
]
SAMPLE_DOCS = SimpleDirectoryReader(
    input_files=[str(docs_dir / f) for f in SAMPLE_FILES]
).load_data()

# Module-level cache so we build the index once and reuse it across examples.
# Building an index calls the embedding API for every node — caching avoids
# paying that cost (time + money) on each example function call.
_index = None

def get_index():
    global _index
    if _index is None:
        parser = SimpleNodeParser.from_defaults(chunk_size=512)
        nodes = parser.get_nodes_from_documents(SAMPLE_DOCS)
        # VectorStoreIndex embeds every node and stores the vectors in memory.
        # At query time it embeds the user's question and finds the nearest nodes.
        _index = VectorStoreIndex(nodes, show_progress=False)
    return _index


def example_1_create_index():
    """Example 1: Create VectorStoreIndex with Mistral embeddings"""
    print("\n" + "="*60)
    print("Example 1: Creating the Index with Mistral Embeddings")
    print("="*60)

    parser = SimpleNodeParser.from_defaults(chunk_size=512)
    nodes = parser.get_nodes_from_documents(SAMPLE_DOCS)

    # This step calls the Mistral API once per node to get embeddings.
    # The vectors are stored in RAM (SimpleVectorStore by default).
    # For production with millions of docs, you'd persist this to disk or Chroma.
    index = VectorStoreIndex(nodes, show_progress=False)

    print(f"\n✓ Index created with Mistral embeddings")
    print(f"  - Number of nodes: {len(nodes)}")
    print(f"  - Embedding model: mistral-embed")


def example_2_query_with_different_k():
    """Example 2: Real search with different top_k values"""
    print("\n" + "="*60)
    print("Example 2: Effect of similarity_top_k on Results")
    print("="*60)

    index = get_index()
    query = "What is Mistral AI?"
    print(f"\nQuery: '{query}'")

    for k in [1, 3, 5]:
        # as_retriever returns raw chunks with similarity scores — no LLM involved.
        # Use this when you want to inspect what was retrieved before generating.
        retriever = index.as_retriever(similarity_top_k=k)
        results = retriever.retrieve(query)
        print(f"\n  top_k={k}: {len(results)} result(s)")
        for r in results:
            # Score is cosine similarity in [0, 1].
            # 1.0 = identical direction in embedding space (perfect match).
            # ~0.7 and above is generally considered a good semantic match.
            print(f"    - [{r.score:.3f}] {r.metadata.get('category')} | {r.text[:60]}...")


def example_3_query_structure():
    """Example 3: Real query and response structure"""
    print("\n" + "="*60)
    print("Example 3: Query and Response Structure")
    print("="*60)

    index = get_index()

    # as_query_engine wraps the retriever with an LLM synthesis step:
    #   1. Retrieve top-k chunks (same as retriever)
    #   2. Pack them into a prompt as "context"
    #   3. Send prompt + user question to the LLM
    #   4. Return the LLM's answer + the source nodes it used
    query_engine = index.as_query_engine(similarity_top_k=3)
    query = "What are the advantages of cloud computing?"

    print(f"\n🔍 Query: '{query}'")
    response = query_engine.query(query)

    print(f"\n✓ Response:")
    print(f"  {str(response)[:200]}...")

    if hasattr(response, 'source_nodes') and response.source_nodes:
        print(f"\n✓ Source nodes ({len(response.source_nodes)}):")
        for i, node in enumerate(response.source_nodes, 1):
            print(f"  {i}. [{node.score:.3f}] {node.metadata.get('category')} | {node.text[:60]}...")


def example_4_different_queries():
    """Example 4: Run different query types"""
    print("\n" + "="*60)
    print("Example 4: Different Query Types")
    print("="*60)

    index = get_index()
    # top_k=2 keeps the context short — enough signal without overloading the LLM prompt.
    query_engine = index.as_query_engine(similarity_top_k=2)

    queries = [
        ("What is Mistral AI?", "Direct question"),
        ("Which language is best for web development?", "Comparison"),
        ("How do I set up a CI/CD pipeline?", "How-to"),
        ("What are cloud computing benefits?", "Concept"),
    ]

    for question, qtype in queries:
        print(f"\n📝 [{qtype}] {question}")
        response = query_engine.query(question)
        # The LLM synthesizes a natural-language answer from the retrieved chunks.
        # It should only use information present in those chunks — not its training data.
        print(f"   → {str(response)[:120]}...")


def example_5_retriever_types():
    """Example 5: Information about different retrievers"""
    print("\n" + "="*60)
    print("Example 5: Types of Retrievers")
    print("="*60)

    # LlamaIndex supports several retrieval strategies.
    # The choice affects accuracy, speed, and whether embeddings are needed.
    retrievers = [
        {
            "name": "VectorIndexRetriever",
            "description": "Searches in the vector store",
            # Best default choice — embeddings capture semantic meaning,
            # so "car" and "automobile" match even without shared keywords.
            "use_case": "Most common cases",
            "pros": ["Fast", "Simple"],
            "cons": ["Requires embeddings"]
        },
        {
            "name": "BM25Retriever",
            "description": "Keyword-based search",
            # Classic TF-IDF style search — no embedding API needed.
            # Fails on synonyms or paraphrased questions.
            "use_case": "Standard text search",
            "pros": ["No embeddings needed", "Very fast"],
            "cons": ["Less accurate for semantic meaning"]
        },
        {
            "name": "HybridRetriever",
            "description": "Combines Vector + BM25",
            # Runs both retrievers and merges results using Reciprocal Rank Fusion.
            # More robust: catches both semantic matches and exact keyword hits.
            "use_case": "Highest accuracy",
            "pros": ["Best results", "Reliable"],
            "cons": ["Slower", "More complex"]
        },
    ]

    for r in retrievers:
        print(f"\n🔍 {r['name']}")
        print(f"   Description: {r['description']}")
        print(f"   Use case: {r['use_case']}")
        print(f"   ✅ Pros: {', '.join(r['pros'])}")
        print(f"   ⚠️  Cons: {', '.join(r['cons'])}")


def main():
    """Run all examples"""
    print("\n🚀 Demo: Query Engine")
    print("="*60)

    try:
        example_1_create_index()
        example_2_query_with_different_k()
        example_3_query_structure()
        example_4_different_queries()
        example_5_retriever_types()

        print("\n" + "="*60)
        print("✅ All examples completed successfully!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
