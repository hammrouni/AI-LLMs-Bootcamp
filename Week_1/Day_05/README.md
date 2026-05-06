
# 📅 اليوم 5: LlamaIndex & RAG Pipeline 🚀

<div dir="rtl">

# كيفاش تبني سيستام RAG كامل بـ LlamaIndex و Mistral AI

</div>

---

## 🎯 الهدف متاع اليوم

<div dir="rtl">

**باش نركّحو pipeline كامل متاع RAG ماللي تشرجي لي documents للـ LLM اللي يجاوبك مريڤل.**

</div>

---

## 📚 المفاهيم الصحيحة (Key Concepts)

<div dir="rtl">

- **Document Loading:** تشرجي files (txt, pdf, md...) وتزيدهم الـ metadata باش تعرف الـ source منين جا.
- **Chunking:** تقص لي documents الطوال لطروف صغار (nodes) بـ `chunk_size` وتخلي تداخل (`chunk_overlap`) باش المعنى ما يضيعش.
- **Embeddings:** تترجم كل طريف (chunk) لـ vector (أرقام) بـ `mistral-embed` (فالـ 1024).
- **Vector Store:** البلاصة وين تخبي لي vectors، يا في الـ RAM يا تسجلهم فالـ disk (باش يقعدو persistés).
- **Query Engine:** تخلط retriever مع LLM = يلوّج عالـ chunks اللي قراب لسؤالك ويعطيك جواب مريڤل.

</div>

---

## 🛠️ كيفاش تبدا تخدم (Steps to Complete Today)

<div dir="rtl">

**الخطة باش تريفز وتطبق نهارك:**

1️⃣ **أقرأ `concept.md` هو الأول** — لازم تفهم "علاش" قبل "كيفاش".
2️⃣ **خَدّم (run) الـ `demo.py`** — شوف الكود "لايف" قدام عينيك كيفاش يتصرف.
3️⃣ **خلوضها وحدك** — بدّل الـ `chunk_size`، بدّل الـ `similarity_top_k`، وتستي.

</div>

```bash
# 1. شعل الـ virtual environment متاعك (Python 3.11 ولا 3.12 برك، أخطاك مالـ 3.13+)
python -m venv bootcamp
bootcamp\Scripts\activate  # Windows
source bootcamp/bin/activate  # Mac/Linux

# 2. صب الـ "سلعة" (packages) اللي باش تستحقها
pip install llama-index llama-index-readers-file \
            llama-index-llms-mistralai \
            llama-index-embeddings-mistralai \
            python-dotenv

# 3. ريكل الـ .env وحط فيه الـ API key
# اعمل فيتشيي .env وزيد فيه:
# MISTRAL_API_KEY=your_key_here
```

---


## 💾 شنية لازم يكون عندك في لخر (Deliverables)

<div dir="rtl">

✨ **كي يوفى النهار، لازم تكون مريقل في هاذوم:**

- ✅ رانيت (Run) لي demos بالترتيب من 01 للـ 05.
- ✅ تستيت بـ `chunk_size` متبدلين وشفت شنية يتبدّل.
- ✅ جربت الـ `similarity_top_k` = 1, 3, 5 وقارنت النتايج بناتهم.
- ✅ سجلت (save) الـ index فالـ disk وعاودت شرجيتو من غير ما تقعد تخسر في فلوس الـ API مرتين عالفارغ.

</div>

---

## 📖 مراجع باش تزيد تشيخ (Resources)

- 📚 **LlamaIndex Documentation:** [docs.llamaindex.ai](https://docs.llamaindex.ai/)
- 🤖 **Mistral AI Console:** [console.mistral.ai](https://console.mistral.ai)
- 💻 **Code Examples:** طل على Dossier `codes/` (من 01 للـ 05).

---

## 🔗 أيام عندها علاقة

- **البارح:** [اليوم 4 - LangChain](../Day_04/README.md)
- **غدوة:** [اليوم 6 - Smart Chatbot Part 1](../Day_06/README.md)

---

## 💡 نصائح ماللخر (Tips)

<div dir="rtl">

- **الـ Mistral** — الـ embeddings هوني يخدمو بـ `mistral-embed` (1024 بُعد).
- **نفس الـ model للي docs وللأسئلة** — كان تبدّل الـ model راك باش تفرعس الـ similarity والكود يدخل في حيط.
- **الـ Persistence حكاية لازمة** — ديما سجّل الـ index متاعك باش ما تقعدش تخلص فالـ API مرتين عالفارغ.
- **الـ Metadata هي الدليل متاعك (traceability)** — زيدها ماللول باش تنجم تبع الجواب منين جاك بالظبط.

</div>