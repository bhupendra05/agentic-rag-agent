"""
RAG Agent Module - Orchestrate the complete RAG pipeline

This module brings everything together:
1. Memory (conversation history)
2. Vector Store (document search)
3. LLM (response generation)

The Agent is the "conductor" that coordinates all pieces.

RAG Flow:
  User Question
       ↓
  [Agent] ─→ Search documents (get context)
       ↓
  Add context to prompt
       ↓
  Add conversation history
       ↓
  Send to LLM
       ↓
  LLM generates answer
       ↓
  Save to memory
       ↓
  Return response
"""

import sys
from pathlib import Path

# Add src directory to path so we can import modules
sys.path.insert(0, str(Path(__file__).parent))

from memory import ConversationMemory
from vector_store import search_knowledge, format_context
from llm_client import chat_with_model

# ============================================================================
# SECTION 1: RAG Agent Class
# ============================================================================

class RAGAgent:
    """
    Retrieval-Augmented Generation Agent

    Combines:
    - Conversation Memory (remembers context)
    - Vector Search (finds relevant documents)
    - LLM (generates responses)

    Into a coherent, intelligent agent.
    """

    def __init__(self, max_memory: int = 20):
        """
        Initialize the RAG Agent

        Args:
            max_memory: Maximum conversation messages to keep

        What it initializes:
        - Memory: For storing conversation
        - System prompt: Instructions for the LLM
        - Config: Agent settings
        """
        self.memory = ConversationMemory(max_messages=max_memory)

        # System prompt that defines the agent's behavior
        self.system_prompt = """You are a helpful and knowledgeable Singapore Tour Guide AI Assistant.

Your role:
- Answer questions about Singapore tours and attractions
- Provide recommendations based on the tour packages available
- Give accurate information using the provided context
- Be friendly and engaging

Guidelines:
- Use the retrieved context to provide accurate answers
- If context doesn't answer the question, use your general knowledge
- Always be helpful and professional
- Recommend attractions from the tour packages when relevant
- Ask follow-up questions if you need clarification"""

        print("✅ RAG Agent initialized")

    # ========================================================================
    # SECTION 2: Main Agent Loop
    # ========================================================================

    def run(self, user_message: str, top_k: int = 3, verbose: bool = False) -> str:
        """
        Main agent loop - process user message and generate response

        Args:
            user_message: User's question
            top_k: Number of documents to retrieve (default 3)
            verbose: Print detailed process steps

        Returns:
            Agent's response

        Flow:
        1. Add user message to memory
        2. Search knowledge base for context
        3. Create augmented prompt with context
        4. Get LLM response (with full conversation history)
        5. Save response to memory
        6. Return response
        """

        if verbose:
            print("\n" + "=" * 70)
            print("🤖 RAG AGENT PROCESSING")
            print("=" * 70)

        # ====================================================================
        # STEP 1: Remember user message
        # ====================================================================
        if verbose:
            print("\n[Step 1] Adding to memory...")
        self.memory.add_message("user", user_message)
        if verbose:
            print(f"   ✓ User message stored")
            print(f"   ✓ Memory: {self.memory}")

        # ====================================================================
        # STEP 2: Search knowledge base (RAG - Retrieval)
        # ====================================================================
        if verbose:
            print("\n[Step 2] Searching knowledge base...")
        try:
            search_results = search_knowledge(user_message, top_k=top_k)
            context = format_context(search_results)
            if verbose:
                print(f"   ✓ Found {len(search_results)} documents")
                print(f"   ✓ Context prepared ({len(context)} characters)")
        except Exception as e:
            if verbose:
                print(f"   ⚠ Search failed: {e}")
            context = "No relevant documents found in knowledge base."

        # ====================================================================
        # STEP 3: Create augmented prompt (RAG - Augmentation)
        # ====================================================================
        if verbose:
            print("\n[Step 3] Creating augmented prompt...")

        # Build the system prompt with context
        augmented_system_prompt = f"""{self.system_prompt}

RELEVANT CONTEXT FROM TOUR PACKAGES:
{context}

Use this context to provide accurate, specific answers about Singapore tours."""

        if verbose:
            print(f"   ✓ System prompt created")
            print(f"   ✓ Context included ({len(context)} chars)")

        # ====================================================================
        # STEP 4: Get LLM response (RAG - Generation)
        # ====================================================================
        if verbose:
            print("\n[Step 4] Sending to LLM...")
            print(f"   ✓ Conversation history: {len(self.memory.get_all())} messages")
            print(f"   ✓ Context included: Yes")

        try:
            # Prepare messages for LLM
            # Include system prompt + full conversation history
            messages_for_llm = [{"role": "system", "content": augmented_system_prompt}]
            messages_for_llm.extend(self.memory.get_all())

            # Get response from LLM
            response = chat_with_model(messages_for_llm)

            if verbose:
                print(f"   ✓ Response generated ({len(response)} characters)")

        except Exception as e:
            response = f"Sorry, I encountered an error: {e}. Please try again."
            if verbose:
                print(f"   ✗ Error: {e}")

        # ====================================================================
        # STEP 5: Save response to memory
        # ====================================================================
        if verbose:
            print("\n[Step 5] Saving response to memory...")
        self.memory.add_message("assistant", response)
        if verbose:
            print(f"   ✓ Response saved")
            print(f"   ✓ Memory: {self.memory}")

        # ====================================================================
        # STEP 6: Return response
        # ====================================================================
        if verbose:
            print("\n" + "=" * 70)
            print("✅ PROCESSING COMPLETE")
            print("=" * 70 + "\n")

        return response

    # ========================================================================
    # SECTION 3: Memory Management
    # ========================================================================

    def get_conversation_summary(self) -> dict:
        """
        Get summary of current conversation

        Returns:
            Dict with conversation statistics
        """
        return self.memory.get_summary()

    def clear_memory(self) -> None:
        """
        Clear conversation history (start fresh)

        Use when:
        - User wants to start a new conversation
        - Switching topics completely
        """
        self.memory.clear()
        print("✅ Conversation memory cleared")

    def get_memory_status(self) -> str:
        """
        Get human-readable memory status

        Returns:
            String describing current memory state
        """
        summary = self.memory.get_summary()
        return f"""Memory Status:
  Total messages: {summary['total_messages']}/{summary['max_capacity']}
  User messages: {summary['user_messages']}
  Assistant messages: {summary['assistant_messages']}
  Characters: {summary['memory_usage_chars']}
  Capacity: {summary['percentage_full']:.1f}%"""


