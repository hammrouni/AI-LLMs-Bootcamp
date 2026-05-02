"""
01 - Environment Demo
=====================
This file shows you what dependencies look like in code,
and how Python knows which packages are available.

HOW TO RUN THIS FILE:
1. Create a virtual environment:   python -m venv bootcamp-env
2. Activate it (Windows):          bootcamp-env\Scripts\activate
3. Install packages:               pip install httpx pydantic
4. Run this file:                  python demo.py
"""

# ============================================================
# PART 1: What is a dependency?
# ============================================================
# These lines IMPORT dependencies (libraries we need)
# If these are not installed, Python will throw an ImportError

import os           # Built-in — comes with Python, no install needed
import sys          # Built-in — comes with Python, no install needed

# This is a THIRD-PARTY dependency — must be installed with pip
# If not installed, you'll see: ModuleNotFoundError: No module named 'httpx'
try:
    import httpx
    print("httpx is installed! Version:", httpx.__version__)
except ImportError:
    print("httpx is NOT installed. Run: pip install httpx")

try:
    import pydantic
    print("pydantic is installed! Version:", pydantic.__version__)
except ImportError:
    print("pydantic is NOT installed. Run: pip install pydantic")


# ============================================================
# PART 2: Check where Python is running from
# ============================================================
print("\n--- Your Python Environment Info ---")
print("Python version:", sys.version)
print("Python location:", sys.executable)
# If you activated a venv, the path will include "bootcamp-env"
# If not, it will point to your system Python


# ============================================================
# PART 3: Show installed packages
# ============================================================
print("\n--- Checking installed packages ---")
import subprocess
result = subprocess.run(
    [sys.executable, "-m", "pip", "list"],
    capture_output=True,
    text=True
)
# Show only first 15 packages so output is not too long
packages = result.stdout.strip().split("\n")
print(f"You have {len(packages) - 2} packages installed:")
for package in packages[:10]:  # Show first 10
    print(" ", package)
print("  ... and more")


# ============================================================
# PART 4: Demonstrate why isolation matters
# ============================================================
print("\n--- Why Isolation Matters ---")
print("Your current Python is at:", sys.executable)
print()
print("If you see 'bootcamp-env' in that path — GREAT! You are isolated.")
print("If you see your system Python path — activate your venv first!")
print()
print("The point: each project gets its OWN Python and packages.")
print("No conflicts. No dependency hell.")
