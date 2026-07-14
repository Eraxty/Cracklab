from pathlib import Path
import re
from analysis.dict import PatternDictionary
from analysis.evaluator import evaluate_candidate
from analysis.eng_words import (
    WORD_SET,
    COMMON_WORDS,
    COMMON_BIGRAMS,
    COMMON_TRIGRAMS,
    COMMON_QUADGRAMS,
)

dictionary = PatternDictionary()
ROOT = Path(__file__).resolve().parent.parent
dictionary.load(ROOT / "data" / "cleaned_words.txt")

crack_text = (ROOT / "crack.txt").read_text(encoding="utf-8")
result_text = (ROOT / "results.txt").read_text(encoding="utf-8")

crack = re.findall(r"[A-Z]+", crack_text.upper())

def count_improvement(old_text, new_text):
    score = 0

    old_words = old_text.split()
    new_words = new_text.split()

    for old, new in zip(old_words, new_words):
        revealed = old.count("_") - new.count("_")
        score += revealed * 10

        if "_" in new:
            continue

        if new in WORD_SET:
            score += 100

        if new in COMMON_WORDS:
            score += 300

        for i in range(len(new) - 1):
            score += COMMON_BIGRAMS.get(new[i:i+2], 0)

        for i in range(len(new) - 2):
            score += COMMON_TRIGRAMS.get(new[i:i+3], 0)

        for i in range(len(new) - 3):
            score += COMMON_QUADGRAMS.get(new[i:i+4], 0)

    return score

def build_filtered(result_text):
    result = re.findall(r"[A-Z_]+", result_text.upper())
    pairs = list(zip(crack, result))

    filtered = []

    for cipher, plain in pairs:
        if "_" in plain and any(c.isalpha() for c in plain):
            filtered.append((cipher, plain))

    filtered.sort(
        key=lambda x: (
            len(dictionary.find_partial_matches(x[1], limit=None)),
            -len(x[1].replace("_", "")),
        )
    )

    return filtered

current_mapping = {}

while True:
    filtered = build_filtered(result_text)

    if not filtered:
        break

    cipher, pattern = filtered[0]

    print(f"\n{cipher} -> {pattern}")

    matches = dictionary.find_partial_matches(pattern, limit=10)

    scored = []

    best_score = float("-inf")
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
        if plaintext is None:
            continue

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

        print(f"{candidate:12} {score}")

        if score > best_score:
            best_score = score
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

(ROOT / "final_result.txt").write_text(result_text)
