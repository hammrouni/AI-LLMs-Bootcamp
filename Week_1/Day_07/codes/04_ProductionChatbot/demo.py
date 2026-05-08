"""
04 - Production Chatbot (Day 07 Capstone)
==========================================
Day 06 chatbot + all Day 07 upgrades working together.

DAY 06 foundation (carried over unchanged):
  ConversationBuffer  -- in-memory deque for the active session
  ContextManager      -- extracts entities/topics per message
  SystemPromptManager -- base personality template
  LangChainBridge     -- real Mistral API via LangChain LCEL

DAY 07 additions (new):
  ChatDatabase        -- SQLite: conversations survive app restarts
  PersonalityAdapter  -- detects user style, adjusts prompt each turn
  InputValidator      -- length + content checks before API call
  ErrorBoundary       -- wraps API call with graceful fallback

HOW TO RUN:
  pip install langchain langchain-openai python-dotenv
  Copy .env.example to .env and set MISTRAL_API_KEY
  python demo.py

COMMANDS (in chat):
  status      -- show chatbot status
  history     -- show active session messages
  dbhistory   -- show full database history (all past sessions)
  context     -- show extracted context + detected style
  reset       -- clear session (database history preserved)
  personality [role] [tone]
  help / quit
"""

import os       # read MISTRAL_API_KEY from environment
import sys      # reconfigure stdout encoding for Windows
import sqlite3  # built-in database — no install needed
import logging  # structured logs for debugging
from collections import deque   # fixed-size list that auto-removes oldest item
from datetime import datetime   # timestamps on every message

# Force UTF-8 output so emojis and Arabic characters print correctly on Windows.
# Without this, Windows uses cp1252 which crashes on any non-Latin character.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# python-dotenv reads MISTRAL_API_KEY from a .env file into os.environ.
# The try/except means the app still runs if the package is not installed —
# it just won't find the key (simulation mode activates instead).
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# LangChain turns the Mistral API into a simple Python call.
# If LangChain is not installed we set a flag and fall back to simulation.
# This way the code runs for every student regardless of their setup.
try:
    from langchain_openai.chat_models.base import BaseChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.messages import HumanMessage, AIMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# Configure logging once at module level.
# Every class uses logger.info / logger.error so we have a single trail
# of what happened and when — essential for debugging in production.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================
# DAY 06 COMPONENTS (unchanged from Day 06)
# ============================================================

class ConversationBuffer:
    """
    Stores the active conversation in memory. (Day 06)

    WHY deque instead of list?
    A list grows forever. A deque(maxlen=20) automatically drops the oldest
    message when the 21st arrives — so API calls never exceed the token limit.
    """

    def __init__(self, max_size=20):
        # maxlen=20 means the buffer holds at most 20 messages.
        # When full, appending a new message silently removes the oldest one.
        self.history = deque(maxlen=max_size)
        self.created_at = datetime.now()  # track when this session started

    def add_message(self, role, content):
        # Every message is stored as a dict with role, content, and timestamp.
        # role is either "user" or "assistant".
        # Timestamp is recorded at add time, not send time, for accurate logs.
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now()
        })

    def get_history(self):
        # Return a plain list so callers can index and slice freely.
        # deque does not support slicing, so we convert it here.
        return list(self.history)

    def get_as_message_objects(self):
        """
        Convert history dicts to LangChain HumanMessage / AIMessage objects.

        WHY? LangChain's MessagesPlaceholder requires typed message objects,
        not plain dicts. This method bridges our internal format to LangChain's.
        If LangChain is not installed we return the raw dicts (simulation mode).
        """
        if not LANGCHAIN_AVAILABLE:
            return list(self.history)

        messages = []
        for msg in self.history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))
        return messages

    def clear(self):
        # Reset both the messages and the session start time.
        self.history.clear()
        self.created_at = datetime.now()

    def __len__(self):
        # Lets us write len(buffer) instead of len(buffer.history).
        return len(self.history)


