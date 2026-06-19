
<div dir="rtl">

# 📅 اليوم 12: Local Models with Ollama 🚀

# نخدمو الـ LLMs على أجهزتنا — بلاش API key، بلاش cloud، وبلاش فلوس

</div>

---
<div dir="rtl">

## 🎯 الهدف متاع اليوم

اليوم باش نتعلّمو كيفاش نخدمو نماذج LLM على لابتوب (بيسي) عادي، بلاش cloud وبلاش اشتراكات (subscriptions)، باستعمال Ollama.

علاش هذا مهم؟ على خاطر الـ data residency (وين تتخبى البيانات)، الـ privacy (الخصوصية)، الـ cost (التكلفة)، والـ offline use (الخدمة بلاش إنترنت). كل شركة تونسية عندها concerns (مخاوف أو شروط) على البيانات متاعها (بنوك، صحة، حكومة) لازمها تعرف الـ stack هذا.

</div>

---
<div dir="rtl">

## 📚 المفاهيم الأساسية (Key Concepts)

* **شنوة هو Ollama:** أداة تخليك تهبّط وتخدم الـ LLMs Local بأمر (command) واحد برك. عبارة على Docker أما مخدوم للنماذج (models).
* **Installing & Running Locally:** كيفاش تهبّط Ollama، وتشارجي model (كيف llama3، mistral، ولا phi3)، وتخدم معاه مالـ terminal مباشرة.
* **اختيار النموذج (Choosing a Model):** الفرق بين 3B، 7B، و 13B parameters. كيفاش تختار النموذج المناسب حسب الـ RAM و الـ use case متاعك.
* **كود بايثون (Python Client):** الـ library متاع ollama في بايثون — تخليك تعمل chat، generate، وتطلع الـ embeddings الكلها مالكود مباشرة.
* **الـ RAG بلاش إنترنت (Offline RAG - Capstone):** نبنيوا نظام RAG كامل يخدم بلاش إنترنت — باستعمال Mistral 7B ومعاه ChromaDB.

</div>

---
<div dir="rtl">

## 🛠️ كيفاش تبدا تخدم (Steps to Complete Today)

**الخطة باش تراجع وتطبق نهارك:**

1️⃣ **اقرأ ملف `concept.md` هو الأول** — لازم تفهم "علاش" قبل "كيفاش".
2️⃣ **ركّب Ollama** — هبّطو من الموقع [ollama.com](https://ollama.com) وشغّل `ollama serve`.
3️⃣ **خدّم (run) الـ `demo.py**` — شوف الكود "لايف" قدام عينيك كيفاش يتصرف.
4️⃣ **خلوضها وحدك** — بدّل الـ model (`mistral`, `llama3`, `phi`)، وقيس الـ latency والـ quality.

</div>

```bash
# 1. ركّب Ollama (مرة وحدة برك)
# Windows: هبّط الـ installer من ollama.com
# Mac:     brew install ollama
# Linux:   curl -fsSL https://ollama.com/install.sh | sh

# 2. خدم Ollama في الـ background
ollama serve

# 3. هبّط الـ model
ollama pull mistral
ollama pull nomic-embed-text

# 4. خدم الـ virtual environment متاعك
bootcamp\Scripts\activate     # Windows
source bootcamp/bin/activate  # Mac/Linux

# 5. صب الـ packages اللي باش تستحقهم
pip install ollama chromadb langchain-text-splitters python-dotenv

# 6. ابدا بالـ "البياسة" الأولى
cd codes\01_OllamaSetup
python demo.py

```

---
<div dir="rtl">

## 📖 مراجع باش تزيد تشيخ (Resources)

* 📚 **Ollama Website:** [ollama.com](https://ollama.com)
* 📚 **Ollama Library:** [ollama.com/library](https://ollama.com/library)
* 📚 **Python Client:** [github.com/ollama/ollama-python](https://github.com/ollama/ollama-python)
* 💻 **Code Examples:** طل على الدوسي `codes/` في اليوم 12.

</div>

---
<div dir="rtl">

## 💾 شنية لازم يكون عندك في الآخر (Deliverables)

✨ **كي يوفى النهار، لازم تكون مريڤل في هاذوم:**

* ✅ `01_OllamaSetup` — الـ Ollama مركّب ويخدم في الـ background. والأمر `ollama list` يوريك model واحد على الأقل.
* ✅ `02_RunningLocally` — كتبت أول chat محلي وفهمت الفرق بين `chat` و `generate`.
* ✅ `03_ChoosingAModel` — جربت 2 models مختلفين وفهمت الـ trade-off بين الـ size والـ quality.
* ✅ `04_PythonClient` — كتبت كود Python يخدم مع Ollama (chat، embed، و streaming).
* ✅ `05_OfflineRAG` — بنيت RAG كامل يخدم بلاش إنترنت (الـ LLM والـ embeddings الزوز محليين).

</div>

---
<div dir="rtl">

## 💡 نصائح ماللخر (Tips)


* **ابدا بـ Mistral 7B Instruct** — يعطيكم أحسن trade-off بين الـ quality والـ RAM (يستحسن تكون عندك 8GB RAM).
* **خلي Ollama يخدم في الـ background** — تعمل `ollama serve` مرة وحدة برك، ومبعد الـ scripts الكل يتصلوا على البورت :11434.
* **تستعمل `nomic-embed-text` للـ embeddings المحلية** — بلاش فلوس، فيه 768 dim، ويخدم نظيف ومريڤل.
* **الـ streaming يعطيك إحساس خير برشا** — الـ output تطلع كعبة كعبة (token-by-token) خير ملي تقعد تستنى في فقرة كاملة تحضر.
* **ما تستناش الـ quality متاع mistral-large محلياً** — نموذج 7B محلي يقرب لـ gpt-3.5 ومش gpt-4، أما يقضي الشور ويخدم مريڤل.

</div>