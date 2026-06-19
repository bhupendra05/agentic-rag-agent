"""
Web Server for RAG Agent with Live Workflow Visualization

Features:
- Flask web server
- Real-time chat interface
- Live workflow visualization
- Shows RAG pipeline steps as they happen
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sys
from pathlib import Path
import json
import time

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agent import RAGAgent

# ============================================================================
# SECTION 1: Flask App Setup
# ============================================================================

app = Flask(__name__, template_folder='../templates', static_folder='../static')
CORS(app)

# Initialize agent globally
agent = None

def init_agent():
    """Initialize RAG agent"""
    global agent
    try:
        agent = RAGAgent(max_memory=20)
        return True
    except Exception as e:
        print(f"Error initializing agent: {e}")
        return False

# ============================================================================
# SECTION 2: API Endpoints
# ============================================================================

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Chat endpoint - processes user message and returns response with workflow

    Expected JSON:
    {
        "message": "user question"
    }

    Returns:
    {
        "response": "agent response",
        "workflow_steps": [
            {"step": "search", "status": "complete", "duration": 500},
            {"step": "augment", "status": "complete", "duration": 100},
            ...
        ],
        "memory": {
            "total_messages": 4,
            "percentage": 40
        }
    }
    """
    try:
        data = request.get_json()
        message = data.get('message', '').strip()

        if not message:
            return jsonify({"error": "Empty message"}), 400

        if not agent:
            return jsonify({"error": "Agent not initialized"}), 500

        # Track workflow steps with timing
        workflow_steps = []

        # Step 1: Add to memory
        start = time.time()
        agent.memory.add_message("user", message)
        workflow_steps.append({
            "step": "memory",
            "name": "Store Input",
            "status": "complete",
            "duration": int((time.time() - start) * 1000)
        })

        # Step 2: Search documents
        start = time.time()
        try:
            from vector_store import search_knowledge, format_context
            search_results = search_knowledge(message, top_k=3)
            context = format_context(search_results)
            workflow_steps.append({
                "step": "search",
                "name": "Search Knowledge Base",
                "status": "complete",
                "duration": int((time.time() - start) * 1000),
                "docs_found": len(search_results)
            })
        except Exception as e:
            context = ""
            workflow_steps.append({
                "step": "search",
                "name": "Search Knowledge Base",
                "status": "error",
                "duration": int((time.time() - start) * 1000),
                "error": str(e)
            })

        # Step 3: Augment prompt with context
        start = time.time()
        augmented_prompt = f"""{agent.system_prompt}

RELEVANT CONTEXT FROM TOUR PACKAGES:
{context}

Use this context to provide accurate answers."""
        workflow_steps.append({
            "step": "augment",
            "name": "Augment Prompt",
            "status": "complete",
            "duration": int((time.time() - start) * 1000)
        })

        # Step 4: Get LLM response
        start = time.time()
        try:
            from llm_client import chat_with_model
            messages_for_llm = [{"role": "system", "content": augmented_prompt}]
            messages_for_llm.extend(agent.memory.get_all())

            response = chat_with_model(messages_for_llm)
            workflow_steps.append({
                "step": "llm",
                "name": "Generate Response",
                "status": "complete",
                "duration": int((time.time() - start) * 1000)
            })
        except Exception as e:
            response = f"Error: {e}"
            workflow_steps.append({
                "step": "llm",
                "name": "Generate Response",
                "status": "error",
                "duration": int((time.time() - start) * 1000),
                "error": str(e)
            })

        # Step 5: Save to memory
        start = time.time()
        agent.memory.add_message("assistant", response)
        workflow_steps.append({
            "step": "memory_save",
            "name": "Save Response",
            "status": "complete",
            "duration": int((time.time() - start) * 1000)
        })

        # Get memory status
        memory_summary = agent.get_conversation_summary()

        return jsonify({
            "success": True,
            "response": response,
            "workflow_steps": workflow_steps,
            "memory": {
                "total_messages": memory_summary['total_messages'],
                "max_capacity": memory_summary['max_capacity'],
                "percentage": memory_summary['percentage_full']
            }
        })

    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/memory', methods=['GET'])
def get_memory():
    """Get current memory status"""
    if not agent:
        return jsonify({"error": "Agent not initialized"}), 500

    summary = agent.get_conversation_summary()
    return jsonify({
        "total_messages": summary['total_messages'],
        "user_messages": summary['user_messages'],
        "assistant_messages": summary['assistant_messages'],
        "memory_usage_chars": summary['memory_usage_chars'],
        "max_capacity": summary['max_capacity'],
        "percentage": summary['percentage_full']
    })

@app.route('/api/clear', methods=['POST'])
def clear_memory():
    """Clear conversation memory"""
    if not agent:
        return jsonify({"error": "Agent not initialized"}), 500

    agent.clear_memory()
    return jsonify({"success": True, "message": "Memory cleared"})

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "agent_initialized": agent is not None
    })

# ============================================================================
# SECTION 3: Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500

# ============================================================================
# SECTION 4: Entry Point
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🚀 RAG Agent Web Server")
    print("=" * 70)

    # Initialize agent
    print("\n🤖 Initializing RAG Agent...")
    if not init_agent():
        print("❌ Failed to initialize agent")
        sys.exit(1)

    print("✅ Agent ready!")
    print("\n🌐 Starting web server...")
    print("📖 Open: http://localhost:5000")
    print("=" * 70 + "\n")

    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False  # Disable reloader to avoid double agent initialization
    )
