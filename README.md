# 🤖 RAG Agent: Singapore Tour Guide

A **Retrieval-Augmented Generation (RAG) Agent** that answers questions about Singapore tours using intelligent document search + AI.

## ⚡ Quick Demo

```
You: "What should I visit in Singapore?"
Agent: "Based on available tours, I recommend visiting Marina Bay Sands, 
       which offers panoramic views from the 57th floor. You should also 
       visit Gardens by the Bay and Universal Studios Singapore..."
```

## 📊 Current Status

**Progress: 70% Complete** ✅

| Component | Status |
|-----------|--------|
| PDF Extraction | ✅ Done |
| Embeddings | ✅ Done |
| Vector Search | ✅ Done |
| Pinecone Index | ✅ Done (28 docs) |
| LLM Integration | ✅ Done |
| Conversation Memory | 🔄 TODO |
| RAG Agent | 🔄 TODO |
| Chat Interface | 🔄 TODO |

## 📚 Documentation

Start here based on your learning goal:

1. **Quick Overview** → `README.md` (you are here)
2. **Current Status** → `PROJECT_STATUS.md` - see what's done & todo
3. **Learn Deeply** → `COMPREHENSIVE_GUIDE.md` - full explanation of architecture & code
4. **Quick Reference** → `QUICK_START.md` - step-by-step instructions
5. **Basic Concepts** → `LEARNING_GUIDE.md` - foundational concepts

## 🚀 Next Steps

### Step 1: Read the Guides
```bash
# Start with understanding what you have
cat PROJECT_STATUS.md

# Deep dive into architecture
cat COMPREHENSIVE_GUIDE.md
```

### Step 2: Build Memory System (30 mins)
```bash
# Coming next: src/memory.py
# Stores conversation history for multi-turn chat
```

### Step 3: Build RAG Agent (60 mins)
```bash
# Coming next: src/agent.py
# Orchestrates everything together
```

### Step 4: Build Chat Interface (15 mins)
```bash
# Coming next: src/main.py
# Simple CLI for users to interact
```

## 🏗️ Architecture

```
User Question
    ↓
[Memory] → Remember context
    ↓
[Vector Store] → Search documents
    ↓
[LLM] → Generate response
    ↓
Return Answer + Update Memory
```

## 📁 Project Structure

```
planningTripRag/
├── src/
│   ├── llm_client.py              ✅ Chat with Gemini
│   ├── pdf_extractor.py           ✅ Extract PDFs
│   ├── gemini_embeddings.py       ✅ Create vectors (FREE)
│   ├── vector_store.py            ✅ Search Pinecone
│   ├── memory.py                  🔄 TODO
│   ├── agent.py                   🔄 TODO
│   └── main.py                    🔄 TODO
├── docs/
│   ├── Shanghai_Tour_Package_Sample.pdf
│   ├── Singapore_Tour_Package_Sample-v2.pdf
│   └── Singapore_Tour_Package_Sample.pdf
└── Documentation
    ├── README.md                  (this file)
    ├── PROJECT_STATUS.md          (what's done)
    ├── COMPREHENSIVE_GUIDE.md     (learn everything)
    ├── QUICK_START.md             (how to run)
    └── LEARNING_GUIDE.md          (concepts)
```

## ✅ What Works Now

### Test Vector Search
```bash
cd planningTripRag
python3 src/vector_store.py
```

**Output:**
```
✅ Connected to Pinecone (28 vectors)
✅ Created embedding (384 dims)
✅ Found 3 similar documents
✅ Formatted context for LLM
```

### Test LLM Chat
```bash
python3 src/llm_client.py
```

## 🎯 Key Technologies

- **LLM**: Google Gemini (FREE)
- **Embeddings**: HuggingFace (LOCAL, FREE)
- **Vector DB**: Pinecone
- **Language**: Python
- **Framework**: None (pure Python)

## 💡 Why RAG?

Instead of relying on LLM's training data:
```
❌ "Tell me about Singapore tours"
   → Generic answer (training data only)

✅ "Tell me about Singapore tours"
   → Smart answer (your documents + LLM)
```

## 📖 Learning Path

1. ✅ Understand PDF → vectors pipeline
2. ✅ Understand vector similarity search
3. ✅ Understand LLM integration
4. 🔄 Learn conversation memory patterns
5. 🔄 Learn agent orchestration
6. 🔄 Build a working system

## 🚀 Ready to Continue?

**Read this in order:**
1. `PROJECT_STATUS.md` - See current progress (5 min read)
2. `COMPREHENSIVE_GUIDE.md` - Understand everything (30 min read)
3. Build `src/memory.py` (30 min code)
4. Build `src/agent.py` (60 min code)
5. Build `src/main.py` (15 min code)

**Then you'll have a working RAG agent!**

---

**Questions?** Check the documentation files above. Everything is explained in detail.

**Ready to build?** Start with: `PROJECT_STATUS.md`
