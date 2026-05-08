# 03 - Advanced Personality Design (Building on Day 06's Personality)

---

## What You Had in Day 06

In **Day 06's RealChatbot**, you implemented **basic personality design** via `SystemPromptManager`:

```python
# Day 06: Static personality defined in system prompt
prompt_mgr = SystemPromptManager(
    name="Ramy",
    role="friendly Tunisian AI assistant",
    tone="warm, helpful, encouraging"
)
```

The system prompt worked great—same personality for all conversations.

---

## What is Advanced Personality Design?

**Advanced Personality Design** goes beyond static system prompts. The chatbot **learns and adapts** personality based on:

1. **User's communication style** — If user is technical, be technical. If casual, be casual.
2. **Conversation context** — Different personalities for support vs learning vs creative work
3. **User preferences** — Learn if user likes humor, detail, or brevity
4. **Multi-turn adaptation** — Adjust personality mid-conversation based on how user responds

---

## What is the Problem?

### Static Personality Doesn't Adapt

```
All conversations → Same "Ramy" personality
User 1 (technical): Gets warm & friendly
User 2 (frustrated): Gets warm & friendly
Result: Personality doesn't fit the context
```

Same personality ≠ right personality for the job.

---

## What is the Solution? Adaptive Personality!

### Day 07's Approach (Dynamic)

```
User 1 (technical, fast-paced) → Become concise & technical
User 2 (confused, needs help) → Become patient & detailed
User 3 (creative brainstorm) → Become enthusiastic & exploratory

Same bot, different personalities based on context.
```

---

## How It Works in Python

### Part 1: Detect User Style from Behavior

```python
class PersonalityAdapter:
    def __init__(self):
        self.user_style = {
            "is_technical": False,
            "prefers_detail": True,
            "likes_humor": False,
            "patience_level": "medium"
        }
    
    def detect_style_from_message(self, user_message):
        # Analyze user's message to infer their style
        # Technical indicators: "API", "syntax", "database", "algorithm"
        # Casual indicators: "please", "thanks", "can u help"
        # Humor indicators: emojis, jokes, sarcasm
        
        words = user_message.lower().split()
        
        # Is user technical?
        technical_words = {"api", "database", "syntax", "algorithm", "function", "variable"}
        self.user_style["is_technical"] = bool(set(words) & technical_words)
        
        # Does user want detail?
        detail_words = {"explain", "detailed", "how", "why", "deep"}
        self.user_style["prefers_detail"] = bool(set(words) & detail_words)
        
        # Does user use casual language?
        casual_words = {"lol", "btw", "haha", "thanks", "plz"}
        self.user_style["likes_humor"] = bool(set(words) & casual_words)
```

### Part 2: Generate Personality Based on Style

```python
def build_adaptive_system_prompt(self):
    """Generate system prompt that matches user's detected style."""
    
    base = "You are Ramy, a Tunisian AI assistant."
    
    if self.user_style["is_technical"]:
        tone = "technical, precise, direct"
        style = "Use terminology accurately. No fluff."
    else:
        tone = "approachable, simple, encouraging"
        style = "Explain in plain language. Use examples."
    
    if self.user_style["prefers_detail"]:
        detail = "Provide comprehensive explanations with examples."
    else:
        detail = "Be concise. Get to the point quickly."
    
    if self.user_style["likes_humor"]:
        personality = "Occasional light humor is OK."
    else:
        personality = "Keep it professional."
    
    return f"""
{base}
Tone: {tone}
{style}
{detail}
{personality}
"""
```

### Part 3: Adapt System Prompt Per Turn

```python
class AdaptiveCompleteChatbot:
    def __init__(self, name="Ramy", api_key=None):
        self.chatbot = CompleteChatbot(name, api_key)  # Day 06's base
        self.adapter = PersonalityAdapter()
    
    def chat(self, user_input):
        # Step 1: Detect user style
        self.adapter.detect_style_from_message(user_input)
        
        # Step 2: Generate adaptive system prompt
        adaptive_prompt = self.adapter.build_adaptive_system_prompt()
        
        # Step 3: Update chatbot's system prompt dynamically
        self.chatbot.prompt_mgr.custom_system_prompt = adaptive_prompt
        
        # Step 4: Get response (using adapted personality)
        response = self.chatbot.chat(user_input)
        return response
```

---

## Real-World Example

```
User sends: "What's a list in Python?"
→ Detected: NOT technical, wants detail
→ System prompt: "Explain in simple language with examples"
→ Response: "A list is like a container... Think of a shopping list..."

User sends: "Implement quicksort algorithm"
→ Detected: VERY technical, wants code
→ System prompt: "Use technical terminology. Provide code."
→ Response: "Quicksort uses divide-and-conquer. Time complexity: O(n log n)..."

Same bot, different personalities.
```

---

## Advanced Patterns

### 1. Multi-Context Personalities

```python
if "bug" in user_input.lower():
    mode = "debugging_assistant"  # Become systematic, methodical
elif "learn" in user_input.lower():
    mode = "mentor"  # Become patient, encouraging
elif "creative" in user_input.lower():
    mode = "brainstorm_partner"  # Become exploratory, enthusiastic
```

### 2. User Preference Learning (Stored in Database)

```python
# Save user's detected style in DB so it persists
db.save_user_profile(user_id, {
    "preferred_tone": "technical",
    "prefers_brief": True,
    "likes_examples": False,
    "communication_style": "formal"
})

# Next session, load and use immediately
profile = db.get_user_profile(user_id)
adapter.user_style = profile["style"]
```

### 3. Gradual Adaptation (Learn Over Time)

```python
def learn_from_feedback(self, user_id, message_id, feedback):
    """User can rate a response as 'too brief', 'too technical', etc."""
    # Adjust personality based on feedback
    # Over time, personality converges to what user likes
    
    if feedback == "too_technical":
        self.user_style["is_technical"] = False
    elif feedback == "too_brief":
        self.user_style["prefers_detail"] = True
```

---

## Why This Matters

**Advanced personality** beats static personality because:
- 🎯 **Relevance**: Personality fits the job (support vs learning vs creative)
- 💬 **User satisfaction**: Bot feels like it "gets" the user
- 📈 **Retention**: Users come back because bot feels personal
- 🧠 **Learning**: Bot improves over time, remembers preferences
- 🚀 **Scale**: Same architecture serves hundreds of users with different needs

---