class ContextManager:
    """
    Silently extracts facts from every message the user sends. (Day 06)

    The chatbot "learns" the user's name, location, and interests
    without ever asking directly — just by reading their messages.
    """

    def __init__(self):
        self.entities = {}      # structured facts: {"user_name": "Bilel", "location": "Tunis"}
        self.preferences = []   # raw messages where the user stated a want/preference
        self.topics = set()     # domains of interest: {"python", "web"}
        self.turn_count = 0     # how many messages have been analyzed

    def extract_from_message(self, message):
        msg_lower = message.lower()  # lowercase once, reuse everywhere
        self.turn_count += 1

        # --- Name extraction ---
        # Look for "my name is X" or "I'm X" patterns.
        # We only keep the first word after the trigger to avoid capturing sentences.
        if "my name is" in msg_lower or "i'm" in msg_lower:
            words = msg_lower.split()
            if "is" in words:
                idx = words.index("is")
                if idx + 1 < len(words):
                    # strip() removes trailing punctuation ("Bilel!" → "Bilel")
                    self.entities["user_name"] = words[idx + 1].strip(".,!?").capitalize()
            elif "i'm" in msg_lower:
                parts = msg_lower.split("i'm")
                if len(parts) > 1 and parts[1].strip():
                    name = parts[1].strip().split()[0].strip(".,!?")
                    self.entities["user_name"] = name.capitalize()

        # --- Location extraction ---
        # A hardcoded list of Tunisian cities is simple but effective for this domain.
        # The break stops after the first match — one location per message is enough.
        for place in ["tunis", "sfax", "sousse", "djerba", "bizerte", "kairouan"]:
            if place in msg_lower:
                self.entities["location"] = place.capitalize()
                break

        # --- Preference extraction ---
        # Any sentence containing an intent verb is worth remembering.
        # These are saved as raw strings so we can analyze them later.
        if any(w in msg_lower for w in ["want", "need", "prefer", "like", "love"]):
            self.preferences.append(message)

        # --- Topic extraction ---
        # Map broad topic names to keyword lists.
        # set.add() is safe to call multiple times — duplicates are ignored.
        topics_map = {
            "python":           ["python", "code", "programming", "function", "loop", "list"],
            "machine learning": ["machine learning", "ai", "neural", "model", "data"],
            "web":              ["web", "javascript", "html", "api", "react"],
            "general":          ["help", "learn", "teach", "understand"],
        }
        for topic, keywords in topics_map.items():
            if any(kw in msg_lower for kw in keywords):
                self.topics.add(topic)

    def get_summary(self):
        # Build a human-readable summary of everything we know about the user.
        parts = []
        if "user_name" in self.entities:
            parts.append(f"Name: {self.entities['user_name']}")
        if "location" in self.entities:
            parts.append(f"Location: {self.entities['location']}")
        if self.topics:
            # sorted() gives consistent output regardless of insertion order
            parts.append(f"Topics: {', '.join(sorted(self.topics))}")
        if self.preferences:
            parts.append(f"Preferences noted: {len(self.preferences)}")
        return "\n  ".join(parts) if parts else "No context extracted yet"

    def reset(self):
        # Called when the user types "reset" — clears context but not the DB.
        self.entities.clear()
        self.preferences.clear()
        self.topics.clear()
        self.turn_count = 0


class SystemPromptManager:
    """
    Manages the chatbot's base personality. (Day 06)

    DAY 07 EXTENSION: get_system_prompt() now accepts style_additions
    so PersonalityAdapter can inject per-message style instructions
    without changing the base personality.
    """

    def __init__(self, name="Nour", role="friendly Tunisian AI assistant", tone="warm, helpful, encouraging"):
        self.name = name
        self.role = role
        self.tone = tone
        # Constraints are sent to the model on every turn.
        # They keep the bot's behavior consistent regardless of what the user asks.
        self.constraints = [
            "Keep responses concise (under 150 words)",
            "Be helpful and empathetic",
            "Reference the user's name or context when possible",
            "Admit when you don't know something",
        ]

    def get_system_prompt(self, style_additions=""):
        """
        Build the full system prompt string.

        style_additions is injected by PersonalityAdapter (Day 07).
        If empty (first message), the base personality is used alone.
        On every subsequent message, the style block updates the prompt.
        """
        # Identity line — tells the model who it is
        prompt = f"You are {self.name}, a {self.role}.\n"
        prompt += f"Your tone is {self.tone}.\n"

        # Inject adaptive style block if PersonalityAdapter has detected anything
        if style_additions:
            prompt += f"\nAdaptive style (detected from user):\n{style_additions}\n"

        # Append fixed behavioral constraints
        prompt += "\nInstructions:\n"
        for c in self.constraints:
            prompt += f"- {c}\n"

        return prompt

    def set_personality(self, role, tone):
        # Called by the "personality" command in the CLI.
        # Only stores new values — _rebuild_chain() in ProductionChatbot
        # must be called separately to apply the change to the API chain.
        self.role = role
        self.tone = tone

    def add_constraint(self, constraint):
        # Guard against duplicates so adding the same constraint twice is safe.
        if constraint not in self.constraints:
            self.constraints.append(constraint)


