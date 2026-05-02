# 📅 اليوم 1: Modern Python & AI APIs Stack

<div dir="rtl">

# مقدمة لأدوات الـ AI وأساسيات Python الحديثة

</div>

---

## 🎯 Today's Goal

<div dir="rtl">

**باش نفهمو الباز متاع الـ Python الحديث (Modern Python) والأدوات اللي نستحقوها باش نبنيو AI Apps صحاح.**

على خاطر باش نقدرو نستعملو الـ APIs بالقدى ونجيبو منهم داتا منظمة، لازمنا نكونو طيارات ومتمكنين من حكايات كيما الـ Async، الـ Data Validation، والـ Structured Outputs.

</div>

---

## 📚 Key Concepts

<div dir="rtl">

- **الـ Environment (`venv`):** كيفاش تعزل الـ projets متاعك باش ما تدخلش الـ libraries في حيط.
- **الـ Async/Await (`asyncio`):** كيفاش تخلّي الكود متاعك يخدم برشا حاجات في نفس الوقت من غير ما يتبلوكا (non-blocking).
- **الـ HTTP Requests (`httpx`):** كيفاش تبعث وتستقبل داتا مالـ APIs بطريقة asynchrone وrapide.
- **الـ Data Validation (`Pydantic`):** كيفاش تضمن اللي الداتا الجاية صحيحة ومريڤلة وما تطيحلكش الكود.
- **الـ Structured AI Output (`Instructor`):** كيفاش تجبر الـ AI باش يرجّعلك داتا منظمة (كيما JSON ولا Pydantic Models) في عوض كتيبة مسيبة.

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
# 1. نصنعو virtual environment ونخدموه
python -m venv bootcamp
bootcamp\Scripts\activate     # Windows
source bootcamp/bin/activate  # Mac/Linux

# 2. نصبّو لي packages اللي باش نستحقوهم
pip install httpx pydantic instructor openai

# 3. نبداو ماللول
cd 01_Environment
python demo.py
```

---

## 📖 Resources

- 💻 **Python Basics & Asyncio:** [python.org/docs](https://python.org/docs)
- 🚀 **HTTPX Docs:** [www.python-httpx.org](https://www.python-httpx.org/)
- 📘 **Pydantic Docs:** [docs.pydantic.dev](https://docs.pydantic.dev/)
- 🤖 **Instructor Docs:** [python.useinstructor.com](https://python.useinstructor.com/)
- 📚 **Code Examples:** Check the `codes/` folder for Day 1 examples

---

## 💾 Expected Deliverables

<div dir="rtl">

✨ **في لخر متاع النهار، لازم يكون عندك:**

- ✅ `01_Environment` — فهمت كيفاش تعزل الـ projet متاعك بـ venv.
- ✅ `02_Async_Await` — كتبت كود يخدم asynchrone بـ asyncio.
- ✅ `03_HTTPX` — بعثت async HTTP requests بـ httpx.
- ✅ `04_Pydantic` — استعملت pydantic باش تفاليدي (valider) الداتا متاعك.
- ✅ `05_Instructor` — جبت output مريڤل و structured مالـ AI.

</div>

---

## 💡 Tips

<div dir="rtl">

- **ما تزربش روحك!** الفهم أهم مالسرعة.
- **اسأل** كان فمّا حكاية ما فهمتهاش.
- **جرّب وحدك** راو الممارسة والتخلويض هوما اللي يعلموك بالرسمي.

</div>