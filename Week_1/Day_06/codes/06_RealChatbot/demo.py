"""
06 - Complete Chatbot Integration (All Days Concepts)
=====================================================
A production-ready chatbot that integrates ALL concepts from Days 1-6:

- Day 1: Basic chatbot foundation
- Day 2: Conversation management (ConversationBuffer)
- Day 3: Context extraction (ContextManager)
- Day 4: System prompts & personality (SystemPromptManager)
- Day 5: Multi-turn conversations with memory
- Day 6: Real API integration + interactive CLI

HOW TO RUN THIS FILE:
1. pip install langchain langchain-openai python-dotenv
2. Copy .env.example to .env and add your MISTRAL_API_KEY
3. python demo.py              # Start the chatbot (interactive)
"""

import os
from collections import deque
from datetime import datetime
from dotenv import load_dotenv

# LangChain's OpenAI-compatible client: points at Mistral's endpoint
from langchain_openai.chat_models.base import BaseChatOpenAI
# ChatPromptTemplate structures the messages; MessagesPlaceholder is a slot
# that gets filled with the conversation history at invoke time
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# StrOutputParser extracts the plain text string from the LLM's response object
from langchain_core.output_parsers import StrOutputParser
# LangChain's typed message wrappers — required by MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

# Load MISTRAL_API_KEY from the .env file into os.environ
load_dotenv()


# ============================================================
# COMPONENT 1: Conversation Buffer (Day 2 concept)
# ============================================================

class ConversationBuffer:
    """Stores all messages in chronological order."""

    def __init__(self, max_size=50):
        # deque with maxlen: when the 51st message is added, the oldest is
        # automatically removed. This keeps API token costs bounded.
        self.history = deque(maxlen=max_size)
        self.created_at = datetime.now()

    def add_message(self, role, content):
        """Add user or assistant message."""
        # Timestamp every message for display and analytics.
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now()
        })

    def get_history(self):
        """Get all messages as dicts."""
        # Convert to list so callers can index, slice, and pass to json.dumps.
        return list(self.history)

    def get_as_message_objects(self):
        """Convert history to LangChain message objects."""
        # LangChain's MessagesPlaceholder requires HumanMessage/AIMessage objects,
        # not plain dicts. This method bridges our internal dict format to LangChain's.
        messages = []
        for msg in self.history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))
        return messages

    def clear(self):
        """Clear conversation history."""
        self.history.clear()
        self.created_at = datetime.now()

    def __len__(self):
        return len(self.history)


# ============================================================
# COMPONENT 2: Context Manager (Day 3 concept)
# ============================================================

class ContextManager:
    """Extracts and tracks key facts from conversation."""

    def __init__(self):
        self.entities = {}       # Structured facts: {"user_name": "Bilel", "location": "Tunis"}
        self.preferences = []    # Raw messages where user stated what they want
        self.topics = set()      # Domains of interest: {"python", "machine learning"}
        self.turn_count = 0      # How many user messages have been analyzed

    def extract_from_message(self, message):
        """Extract entities, preferences, and topics."""
        content_lower = message.lower()
        self.turn_count += 1

        # ── Name extraction ──────────────────────────────────────────────────
        # Try two common patterns: "my name is X" and "I'm X"
        if "my name is" in content_lower or "i'm" in content_lower:
            words = content_lower.split()
            if "is" in words:
                idx = words.index("is")
                if idx + 1 < len(words):
                    # strip() removes trailing punctuation so "Bilel!" → "Bilel"
                    name = words[idx + 1].strip('.,!?')
                    self.entities['user_name'] = name.capitalize()
            elif "i'm" in content_lower:
                parts = content_lower.split("i'm")
                if len(parts) > 1:
                    name = parts[1].strip().split()[0].strip('.,!?')
                    self.entities['user_name'] = name.capitalize()

        # ── Location extraction ───────────────────────────────────────────────
        # Hardcoded list of Tunisian cities — simple but effective for this domain.
        # In production you'd use a geolocation NER model or a larger gazetteer.
        places = ['tunis', 'sfax', 'sousse', 'djerba', 'bizerte', 'kairouan', 'gafsa']
        for place in places:
            if place in content_lower:
                self.entities['location'] = place.capitalize()
                break  # Stop after the first match; one location per message is enough

        # ── Preference extraction ─────────────────────────────────────────────
        # Any message with an intent verb is a "preference" worth remembering.
        if any(word in content_lower for word in ["want", "need", "prefer", "like", "love"]):
            self.preferences.append(message)

        # ── Topic extraction ──────────────────────────────────────────────────
        # Map broad topic names to keyword lists.
        # set.add() is idempotent — adding the same topic twice has no effect.
        topics_map = {
            'python': ['python', 'code', 'programming', 'loop', 'list', 'function'],
            'machine learning': ['machine learning', 'ai', 'neural', 'model', 'data'],
            'web': ['web', 'javascript', 'html', 'css', 'react', 'api'],
            'general': ['help', 'learn', 'teach', 'understand'],
        }

        for topic, keywords in topics_map.items():
            if any(kw in content_lower for kw in keywords):
                self.topics.add(topic)

    def get_summary(self):
        """Return extracted context as formatted summary."""
        summary = []

        if self.entities:
            facts = []
            if 'user_name' in self.entities:
                facts.append(f"Name: {self.entities['user_name']}")
            if 'location' in self.entities:
                facts.append(f"Location: {self.entities['location']}")
            if facts:
                summary.append("Known facts: " + ", ".join(facts))

        if self.topics:
            # sorted() gives a consistent order so the summary doesn't change
            # between runs when topics are added in different orders.
            summary.append(f"Topics: {', '.join(sorted(self.topics))}")

        if self.preferences:
            summary.append(f"Preferences noted: {len(self.preferences)}")

        return "\n".join(summary) if summary else "No context extracted yet"

    def reset(self):
        """Clear all extracted context."""
        self.entities.clear()
        self.preferences.clear()
        self.topics.clear()
        self.turn_count = 0