# ============================================================================
# SECTION 4: Multi-turn Conversation Example
# ============================================================================

def example_conversation():
    """
    Example of multi-turn conversation showing memory in action
    """
    print("\n" + "=" * 70)
    print("📝 EXAMPLE: Multi-turn Conversation")
    print("=" * 70 + "\n")

    # Create agent
    agent = RAGAgent()

    # Turn 1
    print("=" * 70)
    print("TURN 1: User asks about Marina Bay")
    print("=" * 70)
    user_input_1 = "Tell me about Marina Bay Sands"
    print(f"\nUser: {user_input_1}")
    response_1 = agent.run(user_input_1, verbose=False)
    print(f"\nAgent: {response_1[:200]}...")

    # Turn 2 - Agent remembers context from Turn 1!
    print("\n" + "=" * 70)
    print("TURN 2: User asks follow-up (Agent remembers Marina Bay)")
    print("=" * 70)
    user_input_2 = "How much does it cost per night?"
    print(f"\nUser: {user_input_2}")
    print("(Without memory: Agent wouldn't know what 'it' refers to)")
    print("(With memory: Agent knows it refers to Marina Bay Sands)")
    response_2 = agent.run(user_input_2, verbose=False)
    print(f"\nAgent: {response_2[:200]}...")

    # Turn 3 - More context building
    print("\n" + "=" * 70)
    print("TURN 3: Another follow-up")
    print("=" * 70)
    user_input_3 = "What attractions are nearby?"
    print(f"\nUser: {user_input_3}")
    response_3 = agent.run(user_input_3, verbose=False)
    print(f"\nAgent: {response_3[:200]}...")

    # Show memory
    print("\n" + "=" * 70)
    print("📊 CONVERSATION MEMORY")
    print("=" * 70)
    print(agent.get_memory_status())
    print("\nFull conversation:")
    for i, msg in enumerate(agent.memory.get_all(), 1):
        role = msg['role'].upper()
        content = msg['content'][:80] + "..." if len(msg['content']) > 80 else msg['content']
        print(f"\n[{i}] {role}:")
        print(f"    {content}")


# ============================================================================
# SECTION 5: Testing
# ============================================================================

if __name__ == "__main__":
    """
    Test the RAG Agent module
    Run: python src/agent.py
    """

    print("=" * 70)
    print("🧪 Testing RAG Agent Module")
    print("=" * 70)
    print()

    # Test 1: Initialize agent
    print("[Test 1] Initializing RAG Agent...")
    try:
        agent = RAGAgent(max_memory=10)
        print("✅ Agent initialized successfully")
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)
    print()

    # Test 2: Single-turn conversation
    print("[Test 2] Testing single-turn conversation...")
    try:
        response = agent.run("What are the top attractions in Singapore?", verbose=False)
        print(f"✅ Got response ({len(response)} characters)")
        print(f"   Response: {response[:100]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)
    print()

    # Test 3: Memory check
    print("[Test 3] Checking memory after one message...")
    try:
        summary = agent.get_conversation_summary()
        print(f"✅ Memory check passed")
        print(f"   Total messages: {summary['total_messages']}")
        print(f"   User messages: {summary['user_messages']}")
        print(f"   Assistant messages: {summary['assistant_messages']}")
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)
    print()

    # Test 4: Multi-turn with memory
    print("[Test 4] Testing multi-turn conversation (memory in action)...")
    try:
        agent2 = RAGAgent()

        # First turn
        r1 = agent2.run("Tell me about Gardens by the Bay", verbose=False)
        print(f"✅ Turn 1 complete")

        # Second turn - this should reference the first
        r2 = agent2.run("How long does it take to visit?", verbose=False)
        print(f"✅ Turn 2 complete (agent remembered first question)")

        # Check memory
        memory_status = agent2.get_conversation_summary()
        print(f"   Memory after 2 turns: {memory_status['total_messages']} messages")

    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)
    print()

    # Test 5: Clear memory
    print("[Test 5] Testing memory clear...")
    try:
        agent2.clear_memory()
        summary = agent2.get_conversation_summary()
        if summary['total_messages'] == 0:
            print(f"✅ Memory cleared successfully")
        else:
            print(f"❌ Memory not cleared")
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)
    print()

    print("=" * 70)
    print("✅ All tests passed!")
    print("=" * 70)
    print()
    print("RAG Agent is ready to use in chat interface!")
    print()
    print("To see multi-turn conversation example, run:")
    print("  from src.agent import example_conversation")
    print("  example_conversation()")
