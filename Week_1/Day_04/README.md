# 📅 اليوم 4: LangChain Fundamentals 🚀

<div dir="rtl">

# LangChain — Swiss Army Knife متاع الـ LLMs

</div>

---

## 🎯 الهدف متاع اليوم

<div dir="rtl">

**باش نتقنو LangChain — الفريموورك (Framework) اللي يخليك تبني applications AI كاسحين من غير ما تقعد تعاود تكتب في كل شي مالصفر.**

في عوض ما تقعد تبعث في الـ HTTP calls بيدك، وتريڤل لي messages وحدك، وتكسر راسك مع الـ memory — LangChain يحطلك هذا الكل في components حاضرين، تنجم تركبهم في بعضهم بالـ `|` (pipe) وتبني pipeline كامل مزيان.

</div>

---

## 📚 المفاهيم الصحيحة (Key Concepts)

<div dir="rtl">

- **الـ LLM Setup:** كيفاش تكونكتي LangChain بـ Mistral عن طريق `BaseChatOpenAI` بالـ `base_url` — نفس الـ pattern متاع ليامات اللي فاتو. (نستعملو `BaseChatOpenAI` وموش `ChatOpenAI` باش `max_tokens` تمشي صح لـ Mistral بدون ما تتحوّل لـ `max_completion_tokens`.)
- **الـ Prompt Templates:** تخدم بـ `ChatPromptTemplate` مع variables `{variable}` تنجم تعاود تستعملهم (reusable)، منظمين، وتتحكم فيهم كيما تحب.
- **الـ Chains (LCEL):** ركّب components في بعضهم بالـ `|` — LLM + Prompt + Parser في سطر وحد. هذا هو "القلب" متاع LangChain.
- **الـ Conversation Memory:** كيفاش تخلي الـ AI يتذكر شحكيتو — `MessagesPlaceholder` + ليستة (list) تكبر مع كل ريبونس (turn).
- **الـ Mini Chatbot:** شات بوت (Chatbot) كامل مكمّل: system prompt + LCEL + memory + streaming ديريكت فالـ terminal.

</div>

---

## 🛠️ كيفاش تبدا تخدم (Steps to Complete Today)

<div dir="rtl">

**الخطة باش تريفز وتطبق نهارك:**

1️⃣ **أقرأ `concept.md` هو الأول** — لازم تفهم "علاش" قبل "كيفاش".
2️⃣ **خَدّم (run) الـ `demo.py`** — شوف الكود "لايف" قدام عينيك كيفاش يتصرف.
3️⃣ **خلوضها وحدك** — بدّل الـ system prompt، بدّل الـ MAX_TURNS، وتستي الـ streaming.

</div>

```bash
# 1. شعل الـ virtual environment متاعك
bootcamp\Scripts\activate     # Windows
source bootcamp/bin/activate  # Mac/Linux

# 2. صب الـ "سلعة" (packages) اللي باش تستحقها
pip install langchain langchain-openai python-dotenv

# 3. ريكل الـ .env وحط فيه الـ API key
copy codes\.env.example codes\.env
# افتح codes\.env وحط MISTRAL_API_KEY=your_key_here

# 4. ابدا بالـ "البياسة" الأولى
cd codes\01_LLM_Setup
python demo.py
```

---

## 📖 مراجع باش تزيد تشيخ (Resources)

- 📚 **LangChain Docs الرسمية:** [python.langchain.com/docs](https://python.langchain.com/docs/introduction/)
- 📚 **LCEL (LangChain Expression Language):** [python.langchain.com/docs/concepts/lcel](https://python.langchain.com/docs/concepts/lcel/)
- 🤖 **Mistral API Docs:** [docs.mistral.ai](https://docs.mistral.ai/)
- 📘 **ChatPromptTemplate Docs:** [python.langchain.com/docs/concepts/prompt_templates](https://python.langchain.com/docs/concepts/prompt_templates/)
- 💻 **Code Examples:** طل على Dossier `codes/` في اليوم الرابع.

---

## 💾 شنية لازم يكون عندك في لخر (Deliverables)

<div dir="rtl">

✨ **كي يوفى النهار، لازم تكون مريقل في هاذوم:**

- ✅ `01_LLM_Setup` — كونكتيت LangChain بـ Mistral وبعثت أول message.
- ✅ `02_Prompt_Templates` — صنعت templates تنجم تعاود تخدم بيهم (reusable) وفيهم variables ديناميك.
- ✅ `03_Chains` — ركّحت LCEL chain كاملة بالـ `|` وشفت الـ pipeline كيفاش يخدم.
- ✅ `04_Conversation_Memory` — الـ AI ولّى يتذكر فاش تحكيو فالـ session الكل.
- ✅ `05_Mini_Chatbot` — برمجت شات بوت (chatbot) كامل يخدم بالـ streaming ديريكت فالـ terminal.

</div>

---

## 🔗 أيام عندها علاقة

- **البارح:** [اليوم 3 - Advanced Prompt Engineering](../Day_03/README.md)
- **غدوة:** [اليوم 5 - RAG](../Day_05/README.md)

---

## 💡 نصائح ماللخر (Tips)

<div dir="rtl">

- **الـ LCEL كيما الـ Lego** — كل component يخدم وحدو، لصّقهم فالـ `|` كيما تحب وبدّل اللي تحب من غير ما تفرعس الباقي.
- **الـ Prompt Template موش "كتيبة فيكس"** — ديما أخدم بالـ `{variables}` باش يقعد الكود متاعك منظم وتنجم تعاود تستعملو.
- **الـ Memory راهي تتنفخ** — فالـ production، الحديث الطويل ياكل برشا tokens. ديما أعمل ليميت (limit) بالـ `MAX_TURNS`.
- **الـ Streaming يعطي UX طيارة** — الـ user يولي يشوف فالجواب هابط كلمة كلمة في عوض يقعد يستنى، وهذي تحسّن الـ experience برشا.
- **ما تخلّطش بين الـ Chain والـ Agent** — الـ Chain تمشي في ثنية مسطّرة (ثابتة)، أما الـ Agent يدبّر راسو وحدو. اليوم رانا خدمنا بالـ Chains.
</div>
