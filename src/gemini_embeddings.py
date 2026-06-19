"""
Embeddings Module - Convert text to vectors using HuggingFace (FREE, LOCAL)

This module handles:
1. Loading sentence-transformers model
2. Converting text chunks to embedding vectors
3. Handling batch processing efficiently
4. Returning embeddings ready for Pinecone

Why HuggingFace embeddings?
- COMPLETELY FREE (no API costs, runs locally)
- No deprecation issues (production-grade open source)
- Fast & reliable (no rate limits, no API delays)
- Excellent quality (same as paid services)
- Works offline (after first download)
"""

from sentence_transformers import SentenceTransformer
from typing import List, Dict
import time

# ============================================================================
# SECTION 1: Initialize embedding model
# ============================================================================

_model = None

def init_model():
    """
    Initialize the embedding model (lazy loaded)

    What's happening:
    - Load sentence-transformers model
    - Downloaded from HuggingFace (first time only)
    - Cached for future use

    Model: all-MiniLM-L6-v2
    - Fast & lightweight
    - 384 dimensions
    - Good quality for semantic search
    - Perfect for RAG
    """
    global _model
    if _model is None:
        print("📥 Loading embedding model (first time only)...")
        _model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Model loaded!")
    return _model


# ============================================================================
# SECTION 2: Get embedding (local, FREE)
# ============================================================================

def get_embedding(text: str) -> List[float]:
    """
    Convert text to embedding vector using HuggingFace (FREE, LOCAL)

    Args:
        text: The text to embed

    Returns:
        list: Embedding vector (384 dimensions)

    How it works:
    - Input: "Marina Bay Sands is an iconic hotel in Singapore..."
    - Processing: Convert to 384-dimensional vector (LOCAL)
    - Output: [0.234, -0.891, 0.456, ..., 0.123]

    Why 384 dimensions?
    - HuggingFace all-MiniLM model uses 384 dims
    - Smaller than OpenAI (1536) or Gemini (768)
    - Still very good quality for semantic search
    - Super fast to process

    Important note:
    - This IS the embedding dimension for our new Pinecone index
    - All documents must use the same embedding model
    - Runs completely locally (no API calls needed)
    """
    model = init_model()
    embedding = model.encode(text, convert_to_tensor=False)
    return embedding.tolist()


# ============================================================================
# SECTION 3: Batch embedding (faster processing - LOCAL)
# ============================================================================

def embed_documents(documents: List[Dict[str, str]]) -> List[Dict]:
    """
    Convert a list of documents to embeddings (LOCAL, FAST)

    Args:
        documents: List of document dicts with 'id' and 'text' keys
            [
                {'id': 'doc_1', 'text': 'Document text...', 'source': '...'},
                ...
            ]

    Returns:
        list: Documents with embeddings added
            [
                {
                    'id': 'doc_1',
                    'text': 'Document text...',
                    'source': '...',
                    'embedding': [0.234, -0.891, ...]
                },
                ...
            ]

    Why this function?
    - Efficient batch processing (completely local, no API)
    - Shows progress
    - Very FAST (no API delays)
    - No rate limiting needed (local processing)
    - Structured output for Pinecone upload
    """
    print(f"\n🔄 Embedding {len(documents)} with HuggingFace (LOCAL, FREE)...")
    print("=" * 70)

    embedded_docs = []

    for idx, doc in enumerate(documents, 1):
        try:
            # Get embedding (runs locally)
            embedding = get_embedding(doc['text'])

            # Add to document
            embedded_doc = {
                **doc,  # Keep all original fields
                'embedding': embedding
            }
            embedded_docs.append(embedded_doc)

            # Progress indicator
            if idx % 5 == 0:
                print(f"   [{idx}/{len(documents)}] Embedded {idx} documents...")

            # No delays needed! Local processing is fast

        except Exception as e:
            print(f"   ❌ Error embedding doc '{doc['id']}': {e}")
            continue

    print(f"   [{len(embedded_docs)}/{len(documents)}] Complete!")
    print("=" * 70)

    return embedded_docs


# ============================================================================
# SECTION 4: Verify embeddings
# ============================================================================

def verify_embeddings(embedded_docs: List[Dict]) -> Dict:
    """
    Check embedding quality and consistency

    Args:
        embedded_docs: List of documents with embeddings

    Returns:
        dict: Statistics about embeddings
    """
    if not embedded_docs:
        return {"status": "No documents"}

    first_doc = embedded_docs[0]
    embedding_dim = len(first_doc.get('embedding', []))

    stats = {
        'total_docs': len(embedded_docs),
        'embedding_dimension': embedding_dim,
        'first_embedding_sample': first_doc['embedding'][:5],  # First 5 dims
        'status': 'OK'
    }

    # Check all docs have same dimension
    inconsistent = [d for d in embedded_docs
                    if len(d.get('embedding', [])) != embedding_dim]

    if inconsistent:
        stats['status'] = f'⚠️ {len(inconsistent)} docs have wrong dimensions!'
    else:
        stats['status'] = '✅ All documents have consistent dimensions'

    return stats


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    """
    Test HuggingFace embeddings (LOCAL, FREE)
    Run: python src/gemini_embeddings.py
    """

    print("=" * 70)
    print("🧪 Testing HuggingFace Embeddings Module (LOCAL, FREE)")
    print("=" * 70)
    print()

    # Test 1: Initialize model
    print("[Test 1] Initializing embedding model...")
    try:
        init_model()
        print("✅ Model initialized!\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")
        exit(1)

    # Test 2: Create single embedding
    print("[Test 2] Creating embedding for test text...")
    test_text = "Marina Bay Sands is an iconic hotel in Singapore with 57 floors and a rooftop infinity pool."
    try:
        embedding = get_embedding(test_text)
        print(f"✅ Embedding created!")
        print(f"   Dimension: {len(embedding)}")
        print(f"   First 5 values: {embedding[:5]}")
        print(f"   Sample doc embedding length: {len(embedding)}\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")
        exit(1)

    # Test 3: Batch embedding
    print("[Test 3] Batch embedding test...")
    sample_docs = [
        {
            'id': 'test_1',
            'text': 'Singapore is a city-state in Southeast Asia.',
            'source': 'test'
        },
        {
            'id': 'test_2',
            'text': 'The Gardens by the Bay features iconic Supertrees.',
            'source': 'test'
        },
        {
            'id': 'test_3',
            'text': 'Sentosa Island offers beaches and attractions.',
            'source': 'test'
        },
    ]

    try:
        embedded = embed_documents(sample_docs)
        print(f"✅ Batch embedding successful!")

        stats = verify_embeddings(embedded)
        print(f"\n📊 Embedding Statistics:")
        print(f"   Total docs: {stats['total_docs']}")
        print(f"   Dimension: {stats['embedding_dimension']}")
        print(f"   Status: {stats['status']}\n")

    except Exception as e:
        print(f"❌ Error: {e}\n")
        exit(1)

    print("=" * 70)
    print("✅ All tests passed! Ready to reindex Pinecone!")
    print("=" * 70)
