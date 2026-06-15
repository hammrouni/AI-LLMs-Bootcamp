<div dir="rtl">

# 📅 اليوم 10: RAG — الجزء الأول (Retrieval) 🚀

# أيا نركّحو الـ retrieval pipeline: نبداو مال Documents، نقصّوهم chunks، نخرّجولهم الـ embeddings متاعهم، ونصنعو retriever يطلّعلك الجواب.

</div>

---
<div dir="rtl">

## 🎯 الهدف متاع اليوم

**نهار الـ RAG (Retrieval Augmented Generation) — الجزء الأول**. اليوم باش نتعلّمو كيفاش نحضّرو الـ documents، نقسّموهم بذكاء (chunking)، ونبنيو retriever يلقالك الـ context (السياق) المناسب لأي سؤال.

غدوة باش نزيدو الـ LLM من الفوق ونخلّيوه يجاوب مالـ context. اليوم هو الأساس: ما تنجمش تجاوب من ملف ما تعرفش كيفاش تقراه.

</div>

---
<div dir="rtl">

## 📚 المفاهيم الأساسية (Key Concepts)


* **الـ RAG (RAG Architecture):** شنوة هو الـ RAG وعلاش هو الحل اللي خلّى LLM ينجم يجاوب من الـ documents متاعك من غير ما تستحق تعمل fine-tuning.
* **تحضير Documents (Document Preparation):** تنظيف الـ PDFs، الـ DOCX، والـ TXT، تنحية الـ headers والـ footers، وتصليح الـ encoding — عبارة على "غسيل" متاع بيانات.
* **تقسيم النص (Text Chunking):** كيفاش تقسّم نص طويل لـ طروف (pieces) متاع 200-500 token. بالطريقة الـ fixed، الـ recursive، ولا الـ semantic.
* **بناء الـ Retriever:** نربطو الـ chunks بالـ embeddings ونخبيوهم في vector DB. هذا هو الـ retriever.
* **Retrieval Quality - Capstone:** كيفاش تقيس "هل الـ retriever يلقى الـ chunks الصحيحة؟" باستعمال الـ recall@k والـ precision.

</div>

---
<div dir="rtl">

## 🛠️ كيفاش تبدا تخدم (Steps to Complete Today)


**الخطة باش تراجع وتطبق نهارك:**

1️⃣ **اقرأ ملف `concept.md` هو الأول** — لازم تفهم "علاش" قبل "كيفاش".
2️⃣ **خدّم (run) الـ `demo.py**` — شوف الكود "لايف" قدام عينيك كيفاش يتصرف.
3️⃣ **خلوضها وحدك** — بدل الـ chunk_size والـ chunk_overlap، وشوف كيفاش تتبدل نتايج الـ retrieval.

</div>

```bash
# 1. شعل الـ virtual environment متاعك
bootcamp\Scripts\activate     # Windows
source bootcamp/bin/activate  # Mac/Linux

# 2. صب الـ "سلعة" (packages) اللي باش تستحقها
pip install chromadb mistralai pypdf python-docx reportlab langchain-text-splitters python-dotenv

# 3. ريڤل الـ .env وحط فيه الـ API key
copy codes\.env.example codes\.env
# احل codes\.env وحط MISTRAL_API_KEY=your_key_here

# 4. ابدا بالـ "البياسة" الأولى
cd codes\01_RAGArchitecture
python demo.py

```

---
<div dir="rtl">

## 📖 مراجع باش تزيد تشيخ (Resources)


* 📚 **RAG Survey Paper:** [arxiv.org/abs/2312.10997](https://arxiv.org/abs/2312.10997)
* 📚 **LangChain Text Splitters:** [python.langchain.com/docs/modules/data_connection/document_transformers](https://python.langchain.com/docs/modules/data_connection/document_transformers/)
* 📚 **Mistral RAG Cookbook:** [docs.mistral.ai/guides/rag](https://docs.mistral.ai/guides/rag/)
* 💻 **Code Examples:** طل على الدوسي `codes/` في اليوم 10.

</div>

---

<div dir="rtl">

## 💾 شنية لازم يكون عندك في الآخر (Deliverables)


✨ **كي يوفى النهار، لازم تكون مريقل في هاذوم:**

* ✅ `01_RAGArchitecture` — تنجم ترسم diagram للـ RAG وتفسّر كل component.
* ✅ `02_DocumentPreparation` — قريت PDF، DOCX، و TXT بالـ Python ونظّفت النص.
* ✅ `03_TextChunking` — جربت 3 استراتيجيات متاع chunking وفهمت الفرق بيناتهم.
* ✅ `04_BuildingTheRetriever` — بنيت retriever يخدم على corpus (مجموعة نصوص) صغير.
* ✅ `05_RetrievalQuality` — قست الـ recall@k وفهمت علاش الـ evaluation (التقييم) حاجة أساسية.

</div>

---
<div dir="rtl">

## 💡 نصائح ماللخر (Tips)


* **الـ chunking أهم مالـ embedding model** — chunk_size غالط يطيّحلك الـ retrieval حتى لو كان الـ embeddings ممتازة.
* **الـ chunk_size الذهبي: 300-500 tokens، والـ overlap 50-100** — يخدم مريڤل في 80% مالـ حالات.
* **نظّف الـ documents قبل ما تقسّم** — الـ headers، أرقام الصفحات (page numbers)، والـ footers يدخّلو الـ retrieval بعضو.
* **تيستي (اختبر) بـ queries حقيقية مش perfect** — الـ users يكتبوا بـ أغلاط (typos) وبالدارجة.
* **recall@5 هو الـ metric الأهم** — لو كان الجواب موش في الـ top-5 chunks، الـ LLM ماهوش باش يجاوب صحيح.

</div>