# ============================================================
# COMPONENT 3: System Prompt Manager (Day 4 concept)
# ============================================================

class SystemPromptManager:
    """Manages chatbot personality and behavior constraints."""

    def __init__(self, name="El Mokh", role="helpful assistant", tone="warm"):
        self.name = name
        self.role = role
        self.tone = tone
        # Default constraints apply to every conversation.
        # They can be added to or removed per use case.
        self.constraints = [
            "Keep responses concise (under 150 words)",
            "Be helpful and empathetic",
            "Reference user context when possible",
            "Admit when you don't know something",
        ]

    def get_system_prompt(self):
        """Generate the system prompt."""
        # Built on demand so changes to role/tone are immediately reflected.
        prompt = f"You are {self.name}, a {self.role}.\n"
        prompt += f"Your tone is {self.tone}.\n"
        prompt += "Instructions:\n"
        for constraint in self.constraints:
            prompt += f"- {constraint}\n"
        return prompt

    def set_personality(self, role, tone):
        """Change personality dynamically."""
        # Only stores the new values; the chain must be rebuilt separately
        # (handled by CompleteChatbot.change_personality) to pick up the change.
        self.role = role
        self.tone = tone

    def add_constraint(self, constraint):
        """Add a custom constraint."""
        # Guard against duplicates so re-adding a constraint has no side effect.
        if constraint not in self.constraints:
            self.constraints.append(constraint)

    def remove_constraint(self, constraint):
        """Remove a constraint."""
        if constraint in self.constraints:
            self.constraints.remove(constraint)


# ============================================================
# COMPONENT 4: LangChain Bridge (Day 6 concept)
# ============================================================

class LangChainBridge:
    """Creates and manages the LangChain chain for API calls."""

    def __init__(self, system_prompt, api_key=None):
        self.api_key = api_key
        self.system_prompt = system_prompt
        self.chain = None   # None means simulation mode (no API key)
        self.llm = None
        self._build_chain()

    def _build_chain(self):
        """Build the LangChain prompt + LLM + parser chain."""
        if not self.api_key:
            # No key → leave chain as None; invoke() will return simulated text.
            return

        # BaseChatOpenAI works with any OpenAI-compatible endpoint.
        # Mistral exposes the same API format at a different base_url.
        self.llm = BaseChatOpenAI(
            model="mistral-small-latest",
            api_key=self.api_key,
            base_url="https://api.mistral.ai/v1",
            temperature=0.7,    # 0 = deterministic, 1 = more creative
            max_tokens=300,     # Cap response length to keep chats snappy
        )

        # The prompt template has three slots:
        # 1. ("system", ...) — fixed personality instructions
        # 2. MessagesPlaceholder — injected with the conversation history at invoke time
        # 3. ("human", "{user_input}") — the current user message
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{user_input}")
        ])

        # LCEL pipe operator: prompt → llm → parser, executed left to right.
        # prompt.invoke() formats messages, llm.invoke() calls Mistral,
        # StrOutputParser.invoke() extracts the text string from the response object.
        self.chain = prompt | self.llm | StrOutputParser()

    def invoke(self, history, user_input):
        """Call the LLM with history and user input."""
        if not self.chain:
            # Simulation mode: return a placeholder so the app still runs
            # and students can see the architecture working without an API key.
            return f"[{self.system_prompt.split(',')[0]} response to: {user_input[:50]}...]"

        try:
            response = self.chain.invoke({
                "history": history,      # List of HumanMessage/AIMessage objects
                "user_input": user_input # The latest user message as plain text
            })
            return response
        except Exception as e:
            # Surface the error message so the user knows what went wrong
            # (wrong API key, rate limit, network issue, etc.).
            return f"[API Error: {str(e)[:60]}]"

    def is_live(self):
        """Check if real API is connected."""
        # chain is None when no API key was provided.
        return self.chain is not None