class LangChainBridge:
    """
    Wraps the Mistral API call using LangChain's LCEL (LangChain Expression Language). (Day 06)

    WHY LangChain?
    It handles the message formatting, API call, and response parsing in one
    composable pipeline. The LCEL pipe operator (|) chains: prompt → llm → parser.

    SIMULATION MODE: if no API key is provided, chain stays None and invoke()
    returns a placeholder string so the code works without any setup.
    """

    def __init__(self, system_prompt, api_key=None):
        self.api_key = api_key
        self.system_prompt = system_prompt
        self.chain = None   # None = simulation mode
        self._build_chain()

    def _build_chain(self):
        # Skip building if no key or LangChain is not installed.
        if not self.api_key or not LANGCHAIN_AVAILABLE:
            return

        # BaseChatOpenAI works with any OpenAI-compatible API.
        # Mistral exposes the same interface at a different base_url.
        llm = BaseChatOpenAI(
            model="mistral-small-latest",
            api_key=self.api_key,
            base_url="https://api.mistral.ai/v1",
            temperature=0.7,    # 0 = deterministic, 1 = very creative
            max_tokens=300,     # cap response length to keep chats snappy
        )

        # The prompt template has three slots filled at invoke() time:
        #   1. ("system", ...) — fixed personality instructions
        #   2. MessagesPlaceholder — the conversation history so far
        #   3. ("human", "{user_input}") — the current user message
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{user_input}")
        ])

        # LCEL pipe: each | passes its output as input to the next stage.
        # prompt formats messages → llm calls Mistral → StrOutputParser extracts the text.
        self.chain = prompt | llm | StrOutputParser()

    def invoke(self, history, user_input):
        """Call the API. Returns simulation text if no API key is set."""
        if not self.chain:
            # Simulation mode — useful when MISTRAL_API_KEY is not set.
            # The rest of the pipeline (DB, buffer, context) still runs normally.
            return f"[Simulation - set MISTRAL_API_KEY to go live] Response to: {user_input[:60]}..."
        try:
            return self.chain.invoke({
                "history": history,         # list of HumanMessage/AIMessage objects
                "user_input": user_input    # the current user message as plain text
            })
        except Exception as e:
            # Surface the error so the user knows what went wrong
            # (wrong API key, rate limit, network issue, etc.)
            logger.error(f"API call failed: {e}")
            return f"[API Error: {str(e)[:80]}]"

    def is_live(self):
        # Used by show_status() to tell the user if real API is connected.
        return self.chain is not None


# ============================================================
# DAY 07 COMPONENTS (new)
# ============================================================

