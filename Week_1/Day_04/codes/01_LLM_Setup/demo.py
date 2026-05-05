"""
01 - LangChain LLM Setup Demo
==============================
Learn how to connect LangChain to the Mistral API and make your first calls.
Understand the response object and the difference from raw HTTP calls.

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
# HELPER: Build the LangChain LLM client
# ============================================================
def get_llm(temperature: float = 0.7, max_tokens: int = 300):
    """Create a ChatOpenAI client pointing at Mistral's API."""
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        return None

    try:
        from langchain_openai.chat_models.base import BaseChatOpenAI
        return BaseChatOpenAI(
            model="mistral-small-latest",
            api_key=api_key,
            base_url="https://api.mistral.ai/v1",
            temperature=temperature,
            max_tokens=max_tokens,
        )
    except ImportError:
        print("  Install with: pip install langchain langchain-openai")
        return None


# ============================================================
# PART 1: Why LangChain? Raw vs LangChain
# ============================================================
def why_langchain():
    """Show the difference between raw HTTP calls and LangChain."""
    print("=== PART 1: Why LangChain? ===\n")

    print("  WITHOUT LangChain (what you did in Day 01-02):")
    print("""
    import httpx
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "mistral-small-latest",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user",   "content": "What is Python?"}
        ]
    }
    response = httpx.post(url, headers=headers, json=payload)
    text = response.json()["choices"][0]["message"]["content"]
    """)

    print("  WITH LangChain:")
    print("""
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage

    llm = ChatOpenAI(model="mistral-small-latest", api_key=key, base_url="https://api.mistral.ai/v1")
    response = llm.invoke([
        SystemMessage("You are a helpful assistant."),
        HumanMessage("What is Python?")
    ])
    text = response.content
    """)

    print("  Same result. LangChain's value appears when you start chaining steps together.\n")


# ============================================================
# PART 2: First LangChain Call
# ============================================================
def first_langchain_call():
    """Make the very first LangChain call to Mistral."""
    print("=== PART 2: First LangChain Call ===\n")

    llm = get_llm()
    if not llm:
        print("  [SIMULATED — set MISTRAL_API_KEY to see real responses]\n")
        print("  llm.invoke('En une phrase, c\\'est quoi LangChain?')")
        print("  → AIMessage(content='LangChain est un framework Python qui simplifie")
        print("    la création d\\'applications basées sur des modèles de langage...')\n")
        return

    print("  Calling: llm.invoke('En une phrase, c\\'est quoi LangChain?')\n")
    response = llm.invoke("En une phrase, c'est quoi LangChain?")
    print(f"  Response type: {type(response).__name__}")
    print(f"  response.content: {response.content}\n")


# ============================================================
# PART 3: The AIMessage Response Object
# ============================================================
def explore_response_object():
    """Understand everything inside the AIMessage response."""
    print("=== PART 3: The AIMessage Response Object ===\n")

    llm = get_llm(max_tokens=100)
    if not llm:
        print("  [SIMULATED — set MISTRAL_API_KEY to see real responses]\n")
        print("  response.content        → 'Tunis est la capitale de la Tunisie.'")
        print("  response.response_metadata → {'model_name': 'mistral-small-latest', ...}")
        print("  response.usage_metadata → {'input_tokens': 15, 'output_tokens': 9, 'total_tokens': 24}")
        print()
        print("  KEY: Always use response.content to get the plain text string.\n")
        return

    response = llm.invoke("Quelle est la capitale de la Tunisie? Réponds en une phrase.")

    print(f"  response.content:\n    {response.content}\n")

    if hasattr(response, "usage_metadata") and response.usage_metadata:
        print(f"  response.usage_metadata:")
        print(f"    input_tokens:  {response.usage_metadata.get('input_tokens', '?')}")
        print(f"    output_tokens: {response.usage_metadata.get('output_tokens', '?')}")
        print(f"    total_tokens:  {response.usage_metadata.get('total_tokens', '?')}\n")

    print("  KEY: Use response.content to get the plain text. The rest is metadata.\n")


# ============================================================
# PART 4: Passing Messages — SystemMessage + HumanMessage
# ============================================================
def messages_demo():
    """Show how to pass system and user messages to LangChain."""
    print("=== PART 4: SystemMessage + HumanMessage ===\n")

    try:
        from langchain_core.messages import SystemMessage, HumanMessage
    except ImportError:
        print("  Install with: pip install langchain\n")
        return

    llm = get_llm()

    system = SystemMessage("You are a tour guide specializing in Tunisia. Be concise and enthusiastic.")
    user = HumanMessage("What should I visit in Tunis in one day?")

    print("  Messages sent:")
    print(f"  SystemMessage: '{system.content[:60]}...'")
    print(f"  HumanMessage:  '{user.content}'\n")

    if not llm:
        print("  [SIMULATED — set MISTRAL_API_KEY to see real responses]\n")
        print("  Response: 'Start at the medina — a UNESCO World Heritage Site! Then Bardo")
        print("  Museum for world-class mosaics. End at Sidi Bou Said for sunset views. All")
        print("  within easy reach. Bon voyage!'\n")
        return

    response = llm.invoke([system, user])
    print(f"  Response: {response.content}\n")


# ============================================================
# PART 5: Temperature — Controlling Creativity
# ============================================================
def temperature_demo():
    """Show how temperature affects the model's output style."""
    print("=== PART 5: Temperature — Deterministic vs Creative ===\n")

    print("  temperature=0   → always the same, most likely answer (good for facts/code)")
    print("  temperature=0.7 → balanced — default for most chat apps")
    print("  temperature=1.0 → creative, varied, sometimes surprising\n")

    prompt = "Describe Tunisia in exactly 10 words."

    if not get_llm():
        print("  [SIMULATED — set MISTRAL_API_KEY to see real responses]\n")
        print("  temp=0.0: 'Tunisia is a North African country rich in history and culture.'")
        print("  temp=0.0: 'Tunisia is a North African country rich in history and culture.'  ← identical")
        print("  temp=1.0: 'Sun-drenched Tunisia blends ancient ruins with vibrant Mediterranean soul.'")
        print("  temp=1.0: 'Coastal gem where Sahara meets sea and ancient Carthage echoes.'  ← varied\n")
        return

    for temp in [0.0, 1.0]:
        llm = get_llm(temperature=temp, max_tokens=50)
        response = llm.invoke(prompt)
        print(f"  temp={temp}: {response.content}")
    print()


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    why_langchain()
    first_langchain_call()
    explore_response_object()
    messages_demo()
    temperature_demo()

    print("--- Key Takeaways ---")
    print("1. LangChain wraps raw API calls — less boilerplate, more composability")
    print("2. Use ChatOpenAI with base_url='https://api.mistral.ai/v1' to connect to Mistral")
    print("3. llm.invoke() returns an AIMessage object — use .content for the plain text")
    print("4. Pass [SystemMessage(...), HumanMessage(...)] to set role + user message")
    print("5. temperature=0 → deterministic | temperature=1 → creative")
    print("6. LangChain's value multiplies when you start chaining components together")
