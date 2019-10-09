
from runpy import run_path

func = run_path("./func.py")

print("TEST 1")
(func.get("test"))()
print("TEST 2")
