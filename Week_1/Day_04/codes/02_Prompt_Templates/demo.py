"""
02 - Prompt Templates Demo
===========================
Learn how to build reusable, parameterized prompts with LangChain's
ChatPromptTemplate — the foundation of every LangChain pipeline.

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
# PART 1: The Problem Without Templates
# ============================================================
def problem_without_templates():
    """Show why hardcoded prompts are a maintenance nightmare."""
    print("=== PART 1: The Problem Without Templates ===\n")

    print("  Yasmine is building a translation tool. Without templates:")
    print("""
    # Request 1
    prompt1 = "Translate 'bonjour' from French to English."
    # Request 2
    prompt2 = "Translate 'merci' from French to Spanish."
    # Request 3 — Yasmine changed the instruction slightly by accident
    prompt3 = "Translate 'au revoir' from French into German language."
    #                                            ^^^^^^^^^^^^^^^^^^^^^ inconsistent!
    """)
    print("  3 prompts, 3 slight variations in wording → inconsistent AI behavior.")
    print("  With 100 translations, this becomes a disaster.\n")
    print("  Solution: ONE template, consistent every time.\n")


# ============================================================
# PART 2: PromptTemplate — Simple Variable Substitution
# ============================================================
def prompt_template_demo():
    """Basic PromptTemplate with variables."""
    print("=== PART 2: PromptTemplate — Simple Variables ===\n")

    from langchain_core.prompts import PromptTemplate

    template = PromptTemplate.from_template(
        "Write a {length} description of {topic} suitable for {audience}."
    )

    print(f"  Template: '{template.template}'")
    print(f"  Variables: {template.input_variables}\n")

    test_cases = [
        {"length": "one-sentence", "topic": "the Medina of Tunis",   "audience": "tourists"},
        {"length": "two-sentence", "topic": "couscous",               "audience": "children"},
        {"length": "one-sentence", "topic": "the Bardo Museum",       "audience": "art lovers"},
    ]

    for i, values in enumerate(test_cases, 1):
        filled = template.format(**values)
        print(f"  Case {i}: {filled}")
    print()


# ============================================================
# PART 3: ChatPromptTemplate — System + User Messages
# ============================================================
def chat_prompt_template_demo():
    """ChatPromptTemplate with system and human messages."""
    print("=== PART 3: ChatPromptTemplate — System + Human Messages ===\n")

    from langchain_core.prompts import ChatPromptTemplate

    template = ChatPromptTemplate.from_messages([
        ("system", "You are a {role}. Answer in {language}. Be {tone}."),
        ("human",  "{question}"),
    ])

    print(f"  Input variables: {template.input_variables}\n")

    values = {
        "role": "Tunisian history expert",
        "language": "English",
        "tone": "concise and enthusiastic",
        "question": "What made Carthage so powerful in the ancient world?",
    }

    messages = template.format_messages(**values)
    print("  Formatted messages:")
    for msg in messages:
        msg_type = type(msg).__name__
        print(f"    [{msg_type}]: {msg.content[:70]}...")
    print()

    llm = get_llm()
    if not llm:
        print("  [SIMULATED — set MISTRAL_API_KEY to see real responses]\n")
        print("  Response: 'Carthage dominated Mediterranean trade for centuries thanks")
        print("  to its legendary navy, skilled merchants, and strategic location in")
        print("  modern-day Tunisia. At its peak, it rivaled Rome itself!'\n")
        return

    response = llm.invoke(messages)
    print(f"  Response: {response.content}\n")


# ============================================================
# PART 4: Partial Templates — Pre-fill Fixed Variables
# ============================================================
def partial_templates_demo():
    """Pre-fill some variables, leave others dynamic."""
    print("=== PART 4: Partial Templates — Pre-fill Fixed Values ===\n")

    from langchain_core.prompts import ChatPromptTemplate

    base = ChatPromptTemplate.from_messages([
        ("system", "You are a {role} assistant. Always respond in {language}. Keep answers under 60 words."),
        ("human",  "{question}"),
    ])

    # Fix the role and language once — reuse for many questions
    arabic_assistant = base.partial(role="helpful", language="French")

    questions = [
        "Qu'est-ce que LangChain?",
        "Comment fonctionne le Prompt Engineering?",
    ]

    print("  Base template has 3 variables: role, language, question")
    print("  After partial(role='helpful', language='French'), only 'question' remains.\n")

    llm = get_llm()
    for q in questions:
        messages = arabic_assistant.format_messages(question=q)
        print(f"  Q: {q}")

        if not llm:
            print("  [SIMULATED — set MISTRAL_API_KEY to see real responses]")
            print("  A: [réponse en français...]\n")
            continue

        response = llm.invoke(messages)
        print(f"  A: {response.content}\n")


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    problem_without_templates()
    prompt_template_demo()
    chat_prompt_template_demo()
    partial_templates_demo()

    print("--- Key Takeaways ---")
    print("1. PromptTemplate = reusable prompt with {variable} placeholders")
    print("2. Always use ChatPromptTemplate for chat models — supports system + human messages")
    print("3. from_messages([('system', ...), ('human', ...)]) is the standard pattern")
    print("4. template.input_variables shows all placeholders auto-detected by LangChain")
    print("5. partial() pre-fills fixed variables — useful for app-wide settings like language")
