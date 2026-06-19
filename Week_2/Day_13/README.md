<div dir="rtl">

# 📅 اليوم 13: Local Model Optimization 🚀

# نخلّيو الـ local models أسرع، أخف، وحاضرين للـ production — quantization، GPU، و context caching

</div>

---
<div dir="rtl">

## 🎯 الهدف متاع اليوم

**نهار الـ tuning**. البارح ركّبنا Ollama وعملنا RAG . اليوم باش نخلّيو الـ models يخدموا أسرع ويخلّيو الـ RAM مسيّبة للـ apps لُخرا — quantization، GPU acceleration، context-aware caching، و throughput measurement.

في لخر، باش يكون عندك local stack حاضر للـ production يخدم على نفس الـ hardware اللي ما كانش يكفيك البارح.

</div>

---
<div dir="rtl">

## 📚 المفاهيم الأساسية (Key Concepts)

* **Hardware Requirements:** علاش الـ RAM والـ VRAM يلعبوا دور كبير، وكيفاش تقيس شنية تستحق بالضبط.
* **Quantization:** كيفاش نحوّلو FP16 لـ Q4_K_M وننقّصوا مالـ memory بـ 4 مرات من غير ما نخسرو برشا فالـ quality.
* **GPU Acceleration:** CUDA للـ Windows/Linux، و Metal للـ Mac. كيفاش تخلّي Ollama يخدم بالـ GPU.
* **Measuring Latency & Throughput:** tokens/second، time-to-first-token (TTFT)، وكيفاش تقيسهم.
* **Production Local RAG (Capstone):** نبنيوا نظام RAG محلي مع caching، quantized model، و monitoring.

</div>

---
<div dir="rtl">

## 🛠️ كيفاش تبدا تخدم (Steps to Complete Today)

**الخطة باش تراجع وتطبق نهارك:**

1️⃣ **اقرأ ملف `concept.md` هو الأول** — لازم تفهم "علاش" قبل "كيفاش".
2️⃣ **خدّم (run) الـ `demo.py**` — شوف الكود "لايف" قدام عينيك كيفاش يتصرف.
3️⃣ **خلوضها وحدك** — جرب نفس الـ prompt بـ Q4، Q5، و Q8 وقارن بيناتهم فالـ latency والـ quality.

</div>

```bash
# 1. شعل الـ virtual environment متاعك
bootcamp\Scripts\activate     # Windows
source bootcamp/bin/activate  # Mac/Linux

# 2. صب الـ "سلعة" (packages) اللي باش تستحقها
pip install ollama psutil chromadb python-dotenv

# 3. تأكّد اللي Ollama يخدم وهبّط نماذج مختلفة
ollama serve
ollama pull mistral:7b-instruct-q4_K_M
ollama pull mistral:7b-instruct-q8_0

# 4. ابدا بالـ "البياسة" الأولى
cd codes\01_HardwareRequirements
python demo.py

```

---
<div dir="rtl">

## 📖 مراجع باش تزيد تشيخ (Resources)

* 📚 **GGUF Quantization Levels:** [github.com/ggerganov/llama.cpp#quantization](https://github.com/ggerganov/llama.cpp#quantization)
* 📚 **Ollama Modelfile Reference:** [github.com/ollama/ollama/blob/main/docs/modelfile.md](https://github.com/ollama/ollama/blob/main/docs/modelfile.md)
* 📚 **NVIDIA System Management:** `nvidia-smi`
* 💻 **Code Examples:** طل على الدوسي `codes/` في اليوم 13.

</div>

---
<div dir="rtl">

## 💾 شنية لازم يكون عندك في الآخر (Deliverables)

✨ **كي يوفى النهار، لازم تكون مريڤل في هاذوم:**

* ✅ `01_HardwareRequirements` — تنجم تحسب الـ RAM والـ VRAM اللي يستحقها أي model.
* ✅ `02_Quantization` — فهمت الفرق بين Q2، Q4، Q5، و Q8 وجربت زوز منهم على الأقل.
* ✅ `03_GPUAcceleration` — الـ Ollama يستعمل الـ GPU متاعك (إذا عندك كعبة) وقست قداش سرّعلك الخدمة (speedup).
* ✅ `04_MeasuringLatency` — تنجم تقيس الـ tokens/sec والـ TTFT بالصحيح.
* ✅ `05_ProductionLocalRAG` — بنيت RAG محلي مع response caching و monitoring.

</div>

---

<div dir="rtl">

## 💡 نصائح ماللخر (Tips)

* **Q4_K_M هو الـ sweet spot (الأحسن)** — يعطيك quality قريبة للـ Q8 وياخو 4 مرات أقل memory.
* **GPU offloading partial** — حتى لو كان الـ GPU متاعك صغيرة، تنجم تحط عليها شوية مالـ layers بـ `OLLAMA_NUM_GPU_LAYERS`.
* **ركّز مع الـ first-token times** — الـ TTFT هو اللي يحس بيه الـ user، مش الـ total time.
* **caching على الـ system prompt** — كي يبدا عندك prompt ثابت، Ollama يخبّي الـ KV cache والـ requête (الطلب) الجديد يولّي أسرع برشا.
* **ما تقيسش مرة وحدة برك** — التاست الأول ديما يكون "cold"، خوذ الـ moyenne (المتوسط) متاع 5 محاولات بعد ما تعمل warmup.

</div>