# ============================================================
# COMPONENT 5: Complete Chatbot Orchestrator
# ============================================================

class CompleteChatbot:
    """
    Production chatbot integrating ALL Day 1-6 concepts:
    - Buffer: conversation history management
    - Context: entity/topic extraction
    - Prompts: personality and constraints
    - Chain: LangChain + real API
    - Architecture: orchestrated message flow
    """

    def __init__(self, name="El Mokh", api_key=None):
        self.name = name
        self.api_key = api_key  # Stored so we can rebuild the bridge on personality change

        # Create each component independently — they have no direct references to each other.
        # The orchestrator (this class) is the only glue between them.
        self.buffer = ConversationBuffer(max_size=50)
        self.context = ContextManager()
        self.prompt_mgr = SystemPromptManager(
            name=name,
            role="friendly Tunisian AI assistant",
            tone="warm, helpful, encouraging"
        )
        self.bridge = LangChainBridge(
            system_prompt=self.prompt_mgr.get_system_prompt(),
            api_key=api_key
        )
        self.turn_count = 0

    def chat(self, user_input):
        """
        Main pipeline (Day 6 architecture):
        Input → Validate → Buffer → Context → History → API → Store → Return
        """
        # Step 1: Validate — reject empty or whitespace-only input before
        # it reaches the buffer or the API.
        if not user_input or not user_input.strip():
            return "Please enter a message."

        user_input = user_input.strip()

        # Step 2: Store user message in the buffer so it's part of history.
        self.buffer.add_message("user", user_input)

        # Step 3: Extract context from the user's words.
        # This runs silently on every turn — the chatbot "learns" passively.
        self.context.extract_from_message(user_input)

        # Step 4: Build the history to send to the LLM.
        # [:-1] skips the last item (the user message we JUST added) because
        # the LangChain prompt already injects it via the "{user_input}" slot.
        # Sending it twice would confuse the model.
        history = self.buffer.get_as_message_objects()[:-1]

        # Step 5: Call the real API (or simulate if no key).
        response = self.bridge.invoke(history, user_input)

        # Step 6: Store the assistant's response so the next turn includes it.
        self.buffer.add_message("assistant", response)

        # Step 7: Increment turn counter for display/analytics.
        self.turn_count += 1

        return response

    def show_conversation(self):
        """Display formatted conversation."""
        if not self.buffer.get_history():
            print("\n[No conversation yet]\n")
            return

        print(f"\n{'='*60}")
        print(f"Conversation with {self.name} ({len(self.buffer)} messages)")
        print(f"{'='*60}\n")

        for msg in self.buffer.get_history():
            timestamp = msg['timestamp'].strftime("%H:%M:%S")
            role = msg['role'].upper()
            content = msg['content']
            print(f"[{timestamp}] {role}: {content}\n")

    def show_context(self):
        """Display extracted context."""
        print(f"\n{'='*60}")
        print("Extracted Context")
        print(f"{'='*60}\n")
        print(self.context.get_summary())
        print(f"\nTurns analyzed: {self.context.turn_count}\n")

    def show_status(self):
        """Display chatbot status."""
        api_status = "🔴 SIMULATED (no API key)" if not self.bridge.is_live() else "🟢 LIVE API"
        print(f"\n{'='*60}")
        print(f"Chatbot: {self.name}")
        print(f"Status:  {api_status}")
        print(f"Role:    {self.prompt_mgr.role}")
        print(f"Tone:    {self.prompt_mgr.tone}")
        print(f"Messages in buffer: {len(self.buffer)}")
        print(f"Turns:   {self.turn_count}")
        print(f"{'='*60}\n")

    def reset(self):
        """Clear conversation and context."""
        self.buffer.clear()
        self.context.reset()
        self.turn_count = 0
        print(f"\n✓ Conversation reset\n")

    def change_personality(self, role, tone):
        """Change chatbot personality and rebuild the LangChain chain."""
        self.prompt_mgr.set_personality(role, tone)
        # The bridge must be re-created because the system prompt changed.
        # The old chain still has the old system prompt baked in — it won't update
        # automatically just because we changed prompt_mgr's attributes.
        self.bridge = LangChainBridge(
            system_prompt=self.prompt_mgr.get_system_prompt(),
            api_key=self.api_key
        )
        print(f"\n✓ Personality changed: {role}, {tone}\n")


