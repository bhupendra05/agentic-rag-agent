"""
Vector Store Module - Connect to Pinecone and search knowledge base

This module handles:
1. Connecting to Pinecone vector database
2. Converting text queries to embeddings (using FREE local embeddings)
3. Searching for similar documents
4. Returning formatted results

Why this matters:
- Your 1530 Singapore trip documents are stored as vectors in Pinecone
- When a user asks a question, we convert it to a vector
- Then find the most similar documents (semantic search)
- These documents become context for the LLM to answer accurately

Embeddings Strategy:
- Using HuggingFace Sentence Transformers (FREE, local, no API costs)
- Model: all-MiniLM-L6-v2 (384 dims, fast, good quality)
- Works with existing Pinecone documents (close enough to OpenAI embeddings)
"""

from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# SECTION 1: Initialize Pinecone
# ============================================================================

def init_pinecone():
    """
    Connect to Pinecone using credentials from .env

    Returns:
        index: Pinecone index object for searching

    What's happening:
    - Create Pinecone client with your API key
    - Connect to your specific index (singaporetrip)
    - Verify connection works
    """
    # Get credentials from .env
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    pinecone_host = os.getenv("PINECONE_ENVIRONMENT")  # This is actually the host URL

    if not pinecone_api_key or not pinecone_host:
        raise ValueError("Missing PINECONE_API_KEY or PINECONE_ENVIRONMENT in .env")

    # Create Pinecone client
    pc = Pinecone(api_key=pinecone_api_key)

    # Connect to your index
    index_name = os.getenv("PINECONE_INDEX_NAME", "singaporetrip")
    index = pc.Index(index_name, host=pinecone_host)

    # Verify connection by checking index stats
    try:
        stats = index.describe_index_stats()
        total_vectors = stats['total_vector_count']
        print(f"✅ Connected to Pinecone!")
        print(f"   Index: {index_name}")
        print(f"   Total vectors: {total_vectors}")
        return index
    except Exception as e:
        raise ConnectionError(f"Failed to connect to Pinecone: {e}")


# ============================================================================
# SECTION 2: Get Embeddings (Convert text to vectors) - LOCAL, FREE
# ============================================================================

_embedding_model = None

def get_embedding_model():
    """
    Load the embedding model (lazy loaded on first call)

    HuggingFace Sentence Transformers:
    - Completely FREE (open source, local)
    - No API costs or delays
    - 384 dimensions
    - Fast & reliable

    Model: all-MiniLM-L6-v2
    - "all" = works for all types of text
    - "MiniLM" = minimalist language model
    - "L6" = 6 layers (lightweight, fast)
    - "v2" = version 2
    """
    global _embedding_model
    if _embedding_model is None:
        print("📥 Loading embedding model (first time only)...")
        _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Model loaded!")
    return _embedding_model


def get_embedding(text: str) -> list:
    """
    Convert text to embedding vector using HuggingFace (LOCAL, FREE)

    Args:
        text: The text to convert (user question or document)

    Returns:
        list: Vector of numbers (384 dimensions)

    Why HuggingFace embeddings?
    - COMPLETELY FREE (no API costs)
    - Works offline (no internet needed)
    - Super fast (local processing, no API delays)
    - Good quality (same results as paid services)
    - Matches how we reindexed Pinecone!

    How it works:
    - Input: "What should I visit in Singapore?"
    - Processing: Convert to 384-dimensional vector (LOCAL)
    - Output: [0.234, -0.891, 0.456, ..., 0.123]  ← 384 numbers
    - These numbers represent the "meaning" of the text

    Important:
    - Uses SAME embedding model as Pinecone reindexing
    - Ensures search results are accurate
    - Matches document embeddings in the index
    """
    model = get_embedding_model()
    embedding = model.encode(text, convert_to_tensor=False)
    return embedding.tolist()


# ============================================================================
# SECTION 3: Search Pinecone (Find similar documents)
# ============================================================================

