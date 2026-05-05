"""
03 - LCEL Chains Demo
======================
Build LangChain pipelines using the | (pipe) operator.
Connect prompt templates, LLMs, and output parsers into reusable chains.

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
def get_llm(temperature: float = 0.7, max_tokens: int = 250):
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
# PART 1: The Simplest Chain — prompt | llm | parser
# ============================================================
def simplest_chain_demo():
    """Build and run the most basic LCEL chain."""
    print("=== PART 1: The Simplest Chain — prompt | llm | parser ===\n")

    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a concise assistant. Answer in one sentence."),
        ("human", "{question}"),
    ])
    parser = StrOutputParser()
    llm = get_llm(max_tokens=80)

    print("  Building the chain:")
    print("    chain = prompt | llm | StrOutputParser()\n")

    if not llm:
        print("  [SIMULATED — set MISTRAL_API_KEY to see real responses]\n")
        print("  chain.invoke({'question': 'What is LangChain?'})")
        print("  → 'LangChain is a Python framework for building applications")
        print("    powered by large language models.'\n")
        return

    chain = prompt | llm | parser

    result = chain.invoke({"question": "What is LangChain?"})
    print(f"  Input:  {{'question': 'What is LangChain?'}}")
    print(f"  Output: '{result}'\n")
    print("  Note: output is a plain string — not AIMessage — thanks to StrOutputParser\n")


# ============================================================
# PART 2: Chain with Multiple Variables
# ============================================================
def multi_variable_chain():
    """Chain with a template that has multiple input variables."""
    print("=== PART 2: Chain with Multiple Variables ===\n")

    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a {role}. Respond in {language}. Under 80 words."),
        ("human", "{question}"),
    ])

    llm = get_llm(max_tokens=120)

    if not llm:
        print("  [SIMULATED — set MISTRAL_API_KEY to see real responses]\n")
        print("  Input: role='food critic', language='English', question='Best Tunisian dish?'")
        print("  Output: 'The crown jewel is brik — a crispy pastry filled with egg, tuna,")
        print("  and harissa. Followed closely by slow-cooked lamb couscous on Fridays.'")
        print()
        print("  Input: role='history professor', language='French', question='Carthage en 3 mots?'")
        print("  Output: 'Puissance, Commerce, Tragédie.'")
        print()
        return

    chain = prompt | llm | StrOutputParser()

    test_cases = [
        {"role": "Tunisian food critic", "language": "English", "question": "What is the best Tunisian dish?"},
        {"role": "history professor",    "language": "French",  "question": "Décris Carthage en 3 mots."},
    ]

    for inputs in test_cases:
        result = chain.invoke(inputs)
        print(f"  Input: {inputs}")
        print(f"  Output: {result}\n")


# ============================================================
# PART 3: Streaming — Token by Token
# ============================================================
def streaming_chain_demo():
    """Stream chain output token by token."""
    print("=== PART 3: Streaming — Token by Token ===\n")

    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a storyteller. Tell vivid, short stories."),
        ("human",  "Tell me a 3-sentence story set in {location}."),
    ])

    llm = get_llm(max_tokens=150)

    if not llm:
        print("  [SIMULATED — set MISTRAL_API_KEY to see real responses]\n")
        print("  chain.stream({'location': 'the Medina of Tunis'})")
        print("  Streaming: ", end="", flush=True)
        story = "The narrow alleyways of the Medina whispered ancient secrets as Yasmine hurried past the spice vendors. The scent of jasmine and cardamom mingled in the warm evening air. She found the old door her grandmother had described — carved cedar, still standing after three hundred years."
        import time
        for word in story.split():
            print(word + " ", end="", flush=True)
            time.sleep(0.03)
        print("\n")
        return

    chain = prompt | llm | StrOutputParser()

    print("  Streaming: ", end="", flush=True)
    for chunk in chain.stream({"location": "the Medina of Tunis"}):
        print(chunk, end="", flush=True)
    print("\n")


# ============================================================
# PART 4: Batch Processing — Multiple Inputs at Once
# ============================================================
def batch_chain_demo():
    """Run a chain on multiple inputs in parallel."""
    print("=== PART 4: Batch Processing ===\n")

    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Translate to English. Return ONLY the translation, nothing else."),
        ("human", "{text}"),
    ])

    texts = [
        {"text": "Bonjour, comment ça va?"},
        {"text": "مرحبا، كيف حالك؟"},
        {"text": "Ciao, come stai?"},
    ]

    llm = get_llm(max_tokens=30)

    if not llm:
        print("  [SIMULATED — set MISTRAL_API_KEY to see real responses]\n")
        print("  chain.batch([3 inputs])")
        translations = ["Hello, how are you?", "Hello, how are you?", "Hello, how are you?"]
        for text_dict, trans in zip(texts, translations):
            print(f"  '{text_dict['text']}' → '{trans}'")
        print()
        return

    chain = prompt | llm | StrOutputParser()

    print(f"  Running batch with {len(texts)} inputs in parallel...")
    results = chain.batch(texts)

    for text_dict, result in zip(texts, results):
        print(f"  '{text_dict['text']}' → '{result.strip()}'")
    print()


# ============================================================
# PART 5: Multi-Step Chain — Chain Two LLM Calls
# ============================================================
def multi_step_chain_demo():
    """Chain two LLM calls: summarize then translate."""
    print("=== PART 5: Multi-Step Chain — Two LLM Calls ===\n")

    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.runnables import RunnablePassthrough

    summarize_prompt = ChatPromptTemplate.from_messages([
        ("system", "Summarize the following text in exactly 2 sentences."),
        ("human", "{text}"),
    ])

    translate_prompt = ChatPromptTemplate.from_messages([
        ("system", "Translate the following text to French. Return ONLY the translation."),
        ("human", "{summary}"),
    ])

    llm = get_llm(max_tokens=100)

    long_text = """Carthage was a powerful ancient city-state located in what is now Tunisia.
