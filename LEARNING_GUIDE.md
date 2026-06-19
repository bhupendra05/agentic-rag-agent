# 🚀 Building a RAG Agent in Python - Learning Guide

A step-by-step guide to replicate your n8n RAG workflow using Python. Learn concepts, understand WHY each piece matters, and build interview-ready code.

**📖 For a comprehensive deep-dive into architecture, code, and concepts → Read `COMPREHENSIVE_GUIDE.md`**

---

## 📋 Overview

Your RAG workflow has these parts:

```
User Message
    ↓
[AI Agent] ← Connected to:
    ├── OpenAI/Gemini (LLM)
    ├── Memory (Conversation History)
    └── Pinecone (Knowledge Base)
    ↓
Agent searches knowledge → Gets context → Answers question
```

**RAG = Retrieval-Augmented Generation**
- **Retrieval**: Search vector database for relevant docs
- **Augmented**: Add those docs as context
- **Generation**: LLM generates answer using context

---

## ✅ Completed Steps

### **Step 1: Environment Setup**
- Created Python virtual environment
- Installed dependencies

### **Step 2: LLM Client (llm_client.py)**
- Connected to Google Gemini
- Created `chat_with_model()` function
- Sends messages to LLM and gets responses

**File**: `src/llm_client.py`

---

## 🔄 Step 3: Vector Store (Pinecone) - TODAY

### **What is Pinecone?**

Pinecone is a **vector database**. Instead of storing text, it stores vectors (lists of numbers).

**Example:**
```
Text: "Singapore is a beautiful city"
Vector: [0.234, -0.891, 0.456, ..., 0.123]  ← 768 numbers
```

### **Why do we need it?**

**Problem**: If user asks "Tell me about Singapore trips", how do we find relevant documents?

❌ **Bad way**: Search for exact word match
- User: "Tell me about Singapore trips"
- Search: "singaporetrip" (1530 documents)
- Result: ALL 1530 documents (too many!)

✅ **Good way**: Use semantic search (meaning-based)
1. Convert user question to vector: `[0.123, -0.456, ...]`
2. Find similar vectors in Pinecone
3. Return TOP 3-5 most similar documents
4. Use those as context for LLM

### **How Pinecone Works**

```
Step 1: Store (happens in n8n)
  Document: "A week in Singapore visiting Marina Bay..."
       ↓ (convert to vector)
  Vector: [0.234, -0.891, 0.456, ..., 0.123]
       ↓ (store in Pinecone)
  Pinecone Index: [Vector] + metadata (source, title, etc)

Step 2: Retrieve (what we'll code today)
  Query: "What should I visit in Singapore?"
       ↓ (convert to vector)
  Query Vector: [0.156, -0.789, 0.234, ..., 0.456]
       ↓ (find similar vectors)
  Pinecone: "These 5 vectors are closest to your query"
       ↓ (return top results)
  Results: [
    {"text": "Marina Bay Sands is...", "score": 0.92},
    {"text": "Gardens by the Bay is...", "score": 0.89},
    ...
  ]
```

### **Your Pinecone Setup**

```
Index Name: singaporetrip
Total Vectors: 1530
Dimensions: 1536 (default)
Namespace: default
```

Each vector has metadata like: `{"text": "...", "source": "...", ...}`

---

## 🛠️ Building vector_store.py

### **What we'll create:**

A Python file that:
1. **Connects** to Pinecone using your API key
2. **Converts text to vectors** (embeddings)
3. **Searches** Pinecone for similar documents
4. **Returns** the top results with context

### **Function we need:**

```python
def search_knowledge(query: str, top_k=3):
    """
    Search Pinecone for documents relevant to the query
    
    Args:
        query: User's question
        top_k: How many results to return (default 3)
    
    Returns:
        list: Top similar documents with scores
    """
```

---

## 📝 Code Walkthrough

### **Part 1: Initialize Pinecone**

```python
from pinecone import Pinecone

pc = Pinecone(api_key="YOUR_KEY")
index = pc.Index("your-index-name")
```

**What's happening:**
- Create a Pinecone client with your API key
- Connect to your specific index (`singaporetrip`)

### **Part 2: Get Embeddings**

Before we can search, we need to convert the user's question into a vector.

We use **OpenAI Embeddings** (or Gemini Embeddings):

```python
from openai import OpenAI

client = OpenAI()

def get_embedding(text: str):
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"  # Fast, cheap
    )
    return response.data[0].embedding
```

**Why OpenAI embeddings?**
- Your 1530 documents in Pinecone were embedded using OpenAI
- We must use the SAME embedding model to search
- (You created them in n8n, which uses OpenAI by default)

