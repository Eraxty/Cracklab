from pathlib import Path
import re
from analysis.dict import PatternDictionary

dictionary = PatternDictionary()
dictionary.load("data/cleaned_words.txt")

ROOT = Path(__file__).resolve().parent

crack_text = (ROOT / "crack.txt").read_text(encoding="utf-8")
result_text = (ROOT / "results.txt").read_text(encoding="utf-8")

crack = re.findall(r"[A-Z]+", crack_text.upper())
result = re.findall(r"[A-Z_]+", result_text.upper())

pairs = list(zip(crack, result))

filtered = []

for cipher, plain in pairs:
    if "_" in plain and any(c.isalpha() for c in plain):
        filtered.append((cipher, plain))

filtered.sort(
    key=lambda x: len(x[1].replace("_", "")),
    reverse=True,
)

for cipher, pattern in filtered:
    print(f"\n{cipher} = {pattern}")

    matches = dictionary.find_partial_matches(pattern, limit=10)

    for m in matches:
        print("   ", m["word"])