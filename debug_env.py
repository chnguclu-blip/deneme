import sys
import os

print(f"Python Executable: {sys.executable}")
print(f"CWD: {os.getcwd()}")
print("Sys Path:")
for p in sys.path:
    print(f"  - {p}")

try:
    import dotenv
    print(f"dotenv found at: {dotenv.__file__}")
except ImportError as e:
    print(f"dotenv NOT found: {e}")

try:
    from dotenv import load_dotenv
    print("load_dotenv imported successfully")
except ImportError as e:
    print(f"load_dotenv import FAILED: {e}")
