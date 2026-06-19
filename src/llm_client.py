import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load .env file FIRST
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file!")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-3.1-flash-lite")  # Free tier

def chat_with_model(messages):
    """Send messages to Gemini, get response"""
    # Convert to Gemini format (user → user, assistant → model)
    conversation = []
    for msg in messages:
        if msg["role"] == "user":
            conversation.append({"role": "user", "parts": [msg["content"]]})
        else:
            conversation.append({"role": "model", "parts": [msg["content"]]})

    # Send FULL conversation history, not just last message
    response = model.generate_content(conversation)
    return response.text

# Test
if __name__ == "__main__":
    result = chat_with_model([
        {"role": "user", "content": "Hello, who are you?"}
    ])
    print(result)