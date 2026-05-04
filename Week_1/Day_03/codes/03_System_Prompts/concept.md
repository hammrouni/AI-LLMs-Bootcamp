# 03 - System Prompts

---

## 📦 Packages

```bash
pip install openai python-dotenv
```

---

## What is a System Prompt?

In a conversation with an AI, there are two types of messages:

| Message type | Who sends it | What it does |
|---|---|---|
| **System prompt** | YOU (the developer) | Sets the AI's role, personality, rules, and constraints |
| **User message** | The end user | The actual question or task |

The system prompt is like a **job description** you hand to an employee before they start work. It defines:
- Who they are (role/persona)
- What they can and cannot do (constraints)
- How they should respond (format/tone)
- What they should focus on (context)

---

## Why System Prompts Matter

Without a system prompt, the AI is a generalist — it will do anything. With a system prompt, you shape it into a specialist.

**Same question, completely different behavior:**

```
User question: "Tell me about the Roman ruins."

Without system prompt:
→ A general description of Roman history and architecture worldwide.

With system prompt: "You are a tour guide for the Carthage archaeological site in Tunisia."
→ A focused, local guide response about Carthage's ruins, visitor tips, hours, nearby sites.

With system prompt: "You are a children's educator. Explain things simply, use fun analogies."
→ "Imagine Carthage was like a really big, busy city — like Tunis today but 2,000 years ago!"
```

---

## The Four Pillars of a System Prompt

### 1. Role / Persona
Who is the AI in this conversation?

```
"You are a senior Python developer with 10 years of experience."
"You are a friendly customer support agent for TunisAir."
"You are a Tunisian recipe expert specializing in traditional home cooking."
```

### 2. Task / Focus
What should the AI focus on? What is out of scope?

```
"Your job is to help users debug their Python code."
"Only answer questions about our product catalog — nothing else."
"You specialize in explaining AI concepts to complete beginners."
```

### 3. Constraints / Rules
What must the AI never do?

```
"Never reveal confidential pricing information."
"Always recommend consulting a doctor for medical decisions."
"Do not discuss competitors. If asked, politely redirect."
"Respond only in French, regardless of what language the user writes in."
```

### 4. Format / Style
How should responses be structured?

```
"Keep all responses under 3 sentences."
"Always use bullet points for lists."
"End every response with a follow-up question."
"Use a warm, encouraging tone — never be harsh or critical."
```

---

## System Prompt vs User Message vs Few-Shot

These three techniques solve different problems:

| Technique | Best for |
|---|---|
| System prompt | Persistent behavior across all messages (role, tone, rules) |
| Few-shot examples | Teaching a specific input→output format |
| Chain of Thought | Improving reasoning quality on hard problems |

Use all three together for maximum control:
1. System prompt → sets who the AI is
2. Few-shot examples → shows the format you want
3. CoT trigger → improves reasoning quality

---

## Anatomy of a Strong System Prompt

```
You are [ROLE].

Your job is to [TASK].

Rules:
- [CONSTRAINT 1]
- [CONSTRAINT 2]
- [CONSTRAINT 3]

Format:
- [FORMAT RULE 1]
- [FORMAT RULE 2]

Context: [ANY EXTRA CONTEXT THE MODEL NEEDS]
```

**Example for a coding assistant:**
```
You are an expert Python developer and code reviewer.

Your job is to help users write clean, efficient Python code and debug issues.

Rules:
- Always explain WHY something is wrong, not just what to fix.
- If the user's approach is fundamentally flawed, suggest a better approach.
- Never write code that introduces security vulnerabilities.
- If you are not sure about something, say so clearly.

Format:
- Use code blocks for all code snippets.
- Keep explanations short and focused — no unnecessary preamble.
- If fixing a bug, show the broken code and the fixed code side by side.
```

---

## Common Mistakes with System Prompts

### ❌ Too vague
```
"Be helpful."  ← meaningless — the model is always helpful by default
```

### ❌ Too long / contradictory
```
"Be concise. Always give comprehensive answers. Never skip details. Keep it short."
← model gets confused about what "concise" means
```

### ❌ No constraints
```
"You are a customer service agent."
← without constraints, the agent will answer anything, including competitor questions
```

### ✅ Specific + constrained + formatted
```
"You are a customer service agent for Maghreb Telecom.
Only answer questions about our plans, billing, and technical support.
If a customer asks about competitors, say: 'I can only help with Maghreb Telecom services.'
Keep answers under 100 words. Use a friendly, professional tone."
```
