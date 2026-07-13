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

def build_filtered(result_text):
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
    return filtered


current_mapping = {}

while True:
    filtered = build_filtered(result_text)

    if not filtered:
        break

    cipher, pattern = filtered[0]

    print(cipher)
    print(pattern)

    matches = dictionary.find_partial_matches(pattern, limit=10)
    scored = []

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

        scored.append((
            score,
            plaintext,
            mapping,
            candidate,
        ))

        print(f"{candidate:10} {score}")

        if score > best_score:
            best_score = score
            best_word = candidate
            best_plaintext = plaintext
            best_mapping = mapping

    scored.sort(
        key=lambda x: x[0],
        reverse=True,
    )

    best = scored[:5]

    print()

    for score, plaintext, mapping, candidate in best:
        print(candidate)
        print(score)
        print(mapping)
        print()

    if best_mapping is None:
        break

    if best_score <= 0:
        break

    current_mapping = best_mapping.copy()
    result_text = best_plaintext

(ROOT / "final_result.txt").write_text(result_text)