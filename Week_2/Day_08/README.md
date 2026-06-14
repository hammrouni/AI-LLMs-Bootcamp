# 📅 اليوم 8: الـ Embeddings و الـ Vector Databases 🚀

<div dir="rtl">

# نحوّلو الكلام لأرقام ونخبيوهم في DB تنجم تحوّس فيها

</div>

---

## 🎯 الهدف متاع اليوم

<div dir="rtl">

**نهار الفهم متاع "كيفاش الـ AI يلقى الحاجة إلي تشبه"**. كل ما تحب تبني نظام بحث ذكي ولا شات بوت (chatbot) يجاوب من documents لازم تفهم الـ embeddings والـ vector databases.

الـ embeddings = الأساس متاع كل RAG، كل semantic search، وكل recommendation system (نظام اقتراحات). اليوم هو نهار الفونداسيون (الأساس) متاع الجمعة كاملة.

</div>

---

## 📚 المفاهيم الأساسية (Key Concepts)

<div dir="rtl">

* **شنوة هما الـ Embeddings:** الـ embedding هو vector (سلسلة أرقام) يمثل المعنى متاع النص. "كسكسي" و "couscous" يطلعوا قريبين برشا من بعضهم في الـ vector space.
* **مقاييس التشابه (Similarity Metrics):** كيفاش نقيسوا شنوة قريب من شنوة .
* **أساسيات ChromaDB:** أبسط vector database. تركّبها بـ pip وتبدا تخدم. هايلة برشا للـ prototyping.
* **أساسيات Qdrant:** فكتور داتابايز (vector DB) أقوى وأسرع، فيها filtering و metadata قوية. مخدومة للـ production.
* **البحث في الوصفات التونسية (Tunisian Recipe Search):** نبنيوا محرك بحث في وصفات تونسية بالـ semantic search. تكتب "أكلة بالحوت" يلقالك الوصفات اللي فيها حوت حتى لو كان الكلمة مش مكتوبة حرف بحرف.

</div>

---

## 🛠️ كيفاش تبدا تخدم (Steps to Complete Today)

<div dir="rtl">

**كيفاش تقرا وتريفز كل نهار (Day):**

1️⃣ **اقرا `concept.md` ماللول** — افهم علاش (WHY) قبل كيفاش (HOW)
2️⃣ **راني (run) `demo.py`** — شوف الكود كيفاش يخدم قدام عينيك
3️⃣ **جرّب وحدك** — بدّل لي فالور (values)، فرعسو وخليه يتبلّنتا (يطيح)، وشوف شنوة يصير

</div>

```bash
# 1. نصنعو virtual environment ونخدموه
python -m venv bootcamp
bootcamp\Scripts\activate     # Windows
source bootcamp/bin/activate  # Mac/Linux

# 2. صب الـ "سلعة" (packages) اللي باش تستحقها
pip install mistralai chromadb qdrant-client numpy python-dotenv

# 3. نبداو ماللول
cd 01_WhatAreEmbeddings
python demo.py

```

---

## 📖 مراجع باش تزيد تشيخ (Resources)

<div dir="rtl">

* 📚 **Mistral Embeddings:** [docs.mistral.ai/capabilities/embeddings](https://docs.mistral.ai/capabilities/embeddings/)
* 📚 **ChromaDB Docs:** [docs.trychroma.com](https://docs.trychroma.com/)
* 📚 **Qdrant Docs:** [qdrant.tech/documentation](https://qdrant.tech/documentation/)
* 🤖 **Mistral API Docs:** [docs.mistral.ai](https://docs.mistral.ai/)
* 💻 **Code Examples:** طل على  `codes/` في اليوم 8.

</div>

---

## 💾 شنية لازم يكون عندك في الآخر (Deliverables)

<div dir="rtl">

✨ **كي يوفى النهار، لازم تكون مريقل في هاذوم:**

* ✅ `01_WhatAreEmbeddings` — فهمت شنوة embedding وكيفاش النص يولي vector.
* ✅ `02_SimilarityMetrics` — تنجم تحسب cosine similarity بيدك وتعرف علاش هو الأفضل لل Text.
* ✅ `03_ChromaDBBasics` — ركبت ChromaDB، عملت collection، زدت documents، وحوست بـ semantic search.
* ✅ `04_QdrantBasics` — جربت Qdrant وفهمت الفرق بينها وبين ChromaDB.
* ✅ `05_TunisianRecipeSearch` — بنيت محرك بحث في وصفات تونسية.

</div>

---

## 💡 نصائح ماللخر (Tips)

<div dir="rtl">

* **الـ embedding model مهم برشا** — `mistral-embed` يخدم نظيف للعربي، الفرنساوي والأنڨليزي، ما تستعملش models قديمة.
* **الـ dimensions ما يتبدلوش** — لو كان بديت بـ 1024 dim، لازم كل الـ vectors في الـ collection يكونوا نفس الـ dimension. ما تخلطش.
* **Cosine similarity هو الستاندارد للنصوص** — Euclidean يخدم أما cosine خير خاطر النصوص الطويلة والقصيرة ينجموا يكونوا متقاربين.
* **خبي الـ embeddings ما تعاودش تحسبهم** — كل API call يتكلف، اعمل embed مرة برك وخبي في الـ DB.
* **ابدا بـ ChromaDB قبل Qdrant** — أبسط، embedded، وما تستحقش (server). Qdrant تستحقها كي يكبر المشروع (project).

</div>