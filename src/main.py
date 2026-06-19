"""
Main Chat Interface - User-friendly CLI for the RAG Agent

This is the entry point where users interact with the RAG agent.

It handles:
1. Initializing the agent
2. Getting user input
3. Processing with agent
4. Displaying responses
5. Managing conversation

Simple but powerful - all complexity is hidden in agent.py
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agent import RAGAgent
from memory import ConversationMemory

# ============================================================================
# SECTION 1: Chat Interface
# ============================================================================

def print_banner():
    """
    Print welcome banner
    """
    print("\n" + "=" * 70)
    print("🤖 RAG AGENT - Singapore Tour Guide")
    print("=" * 70)
    print("\nWelcome! I'm your AI Singapore tour guide.")
    print("Ask me anything about Singapore attractions, tours, and packages.")
    print("\nCommands:")
    print("  • Type your question to get answers")
    print("  • Type 'memory' to see conversation stats")
    print("  • Type 'clear' to start fresh conversation")
    print("  • Type 'verbose' to toggle detailed processing info")
    print("  • Type 'help' for more information")
    print("  • Type 'exit' to quit")
    print("\n" + "=" * 70 + "\n")


def print_help():
    """
    Print detailed help information
    """
    help_text = """
📚 HELP - How to Use the RAG Agent

ASKING QUESTIONS:
  • "Tell me about Marina Bay Sands"
  • "How much does it cost?"
  • "What attractions are nearby?"
  • "What's the best time to visit?"

THE AGENT WILL:
  1. Search your tour documents (Pinecone)
  2. Find relevant information
  3. Remember previous questions
  4. Provide accurate answers

SPECIAL COMMANDS:
  memory  - Show conversation statistics
  clear   - Clear conversation history (start fresh)
  verbose - Toggle detailed step-by-step processing info
  help    - Show this message
  exit    - Quit the program

TIPS:
  • Ask follow-up questions! Agent remembers context
  • Be specific ("Marina Bay" vs "that hotel")
  • Agent combines multiple docs for complete answers
  • Memory keeps last 20 messages to manage costs

MULTI-TURN EXAMPLE:
  You: "Tell me about Marina Bay Sands"
  Bot: "Marina Bay Sands is a 57-story integrated resort..."

  You: "How much does it cost?"
  Bot: Remembers Marina Bay from previous question
  Bot: "Marina Bay Sands costs $500-$1000 per night..."

  You: "What's nearby?"
  Bot: Still remembers Marina Bay context
  Bot: "Near Marina Bay, you'll find Gardens by the Bay..."

Questions? The agent will do its best to help!
"""
    print(help_text)


def print_memory_status(agent: RAGAgent):
    """
    Print current memory/conversation statistics

    Args:
        agent: The RAG agent instance
    """
    summary = agent.get_conversation_summary()

    print("\n" + "=" * 70)
    print("📊 CONVERSATION MEMORY STATUS")
    print("=" * 70)
    print(f"Total messages: {summary['total_messages']}/{summary['max_capacity']}")
    print(f"User questions: {summary['user_messages']}")
    print(f"Agent responses: {summary['assistant_messages']}")
    print(f"Text stored: {summary['memory_usage_chars']:,} characters")
    print(f"Memory usage: {summary['percentage_full']:.1f}%")

    if summary['user_messages'] > 0:
        print(f"\nConversation turns: {summary['user_messages']}")
        print("Recent topics:")
        for i, msg in enumerate(agent.memory.get_user_messages()[-3:], 1):
            preview = msg[:60] + "..." if len(msg) > 60 else msg
            print(f"  {i}. {preview}")

    print("=" * 70 + "\n")


def main():
    """
    Main chat loop

    Flow:
    1. Print welcome banner
    2. Initialize agent
    3. Loop for user input
    4. Process with agent
    5. Display response
    6. Handle special commands
    7. Exit gracefully
    """

    # Initialize agent
    print_banner()
    print("🚀 Initializing agent...")

    try:
        agent = RAGAgent(max_memory=20)
        print("✅ Agent ready!\n")
    except Exception as e:
        print(f"❌ Error initializing agent: {e}")
        print("Please check your .env file and API keys.")
        sys.exit(1)

    # Conversation settings
    verbose = False  # Toggle for detailed output
    conversation_count = 0

    # Main loop
    try:
        while True:
            # Get user input
            try:
                user_input = input("You: ").strip()
            except EOFError:
                # Handle Ctrl+D
                print("\n\nGoodbye! 👋")
                break
            except KeyboardInterrupt:
                # Handle Ctrl+C
                print("\n\nGoodbye! 👋")
                break

            # Skip empty input
            if not user_input:
                continue

            # ================================================================
            # SECTION 2: Handle Special Commands
            # ================================================================

            # Exit command
            if user_input.lower() == "exit":
                print("\n" + "=" * 70)
                print("Thank you for using RAG Agent!")
                print(f"Total conversations: {conversation_count}")
                summary = agent.get_conversation_summary()
                if summary['user_messages'] > 0:
                    print(f"Questions asked: {summary['user_messages']}")
                print("Goodbye! 👋")
                print("=" * 70 + "\n")
                break

            # Memory command
            if user_input.lower() == "memory":
                print_memory_status(agent)
                continue

            # Clear command
            if user_input.lower() == "clear":
                agent.clear_memory()
                conversation_count = 0
                print("\n✨ Conversation cleared! Starting fresh...\n")
                continue

            # Verbose command
            if user_input.lower() == "verbose":
                verbose = not verbose
                status = "ON" if verbose else "OFF"
                print(f"\n📝 Verbose mode: {status}\n")
                continue

            # Help command
            if user_input.lower() == "help":
                print_help()
                continue

            # ================================================================
            # SECTION 3: Process User Input with Agent
            # ================================================================

            conversation_count += 1

            print("\n🤔 Thinking...\n")

            try:
                # This is the main call to the agent
                # Everything happens here:
                # 1. Add to memory
                # 2. Search documents
                # 3. Generate response
                # 4. Save to memory
                response = agent.run(
                    user_input,
                    top_k=3,  # Return top 3 documents
                    verbose=verbose  # Print detailed steps if enabled
                )

                # Display response
                print(f"Agent: {response}\n")

            except Exception as e:
                print(f"\n❌ Error processing query: {e}")
                print("Please try again or type 'help' for assistance.\n")
                continue

    except KeyboardInterrupt:
        # Handle Ctrl+C from main loop
        print("\n\nGoodbye! 👋")
    except Exception as e:
        print(f"\n❌ Unexpected error in main loop: {e}")


# ============================================================================
# SECTION 4: Entry Point
# ============================================================================

if __name__ == "__main__":
    """
    Entry point for the application

    Usage:
      python src/main.py
    """
    try:
        main()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
