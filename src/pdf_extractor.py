"""
PDF Extractor Module - Extract text from PDF documents

This module handles:
1. Reading PDF files
2. Extracting text from each page
3. Chunking text into manageable pieces
4. Returning structured document data

Why we need this:
- Your source documents are PDFs (Shanghai, Singapore tour packages)
- We need to convert PDF → plain text
- Then chunk them into documents for embedding
"""

import PyPDF2
import os
from pathlib import Path
from typing import List, Dict

# ============================================================================
# SECTION 1: Extract text from PDF
# ============================================================================

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract all text from a PDF file

    Args:
        pdf_path: Path to the PDF file

    Returns:
        str: All text from the PDF

    How it works:
    - Open PDF file
    - Read each page
    - Extract text from each page
    - Combine all text
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    text = []
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            print(f"📄 Extracting text from {os.path.basename(pdf_path)} ({num_pages} pages)...")

            for page_num, page in enumerate(pdf_reader.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
                    print(f"   Page {page_num}/{num_pages} ✓")

        full_text = "\n".join(text)
        print(f"✅ Extracted {len(full_text)} characters\n")
        return full_text

    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {e}")


# ============================================================================
# SECTION 2: Chunk text into documents
# ============================================================================

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """
    Split long text into smaller chunks with overlap

    Args:
        text: The full text to chunk
        chunk_size: Characters per chunk (default 500)
        overlap: Characters to overlap between chunks (default 100)

    Returns:
        list: List of text chunks

    Why chunking?
    - LLMs and embeddings work better with smaller pieces
    - Helps preserve context while staying manageable
    - Overlap ensures we don't lose information at chunk boundaries

    Example:
    Text: "AAABBBCCCDDDEEEFFFGGG"
    Chunks of 5 with overlap 2:
    - "AAABB"
    - "BBCCC"
    - "CCDDD"
    - etc.

    This way no information is lost between chunks.
    """
    chunks = []
    start = 0

    while start < len(text):
        # Create chunk from start to start+chunk_size
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()

        if chunk:  # Only add non-empty chunks
            chunks.append(chunk)

        # Move start forward by (chunk_size - overlap)
        # This creates overlap between consecutive chunks
        start += chunk_size - overlap

    return chunks


# ============================================================================
# SECTION 3: Process documents (PDF → chunks)
# ============================================================================

def process_documents(docs_folder: str) -> List[Dict[str, str]]:
    """
    Process all PDFs in a folder into document chunks

    Args:
        docs_folder: Path to folder containing PDF files

    Returns:
        list: Documents with text and metadata
            [
                {
                    'id': 'Shanghai_Tour_Package_chunk_1',
                    'text': 'Full chunk text here...',
                    'source': 'Shanghai_Tour_Package.pdf',
                    'chunk_num': 1
                },
                ...
            ]

    Why this function?
    - Centralized processing of all documents
    - Adds metadata (source file, chunk number)
    - Ready for embedding and Pinecone upload
    """
    documents = []
    doc_id_counter = 0

    # Check if folder exists
    if not os.path.exists(docs_folder):
        raise FileNotFoundError(f"Docs folder not found: {docs_folder}")

    # Find all PDF files
    pdf_files = list(Path(docs_folder).glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in {docs_folder}")

    print(f"🔍 Found {len(pdf_files)} PDF files\n")

    # Process each PDF
    for pdf_file in sorted(pdf_files):
        print(f"Processing: {pdf_file.name}")
        print("=" * 70)

        # Extract text
        text = extract_text_from_pdf(str(pdf_file))

        # Chunk text
        chunks = chunk_text(text, chunk_size=500, overlap=100)
        print(f"📦 Created {len(chunks)} chunks\n")

        # Create document objects
        for chunk_num, chunk in enumerate(chunks, 1):
            doc_id = f"{pdf_file.stem}_chunk_{chunk_num}"
            documents.append({
                'id': doc_id,
                'text': chunk,
                'source': pdf_file.name,
                'chunk_num': chunk_num
            })
            doc_id_counter += 1

    print("=" * 70)
    print(f"✅ Total documents created: {len(documents)}\n")

    return documents


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    """
    Test the PDF extractor module
    Run: python src/pdf_extractor.py
    """

    print("=" * 70)
    print("🧪 Testing PDF Extractor Module")
    print("=" * 70)
    print()

    # Define docs folder
    docs_folder = "docs"

    # Check if docs folder exists
    if not os.path.exists(docs_folder):
        print(f"❌ Folder '{docs_folder}' not found!")
        print(f"📁 Please create it and add your PDF files:")
        print(f"   mkdir -p {docs_folder}")
        print(f"   # Download PDFs from Google Drive to {docs_folder}/")
        exit(1)

    # Find PDF files
    pdf_files = list(Path(docs_folder).glob("*.pdf"))
    if not pdf_files:
        print(f"❌ No PDF files found in '{docs_folder}'!")
        print(f"📁 Please download your PDFs from Google Drive:")
        print(f"   - Shanghai_Tour_Package.pdf")
        print(f"   - Singapore_Tour_Package_Sample-v1.pdf")
        print(f"   - Singapore_Tour_Package_Sample-v2.pdf")
        exit(1)

    print(f"✅ Found {len(pdf_files)} PDF files\n")

    # Process documents
    try:
        documents = process_documents(docs_folder)

        # Show sample
        if documents:
            print("\n📋 Sample Document:")
            print("-" * 70)
            sample = documents[0]
            print(f"ID: {sample['id']}")
            print(f"Source: {sample['source']}")
            print(f"Text preview: {sample['text'][:200]}...")
            print("-" * 70)

    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)

    print("\n✅ PDF extraction successful!")
