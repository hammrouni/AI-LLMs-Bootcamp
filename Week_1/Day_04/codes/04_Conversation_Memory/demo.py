"""
04 - Conversation Memory Demo
==============================
Build AI conversations that actually remember context across multiple turns.
Learn the modern LCEL approach: manage history explicitly, no hidden magic.

HOW TO RUN:
    pip install langchain langchain-openai python-dotenv
    python demo.py

Set MISTRAL_API_KEY in a .env file to run live API examples.
Get a free key at: https://console.mistral.ai
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# HELPER: Build LLM client
# ============================================================
def get_llm(max_tokens: int = 200):
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
            max_tokens=max_tokens,
        )
    except ImportError:
        print("  Install with: pip install langchain langchain-openai")
        return None


# ============================================================
# PART 1: The Problem — No Memory Between Calls
# ============================================================
def show_no_memory_problem():
    """Demonstrate that LLMs are stateless by default."""
    print("=== PART 1: The Problem — AI Has No Memory ===\n")

    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Be concise."),
        ("human", "{question}"),
    ])

    llm = get_llm(max_tokens=60)

    conversation = [
        "My name is Yasmine and I work as a data scientist in Tunis.",
        "What is my job?",
        "What city do I work in?",
    ]

    print("  Sending 3 messages WITHOUT conversation history:\n")

    if not llm:
        print("  [SIMULATED — set MISTRAL_API_KEY to see real responses]\n")
        print("  Turn 1 — Q: 'My name is Yasmine and I work as a data scientist in Tunis.'")
        print("           A: 'Nice to meet you, Yasmine!'")
        print()
        print("  Turn 2 — Q: 'What is my job?'")
        print("           A: 'I don\\'t have information about your job.'  ← forgot!")
        print()
        print("  Turn 3 — Q: 'What city do I work in?'")
        print("           A: 'I don\\'t have that information.'  ← forgot!\n")
        return

    chain = prompt | llm | StrOutputParser()
    for i, question in enumerate(conversation, 1):
        result = chain.invoke({"question": question})
        print(f"  Turn {i} — Q: '{question}'")
        print(f"           A: '{result}'\n")

    print("  Observation: Turn 2 and 3 have no context — the model forgot everything.\n")


# ============================================================
# PART 2: The Fix — Manual Chat History
# ============================================================
def manual_chat_history_demo():
    """Maintain history manually and inject it into each request."""
    print("=== PART 2: The Fix — Manual Chat History ===\n")

    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.messages import HumanMessage, AIMessage

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Be concise — under 40 words."),
        MessagesPlaceholder("chat_history"),
        ("human", "{user_input}"),
    ])

    llm = get_llm(max_tokens=80)

    conversation = [
        "My name is Yasmine and I work as a data scientist in Tunis.",
        "What is my job?",
        "What city do I work in?",
        "Recommend one Python library for my field.",
    ]

    chat_history = []

    print("  Same messages, now WITH chat history injected each turn:\n")

    simulated_responses = [
        "Nice to meet you, Yasmine! Data science is a great field.",
        "You work as a data scientist.",
        "You work in Tunis.",
        "I recommend pandas — essential for data manipulation and analysis in data science.",
    ]

    if not llm:
        print("  [SIMULATED — set MISTRAL_API_KEY to see real responses]\n")
        for i, (msg, sim_resp) in enumerate(zip(conversation, simulated_responses), 1):
            print(f"  Turn {i} — Q: '{msg}'")
            print(f"    History: {len(chat_history)} messages")
            print(f"           A: '{sim_resp}'")
            chat_history.append(HumanMessage(msg))
            chat_history.append(AIMessage(sim_resp))
            print()
        return

    chain = prompt | llm | StrOutputParser()

    for i, user_msg in enumerate(conversation, 1):
        result = chain.invoke({
            "chat_history": chat_history,
            "user_input": user_msg,
        })

        print(f"  Turn {i} — Q: '{user_msg}'")
        print(f"    History sent: {len(chat_history)} messages")
        print(f"           A: '{result}'\n")

        chat_history.append(HumanMessage(user_msg))
        chat_history.append(AIMessage(result))

    print("  Observation: The model correctly answers turns 2, 3, 4 using context.\n")


# ============================================================
# PART 3: Buffer Memory — Limit History to Last N Turns
# ============================================================
def buffer_memory_demo():
    """Show how to cap history at N turns to control token usage."""
    print("=== PART 3: Buffer Memory — Last N Turns Only ===\n")

    from langchain_core.messages import HumanMessage, AIMessage

    MAX_TURNS = 3  # keep only last 3 human+AI pairs

    def trim_history(history: list, max_turns: int) -> list:
        """Keep only the most recent max_turns pairs of messages."""
        max_messages = max_turns * 2  # each turn = 1 human + 1 AI message
        if len(history) > max_messages:
            return history[-max_messages:]
        return history

    # Simulate a long conversation history
    full_history = [
        HumanMessage("Turn 1 question"),   AIMessage("Turn 1 answer"),
        HumanMessage("Turn 2 question"),   AIMessage("Turn 2 answer"),
        HumanMessage("Turn 3 question"),   AIMessage("Turn 3 answer"),
        HumanMessage("Turn 4 question"),   AIMessage("Turn 4 answer"),
        HumanMessage("Turn 5 question"),   AIMessage("Turn 5 answer"),
    ]

    trimmed = trim_history(full_history, MAX_TURNS)

    print(f"  Full history: {len(full_history)} messages (5 turns)")
    print(f"  After trim (max {MAX_TURNS} turns): {len(trimmed)} messages\n")
    print("  Messages kept:")
    for i, msg in enumerate(trimmed):
        role = "Human" if isinstance(msg, HumanMessage) else "AI"
        print(f"    [{role}]: {msg.content}")
    print()
    print("  Use this trim() call before each chain.invoke() to control token cost.\n")


# ============================================================
# PART 4: Token Cost Awareness
# ============================================================
def token_cost_demo():
    """Show how history grows the token count over many turns."""
    print("=== PART 4: Token Cost — Why Memory Is Expensive ===\n")

    avg_tokens_per_turn = 150  # rough average (human + AI)
    system_tokens = 30

    print("  Approximate token count per request as conversation grows:\n")
    print("  ┌───────┬──────────────────┬───────────────────┐")
    print("  │ Turn  │ History tokens   │ Total in request  │")
    print("  ├───────┼──────────────────┼───────────────────┤")
    for turn in [1, 3, 5, 10, 20]:
        history_tokens = (turn - 1) * avg_tokens_per_turn
        total = system_tokens + history_tokens + avg_tokens_per_turn
        print(f"  │  {turn:3d}  │   {history_tokens:6d} tokens   │    {total:6d} tokens   │")
    print("  └───────┴──────────────────┴───────────────────┘\n")

    print("  Mistral free tier: ~500k tokens/month")
    print("  Turn 20 alone: ~3,000 tokens per request")
    print("  Recommendation: buffer at 5-10 turns for free-tier development.\n")


# ============================================================
# PART 5: Multi-Session Memory Pattern
# ============================================================
def multi_session_pattern():
    """Show how to save and restore history across sessions."""
    print("=== PART 5: Saving & Restoring History Across Sessions ===\n")

    import json
    from langchain_core.messages import HumanMessage, AIMessage

    def history_to_json(history: list) -> str:
        """Serialize chat history to JSON string for storage."""
        serialized = []
        for msg in history:
            serialized.append({
                "role": "human" if isinstance(msg, HumanMessage) else "ai",
                "content": msg.content,
            })
        return json.dumps(serialized, ensure_ascii=False, indent=2)

    def json_to_history(json_str: str) -> list:
        """Restore chat history from JSON string."""
        data = json.loads(json_str)
        history = []
        for item in data:
            if item["role"] == "human":
                history.append(HumanMessage(item["content"]))
            else:
                history.append(AIMessage(item["content"]))
        return history

    # Simulate session 1
    session1_history = [
        HumanMessage("My name is Bilel and I'm learning LangChain."),
        AIMessage("Great to meet you, Bilel! LangChain is a powerful framework."),
        HumanMessage("I'm based in Sfax."),
        AIMessage("Sfax is a great city! How can I help you with LangChain?"),
    ]

    # Save to JSON (would normally go to a database or file)
    saved = history_to_json(session1_history)
    print("  Saved history (JSON):")
    print(f"  {saved[:150]}...\n")

    # Restore in session 2
    restored = json_to_history(saved)
    print(f"  Restored: {len(restored)} messages")
    print(f"  First message: '{restored[0].content}'\n")
    print("  The user can close the app and reopen it — conversation continues seamlessly.")
    print("  Store this JSON in SQLite, Redis, or a file for persistent memory.\n")


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    show_no_memory_problem()
    manual_chat_history_demo()
    buffer_memory_demo()
    token_cost_demo()
    multi_session_pattern()

    print("--- Key Takeaways ---")
    print("1. LLMs are stateless — they forget everything between API calls")
    print("2. Fix: send the full conversation history in every request")
    print("3. Use MessagesPlaceholder in your template + grow a history list each turn")
    print("4. Always append: history.append(HumanMessage(msg)) + history.append(AIMessage(resp))")
    print("5. Trim history to last N turns to control token cost (MAX_TURNS = 5-10 is practical)")
    print("6. Serialize history to JSON → store in SQLite/file → restore next session")
