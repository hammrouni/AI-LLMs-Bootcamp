"""
05 - Mini Chatbot Demo
========================
A complete chatbot that combines everything from Day 4:
ChatPromptTemplate + LCEL Chain + Conversation Memory + Streaming.

Two modes:
  1. Automated demo (no input needed — shows the full flow)
  2. Interactive mode (type your own messages — requires MISTRAL_API_KEY)

HOW TO RUN:
    pip install langchain langchain-openai python-dotenv
    python demo.py

Set MISTRAL_API_KEY in a .env file to enable live chat.
Get a free key at: https://console.mistral.ai
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# CHATBOT CONFIGURATION
# ============================================================
SYSTEM_PROMPT = """You are Anis, a friendly AI assistant specializing in Tunisian culture, history, and travel.

Your expertise: Tunisian history (Carthage, Roman era, Islamic period), cuisine, traditions, travel tips, and modern Tunisia.

Rules:
- Be warm, enthusiastic, and proud of Tunisian heritage.
- Keep answers concise — under 80 words unless a detailed explanation is truly needed.
- If asked about unrelated topics, answer briefly but steer back to Tunisia.

Format: Use simple language. Bullet points for lists. No unnecessary preamble."""

MAX_HISTORY_TURNS = 5  # keep last 5 turns to control token cost


# ============================================================
# HELPER: Build LLM client
# ============================================================
def get_llm():
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        return None
    try:
        from langchain_openai.chat_models.base import BaseChatOpenAI
        return BaseChatOpenAI(
            model="mistral-small-latest",
            api_key=api_key,
            base_url="https://api.mistral.ai/v1",
            temperature=0.7,
            max_tokens=250,
        )
    except ImportError:
        print("Install with: pip install langchain langchain-openai")
        return None


# ============================================================
# HELPER: Trim history to last N turns
# ============================================================
def trim_history(history: list, max_turns: int) -> list:
    max_messages = max_turns * 2
    return history[-max_messages:] if len(history) > max_messages else history


# ============================================================
# HELPER: Build the chain
# ============================================================
def build_chain(llm):
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.output_parsers import StrOutputParser

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder("chat_history"),
        ("human", "{user_input}"),
    ])

    return prompt | llm | StrOutputParser()


# ============================================================
# PART 1: Architecture Walkthrough (no API needed)
# ============================================================
def show_architecture():
    """Explain what the chatbot does step by step."""
    print("=== PART 1: Chatbot Architecture ===\n")

    print("  Components combined from Day 4:\n")
    print("  ┌─────────────────────────────────────────────────────┐")
    print("  │  User types a message                               │")
    print("  │         ↓                                           │")
    print("  │  [01] ChatPromptTemplate                            │")
    print("  │       system prompt + history slot + user input     │")
    print("  │         ↓                                           │")
    print("  │  [02] ChatOpenAI → Mistral API                      │")
    print("  │       LCEL chain via | operator                     │")
    print("  │         ↓                                           │")
    print("  │  [03] StrOutputParser → plain text                  │")
    print("  │         ↓                                           │")
    print("  │  [04] Append to chat_history                        │")
    print("  │         ↓                                           │")
    print("  │  [05] Stream response to screen                     │")
    print("  │         ↓                                           │")
    print("  │  Loop — wait for next user message                  │")
    print("  └─────────────────────────────────────────────────────┘\n")

    print(f"  System prompt: '{SYSTEM_PROMPT[:80]}...'\n")
    print(f"  Max history: {MAX_HISTORY_TURNS} turns ({MAX_HISTORY_TURNS * 2} messages)\n")


# ============================================================
# PART 2: Automated Demo — Simulated Conversation
# ============================================================
def automated_demo():
    """Run a scripted conversation to show the full flow."""
    print("=== PART 2: Automated Demo — Scripted Conversation ===\n")

    from langchain_core.messages import HumanMessage, AIMessage

    scripted_exchanges = [
        ("Salam! What's the most famous ancient site in Tunisia?",
         "Salam! 🏛️ Without a doubt — Carthage! The ancient Phoenician city near Tunis that once rivaled Rome. You can visit the ruins today: the Antonine Baths, the Tophet, and the Punic ports. A must-see for any history lover!"),
        ("Tell me more about the Bardo Museum.",
         "The Bardo Museum in Tunis is world-famous for its extraordinary Roman mosaic collection — one of the largest in the world. The mosaics come from excavations across Tunisia and are breathtaking in size and detail. Entry is around 11 TND for tourists."),
        ("What should I eat when I visit?",
         "Tunisian food is incredible! Top picks:\n• Brik — crispy pastry with egg and tuna\n• Lablabi — chickpea soup with cumin and harissa\n• Couscous bil merguez — Friday classic\n• Fresh ojja with seafood on the coast\nDon't miss harissa on everything! 🌶️"),
    ]

    llm = get_llm()
    chat_history = []

    if not llm:
        print("  [SIMULATED — set MISTRAL_API_KEY for real responses]\n")
        for user_msg, bot_reply in scripted_exchanges:
            print(f"  You: {user_msg}")
            print(f"  Anis: {bot_reply}")
            print(f"  [History: {len(chat_history)} messages]\n")
            chat_history.append(HumanMessage(user_msg))
            chat_history.append(AIMessage(bot_reply))
        return

    chain = build_chain(llm)

    for user_msg, _ in scripted_exchanges:
        trimmed = trim_history(chat_history, MAX_HISTORY_TURNS)

        print(f"  You: {user_msg}")
        print(f"  Anis: ", end="", flush=True)

        full_response = ""
        for chunk in chain.stream({"chat_history": trimmed, "user_input": user_msg}):
            print(chunk, end="", flush=True)
            full_response += chunk
        print(f"\n  [History: {len(chat_history)} messages]\n")

        chat_history.append(HumanMessage(user_msg))
        chat_history.append(AIMessage(full_response))


# ============================================================
# PART 3: Memory Test — Does It Remember?
# ============================================================
def memory_test():
    """Verify the chatbot actually remembers context."""
    print("=== PART 3: Memory Test ===\n")

    from langchain_core.messages import HumanMessage, AIMessage

    memory_conversation = [
        "My name is Bilel and I'm planning a trip to Tunisia.",
        "I'm arriving in Tunis and then going south.",
        "What's my name?",
        "Which direction am I traveling in Tunisia?",
    ]

    llm = get_llm()
    chat_history = []

    if not llm:
        print("  [SIMULATED — set MISTRAL_API_KEY for real responses]\n")
        simulated = [
            "Welcome, Bilel! Tunisia is a wonderful destination. What are your interests?",
            "Great plan! Heading south means Matmata cave houses, Tozeur oasis, and the Sahara dunes!",
            "Your name is Bilel.",
            "You're traveling south through Tunisia.",
        ]
        for msg, sim in zip(memory_conversation, simulated):
            print(f"  You: {msg}")
            print(f"  Anis: {sim}\n")
        return

    chain = build_chain(llm)

    for user_msg in memory_conversation:
        trimmed = trim_history(chat_history, MAX_HISTORY_TURNS)
        response = chain.invoke({"chat_history": trimmed, "user_input": user_msg})

        print(f"  You: {user_msg}")
        print(f"  Anis: {response}\n")

        chat_history.append(HumanMessage(user_msg))
        chat_history.append(AIMessage(response))


# ============================================================
# PART 4: Interactive Chat (requires API key)
# ============================================================
def interactive_chat():
    """Run a real interactive chatbot in the terminal."""
    print("=== PART 4: Interactive Chat ===\n")

    llm = get_llm()
    if not llm:
        print("  Set MISTRAL_API_KEY in .env to run the interactive chatbot.\n")
        print("  Commands you'll have when running:")
        print("    /clear   → clear conversation history")
        print("    /history → show how many messages are in history")
        print("    exit     → quit the chatbot\n")
        return

    from langchain_core.messages import HumanMessage, AIMessage

    chain = build_chain(llm)
    chat_history = []

    print("  Chatbot 'Anis' is ready! Type your message and press Enter.")
    print("  Commands: /clear  /history  exit\n")
    print("  " + "─" * 50)

    while True:
        try:
            user_input = input("\n  You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Goodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit", "q"):
            print("  Anis: Goodbye! Ahlan wa sahlan — come back anytime! 👋")
            break

        if user_input.lower() == "/clear":
            chat_history = []
            print("  [History cleared]")
            continue

        if user_input.lower() == "/history":
            turns = len(chat_history) // 2
            print(f"  [History: {turns} turns, {len(chat_history)} messages]")
            continue

        trimmed = trim_history(chat_history, MAX_HISTORY_TURNS)

        print("  Anis: ", end="", flush=True)
        full_response = ""

        for chunk in chain.stream({"chat_history": trimmed, "user_input": user_input}):
            print(chunk, end="", flush=True)
            full_response += chunk
        print()

        chat_history.append(HumanMessage(user_input))
        chat_history.append(AIMessage(full_response))


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    show_architecture()
    automated_demo()
    memory_test()
    interactive_chat()

    print("--- Key Takeaways ---")
    print("1. Full chatbot = ChatPromptTemplate + MessagesPlaceholder + LCEL chain + history list")
    print("2. stream() instead of invoke() gives a live typing effect — better UX")
    print("3. Trim history to MAX_TURNS before each invoke() to control token cost")
    print("4. Always append HumanMessage + AIMessage to history AFTER getting the response")
    print("5. Special commands (/clear, /history) make the chatbot more usable")
    print("6. Next step: connect this chatbot to your own documents with RAG (Day 5)")
