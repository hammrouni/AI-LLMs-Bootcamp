<div dir="rtl">

# 📅 اليوم 11: RAG — الجزء الثاني🚀

# أيا نزيدو الـ LLM من الفوق الـ retriever، ونخليو الـ RAG يخرّجلك الجواب من Documents تونسية

</div>

---
<div dir="rtl">

## 🎯 الهدف متاع اليوم

**نهار اللي "نكملو فيه الـ RAG"**. البارح بنينا الـ retriever. اليوم باش نربطوه بـ LLM (Mistral)، نكتبو prompts grounded (مربوطة بال Context)، نزيدو الـ re-ranking باش تطلع النتايج المزيانة والأصح، ونقيسو جودة الجواب النهائي.

في آخر النهار، باش يولّي عندك مساعد ذكي يقرا من PDFs تونسية ويجاوبك بـمصادر/استشهادات حقيقية.

</div>

---
<div dir="rtl">

## 📚 المفاهيم الأساسية (Key Concepts)

* **End-to-End RAG Pipeline:** نربطو الـ retriever (متاع البارح) بـ LLM (Mistral) 
`ask(question) → answer`.
* **Prompt Templates for Grounding:** كيفاش تكتب prompt يلزّ الـ LLM باش يجاوب مالـ context برك، ويقول "ما نعرفش" كي يلزم.
* **Re-Ranking:** الـ top-k مالـ retriever مش ديما مرتّبة بالصحيح. الـ cross-encoder rerankers يحسّنو الـ order.
* **Hybrid Search (البحث المخلّط):** نخلطو الـ keyword (BM25) + vector. كل واحد فيهم يلقى حاجة لاخر ينجم يفلتها.
* **End-to-End Eval (Capstone):** نقيسو جودة الجواب النهائي مش بالـ retrieval برك — الدقة متاع الجواب (answer accuracy)، صحة الـ citations، والـ faithfulness (الموثوقية).

</div>

---
<div dir="rtl">

## 🛠️ كيفاش تبدا تخدم (Steps to Complete Today)


**الخطة باش تراجع وتطبق نهارك:**

1️⃣ **اقرأ ملف `concept.md` هو الأول** — لازم تفهم "علاش" قبل "كيفاش".
2️⃣ **خدّم (run) الـ `demo.py**` — شوف الكود "لايف" قدام عينيك كيفاش يتصرف.
3️⃣ خلوضها وحدك — بدّل الـ system prompt، جرّب k مختلفة (3 ولّا 5 ولّا 10)، وأكتيفي ولّا ديزاكتيفي الـ reranker.
</div>

```bash
# 1. شعل الـ virtual environment متاعك
bootcamp\Scripts\activate     # Windows
source bootcamp/bin/activate  # Mac/Linux

# 2. صب الـ "سلعة" (packages) اللي باش تستحقها
pip install chromadb mistralai langchain-text-splitters rank-bm25 python-dotenv

# 3. ريڤل الـ .env وحط فيه الـ API key
copy codes\.env.example codes\.env
# احل codes\.env وحط MISTRAL_API_KEY=your_key_here

# 4. ابدا بالـ "البياسة" الأولى
cd codes\01_EndToEndPipeline
python demo.py

```

---
<div dir="rtl">

## 📖 مراجع باش تزيد تشيخ (Resources)

* 📚 **Mistral Chat API:** [docs.mistral.ai/api](https://docs.mistral.ai/api/)
* 📚 **Reranking Models:** [huggingface.co/cross-encoder](https://huggingface.co/cross-encoder)
* 📚 **rank_bm25 Library:** [github.com/dorianbrown/rank_bm25](https://github.com/dorianbrown/rank_bm25)
* 💻 **Code Examples:** طل على الدوسي `codes/` في اليوم 11.

</div>

---
<div dir="rtl">

## 💾 شنية لازم يكون عندك في الآخر (Deliverables)

✨ **كي يوفى النهار، لازم تكون مريڤل في هاذوم:**

* ✅ `01_EndToEndPipeline` — تنجم تكتب function `ask(question)` تخدم retrieval + generation مع بعضهم.
* ✅ `02_PromptTemplates` — كتبت prompt يلز الـ LLM باش يجاوب مالـ context برك مع citations.
* ✅ `03_ReRanking` — فهمت الفرق بين bi-encoder و cross-encoder وطبقت reranker.
* ✅ `04_HybridSearch` — خلّطت الـ keyword search (BM25) مع الـ vector search.
* ✅ `05_TunisianFAQBot` — بنيت bot كامل يجاوب من قاعدة بيانات (knowledge base) تونسية بـ citations.

</div>

---
<div dir="rtl">

## 💡 نصائح ماللخر (Tips)


* **"Answer ONLY from context"** هو الستاندارد متاع الـ grounding prompt — حطو ديما في الـ system message.
* **citation = trust (الثقة)** — ديما خلي الـ bot يكتب `[source: filename]` بعد الجواب.
* **k=3 إلى 5** هو الـ default — أكثر = الـ LLM يدخل بعضو، أقل = تنقصك info (معلومات).
* **اعمل rerank كان لو الـ recall ضعيف** — لو كان الـ retriever الأصلي يجيبلك الجواب في الـ top-3، الـ rerank ماهوش باش يزيدك برشا.
* **الـ hybrid search يمنعك مالـ acronyms (الاختصارات)** — الـ embedding ما يفهمش "BIAT" و "ATB"، أما الـ BM25 يفهم.

</div>