class ChatDatabase:
    """
    SQLite persistence layer. (Day 07)

    WHY SQLite?
    It is a file-based database that requires no server setup.
    Every message is written to disk immediately, so conversations
    survive app restarts, crashes, and power cuts.

    DAY 06 vs DAY 07:
      Day 06 stored messages only in ConversationBuffer (lost on exit).
      Day 07 also writes to SQLite so nothing is ever lost.
    """

    def __init__(self, db_path="production_chat.db"):
        self.db_path = db_path
        # check_same_thread=False allows the same connection to be used
        # from different parts of the code (safe here since we run single-threaded).
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        cursor = self.conn.cursor()
        # CREATE TABLE IF NOT EXISTS means this is safe to call every startup.
        # It only creates the table if it doesn't already exist — existing data is never touched.
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id         INTEGER PRIMARY KEY,   -- auto-increments, used for ordering
                role       TEXT,                  -- "user" or "assistant"
                content    TEXT,                  -- the message text
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP  -- set automatically by SQLite
            )
        ''')
        self.conn.commit()  # commit makes the table creation permanent
        logger.info(f"Database ready: {self.db_path}")

    def save_message(self, role, content):
        """
        Write one message to the database.

        WHY save BEFORE the API call?
        If the API crashes after we call it but before we save, we lose
        the user's message. Saving first guarantees we always have the input.
        """
        try:
            cursor = self.conn.cursor()
            # ? placeholders prevent SQL injection — never use f-strings for SQL values.
            cursor.execute(
                "INSERT INTO messages (role, content) VALUES (?, ?)",
                (role, content)
            )
            self.conn.commit()  # write to disk immediately
            return True
        except Exception as e:
            logger.error(f"Save failed: {e}")
            return False  # caller decides what to do (chat continues even if save fails)

    def get_history(self, limit=50):
        """
        Retrieve the most recent N messages, ordered oldest first.

        WHY ORDER BY id ASC?
        The id column increments with each insert, so id order = insertion order.
        Ordering by id is faster and more reliable than ordering by created_at
        when multiple messages are inserted in the same second.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT role, content FROM messages ORDER BY id ASC LIMIT ?",
                (limit,)
            )
            return cursor.fetchall()  # list of (role, content) tuples
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return []  # return empty list so callers don't crash on None

    def count_messages(self):
        # Used by show_status() to show the total number of saved messages.
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM messages")
        return cursor.fetchone()[0]  # fetchone returns a tuple, [0] extracts the number


class PersonalityAdapter:
    """
    Detects user communication style from each message and generates
    style-specific instructions to add to the system prompt. (Day 07)

    DAY 06 vs DAY 07:
      Day 06: same system prompt for every message (static personality).
      Day 07: prompt rebuilds each turn based on detected style (adaptive).

    HOW IT WORKS:
      1. analyze() reads the user's message and updates 4 style flags.
      2. get_style_additions() turns those flags into instruction text.
      3. ProductionChatbot._rebuild_chain() injects that text into the prompt.
    """

    def __init__(self):
        # Start with neutral defaults — no style assumed before the first message.
        self.style = {
            "is_technical":   False,  # does the user use technical terms?
            "prefers_detail": False,  # does the user ask for explanations?
            "likes_humor":    False,  # does the user use humor/emoji?
            "impatient":      False,  # does the user want quick answers?
        }
        self.context = "general"  # what kind of conversation is this?

    def analyze(self, message):
        """
        Read the user's message and update all style flags.
        Called on every turn so the personality adapts in real time.

        WHY substring search instead of exact word match?
        Exact match misses plurals and compounds ("api" won't match "apis",
        "database" won't match "databases"). Substring search catches all forms.
        """
        msg = message.lower()  # lowercase once so all comparisons are case-insensitive

        # --- Technical level ---
        # If the user uses technical terms, they are likely a developer.
        # Adapt to use technical language and include code examples.
        technical_words = [
            "api", "database", "syntax", "algorithm", "function", "variable",
            "loop", "class", "method", "async", "framework", "json", "sql",
            "performance", "optimization", "query", "stack", "xml",
        ]
        self.style["is_technical"] = any(w in msg for w in technical_words)

        # --- Detail preference ---
        # Words like "explain" or "step-by-step" signal the user wants depth.
        detail_words = [
            "explain", "detailed", "step-by-step", "why", "elaborate",
            "how does", "deep dive", "break down",
        ]
        self.style["prefers_detail"] = any(w in msg for w in detail_words)

        # --- Humor ---
        # If the user is joking around, matching their energy builds rapport.
        self.style["likes_humor"] = any(w in msg for w in ["lol", "haha", "funny", "joke"])

        # --- Impatience ---
        # Words like "quick" or "asap" mean the user wants the answer first,
        # explanation later. Skip preamble and get straight to the point.
        self.style["impatient"] = any(w in msg for w in ["quick", "asap", "hurry", "urgent", "fast"])

        # --- Conversation context ---
        # Detect the TYPE of conversation to set the right mode:
        #   support  → empathetic, diagnostic, solution-focused
        #   learning → patient, guiding, don't just give answers
        #   creative → enthusiastic, exploratory, open-ended
        #   general  → friendly chat
        if any(w in msg for w in ["bug", "error", "issue", "problem", "crash", "broken"]):
            self.context = "support"
        elif any(w in msg for w in ["learn", "teach", "how", "explain", "beginner"]):
            self.context = "learning"
        elif any(w in msg for w in ["create", "design", "brainstorm", "idea"]):
            self.context = "creative"
        else:
            self.context = "general"

    def get_style_additions(self):
        """
        Convert current style flags into instruction lines for the system prompt.

        These lines are injected into the prompt under "Adaptive style:"
        so the model follows them alongside the base personality.
        """
        lines = []

        # Language complexity: match the user's technical level
        if self.style["is_technical"]:
            lines.append("- Use technical terminology. Include code examples when relevant.")
        else:
            lines.append("- Use plain language. Avoid jargon. Use everyday analogies.")

        # Response length: match the user's preference for depth
        if self.style["prefers_detail"]:
            lines.append("- Give thorough explanations with examples and edge cases.")
        else:
            lines.append("- Be concise. Get to the point quickly.")

        # Humor: only add if detected — never force it
        if self.style["likes_humor"]:
            lines.append("- Light humor is welcome. Keep it natural.")

        # Speed: impatient users get the answer first, no warm-up
        if self.style["impatient"]:
            lines.append("- Lead with the answer. Skip preamble and pleasantries.")

        # Context-specific instruction
        context_map = {
            "support":  "- User needs help. Be empathetic and solution-focused.",
            "learning": "- User is learning. Guide them — don't just give answers.",
            "creative": "- User is brainstorming. Be exploratory and enthusiastic.",
            "general":  "- Friendly conversation mode.",
        }
        lines.append(context_map.get(self.context, ""))

        return "\n".join(lines)

    def get_summary(self):
        # Human-readable summary for the "context" CLI command.
        return (
            f"Technical: {self.style['is_technical']} | "
            f"Detail: {self.style['prefers_detail']} | "
            f"Humor: {self.style['likes_humor']} | "
            f"Impatient: {self.style['impatient']} | "
            f"Context: {self.context}"
        )


class InputValidator:
    """
    Checks every message before it reaches the API. (Day 07)

    WHY validate before the API call?
    Sending empty or giant messages to the API wastes tokens and money.
    Catching them early gives the user a clear error immediately.

    WHY a static method?
    Validation is a pure function — it needs no instance state.
    @staticmethod lets us call InputValidator.validate(text) directly
    without creating an InputValidator object.
    """

    MAX_LENGTH = 500  # characters — adjust based on your token budget

    @staticmethod
    def validate(text):
        """
        Check if text is valid.
        Returns a tuple: (is_valid: bool, error_message: str or None).

        WHY return a tuple instead of raising an exception?
        Validation failures are expected (user types something wrong).
        Exceptions are for unexpected errors. A tuple lets the caller
        decide how to handle the failure without a try/except block.
        """
        # Reject empty or whitespace-only input
        if not text or not text.strip():
            return False, "Message cannot be empty."

        # Reject messages that would exceed the API token budget
        if len(text) > InputValidator.MAX_LENGTH:
            return False, f"Message too long ({len(text)} chars, max {InputValidator.MAX_LENGTH})."

        return True, None  # None means "no error"


class ErrorBoundary:
    """
    Wraps any function with a try/except and returns a fallback on failure. (Day 07)

    WHY a wrapper/decorator pattern instead of try/except in the caller?
    One ErrorBoundary protects any function. The API call logic stays clean
    and readable without being buried in error-handling code.

    HOW IT WORKS:
      safe_fn = ErrorBoundary.wrap(risky_fn)
      result = safe_fn()        # never raises — returns fallback on error
    """

    @staticmethod
    def wrap(func, fallback="I encountered an error. Please try again."):
        # wrapper is a closure — it captures func and fallback from the outer scope.
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Log the real error for debugging, return a friendly message to the user.
                logger.error(f"Error in {func.__name__}: {e}")
                return fallback
        return wrapper  # return the wrapper function, not the result


# ============================================================
# PRODUCTION CHATBOT — Day 06 + Day 07
# ============================================================

class ProductionChatbot:
    """
    The main orchestrator: brings all Day 06 and Day 07 components together.

    DESIGN PATTERN: composition
    Each feature lives in its own class. ProductionChatbot wires them together
    and defines the order in which they run. This makes each piece easy to
    test, replace, or upgrade independently.

    Day 06 pipeline:  input -> buffer -> context -> LangChain API -> buffer
    Day 07 additions: validate -> adapt personality -> save to SQLite
                      -> (Day 06 pipeline) -> save response to SQLite
    """

    def __init__(self, name="Nour", api_key=None):
        self.name = name        # the chatbot's displayed name
        self.api_key = api_key  # stored so we can rebuild the chain after personality changes
        self.turn_count = 0     # counts completed conversations turns for logging

        # --- Day 06 components ---
        # ConversationBuffer: keeps the last 20 messages in RAM for fast access.
        # 20 messages ≈ 10 back-and-forth turns — enough context without token overload.
        self.buffer = ConversationBuffer(max_size=20)

        # ContextManager: silently reads every message and extracts facts.
        self.context = ContextManager()

        # SystemPromptManager: holds the base personality text.
        # Day 07 extends it to also accept style_additions from PersonalityAdapter.
        self.prompt_mgr = SystemPromptManager(
            name=name,
            role="friendly Tunisian AI assistant",
            tone="warm, helpful, encouraging"
        )

        # --- Day 07 components ---
        # ChatDatabase: writes every message to SQLite so nothing is lost on restart.
        self.db = ChatDatabase()

        # PersonalityAdapter: detects user style and adjusts the prompt each turn.
        self.adapter = PersonalityAdapter()

        # Build the initial LangChain chain with the base prompt (no style yet).
        # This will be rebuilt on every turn once PersonalityAdapter has data.
        self.bridge = LangChainBridge(
            system_prompt=self.prompt_mgr.get_system_prompt(),
            api_key=api_key
        )

        # DAY 07: load the last session from SQLite into the buffer.
        # This is what makes the chatbot remember across restarts.
        self._restore_session()
        logger.info(f"Chatbot ready: {name}")

    def _restore_session(self):
        """
        Load the 10 most recent messages from the database into the in-memory buffer.

        WHY only 10?
        Loading the full history could fill the buffer (max 20) and use too many
        tokens. 10 messages = 5 turns of context — enough to feel continuous.

        After this, the buffer behaves normally. The model "remembers" the last
        session because those messages are now part of the active history.
        """
        history = self.db.get_history(limit=10)
        if history:
            for role, content in history:
                self.buffer.add_message(role, content)
            logger.info(f"Restored {len(history)} messages from previous session")

    def _rebuild_chain(self):
        """
        Recreate the LangChain chain with the current adaptive system prompt.

        WHY rebuild instead of update?
        LangChain's chain bakes the system prompt at construction time.
        There is no "update prompt" method — we must create a new chain object.
        This is called after every style detection so the model always has
        the freshest prompt reflecting the user's current communication style.
        """
        style_additions = self.adapter.get_style_additions()  # e.g. "- Use technical terms."
        system_prompt = self.prompt_mgr.get_system_prompt(style_additions)
        # Replace the old bridge with a new one that has the updated prompt
        self.bridge = LangChainBridge(system_prompt=system_prompt, api_key=self.api_key)

    def chat(self, user_input):
        """
        The full Day 07 message pipeline. Every step is labelled [Day 06] or [Day 07]
        so you can see exactly what is new versus inherited.

        Pipeline:
          [Day 07] Step 1: Validate — reject bad input before anything else
          [Day 07] Step 2: Detect style → rebuild adaptive prompt
          [Day 07] Step 3: Save user message to SQLite
          [Day 06] Step 4: Add to buffer + extract context
          [Day 06+07] Step 5: Call API wrapped in ErrorBoundary
          [Day 07] Step 6: Save response to SQLite
          [Day 06] Step 7: Add response to buffer
        """

        # Step 1 — Validate [Day 07]
        # Check length and content BEFORE touching the database or the API.
        # If the input is invalid, return the error immediately and do nothing else.
        is_valid, error = InputValidator.validate(user_input)
        if not is_valid:
            return error

        user_input = user_input.strip()  # remove accidental leading/trailing spaces

        # Step 2 — Adaptive personality [Day 07]
        # Analyze the message to detect style flags (technical, impatient, etc.).
        # Then rebuild the LangChain chain with the updated system prompt.
        # This means the SAME question from two different users gets different responses.
        self.adapter.analyze(user_input)
        self._rebuild_chain()

        # Step 3 — Save user message to SQLite [Day 07]
        # Save BEFORE the API call. If the API crashes, we still have the user's message.
        self.db.save_message("user", user_input)

        # Step 4 — Buffer + context extraction [Day 06]
        # Add to the in-memory buffer (used by LangChain as conversation history).
        # Run context extraction to silently pick up names, topics, preferences.
        self.buffer.add_message("user", user_input)
        self.context.extract_from_message(user_input)

        # Step 5 — Call the API with ErrorBoundary [Day 06 + Day 07]
        # Define the API call as a local function so ErrorBoundary can wrap it.
        def _call_api():
            # [:-1] removes the last message from history (the one we just added)
            # because LangChain already injects the current message via {user_input}.
            # Sending it twice would confuse the model and waste tokens.
            history = self.buffer.get_as_message_objects()[:-1]
            return self.bridge.invoke(history, user_input)

        # ErrorBoundary.wrap turns _call_api into a safe version that never raises.
        # If Mistral is down or the key is wrong, the user gets a friendly message
        # instead of a Python traceback.
        response = ErrorBoundary.wrap(_call_api)()

        # Step 6 — Save response to SQLite [Day 07]
        # Both sides of the conversation are persisted so replay is complete.
        self.db.save_message("assistant", response)

        # Step 7 — Add response to buffer [Day 06]
        # The assistant's reply becomes part of history for the next turn.
        self.buffer.add_message("assistant", response)

        self.turn_count += 1
        logger.info(f"Turn {self.turn_count} | style={self.adapter.context} | live={self.bridge.is_live()}")
        return response

    def show_status(self):
        """Print a summary of the current chatbot state."""
        api_status = "[LIVE API]" if self.bridge.is_live() else "[SIMULATION - no API key]"
        total = self.db.count_messages()  # total messages ever saved (all sessions)
        print(f"\n{'='*60}")
        print(f"  {self.name} -- Production Chatbot (Day 07)")
        print(f"{'='*60}")
        print(f"  API:               {api_status}")
        print(f"  Session turns:     {self.turn_count}")
        print(f"  Buffer messages:   {len(self.buffer)}")   # messages in RAM this session
        print(f"  DB total messages: {total}")              # all messages ever saved
        print(f"{'='*60}\n")

    def show_conversation(self):
        """Print the current session messages from the in-memory buffer."""
        history = self.buffer.get_history()
        if not history:
            print("\n[No messages in this session yet]\n")
            return
        print(f"\n{'='*60}")
        print(f"  Active Session  ({len(history)} messages)")
        print(f"{'='*60}\n")
        for msg in history:
            ts = msg["timestamp"].strftime("%H:%M:%S")
            print(f"  [{ts}] {msg['role'].upper()}: {msg['content']}\n")

    def show_db_history(self):
        """
        Print the full conversation from SQLite — includes all previous sessions.
        This is the key Day 07 feature: memory that survives restarts.
        """
        rows = self.db.get_history(limit=100)
        if not rows:
            print("\n[No history in database]\n")
            return
        print(f"\n{'='*60}")
        print(f"  Full Database History  ({len(rows)} messages)")
        print(f"{'='*60}\n")
        for role, content in rows:
            # Truncate long messages so the display stays readable
            preview = content[:80] + ("..." if len(content) > 80 else "")
            print(f"  {role.upper()}: {preview}\n")

    def show_context(self):
        """Print extracted facts (from ContextManager) and detected style (from PersonalityAdapter)."""
        print(f"\n{'='*60}")
        print("  Extracted Context + Detected Style")
        print(f"{'='*60}\n")
        print(f"  {self.context.get_summary()}")
        print(f"\n  Style: {self.adapter.get_summary()}\n")

    def reset(self):
        """
        Clear the active session — buffer and context.
        The database is NOT cleared so history is always preserved.
        """
        self.buffer.clear()
        self.context.reset()
        self.turn_count = 0
        print("\n[Session cleared. Database history preserved.]\n")

    def change_personality(self, role, tone):
        """Update the base personality and immediately rebuild the API chain."""
        self.prompt_mgr.set_personality(role, tone)
        # Must rebuild after changing personality — the chain has the old prompt baked in.
        self._rebuild_chain()
        print(f"\n[Personality changed: {role}, {tone}]\n")


# ============================================================
# INTERACTIVE CLI
# ============================================================

class InteractiveCLI:
    """
    Command-line interface — the front door of the chatbot.

    DESIGN: two types of input are handled differently:
      Commands (status, history, etc.) → call a chatbot method directly
      Regular text                     → goes through the full chat() pipeline
    """

    # Dict of commands and their descriptions, used by _show_help().
    COMMANDS = {
        "help":                       "Show this help",
        "status":                     "Show chatbot status (API, DB, session)",
        "history":                    "Show active session messages",
        "dbhistory":                  "Show full database history (all sessions)",
        "context":                    "Show extracted context + detected style",
        "reset":                      "Clear session (database history preserved)",
        "personality [role] [tone]":  'Change personality  e.g. "personality mentor calm"',
        "quit":                       "Exit (conversation auto-saved to DB)",
    }

    def __init__(self, chatbot):
        self.chatbot = chatbot  # the ProductionChatbot instance to drive

    def run(self):
        """
        Start the interactive chat loop.

        PATTERN: event loop
        The while True loop waits for input, routes it to the right handler,
        and repeats. It exits on "quit", KeyboardInterrupt (Ctrl+C), or EOFError
        (piped input ended). Any other exception is caught and printed so one
        bad message never crashes the entire session.
        """
        print(f"\n{'='*60}")
        print(f"  {self.chatbot.name} -- Day 07 Production Chatbot")
        print(f"{'='*60}")
        self.chatbot.show_status()
        print("  Type 'help' for commands, 'quit' to exit.\n")

        while True:
            try:
                user_input = input("You: ").strip()

                # Skip blank Enter presses without printing anything
                if not user_input:
                    continue

                # Lowercase the command check only — preserve case for chat messages
                cmd = user_input.lower()

                if cmd == "help":
                    self._show_help()
                elif cmd == "status":
                    self.chatbot.show_status()
                elif cmd == "history":
                    self.chatbot.show_conversation()
                elif cmd == "dbhistory":
                    self.chatbot.show_db_history()
                elif cmd == "context":
                    self.chatbot.show_context()
                elif cmd == "reset":
                    self.chatbot.reset()
                elif cmd.startswith("personality "):
                    # "personality mentor encouraging" → role="mentor", tone="encouraging"
                    self._change_personality(user_input)
                elif cmd == "quit":
                    print(f"\n{self.chatbot.name}: Goodbye! Your conversation has been saved.\n")
                    break
                else:
                    # Everything that is not a command goes to the chatbot
                    response = self.chatbot.chat(user_input)
                    print(f"\n{self.chatbot.name}: {response}\n")

            except (KeyboardInterrupt, EOFError):
                # Ctrl+C or piped input ended — exit cleanly the same way as "quit"
                print(f"\n\n{self.chatbot.name}: Goodbye! Your conversation has been saved.\n")
                break
            except Exception as e:
                # Print the error but keep the loop running — one bad message
                # should never kill the entire session
                print(f"Error: {e}\n")

    def _show_help(self):
        """Print all available commands in a formatted table."""
        print(f"\n{'='*60}")
        print("  COMMANDS")
        print(f"{'='*60}")
        for cmd, desc in self.COMMANDS.items():
            # Left-justify each command to 38 chars so descriptions line up
            print(f"  {cmd:<38} {desc}")
        print(f"{'='*60}\n")

    def _change_personality(self, command):
        """
        Parse "personality [role] [tone]" and apply it.

        Example: "personality mentor encouraging"
          parts[0] = "personality"
          parts[1] = "mentor"          → role
          parts[2:] = ["encouraging"]  → tone (joined so multi-word tones work)
        """
        parts = command.split()
        if len(parts) >= 3:
            role = parts[1]
            tone = " ".join(parts[2:])  # join remaining words so "very calm" works
            self.chatbot.change_personality(role, tone)
        else:
            print("Usage: personality [role] [tone]\n")


# ============================================================
# MAIN — entry point
# ============================================================

if __name__ == "__main__":
    # Read the API key from the .env file (loaded at the top by load_dotenv()).
    # If missing, ProductionChatbot runs in simulation mode automatically —
    # no crash, no setup required to run the demo.
    api_key = os.getenv("MISTRAL_API_KEY")

    # Create the chatbot. All Day 06 + Day 07 components initialize here.
    # Previous session messages are loaded from SQLite automatically in __init__.
    chatbot = ProductionChatbot(
        name="Nour",        # change this to rename your chatbot
        api_key=api_key,
    )

    # Hand control to the interactive CLI loop.
    cli = InteractiveCLI(chatbot)
    cli.run()
