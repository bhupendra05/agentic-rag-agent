"""
Conversation Memory Module - Store and manage chat history

This module handles:
1. Storing user and assistant messages
2. Retrieving conversation history
3. Managing memory capacity (keep recent messages)
4. Providing context for multi-turn conversations

Why Memory?
Without memory:
  User: "Tell me about Marina Bay Sands"
  Bot: "Marina Bay Sands is..."

  User: "How much does it cost?"  ← Bot doesn't know what "it" refers to
  Bot: "I need more context..."

With memory:
  User: "Tell me about Marina Bay Sands"
  Bot: "Marina Bay Sands is..."
  Memory: [User asked about Marina Bay Sands]

  User: "How much does it cost?"
  Bot: Understands it refers to Marina Bay Sands
  Bot: "Marina Bay Sands costs $500/night..."
"""

from typing import List, Dict
import json
from datetime import datetime

# ============================================================================
# SECTION 1: Conversation Memory Class
# ============================================================================

class ConversationMemory:
    """
    Simple conversation memory that stores messages in order

    Format:
    [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
        {"role": "user", "content": "How are you?"},
        {"role": "assistant", "content": "I'm doing great!"},
    ]

    This format is standard for LLM APIs (Gemini, OpenAI, etc.)
    """

    def __init__(self, max_messages: int = 20):
        """
        Initialize memory

        Args:
            max_messages: Maximum number of messages to keep
                         (prevents memory from growing infinitely)

        Why max_messages?
        - LLMs have token limits (can't send 1000 messages)
        - Cost: More messages = more API calls = more $
        - Performance: Fewer messages = faster responses
        - Default 20 messages = ~10 conversation turns
        """
        self.messages: List[Dict[str, str]] = []
        self.max_messages = max_messages

    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to memory

        Args:
            role: "user" or "assistant"
            content: The message text

        Example:
            memory.add_message("user", "Hello")
            memory.add_message("assistant", "Hi there!")

        What happens:
        1. Create message dict with role and content
        2. Add to messages list
        3. If too many messages, remove oldest one
        """
        # Create message object
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()  # Track when message was added
        }

        # Add message
        self.messages.append(message)

        # Keep only recent messages
        if len(self.messages) > self.max_messages:
            # Remove oldest message
            self.messages.pop(0)

    def get_all(self) -> List[Dict[str, str]]:
        """
        Get all messages in conversation history

        Returns:
            List of messages in format ready for LLM
            [{"role": "user", "content": "..."}, ...]

        Why this format?
        Google Gemini, OpenAI, and other LLMs expect this exact format.
        It's the standard for conversation APIs.
        """
        # Return messages without timestamp (LLM doesn't need it)
        return [
            {
                "role": msg["role"],
                "content": msg["content"]
            }
            for msg in self.messages
        ]

    def get_user_messages(self) -> List[str]:
        """
        Get only user messages (for debugging/analysis)

        Returns:
            List of user message content
        """
        return [msg["content"] for msg in self.messages if msg["role"] == "user"]

    def get_assistant_messages(self) -> List[str]:
        """
        Get only assistant messages (for debugging/analysis)

        Returns:
            List of assistant message content
        """
        return [msg["content"] for msg in self.messages if msg["role"] == "assistant"]

    def get_last_n_messages(self, n: int) -> List[Dict[str, str]]:
        """
        Get last N messages (useful for recent context)

        Args:
            n: Number of recent messages to return

        Example:
            memory.get_last_n_messages(4)  # Last 2 turns (user + assistant each)

        Returns:
            Last N messages
        """
        return self.get_all()[-n:]

    def clear(self) -> None:
        """
        Clear all messages (start fresh conversation)

        Use when:
        - User says "start over"
        - Starting a new conversation
        - Memory getting too large
        """
        self.messages = []

    def get_summary(self) -> Dict:
        """
        Get memory statistics (for debugging)

        Returns:
            Dict with stats about the conversation

        Example output:
        {
            "total_messages": 10,
            "user_messages": 5,
            "assistant_messages": 5,
            "memory_usage": "~2500 characters",
            "max_capacity": 20
        }
        """
        total_chars = sum(len(msg["content"]) for msg in self.messages)

        return {
            "total_messages": len(self.messages),
            "user_messages": len(self.get_user_messages()),
            "assistant_messages": len(self.get_assistant_messages()),
            "memory_usage_chars": total_chars,
            "max_capacity": self.max_messages,
            "percentage_full": (len(self.messages) / self.max_messages) * 100
        }

    def __repr__(self) -> str:
        """String representation of memory"""
        summary = self.get_summary()
        return f"ConversationMemory(messages={summary['total_messages']}/{summary['max_capacity']})"


# ============================================================================
# SECTION 2: Testing
# ============================================================================

if __name__ == "__main__":
    """
    Test the conversation memory module
    Run: python src/memory.py
    """

    print("=" * 70)
    print("🧪 Testing Conversation Memory Module")
    print("=" * 70)
    print()

    # Test 1: Create memory
    print("[Test 1] Creating memory...")
    memory = ConversationMemory(max_messages=10)
    print(f"✅ Memory created: {memory}")
    print()

    # Test 2: Add messages
    print("[Test 2] Adding messages...")
    memory.add_message("user", "Tell me about Singapore")
    memory.add_message("assistant", "Singapore is a city-state in Southeast Asia...")
    memory.add_message("user", "What's the best time to visit?")
    memory.add_message("assistant", "The best time is December to February...")
    print(f"✅ Added 4 messages")
    print()

    # Test 3: Get all messages
    print("[Test 3] Retrieving all messages...")
    all_messages = memory.get_all()
    print(f"✅ Retrieved {len(all_messages)} messages")
    for i, msg in enumerate(all_messages, 1):
        role = msg["role"].upper()
        content = msg["content"][:50] + "..." if len(msg["content"]) > 50 else msg["content"]
        print(f"   [{i}] {role}: {content}")
    print()

    # Test 4: Get last N messages
    print("[Test 4] Getting last 2 messages...")
    last_2 = memory.get_last_n_messages(2)
    print(f"✅ Retrieved {len(last_2)} messages")
    for msg in last_2:
        print(f"   {msg['role'].upper()}: {msg['content'][:60]}...")
    print()

    # Test 5: Get memory summary
    print("[Test 5] Memory statistics...")
    summary = memory.get_summary()
    print(f"✅ Memory Summary:")
    print(f"   Total messages: {summary['total_messages']}/{summary['max_capacity']}")
    print(f"   User messages: {summary['user_messages']}")
    print(f"   Assistant messages: {summary['assistant_messages']}")
    print(f"   Characters stored: {summary['memory_usage_chars']}")
    print(f"   Capacity used: {summary['percentage_full']:.1f}%")
    print()

    # Test 6: Message format for LLM
    print("[Test 6] Format for LLM (Gemini)...")
    llm_format = memory.get_all()
    print(f"✅ Messages ready for LLM:")
    print(f"   Format: {json.dumps(llm_format[:2], indent=2)}")
    print()

    # Test 7: Clear memory
    print("[Test 7] Clearing memory...")
    memory.clear()
    print(f"✅ Memory cleared: {memory}")
    print(f"   Messages remaining: {len(memory.get_all())}")
    print()

    print("=" * 70)
    print("✅ All tests passed!")
    print("=" * 70)
    print()
    print("Memory module is ready to use in agent!")
