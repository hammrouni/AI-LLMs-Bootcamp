# 01 - Environment Setup

---

## What is a Dependency?

A **dependency** is a library (a package of pre-written code) that your project NEEDS to work.

Think of it like cooking:
- Your recipe (your Python project) needs ingredients (libraries)
- If you need to make a cake, you depend on eggs, flour, sugar
- In Python, if you build an AI app, you depend on `openai`, `httpx`, `pydantic`, etc.

You install dependencies using pip:
```
pip install openai
pip install httpx
```

---

## What is Dependency Hell?

Imagine this real nightmare:

- **Project A** needs `library X version 1.0`
- **Project B** needs `library X version 3.0`
- Version 1.0 and 3.0 are NOT compatible (they changed things)
- You install both projects on your computer
- Now everything BREAKS because you can't have both versions at the same time

This is called **Dependency Hell** — when different projects need conflicting versions of the same library, and they fight each other and break.

---

## What is the Solution? Virtual Environments!

A **virtual environment** is like a **separate room** for each project.

- Each room has its OWN copy of Python and its OWN libraries
- Project A's room has `library X version 1.0`
- Project B's room has `library X version 3.0`
- They NEVER interfere with each other

Your computer stays clean. Your projects stay isolated.

---

## venv vs Conda — What's the Difference?

| Feature | venv | conda |
|---|---|---|
| Built into Python? | YES (no install needed) | NO (must install Anaconda/Miniconda) |
| Manages Python version? | NO (uses whatever Python you have) | YES (can install Python 3.9, 3.11, etc.) |
| Manages non-Python packages? | NO | YES (C libraries, CUDA, etc.) |
| Speed | Fast | Slower |
| Best for | Pure Python projects | Data Science, ML, AI with native deps |

---

## How to Choose?

**Use `venv` when:**
- You are doing web apps, APIs, scripts
- You just need Python libraries
- You want something simple and fast
- This bootcamp — venv is perfect

**Use `conda` when:**
- You are doing Machine Learning / Deep Learning
- You need packages like TensorFlow, PyTorch with GPU support
- You need to manage multiple Python versions on one machine

---

## Quick Commands Reference

### Using venv (recommended for this bootcamp)
```bash
# Create a virtual environment called "bootcamp"
python -m venv bootcamp

# Activate it (Windows)
bootcamp\Scripts\activate

# Activate it (Mac/Linux)
source bootcamp/bin/activate

# You will see (bootcamp) in your terminal — you are inside!

# Install packages
pip install httpx pydantic instructor

# Save your dependencies to a file
pip freeze > requirements.txt

# Install from that file (for sharing with teammates)
pip install -r requirements.txt

# Deactivate (exit the environment)
deactivate
```