**Important**: Query embedding + Document embeddings must match!

### **Part 3: Search Pinecone**

```python
def search_knowledge(query: str, top_k=3):
    # Step 1: Convert query to vector
    query_vector = get_embedding(query)
    
    # Step 2: Search in Pinecone
    results = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True  # Get doc text, not just vectors
    )
    
    # Step 3: Format and return results
    return results
```

**What happens:**
1. User asks: "What's the best time to visit Singapore?"
2. Convert to vector: `[0.234, -0.891, ...]`
3. Pinecone finds 3 closest vectors
4. Return documents with similarity scores

---

## 🎯 Interview Talking Points

When you discuss this with interviewers:

**"I use Pinecone as a vector database to store 1530 travel documents. When a user asks a question, I:
1. Convert their question to a vector using embeddings
2. Query Pinecone to find the 3 most similar documents (based on semantic meaning, not keyword match)
3. Use those documents as context for the LLM to answer accurately
4. This is called RAG - Retrieval-Augmented Generation"**

---

## 🔄 BONUS: Recreating Pinecone Index with Gemini Embeddings

### **The Problem**
- Old index: 1536 dimensions (OpenAI, costs $)
- New approach: 768 dimensions (Gemini, FREE)
- Solution: Recreate the index with Gemini embeddings

### **The Solution - 3 Files**

#### **1️⃣ pdf_extractor.py**
Extracts text from your PDF tour packages
```
Input: Shanghai_Tour_Package.pdf (22 KB)
Process: Extract text → Split into chunks (500 chars, 100 overlap)
Output: 15 documents, each ~500 characters
```

#### **2️⃣ gemini_embeddings.py**
Converts text chunks to vectors using Gemini (FREE)
```
Input: 15 text chunks
Process: Send each to Gemini embedding API
Output: 15 vectors (768 dimensions each)
Cost: $0 ✅
```

#### **3️⃣ reindex_pinecone.py**
Main orchestration script
```
1. Extract PDFs → Get documents
2. Embed with Gemini → Get vectors
3. Delete old Pinecone index (1536 dims)
4. Create new Pinecone index (768 dims)
5. Upload documents with embeddings
6. Verify everything works
```

### **How to Use It**

```bash
# Step 1: Download PDFs from Google Drive to docs/ folder
mkdir -p docs
# Download these 3 files to docs/:
# - Shanghai_Tour_Package.pdf
# - Singapore_Tour_Package_Sample-v1.pdf
# - Singapore_Tour_Package_Sample-v2.pdf

# Step 2: Install PDF reader
pip install PyPDF2

# Step 3: Run the reindexing pipeline
cd /path/to/planningTripRag
python src/reindex_pinecone.py
```

### **What Happens**
```
📄 Extract PDFs
   ├─ Shanghai_Tour_Package.pdf → 10 chunks
   ├─ Singapore_Tour_Package_Sample-v1.pdf → 8 chunks
   └─ Singapore_Tour_Package_Sample-v2.pdf → 7 chunks
   Total: 25 documents

🔤 Embed with Gemini
   ├─ Each doc: 500 chars → 768-dimensional vector
   └─ Cost: $0 (free tier)

📌 Pinecone
   ├─ Delete old index (1536 dims)
   ├─ Create new index (768 dims)
   └─ Upload 25 documents
```

### **Why This Approach?**
- ✅ FREE (Gemini free tier)
- ✅ No dimension conflicts
- ✅ Fast (Gemini is optimized)
- ✅ Good quality (Gemini is Google's production model)
- ✅ Reproducible (you can rebuild anytime)

---

## 🚀 Next Steps

After Reindexing, we'll build:
- **Step 4**: Update vector_store.py to use Gemini embeddings
- **Step 5**: Conversation Memory
- **Step 6**: Full RAG Agent (orchestrate everything)
- **Step 7**: Chat interface

---

## 📚 Key Concepts to Remember

| Concept | Meaning |
|---------|---------|
| **Vector** | List of numbers representing meaning (embedding) |
| **Embedding** | Converting text → vector |
| **Semantic Search** | Finding similar meaning, not keyword match |
| **Top-K** | Return top K most similar results |
| **Similarity Score** | 0-1, higher = more similar |
| **Namespace** | Partition in Pinecone index (we use default) |

---

## 🔗 Resources

- [Pinecone Docs](https://docs.pinecone.io/)
- [Embeddings Explained](https://huggingface.co/spaces/mteb/leaderboard)
- [RAG Pattern](https://docs.anthropic.com/en/docs/build-a-system/rag)

