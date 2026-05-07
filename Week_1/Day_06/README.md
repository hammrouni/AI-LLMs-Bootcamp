# 📅 اليوم 6: Smart Chatbot Project - Part 1 🚀

<div dir="rtl">

# مشروع الجمعة: كيفاش تبني Chatbot كاسح ويتفكر شحكيتو

</div>

---

## 🎯 الهدف متاع اليوم

<div dir="rtl">

**باش نبداو نبرمجو chatbot بروفيسيونال (Pro) يتذكر الـ historique متاع المحادثات ويفهم الـ context.**

توة جا الوقت باش نطبقو اللي تعلمناها ليامات اللي فاتو الكل في بروجي (projet) حقيقي !

</div>

---

## 📚 المفاهيم الصحيحة (Key Concepts)

<div dir="rtl">

- **Conversation Management:** كيفاش تنظم الـ messages وتركّح التسلسل متاع الأسئلة والأجوبة.
- **Memory Types:** فما الـ Short-term (يتذكر آخر مساجات بعثتهم) والـ Long-term (يخبي المعلومات المهمة باش ما ينساهاش جملة).
- **Context Management:** كيفاش تخلي الـ AI شادد الخيط ويفهم السياق (context) باش يجاوبك إجابات دقيقة وما يهزّش وينفض.
- **CLI Interface:** كيفاش تبني interface مزيانة فالـ terminal (Command Line) باش تحكي مع الـ bot متاعك.

</div>

---

## 🛠️ كيفاش تبدا تخدم (Steps to Complete Today)

<div dir="rtl">

**الخطة باش تريفز وتطبق نهارك:**

1️⃣ **أقرأ `concept.md` هو الأول** — لازم تفهم "علاش" قبل "كيفاش".
2️⃣ **خَدّم (run) الـ `demo.py`** — شوف الكود "لايف" قدام عينيك كيفاش يتصرف.
3️⃣ **خلوضها وحدك** — بدّل الـ memory size، ريڤل الـ system prompt، وتستي بـ multi-turn conversations (حديث طويل).

</div>

```bash
# 1. شعل الـ virtual environment متاعك
python -m venv bootcamp
bootcamp\Scripts\activate  # Windows
source bootcamp/bin/activate  # Mac/Linux

# 2. صب الـ "سلعة" (packages) اللي باش تستحقها
pip install langchain langchain-openai python-dotenv

# 3. ريكل الـ .env وحط فيه الـ API key
# اعمل فيتشيي .env وزيد فيه:
# MISTRAL_API_KEY=your_key_here
```

---

## 💾 شنية لازم يكون عندك في لخر (Deliverables)

<div dir="rtl">

✨ **كي يوفى النهار، لازم تكون مريقل في هاذوم:**

- ✅ **Architecture:** رسمت ولا فهمت الـ architecture متاع الـ chatbot (كيفاش لي classes و الـ modules يخدمو مع بعضهم).
- ✅ **Conversation Memory:** ركّحت memory تلم الـ messages وتشد الـ context مريڤل.
- ✅ **CLI Interface:** برمجت interface فالـ terminal تخدم بالقدى وتنجم تحكي وتستقبل منها الأجوبة.
- ✅ **Testing:** تستيت محادثات حقيقية طويلة (multi-turn) وشفت الـ AI كيفاش يجاوب و يتذكر شقلتلو ماللول.

</div>

---

## 📖 مراجع باش تزيد تشيخ (Resources)

- 📚 **LangChain Memory Types:** [python.langchain.com/docs/modules/memory/](https://python.langchain.com/docs/modules/memory/)
- 📚 **Conversation Patterns:** [python.langchain.com/docs/modules/chains/memory/](https://python.langchain.com/docs/modules/chains/memory/)
- 💻 **Code Examples:** طل على Dossier `codes/` متاع اليوم السادس.

---

## 🔗 أيام عندها علاقة

- **البارح:** [اليوم 5 - LlamaIndex & RAG Pipeline](../Day_05/README.md)
- **غدوة:** [اليوم 7 - Smart Chatbot Part 2](../Day_07/README.md)

---

## 💡 نصائح ماللخر (Tips)

<div dir="rtl">

- **أبدا بحاجة سامبل (Simple):** خلي المحادثة تخدم عادية ماللول، ومبعد أبدا زيد فالـ features (options) بالشوية بالشوية.
- **تستي الـ cas الكل:** جرب احكي معاه برشا (محادثات طويلة)، عاودلو نفس السؤال، ودخلو في context معقد وشوفو يضيع ولا لا.
- **الـ System Prompt هو الكل:** وصّي الـ AI كيفاش تحبو يجاوب (رسمي، تفدليك، تكنيك...) ماللول باش يشد الثنية.
- **سجّل لي logs (الـ Historique):** ديما خبي المحادثات باش تنجم ترجعلهم مبعد وتحلل الـ bugs وتصلحهم.

</div>