Founded by Phoenician settlers in the 9th century BC, it grew into one of the most
important trading centers of the ancient Mediterranean. The city controlled vast sea
trade routes and became the rival of Rome, leading to the three Punic Wars. The third
Punic War ended with Rome destroying Carthage completely in 146 BC."""

    print("  Pipeline: [Summarize in English] → [Translate to French]\n")
    print(f"  Input text (excerpt): '{long_text[:80]}...'\n")

    if not llm:
        print("  [SIMULATED — set MISTRAL_API_KEY to see real responses]\n")
        print("  After Step 1 (Summarize):")
        print("    'Carthage was a powerful Phoenician city in Tunisia that became Rome's")
        print("     greatest rival. It was completely destroyed after the third Punic War in 146 BC.'")
        print()
        print("  After Step 2 (Translate to French):")
        print("    'Carthage était une puissante cité phénicienne en Tunisie qui devint le")
        print("     principal rival de Rome. Elle fut entièrement détruite après la troisième")
        print("     guerre punique en 146 av. J.-C.'\n")
        return

    # Build each step as a sub-chain
    summarize_chain = summarize_prompt | llm | StrOutputParser()
    translate_chain = translate_prompt | llm | StrOutputParser()

    # Connect them: output of summarize goes into "summary" variable of translate
    full_chain = (
        {"summary": summarize_chain}
        | translate_prompt
        | llm
        | StrOutputParser()
    )

    # Step by step for clarity
    summary = summarize_chain.invoke({"text": long_text})
    print(f"  Step 1 — Summary:\n  '{summary}'\n")

    french = translate_chain.invoke({"summary": summary})
    print(f"  Step 2 — French translation:\n  '{french}'\n")


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    simplest_chain_demo()
    multi_variable_chain()
    streaming_chain_demo()
    batch_chain_demo()
    multi_step_chain_demo()

    print("--- Key Takeaways ---")
    print("1. LCEL chain = prompt | llm | parser — pipe operator connects components")
    print("2. chain.invoke(dict) → run once | chain.stream(dict) → token by token")
    print("3. chain.batch([list]) → run multiple inputs in parallel — fast for bulk tasks")
    print("4. StrOutputParser() converts AIMessage → plain string — always add it at the end")
    print("5. Multi-step chains: output of one chain becomes input of the next")
    print("6. LCEL replaces the old LLMChain — use it for all new code")
