# 📅 اليوم 3: Advanced Prompt Engineering 🚀

<div dir="rtl">

# أعرف كيفاش تحكي مع ال-AI

</div>

---

## 🎯 الهدف متاع اليوم

<div dir="rtl">

**اليوم باش نوليو "سنايعية" في الـ Prompt Engineering. باش تتعلم كيفاش تحكي مع للـ AI وتخليه يفهم بالظبط شنية تحب، ويرجعلك إجابات منظمة، ومريقلة تستعملها ديريكت في الكود متاعك.**

بما أنو الـ API متاعك تخدم، الـ Prompt هو "القلب" متاع السيستيم. ما ترميش أسئلة "عالحيط" وتستنى نتايج صحيحة. تعلم تخدم بذكاء وتحكم في الـ output كيما تحب إنتي.

</div>

---

## 📚 المفاهيم الصحيحة (Key Concepts)

<div dir="rtl">

- **الـ Chain of Thought (CoT):** قولو "وحدة وحدة يا صاحبي". خليه يفكّر خطوة بخطوة قبل ما يعطيك الجواب — هكا تضمن الدقة خاصة في الحساب والمنطق (Reasoning).
- **الـ Few-Shot Learning:** ما تبعثوش "عاري لابس". أعطيه كعبات أمثلة (2-5) قبل ما تسألو — باش يفهم الـ "ستيل" والـ "فورما" اللي تحب عليها ويتبّعها.
- **الـ System Prompts:** إنتي الـ "Patron" حدد دور الـ AI، شنية "الخطوط الحمراء"، وكيفاش يتكلم — كيما تصحح معاه "كنتراتو" قبل ما يبدا الخدمة.
- **الـ JSON Output:** خلي الـ AI يرجعلك "داتا" JSON منظمة — هكا تستعملها ديريكت في الكود متاعك من غير ما تكسر راسك مع الـ parsing.
- **الـ Prompt Comparison:** ما تخدمش "رعواني". قارن الـ prompts متاعك وشوف أنا هو اللي يعطي خير (Score, A/B test) ووحسن فيها شوي شوي.

</div>

---

## 🛠️ كيفاش تبدا تخدم (Steps to Complete Today)

<div dir="rtl">

**الخطة باش تريفز وتطبق نهارك:**

1️⃣ **أقرأ `concept.md` هو الأول** — لازم تفهم "علاش" قبل "كيفاش".
2️⃣ **خَدّم (run) الـ `demo.py`** — شوف الكود "لايف" قدام عينيك كيفاش يتصرف.
3️⃣ **خلوضها وحدك** — بدّل الـ prompts، بدّل الأمثلة، وشوف العجب كيفاش يتبدل في الـ output.

</div>

```bash
# 1. شعل الـ virtual environment متاعك
bootcamp\Scripts\activate     # Windows
source bootcamp/bin/activate  # Mac/Linux

# 2. صب الـ "سلعة" (packages) اللي باش تستحقها
pip install openai python-dotenv pydantic

# 3. ريكل الـ .env وحط فيه الـ API key
copy codes\.env.example codes\.env
# افتح codes\.env وحط MISTRAL_API_KEY=your_key_here

# 4. ابدا بالـ "البياسة" الأولى
cd codes\01_Chain_of_Thought
python demo.py
```

---

## 📖 مراجع باش تزيد تشيخ (Resources)

- 📚 **دليل OpenAI للـ Prompt Engineering:** [platform.openai.com/docs/guides/prompt-engineering](https://platform.openai.com/docs/guides/prompt-engineering)
- 📚 **الورقة البحثية متاع Chain of Thought:** [arxiv.org/abs/2201.11903](https://arxiv.org/abs/2201.11903)
- 🤖 **Mistral API Docs:** [docs.mistral.ai](https://docs.mistral.ai/)
- 📘 **Pydantic Docs (متاع الـ Validation):** [docs.pydantic.dev](https://docs.pydantic.dev/)
- 💻 **Code Examples:** طل على Dossier `codes/` في اليوم الثالث.

---

## 💾 شنية لازم يكون عندك في لخر (Deliverables)

<div dir="rtl">

✨ **كي يوفى النهار، لازم تكون مريقل في هاذوم:**

- ✅ `01_Chain_of_Thought` — فهمت كيفاش تخلي الـ AI يحلل المشاكل المعقدة.
- ✅ `02_Few_Shot` — وليت تعرف تعطي أمثلة تحسن الـ output.
- ✅ `03_System_Prompts` — ركبت سيستيم برومبت "قوي" يفرض هيبتو عالـ AI.
- ✅ `04_JSON_Output` — الـ AI ولا يرجعلك JSON نظيف ومثبّت بـ Pydantic.
- ✅ `05_Prompt_Comparison` — وليت تعرف تقارن بين الزوز برومبتات وتختار الرابح.

</div>

---

## 🔗 أيام عندها علاقة

- **البارح:** [اليوم 2 - Professional APIs](../Day_02/README.md)
- **غدوة:** [اليوم 4 - LangChain](../Day_04/README.md)

---

## 💡 نصائح ماللخر (Tips)

<div dir="rtl">

- **جرب وقارن** — نفس السؤال بـ برومبت مختلف يعطيك دنيا أخرى، هذا هو الـ "Logic" متاع الخدمة.
- **الـ CoT مش ديمة باهي** — ساعات تحب إجابة سريعة وديريكت، جرب الزوز وشوف شكون يسلكها خير.
- **الـ System Prompt = الكنتراتو** — كل ما كان واضح ومحدد، كل ما الـ AI خدم خدمتو "نظيفة".
- **كبّش في "ONLY JSON"** — كان ما تقولوش "خرجلي JSON وبرة"، الـ AI باش يبدا "يمرّج" فيك بالكتيبة الزايدة ويفسدلك الـ parsing.
- **ما تصلحش كل شيء مع بعضو** — كل مرة بدل حاجة بركة في الـ prompt باش تعرف شنوة اللي حسن النتيجة بالظبط.

</div>
```