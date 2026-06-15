# 📅 اليوم 9: Advanced Vector Databases 🚀

<div dir="rtl">

# نحوّلو الـ vector DB من prototype لحاجة جاهزة للـ production بـ collections متعددة، metadata filtering، و batch ops

</div>

---
<div dir="rtl">

## 🎯 الهدف متاع اليوم

**نهار الـ "scale up"**. الـ embeddings فهمناهم البارح، اليوم باش نتعلّمو كيفاش نتحكموا في الـ vector DB كي يكبر — collections متعددة، filtering ذكي، insert بالـ batch، و indexing فيه performance قوي.

 تبني في RAG، ولا AI search، ولا recommendation system لازم تتعدّى بالأدوات هاذوم. هذا هو نهار الـ "professional" متاع الـ vector databases.

</div>

---
<div dir="rtl">

## 📚 المفاهيم الأساسية (Key Concepts)

* **إدارة المجموعات (Collection Management):** كيفاش تنظّم datas في collections مختلفة (recipes، users، products)، وعلاش لازم ما تخلطش بيناتهم.
* **الفلترة ب Metadata (Metadata Filtering):** البحث بالـ vector ما يكفيش ساعات تحب تفلتر بالـ region (المنطقة)، الـ price (السوم)، ولا الـ date (التاريخ). هذي هي قوة الـ vector DB الحقيقية.
* **Batch Operations:** تعمل insert لـ 100 وثيقة كعبة كعبة = 100 API call. أما كيف تعمل الـ insert بالـ batch = يتسمّى call واحد برك. الفرق في الـ speed (السرعة) والـ cost (التكلفة) كبير برشا.
* **الفهرسة (Indexing & Performance):** كيفاش تخلي الـ search سريع حتى كي تبدأ عندك مليون vector.
* **Tunisian Product Catalog:** نبنيوا vector DB كامل لـ كاتالوغ (catalog) متاع منتجات تونسية مع filtering بالـ region، الـ prix، والـ category.

</div>

---
<div dir="rtl">

## 🛠️ كيفاش تبدا تخدم (Steps to Complete Today)

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
pip install chromadb qdrant-client mistralai python-dotenv

# 3. ريڤل الـ .env وحط فيه الـ API key
copy codes\.env.example codes\.env
# احل codes\.env وحط MISTRAL_API_KEY=your_key_here

# 4. نبداو ماللول
cd codes\01_CollectionManagement
python demo.py

```

---
<div dir="rtl">

## 📖 مراجع باش تزيد تشيخ (Resources)

* 📚 **ChromaDB Filtering:** [docs.trychroma.com/usage-guide#using-where-filters](https://docs.trychroma.com/usage-guide)
* 📚 **Qdrant Filtering:** [qdrant.tech/documentation/concepts/filtering](https://qdrant.tech/documentation/concepts/filtering/)
* 📚 **HNSW Algorithm:** [arxiv.org/abs/1603.09320](https://arxiv.org/abs/1603.09320)
* 🤖 **Mistral API Docs:** [docs.mistral.ai](https://docs.mistral.ai/)
* 💻 **Code Examples:** طل على الدوسي `codes/` في اليوم 9.

</div>

---
<div dir="rtl">

## 💾 شنية لازم يكون عندك في الآخر (Deliverables)


✨ **كي يوفى النهار، لازم تكون مريقل في هاذوم:**

* ✅ `01_CollectionManagement` — تعرف تصنع، تفسّخ، وتنظّم collections متعددة.
* ✅ `02_MetadataFiltering` — تنجم تكتب where clauses معقدة (AND/OR/IN/range) في ChromaDB و Qdrant.
* ✅ `03_BatchOperations` — تستعمل bulk insert/update وتعرف علاش هو أسرع برشا.
* ✅ `04_IndexingPerformance` — فهمت HNSW وكيفاش تختار الـ index parameters.
* ✅ `05_TunisianProductCatalog` — بنيت catalog vector DB مع filtering جاهز للـ production.

</div>

---
<div dir="rtl">

## 💡 نصائح ماللخر (Tips)


* **collection واحدة لنوع بيانات واحد** — ما تخلطش الـ recipes والـ products في collection وحدة، حتى لو كانوا embed بنفس الـ model.
* **الـ metadata رخيصة، استعملها برشا** — كل field تعرف روحك تنجم تحب تفلتر بيها مبعد، لازم تحطها في الـ metadata.
* **batch size بين 50 و 200** هو الـ sweet spot (الأحسن) في الأغلب — أقل = wasted calls (مضيعة للـ calls)، أكثر = ريسك متاع timeout.
* **HNSW = الـ default الصحيح** للـ vector search — قيم كيف m=16 و ef_construction=200 يخدموا نظاف في الغالب.
* **خبي الـ embeddings backup** — لو كان يفسد الـ index، الـ recomputation (إعادة الحساب) تتكلف برشا. خبي ملف JSON فيه الـ raw vectors.

</div>