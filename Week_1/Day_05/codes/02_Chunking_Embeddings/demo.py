"""
Demo: Chunking & Embeddings
Splitting documents into chunks and converting to vectors using Mistral
"""

import os
import sys
from pathlib import Path
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SimpleNodeParser
from dotenv import load_dotenv

# Load environment variables
project_root = Path(__file__).parent.parent
load_dotenv(project_root / ".env")

docs_dir = project_root / "sample_documents"
SAMPLE_DOCS = SimpleDirectoryReader(
    input_files=[
        str(docs_dir / "programming_basics.txt"),
        str(docs_dir / "mistral_ai.txt"),
        str(docs_dir / "machine_learning.txt"),
    ]
).load_data()


def example_1_simple_chunking():
    """Example 1: Simple text chunking"""
    print("\n" + "="*60)
    print("Example 1: Splitting Text with SimpleNodeParser")
    print("="*60)

    # chunk_size is measured in TOKENS, not characters.
    # ~1 token ≈ 4 characters in English, so 256 tokens ≈ 1024 characters.
    # Smaller chunks = more precise retrieval but less context per chunk.
    # Larger chunks = more context but may dilute the relevant signal.
    parser = SimpleNodeParser.from_defaults(
        chunk_size=256,
        # chunk_overlap duplicates the last N tokens of one chunk into the
        # start of the next. This prevents an idea split across a boundary
        # from being lost — e.g. a sentence that starts at token 250 and
        # ends at token 270 would be cut in half without overlap.
        chunk_overlap=64
    )

    # Each Document becomes one or more TextNode objects (called "nodes").
    # A node = a chunk of text + its metadata + a unique node_id.
    nodes = parser.get_nodes_from_documents(SAMPLE_DOCS)

    print(f"\n✓ Split {len(SAMPLE_DOCS)} documents into {len(nodes)} nodes")

    for i, node in enumerate(nodes[:3], 1):
        text_preview = node.text[:80] + "..." if len(node.text) > 80 else node.text
        print(f"\nNode #{i}:")
        print(f"  - Size: {len(node.text)} characters")
        print(f"  - Content: {text_preview}")
        # node_id is a UUID assigned at creation — used to look up the node
        # in the vector store after a similarity search returns its id.
        print(f"  - ID: {node.node_id}")


def example_2_different_chunk_sizes():
    """Example 2: Compare different chunk sizes"""
    print("\n" + "="*60)
    print("Example 2: Comparing Different Chunk Sizes")
    print("="*60)

    chunk_sizes = [128, 256, 512, 1024]

    for size in chunk_sizes:
        parser = SimpleNodeParser.from_defaults(
            chunk_size=size,
            chunk_overlap=int(size * 0.2)  # keep overlap at 20% of chunk size
        )

        nodes = parser.get_nodes_from_documents(SAMPLE_DOCS)
        total_chars = sum(len(node.text) for node in nodes)
        avg_size = total_chars / len(nodes) if nodes else 0

        # Notice: above a certain threshold the chunk count stops growing.
        # That's because these short documents fit inside a single large chunk.
        print(f"\n📊 Chunk Size = {size} tokens:")
        print(f"  - Number of chunks: {len(nodes)}")
        print(f"  - Average size: {avg_size:.0f} characters")
        print(f"  - Total: {total_chars} characters")


def example_3_mistral_embeddings():
    """Example 3: Using Mistral embeddings"""
    print("\n" + "="*60)
    print("Example 3: Mistral Embeddings")
    print("="*60)

    api_key = os.getenv("MISTRAL_API_KEY")

    if not api_key:
        print("\n⚠️  MISTRAL_API_KEY not found in .env")
        print("To use Mistral embeddings:")
        print("  1. Get API key from https://console.mistral.ai")
        print("  2. Add to .env: MISTRAL_API_KEY=your_key")
        return

    try:
        from llama_index.embeddings.mistralai import MistralAIEmbedding

        # mistral-embed converts text into a 1024-dimensional vector.
        # Each dimension captures a different aspect of meaning — the model
        # was trained so that semantically similar texts produce vectors that
        # point in the same direction in that 1024-dimensional space.
        embed_model = MistralAIEmbedding(
            api_key=api_key,
            model="mistral-embed"
        )

        text_to_embed = "Machine Learning with Mistral"
        embedding = embed_model.get_text_embedding(text_to_embed)

        print(f"\n✓ Successfully created Mistral embeddings")
        print(f"  - Model: mistral-embed")
        # 1024 floats per embedding — every text maps to a fixed-length vector
        # regardless of how long the text is.
        print(f"  - Dimensions: {len(embedding)}")
        print(f"  - Text: '{text_to_embed}'")
        # The individual float values have no human-readable meaning on their own;
        # it's the relative distance between two embedding vectors that matters.
        print(f"  - First 5 values: {embedding[:5]}")

    except ImportError:
        print("\n⚠️  Missing dependency")
        print("Install with: pip install llama-index-embeddings-mistralai")
    except Exception as e:
        print(f"\n⚠️  Error: {e}")
        print("Make sure MISTRAL_API_KEY is correct")


def example_4_node_metadata():
    """Example 4: Node metadata"""
    print("\n" + "="*60)
    print("Example 4: Node Metadata")
    print("="*60)

    parser = SimpleNodeParser.from_defaults(chunk_size=256)
    nodes = parser.get_nodes_from_documents(SAMPLE_DOCS)

    print(f"\n✓ Information about {len(nodes)} nodes:")

    for i, node in enumerate(nodes[:2], 1):
        print(f"\nNode #{i}:")
        print(f"  - ID: {node.node_id[:20]}...")
        print(f"  - Text size: {len(node.text)} characters")
        # source_node links back to the original Document this chunk came from.
        # This is how the system can cite "this answer came from file X" at query time.
        print(f"  - Source document: {node.source_node.metadata if node.source_node else 'N/A'}")
        # node.metadata inherits the parent document's metadata automatically.
        # Any key added to the Document's metadata is visible here too.
        print(f"  - Node metadata: {node.metadata}")


def example_5_chunking_statistics():
    """Example 5: Chunking statistics"""
    print("\n" + "="*60)
    print("Example 5: Chunking Statistics")
    print("="*60)

    parser = SimpleNodeParser.from_defaults(chunk_size=512)
    nodes = parser.get_nodes_from_documents(SAMPLE_DOCS)

    total_chars = sum(len(node.text) for node in nodes)
    total_words = sum(len(node.text.split()) for node in nodes)
    avg_chars = total_chars / len(nodes) if nodes else 0
    avg_words = total_words / len(nodes) if nodes else 0

    # Average words per chunk gives a rough sense of reading time and
    # how much context the LLM will receive per retrieved chunk.
    # ~86 words ≈ a short paragraph — suitable for focused Q&A.
    print(f"\n📊 Statistics:")
    print(f"  - Original documents: {len(SAMPLE_DOCS)}")
    print(f"  - Chunks after splitting: {len(nodes)}")
    print(f"  - Total characters: {total_chars}")
    print(f"  - Total words: {total_words}")
    print(f"  - Average characters per chunk: {avg_chars:.0f}")
    print(f"  - Average words per chunk: {avg_words:.0f}")


def main():
    """Run all examples"""
    print("\n🚀 Demo: Chunking & Embeddings")
    print("="*60)

    try:
        example_1_simple_chunking()
        example_2_different_chunk_sizes()
        example_3_mistral_embeddings()
        example_4_node_metadata()
        example_5_chunking_statistics()

        print("\n" + "="*60)
        print("✅ All examples completed successfully!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
