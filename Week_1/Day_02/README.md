# 📅 اليوم 2: Professional API Integration

<div dir="rtl">

# كيفاش نتعاملو مع الـ APIs بطريقة احترافية (Pro)

</div>

---

## 🎯 Today's Goal

<div dir="rtl">

**باش نخدمو الـ APIs بطريقة Pro وكاسحة — نحميو الكود متاعنا مالـ bugs، نعاودو المحاولة (retry) بذكاء، ونعسو على كل شي.**

على خاطر الـ AI APIs ينجمو يطيحو ساعات — كونيكسيون تقص، rate limits، مشاكل فالـ server — لازمنا نكونو حاضرين للضربات الكل وما نخليوش الـ app متاعنا تتبلنتا.

</div>

---

## 📚 Key Concepts

<div dir="rtl">

- **التعامل مع الـ Bugs (`Error Handling`):** كيفاش تفهم أنواع لي errors (401, 429, 500) وتركحهم بـ `try/except` من غير ما يطيحلك الكود.
- **الـ Retry Logic (`tenacity`):** كيفاش تعاود تبعث الـ request بذكاء بـ exponential backoff و jitter باش ما تطيّحش الـ server.
- **الـ Streaming (`httpx` + `openai`):** كيفاش تجيب الـ response الطويلة كعبة كعبة (token بـ token) في عوض تستنى للخر — كيما ChatGPT بالظبط.
- **حساب الـ Tokens (`Token Usage`):** كيفاش تقرا الـ `usage` مالـ response وتحسب قداش تكلفتلك كل request.
- **الـ Logging:** كيفاش تقيّد كل request، كل bug، وقداش شدّت وقت في فيتشيي (fichier) باش تنجم تعس عالـ app متاعك.

</div>

---

## 🛠️ Steps to Complete Today

<div dir="rtl">

**كيفاش تقرا وتريفز كل نهار (Day):**

1️⃣ **اقرا `concept.md` ماللول** — افهم علاش (WHY) قبل كيفاش (HOW)
2️⃣ **راني (run) `demo.py`** — شوف الكود كيفاش يخدم قدام عينيك
3️⃣ **جرّب وحدك** — بدّل لي فالور (values)، فرعسو وخليه يتبلّنتا (يطيح)، وشوف شنوة يصير

</div>

```bash
# 1. نخدمو الـ virtual environment
bootcamp\Scripts\activate     # Windows
source bootcamp/bin/activate  # Mac/Linux

# 2. نصبّو لي packages اللي باش نستحقوهم
pip install httpx python-dotenv openai tenacity

# 3. نعملو فيتشيي .env ونحطو فيه الـ API key متاعنا
copy codes\.env.example codes\.env
# افتحو codes\.env وحطو MISTRAL_API_KEY=your_key_here

# 4. نبداو ماللول
cd codes\01_Error_Handling
python demo.py
```

---

## 📖 Resources

- 🚀 **HTTPX Docs:** [www.python-httpx.org](https://www.python-httpx.org/)
- 🤖 **Mistral API Docs:** [docs.mistral.ai](https://docs.mistral.ai/)
- 📘 **Python Exceptions:** [docs.python.org/3/tutorial/errors.html](https://docs.python.org/3/tutorial/errors.html)
- 🔁 **tenacity Docs:** [tenacity.readthedocs.io](https://tenacity.readthedocs.io/)
- 📋 **Python logging:** [docs.python.org/3/howto/logging.html](https://docs.python.org/3/howto/logging.html)
- 📚 **Code Examples:** Check the `codes/` folder for Day 2 examples

---

## 💾 Expected Deliverables

<div dir="rtl">

✨ **في لخر متاع النهار، لازم يكون عندك:**

- ✅ `01_Error_Handling` — فهمت أنواع لي errors وكتبت `safe_api_call` يريڤلهم الكل.
- ✅ `02_Retry_Logic` — خدمت بالـ exponential backoff مع الـ jitter وعرفت وقتاش تعاود تبعث ووقتاش تسيّب عليك.
- ✅ `03_Streaming` — جبت الـ response متاع الـ AI كعبة كعبة (token بـ token) بـ httpx وبالـ OpenAI SDK.
- ✅ `04_Token_Usage` — قيّدت الـ prompt/completion tokens وحسبت قداش تكلفتلك كل request.
- ✅ `05_Logging` — صنعت سيستام logging يكتب فالـ terminal وفي فيتشيي دايم مع الـ rotation.

</div>

---

## 💡 Tips

<div dir="rtl">

- **تستي لي errors بلعاني** — حط key غالط باش تشوف الـ 401، وقص الكونيكسيون باش تشوف الـ ConnectError.
- **ما تعاودش تبعث ديريكت** — الـ exponential backoff مجعول لحكاية، خلي الـ server يتنفس شوية.
- **لوڤي (Log) كل شي** — راك مبعد باش ترحم على والديك عالـ logs كي توحل وتحب تفهم شنية الخلوضة اللي صارت.
- **الـ Mistral تخدم مريڤلة مع الـ OpenAI SDK** — على خاطرها compatible مع الـ format متاع OpenAI، نجمو نستعملو الـ `openai` SDK في عوض نكتبو كود HTTP مالصفر.

</div>