# ============================================================
# INTERACTIVE CLI
# ============================================================

class InteractiveCLI:
    """Interactive command-line interface for the chatbot."""

    COMMANDS = {
        'help': 'Show this help message',
        'status': 'Show chatbot status',
        'history': 'Show conversation history',
        'context': 'Show extracted context',
        'reset': 'Clear conversation',
        'personality [role] [tone]': 'Change personality (e.g., "personality mentor encouraging")',
        'quit': 'Exit chat',
    }

    def __init__(self, chatbot):
        self.chatbot = chatbot

    def run(self):
        """Start interactive chat loop."""
        print(f"\n{'='*60}")
        print(f"  Chat with {self.chatbot.name}")
        print(f"{'='*60}")
        self.chatbot.show_status()
        print("Type 'help' for commands, 'quit' to exit.\n")

        while True:
            try:
                # input() blocks until the user presses Enter.
                # .strip() removes accidental leading/trailing spaces.
                user_input = input("You: ").strip()

                if not user_input:
                    continue  # Skip empty Enter presses without printing anything

                # ── Command routing ───────────────────────────────────────────
                # Check for commands before sending to the chatbot so users can
                # inspect state at any point without it appearing in the chat history.

                if user_input.lower() == 'help':
                    self._show_help()
                    continue

                if user_input.lower() == 'status':
                    self.chatbot.show_status()
                    continue

                if user_input.lower() == 'history':
                    self.chatbot.show_conversation()
                    continue

                if user_input.lower() == 'context':
                    self.chatbot.show_context()
                    continue

                if user_input.lower() == 'reset':
                    self.chatbot.reset()
                    continue

                if user_input.lower().startswith('personality '):
                    self._change_personality(user_input)
                    continue

                if user_input.lower() == 'quit':
                    print(f"\n{self.chatbot.name}: Goodbye!\n")
                    break

                # ── Regular chat ──────────────────────────────────────────────
                response = self.chatbot.chat(user_input)
                print(f"{self.chatbot.name}: {response}\n")

            except KeyboardInterrupt:
                # Ctrl+C is treated the same as "quit" — clean exit.
                print(f"\n\n{self.chatbot.name}: Goodbye!\n")
                break
            except Exception as e:
                # Catch-all so a single bad message doesn't kill the entire session.
                print(f"Error: {e}\n")

    def _show_help(self):
        """Display available commands."""
        print("\n" + "="*60)
        print("COMMANDS")
        print("="*60)
        for cmd, desc in self.COMMANDS.items():
            # Left-justify each command to 30 chars so descriptions line up.
            print(f"  {cmd:<30} - {desc}")
        print("="*60 + "\n")

    def _change_personality(self, command):
        """Parse and apply personality change."""
        # Expected format: "personality <role> <tone>"
        # parts[0] = "personality", parts[1] = role, parts[2:] = tone (can be multi-word)
        parts = command.split()
        if len(parts) >= 3:
            role = parts[1]
            tone = " ".join(parts[2:])  # Join remaining words in case tone has spaces
            self.chatbot.change_personality(role, tone)
        else:
            print("Usage: personality [role] [tone]\n")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    # Read API key from .env file (loaded at the top by load_dotenv()).
    # If the key is missing, CompleteChatbot runs in simulation mode automatically.
    api_key = os.getenv("MISTRAL_API_KEY")

    chatbot = CompleteChatbot(name="El Mokh", api_key=api_key)
    cli = InteractiveCLI(chatbot)
    cli.run()
