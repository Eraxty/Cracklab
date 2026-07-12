from pathlib import Path
import re
from analysis.dict import PatternDictionary
from analysis.evaluator import evaluate_candidate
from analysis.english_scorer import WORD_SET

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

def count_improvement(old_text, new_text):
    score = 0
    old_words = old_text.split()
    new_words = new_text.split()
    for old, new in zip(old_words, new_words):
        score += old.count("_") - new.count("_")
        if "_" not in new and new in WORD_SET:
            score += 100
    return score

cipher, pattern = filtered[0]
print(cipher)
print(pattern)

matches = dictionary.find_partial_matches(pattern, limit=10)

best_score = float("-inf")
best_word = None
best_plaintext = None
best_mapping = None

for m in matches:
    candidate = m["word"]

    plaintext, mapping = evaluate_candidate(
        crack,
        current_mapping,
        cipher,
        pattern,
        candidate,
    )

    words = plaintext.split()
    words[crack.index(cipher)] = candidate
    plaintext = " ".join(words)
    score = count_improvement(result_text, plaintext)
    print(f"{candidate:10} {score}")
    if score > best_score:
        best_score = score
        best_word = candidate
        best_plaintext = plaintext
        best_mapping = mapping

print()
print("winner:", best_word)
print("score:", best_score)
print(best_mapping)
print()
print(best_plaintext)