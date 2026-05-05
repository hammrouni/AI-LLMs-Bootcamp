# 05 - Mini Chatbot — Putting It All Together

---

## 📦 Packages

```bash
pip install langchain langchain-openai python-dotenv
```

---

## What We're Building

A complete conversational chatbot that combines everything from Day 4:

```
[User types a message]
        ↓
[ChatPromptTemplate]  ← system prompt + history + user input
        ↓
[BaseChatOpenAI → Mistral]  ← LCEL chain
        ↓
[StrOutputParser]  ← extract plain text
        ↓
[Update chat_history]  ← append human + AI messages
        ↓
[Display response]
        ↓
[Loop — wait for next input]
```

---

## The Architecture

```python
# 1. Prompt template with system persona + history slot + user input
prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder("chat_history"),
    ("human", "{user_input}"),
])

# 2. LCEL chain
chain = prompt | llm | StrOutputParser()

# 3. State: growing history list
chat_history = []

# 4. Conversation loop
while True:
    user_input = input("You: ")
    if user_input.lower() in ("exit", "quit", "q"):
        break

    response = chain.invoke({
        "chat_history": trim(chat_history),
        "user_input": user_input,
    })

    print(f"Bot: {response}")
    chat_history.append(HumanMessage(user_input))
    chat_history.append(AIMessage(response))
```

---

## What Makes a Good Chatbot System Prompt?

The system prompt is what gives your chatbot its personality and constraints. For a well-behaved chatbot:

```
You are [NAME], a [ROLE].

Your expertise: [WHAT YOU KNOW]
Your job: [WHAT YOU DO FOR THE USER]

Rules:
- [CONSTRAINT 1]
- [CONSTRAINT 2]

Format:
- Keep responses concise — under [N] words.
- [OTHER FORMAT RULES]
```

**Example — a Tunisian tourism assistant:**
```
You are Leila, a friendly Tunisian tourism expert.

You help visitors discover Tunisia's best experiences: historical sites,
food, culture, beaches, and practical travel tips.

Rules:
- Only answer questions about Tunisia and travel.
- If asked about unrelated topics, politely redirect.
- Always be warm and enthusiastic about Tunisian culture.

Format: Keep answers under 100 words. Use bullet points for lists.
```

---

## Streaming in a Chatbot

For a better user experience, stream responses instead of waiting for the full reply:

```python
# Without streaming — user waits 3-5 seconds, then sees everything at once
response = chain.invoke({"chat_history": ..., "user_input": ...})
print(f"Bot: {response}")

# With streaming — text appears immediately, one token at a time
print("Bot: ", end="", flush=True)
full_response = ""
for chunk in chain.stream({"chat_history": ..., "user_input": ...}):
    print(chunk, end="", flush=True)
    full_response += chunk
print()
```

Streaming is especially important for long answers (e.g., explaining code, writing stories).

---

## Special Commands in a Chatbot

Production chatbots often support meta-commands:

```python
if user_input.lower() == "/clear":
    chat_history = []
    print("Chat history cleared.")
    continue

if user_input.lower() == "/history":
    print(f"History: {len(chat_history)} messages")
    continue

if user_input.lower() in ("exit", "quit", "/q"):
    break
```

---

## What's Next After This Chatbot?

This chatbot covers the Day 4 fundamentals. In real applications, you'd add:

| Feature | Tool | Covered in |
|---|---|---|
| Connect to your own documents | LlamaIndex / RAG | Day 5 |
| Persistent memory across restarts | SQLite / Redis | Day 6-7 |
| LLM agents that use tools | LangChain Agents | Advanced |
| Web interface | Streamlit / FastAPI | Beyond Week 1 |
