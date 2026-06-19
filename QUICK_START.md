# ⚡ Quick Start Guide - Recreate Pinecone Index

## 📋 Prerequisites

✅ Python virtual environment (already have)
✅ Gemini API key (already in .env)
✅ Pinecone API key (already in .env)
✅ Your 3 PDF tour packages (in Google Drive)

---

## 🚀 Step-by-Step Instructions

### **Step 1: Download PDFs** (1 min)

Create docs folder and download your PDFs:

```bash
mkdir -p /Users/bhupendra/Desktop/LearningAiAgent/LearningRAG_Workflows/planningTripRag/docs
```

Download these 3 files from Google Drive to the `docs/` folder:
- `Shanghai_Tour_Package.pdf`
- `Singapore_Tour_Package_Sample-v1.pdf`
- `Singapore_Tour_Package_Sample-v2.pdf`

**Verify:**
```bash
ls -la docs/
# Should show 3 PDF files
```

---

### **Step 2: Install Dependencies** (2 min)

```bash
cd /Users/bhupendra/Desktop/LearningAiAgent/LearningRAG_Workflows/planningTripRag
pip install PyPDF2
```

Check you have everything:
```bash
pip list | grep -E "PyPDF2|pinecone|google-generativeai|sentence"
```

---

### **Step 3: Run Reindexing Pipeline** (5-10 min)

This is the MAIN command. It will:
1. Extract text from your 3 PDFs
2. Embed with Gemini (FREE)
3. Delete old Pinecone index
4. Create new Pinecone index (768 dims)
5. Upload all documents

```bash
cd /Users/bhupendra/Desktop/LearningAiAgent/LearningRAG_Workflows/planningTripRag
python src/reindex_pinecone.py
```

**Expected output:**
```
======================================================================
🚀 REINDEXING PIPELINE - PDF → Gemini → Pinecone
======================================================================

STEP 1: Extract documents from PDFs
...
📦 Created 8 chunks

STEP 2: Embed documents with Gemini
🔄 Embedding 25 documents with Gemini...
✅ Embedding created!

STEP 3: Initialize Pinecone
✅ Pinecone client ready

STEP 4: Delete old index
✅ Deleted old index: singaporetrip

STEP 5: Create new index
✅ Index created and ready!

STEP 6: Upload documents to new index
📤 Uploading 25 documents to Pinecone...
✓ Uploaded 25/25

STEP 7: Verify upload
✅ New index has 25 vectors!

======================================================================
✅ REINDEXING COMPLETE!
======================================================================
```

---

### **Step 4: Test the Vector Store** (2 min)

Make sure search works with your new index:

```bash
python src/vector_store.py
```

**Expected output:**
```
==============================================================
🧪 Testing Vector Store Module
==============================================================

[Test 1] Connecting to Pinecone...
✅ Connected to Pinecone!
   Index: singaporetrip
   Total vectors: 25

[Test 2] Creating embedding...
✅ Embedding created! Vector length: 768
   First 5 dimensions: [0.234, -0.891, ...]

[Test 3] Searching knowledge base...
✅ Search successful! Found 3 results
   [1] Similarity: 0.92
   [2] Similarity: 0.89
```

---

## 🎯 What Just Happened?

| Before | After |
|--------|-------|
| 33 vectors | 25 vectors (from PDFs) |
| 1536 dimensions | 768 dimensions |
| OpenAI embedding | Gemini embedding |
| Costs $ | FREE ✅ |

---

## 📊 Architecture Now

```
Your PDFs (Google Drive)
    ↓
[pdf_extractor.py] → Extract text & chunk
    ↓
Chunks (500 chars each)
    ↓
[gemini_embeddings.py] → Convert to vectors (FREE)
    ↓
Vectors (768 dims)
    ↓
[Pinecone] → Store & search
    ↓
[vector_store.py] → Query Pinecone
    ↓
[llm_client.py] → Send context to Gemini
    ↓
Agent Response → User
```

---

## 🚨 Troubleshooting

**Problem: "No PDF files found"**
- Make sure PDFs are in `docs/` folder
- Check filename spelling matches

**Problem: "GEMINI_API_KEY not found"**
- Check `.env` file has `GEMINI_API_KEY=...`
- Make sure it's not empty

**Problem: "Vector dimension mismatch"**
- Old index still exists? That's the problem
- Reindex script deletes it automatically
- Run: `python src/reindex_pinecone.py` again

**Problem: Takes too long**
- Gemini embedding is rate-limited on free tier
- Script has delays built in
- Just wait, it's working in background

---

## ✅ Next Steps

Once reindexing is complete:

1. ✅ **Step 1**: Environment setup
2. ✅ **Step 2**: LLM Client (llm_client.py)
3. ✅ **Step 3**: Vector Store (vector_store.py)
4. ✅ **Step 4**: Embeddings (gemini_embeddings.py)
5. **→ Next**: Memory (conversation history)
6. **→ Next**: RAG Agent (orchestrate everything)
7. **→ Next**: Chat interface

---

## 💡 Key Files

| File | Purpose |
|------|---------|
| `src/llm_client.py` | Chat with Gemini |
| `src/pdf_extractor.py` | Extract text from PDFs |
| `src/gemini_embeddings.py` | Convert to vectors |
| `src/vector_store.py` | Search Pinecone |
| `src/reindex_pinecone.py` | MAIN: Orchestrate reindexing |
| `LEARNING_GUIDE.md` | Full learning guide |
| `QUICK_START.md` | This file |

---

## 🎓 Learning Points

What you're learning:

1. **PDF Processing**: Extract text, chunk into pieces
2. **Embeddings**: Convert text to vectors (semantic meaning)
3. **Vector DB**: Store & search by similarity
4. **Free APIs**: Use Gemini instead of expensive OpenAI
5. **Pipelines**: Orchestrate multi-step workflows

---

**Ready? Run Step 3 above and let me know! 🚀**