def search_knowledge(query: str, top_k: int = 3) -> list:
    """
    Search Pinecone for documents similar to the query

    Args:
        query: User's question or search query
        top_k: How many results to return (default 3)

    Returns:
        list: Top K documents with similarity scores
            Each item: {
                'id': 'doc_id',
                'score': 0.92,  ← Similarity (0-1, higher is better)
                'metadata': {
                    'text': 'Full document text...',
                    'source': 'where doc came from'
                }
            }

    Flow:
    1. Convert query to vector using embeddings
    2. Search Pinecone for similar vectors
    3. Return top K results with metadata
    """
    # Initialize Pinecone (if not already done)
    index = init_pinecone()

    # Step 1: Convert user question to vector
    print(f"\n🔍 Searching for: '{query}'")
    query_embedding = get_embedding(query)
    print(f"   Query converted to vector ({len(query_embedding)} dimensions)")

    # Step 2: Search in Pinecone
    print(f"   Querying Pinecone for top {top_k} results...")
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True  # Include document text, not just vectors
    )

    # Step 3: Format results
    print(f"   Found {len(results['matches'])} results")

    formatted_results = []
    for i, match in enumerate(results['matches'], 1):
        # Each match has: id, score, metadata
        result = {
            'rank': i,
            'score': match['score'],  # Similarity score (0-1)
            'text': match['metadata'].get('text', 'N/A'),
            'metadata': match['metadata']
        }
        formatted_results.append(result)
        print(f"\n   [{i}] Similarity: {match['score']:.3f}")
        print(f"       Text: {match['metadata'].get('text', 'N/A')[:100]}...")

    return formatted_results


# ============================================================================
# SECTION 4: Format context for LLM (Prepare results for agent)
# ============================================================================

def format_context(search_results: list) -> str:
    """
    Format search results into a clean context string for the LLM

    Args:
        search_results: Results from search_knowledge()

    Returns:
        str: Formatted context string

    Why this matters:
    - LLM needs the search results in a clean, readable format
    - We'll prepend this to the system prompt
    - Helps LLM answer using the retrieved documents

    Example output:
    '''
    Retrieved Context:

    [1] (Similarity: 0.92)
    Marina Bay Sands is one of Singapore's most iconic...

    [2] (Similarity: 0.89)
    Gardens by the Bay features Supertrees and nightly light shows...
    '''
    """
    if not search_results:
        return "No relevant documents found."

    context_parts = ["Retrieved Context from Knowledge Base:\n"]

    for result in search_results:
        # Format each result with rank and similarity score
        similarity = result['score']
        text = result['text']

        context_parts.append(f"[{result['rank']}] (Similarity: {similarity:.2%})")
        context_parts.append(text)
        context_parts.append("")  # Blank line for readability

    return "\n".join(context_parts)


# ============================================================================
# TESTING & DEBUGGING
# ============================================================================

if __name__ == "__main__":
    """
    Test the vector store module
    Run: python src/vector_store.py
    """

    print("=" * 70)
    print("🧪 Testing Vector Store Module")
    print("=" * 70)

    # Test 1: Connect to Pinecone
    print("\n[Test 1] Connecting to Pinecone...")
    try:
        index = init_pinecone()
        print("✅ Pinecone connection successful!")
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)

    # Test 2: Get embeddings
    print("\n[Test 2] Creating embedding for test query...")
    test_query = "What are the best places to visit in Singapore?"
    try:
        embedding = get_embedding(test_query)
        print(f"✅ Embedding created! Vector length: {len(embedding)}")
        print(f"   First 5 dimensions: {embedding[:5]}")
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)

    # Test 3: Search knowledge base
    print("\n[Test 3] Searching knowledge base...")
    try:
        results = search_knowledge(test_query, top_k=3)
        print(f"✅ Search successful! Found {len(results)} results")
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)

    # Test 4: Format context
    print("\n[Test 4] Formatting context for LLM...")
    try:
        context = format_context(results)
        print("✅ Context formatted!")
        print("\nFormatted Context Preview:")
        print("-" * 70)
        print(context[:500] + "..." if len(context) > 500 else context)
        print("-" * 70)
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)

    print("\n" + "=" * 70)
    print("✅ All tests passed!")
    print("=" * 70)
