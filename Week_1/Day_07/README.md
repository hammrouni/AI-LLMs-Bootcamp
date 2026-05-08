# 📅 اليوم 7: Smart Chatbot - Part 2 🚀

---

## 🎯 الهدف متاع اليوم

<div dir="rtl">

**توة عندك chatbot يخدم مريڤل جا الوقت باش تردو Pro بالرسمي. اليوم باش نزيدوه  features كاسحين: الـ memory تقعد مسجلة حتى كي تعمل restart، والـ personality تتبدّل على قياسو.**

اليوم باش نبنيو عاللي خدمناه فالنهار السادس: باش نهزو الـ `06_RealChatbot` ونردوه chatbot حاضر للـ Production.

</div>

---

## 📚 المفاهيم الصحيحة (Key Concepts)

<div dir="rtl">

- **Persistent Storage:** في عوض ما تخلي المحادثات مطيشة فالـ RAM (وتطير كي تعمل restart)، باش نخبيوهم في base de données — باش نبداو بالـ SQLite.
- **Session Management:** كل user عندو المحادثات متاعو وحدو، والـ chatbot يعرفو شكونو من أول ضربة.
- **User Profiling:** الـ chatbot يولي يتعلم الجو متاع كل user بالشوية بالشوية (preferences) — الـ style متاع كتيبتو، السوجيات (sujets) اللي يشيخ عليهم...
- **Advanced Personality:** الشخصية متاع الـ bot تتبدل على حساب الـ context والـ style متاع الـ user — موش حكاية system prompt فيكس وكهو.
- **Error Handling:** كيفاش تريڤل لي bugs بطريقة Pro: تخدم بالـ retries، الـ timeouts، والـ graceful degradation — باش الـ user ما يشوفش الـ app مبلنتية بطريقة خايبة.

</div>

---

## 🛠️ كيفاش تبدا تخدم (Steps to Complete Today)

<div dir="rtl">

**الخطة باش تريفز وتطبق نهارك:**

1️⃣ **أقرأ `concept.md` هو الأول** — لازم تفهم "علاش" قبل "كيفاش".
2️⃣ **خَدّم (run) الـ `demo.py`** — شوف الكود "لايف" قدام عينيك كيفاش يتصرف.
3️⃣ **خلوضها وحدك** — بدّل الـ database path، ريڤل الـ user profiles، وتستي الـ multi-session conversations.

</div>

```bash
# 1. شعل الـ virtual environment متاعك
bootcamp\Scripts\activate     # Windows
source bootcamp/bin/activate  # Mac/Linux

# 2. صب الـ "سلعة" (packages) اللي باش تستحقها
pip install langchain langchain-openai python-dotenv sqlite3

# 3. ريڤل الـ .env وحط فيه الـ API key
copy codes\.env.example codes\.env
# افتح codes\.env وحط MISTRAL_API_KEY=your_key_here

# 4. ابدا بالـ "البياسة" الأولى
cd codes\01_PersistentMemory
python demo.py

```

---

## 📖 مراجع باش تزيد تشيخ (Resources)

* 📚 **SQLite Python Docs:** [docs.python.org/3/library/sqlite3.html](https://docs.python.org/3/library/sqlite3.html)
* 📚 **LangChain Memory:** [python.langchain.com/docs/modules/memory/](https://python.langchain.com/docs/modules/memory/)
* 🤖 **Mistral API Docs:** [docs.mistral.ai](https://docs.mistral.ai/)
* 💻 **Code Examples:** طل على Dossier `codes/` متاع اليوم السابع.

---

## 💾 شنية لازم يكون عندك في لخر (Deliverables)

✨ **كي يوفى النهار، لازم تكون مريقل في هاذوم:**

* ✅ `01_PersistentMemory` — طيّشت الـ ConversationBuffer وبدلتو بـ SQLite database باش المحادثات تقعد مسجلة حتى بعد الـ restart.
* ✅ `02_PersonalityDesign` — ركّحت personality تتبدّل وتتأقلم مع الـ style متاع الـ user (موش system prompt راقد).
* ✅ `03_ErrorHandling` — زدت الـ retry logic، فاليديت الـ input (validation)، وركحت مساجات مزيانة كي تطيح error.
* ✅ `04_ProductionChatbot` — لمّيت الخلوضة هذي الكل في سيستام واحد مريڤل وحاضر للـ Production.

---

## 🔗 أيام عندها علاقة

* **البارح:** [اليوم 6 - Smart Chatbot Part 1](https://www.google.com/search?q=../Day_06/README.md)
* **غدوة:** [Week 2 - Embeddings & RAG](https://www.google.com/search?q=../../Week_2/README.md)

---

## 💡 نصائح ماللخر (Tips)

* **ابدى بالـ SQLite** — ساهل، ما يستحقش installation، ومزيان باش تتعلم بيه قبل ما تتعدى للـ MongoDB.
* **تستي بـ زوز users متبدلين** — ثبت اللي الـ context ما يدخلش بعضو بيناتهم واللي الـ personality تتبدل بالرسمي.
* **جرب أعمل restart** — سكّر الـ chatbot، عاود شعلو، وثبت اللي المحادثات ما طاروش وقعدو مسجلين.
* **تستي لي errors بلعاني** — قص الكونيكسيون ولا حط API key غالط وشوف الـ error handling كيفاش يسلّكها.
* **الـ Git commit history** — أعمل commit لكل feature وحدها باش تنجم ترجعلها وتفهم الـ progression متاعك.