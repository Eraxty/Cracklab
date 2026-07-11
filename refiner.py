from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent

crack_text = (ROOT / "crack.txt").read_text(encoding="utf-8")
result_text = (ROOT / "results.txt").read_text(encoding="utf-8")

crack = re.findall(r"[A-Z]+", crack_text.upper())
result = re.findall(r"[A-Z_]+", result_text.upper())
pairs = list(zip(crack, result))

print(pairs)