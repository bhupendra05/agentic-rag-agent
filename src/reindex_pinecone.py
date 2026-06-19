"""
Reindex Pinecone - Complete pipeline to recreate Pinecone index with Gemini embeddings

This is the MAIN script that orchestrates:
1. Extract text from PDFs
2. Convert to Gemini embeddings
3. Delete old Pinecone index
4. Create new Pinecone index
5. Upload documents with embeddings

Why we need this:
- Your old index had 1536-dim vectors (OpenAI)
- New index will have 768-dim vectors (Gemini, FREE)
- Complete fresh start, no dimension conflicts
"""

import os
from dotenv import load_dotenv
from pinecone import Pinecone
import time

# Import our custom modules
from pdf_extractor import process_documents
from gemini_embeddings import embed_documents, verify_embeddings

# Load environment
load_dotenv()

# ============================================================================
# SECTION 1: Initialize Pinecone
# ============================================================================

def init_pinecone():
    """
    Initialize Pinecone client

    Returns:
        Pinecone client
    """
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        raise ValueError("PINECONE_API_KEY not found in .env!")

    pc = Pinecone(api_key=api_key)
    return pc


# ============================================================================
# SECTION 2: Delete old index
# ============================================================================

def delete_old_index(pc, index_name: str):
    """
    Delete the old Pinecone index (to avoid conflicts)

    Args:
        pc: Pinecone client
        index_name: Name of index to delete

    Why?
    - Old index has 1536 dimensions (OpenAI)
    - New index needs 768 dimensions (Gemini)
    - Can't change dimensions on existing index
    - Must delete and recreate
    """
    try:
        pc.delete_index(index_name)
        print(f"✅ Deleted old index: {index_name}")
        time.sleep(5)  # Wait for deletion to complete
    except Exception as e:
        if "not found" in str(e).lower():
            print(f"✅ Index doesn't exist yet: {index_name}")
        else:
            raise


# ============================================================================
# SECTION 3: Create new index
# ============================================================================

def create_new_index(pc, index_name: str, dimension: int = 768):
    """
    Create a new Pinecone index with correct dimensions

    Args:
        pc: Pinecone client
        index_name: Name for new index
        dimension: Embedding dimension (768 for Gemini)

    Why these settings?
    - dimension=768: Gemini embeddings are 768-dimensional
    - metric="cosine": Good for semantic search
    - spec: Defines hosting (starter plan = free)
    """
    try:
        print(f"\n📌 Creating new index: {index_name}")
        print(f"   Dimensions: {dimension}")
        print(f"   Metric: cosine")

        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric="cosine",
            spec={
                "serverless": {
                    "cloud": "aws",
                    "region": "us-east-1"
                }
            }
        )

        # Wait for index to be ready
        print("   ⏳ Waiting for index to be ready...")
        time.sleep(10)  # Initial wait

        # Poll until ready
        max_attempts = 30
        attempt = 0
        while attempt < max_attempts:
            try:
                index = pc.Index(index_name)
                stats = index.describe_index_stats()
                print(f"✅ Index created and ready!")
                return index
            except:
                attempt += 1
                print(f"   ⏳ Waiting... ({attempt}/{max_attempts})")
                time.sleep(2)

        raise TimeoutError("Index took too long to be ready")

    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"✅ Index already exists: {index_name}")
            time.sleep(5)
            return pc.Index(index_name)
        else:
            raise


# ============================================================================
# SECTION 4: Upload documents to Pinecone
# ============================================================================

def upload_to_pinecone(index, documents: list):
    """
    Upload embedded documents to Pinecone

    Args:
        index: Pinecone index object
        documents: List of documents with embeddings

    What happens:
    - Batch upload vectors to Pinecone
    - Each vector has: id, embedding, metadata
    - Metadata includes original text and source file
    """
    print(f"\n📤 Uploading {len(documents)} documents to Pinecone...")
    print("=" * 70)

    # Prepare vectors for upload
    vectors = []
    for doc in documents:
        vector = (
            doc['id'],                          # Vector ID
            doc['embedding'],                   # The embedding vector
            {                                   # Metadata
                'text': doc['text'],
                'source': doc['source'],
                'chunk_num': doc.get('chunk_num', 0)
            }
        )
        vectors.append(vector)

    # Upload in batches (Pinecone prefers batches)
    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        index.upsert(vectors=batch)
        print(f"   ✓ Uploaded {min(i + batch_size, len(vectors))}/{len(vectors)}")

    print("=" * 70)
    print(f"✅ All documents uploaded!")


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def main():
    """
    Main pipeline: Extract → Embed → Reindex

    Flow:
    1. Load PDFs from docs/ folder
    2. Extract text and chunk
    3. Embed with Gemini
    4. Delete old Pinecone index
    5. Create new Pinecone index (768 dims)
    6. Upload documents
    7. Verify everything works
    """

    print("\n" + "=" * 70)
    print("🚀 REINDEXING PIPELINE - PDF → Gemini → Pinecone")
    print("=" * 70 + "\n")

    try:
        # Step 1: Extract documents from PDFs
        print("STEP 1: Extract documents from PDFs")
        print("-" * 70)
        docs_folder = "docs"
        documents = process_documents(docs_folder)

        # Step 2: Embed documents with HuggingFace (LOCAL, FREE)
        print("\nSTEP 2: Embed documents with HuggingFace (LOCAL, FREE)")
        print("-" * 70)
        embedded_docs = embed_documents(documents)

        # Verify embeddings
        stats = verify_embeddings(embedded_docs)
        print(f"\n📊 Embedding Stats:")
        print(f"   {stats['status']}")
        print(f"   Dimension: {stats['embedding_dimension']}")
        print(f"   Total docs: {stats['total_docs']}")

        # Step 3: Initialize Pinecone
        print("\nSTEP 3: Initialize Pinecone")
        print("-" * 70)
        pc = init_pinecone()
        print("✅ Pinecone client ready")

        # Step 4: Delete old index
        print("\nSTEP 4: Delete old index")
        print("-" * 70)
        index_name = os.getenv("PINECONE_INDEX_NAME", "singaporetrip")
        delete_old_index(pc, index_name)

        # Step 5: Create new index
        print("\nSTEP 5: Create new index")
        print("-" * 70)
        embedding_dim = stats['embedding_dimension']
        index = create_new_index(pc, index_name, dimension=embedding_dim)

        # Step 6: Upload documents
        print("\nSTEP 6: Upload documents to new index")
        print("-" * 70)
        upload_to_pinecone(index, embedded_docs)

        # Step 7: Verify
        print("\nSTEP 7: Verify upload")
        print("-" * 70)
        stats = index.describe_index_stats()
        total_vectors = stats['total_vector_count']
        print(f"✅ New index has {total_vectors} vectors!")

        print("\n" + "=" * 70)
        print("✅ REINDEXING COMPLETE!")
        print("=" * 70)
        print(f"\nYour new Pinecone index '{index_name}' is ready!")
        print(f"- Dimensions: {embedding_dim}")
        print(f"- Documents: {total_vectors}")
        print(f"- Embedding model: HuggingFace (LOCAL, FREE, FAST)")
        print()

    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print(f"\n📁 Make sure your PDFs are in the 'docs' folder:")
        print(f"   mkdir -p docs")
        print(f"   # Download PDFs from Google Drive to docs/")
        exit(1)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    main()
