from pathlib import Path

from analysis.eng_words import (
    COMMON_LETTERS,
    COMMON_BIGRAMS,
    COMMON_TRIGRAMS,
    COMMON_ENDINGS,
    VOWELS,
    RARE_PENALTY,
)
from analysis.patterns import word_pattern


def _score_letter_frequency(word):
    score = 0
    for letter in word:
        if letter in COMMON_LETTERS:
            score += len(COMMON_LETTERS) - COMMON_LETTERS.index(letter)
    return score


def _score_bigrams(word):
    score = 0
    for i in range(len(word) - 1):
        if word[i:i + 2] in COMMON_BIGRAMS:
            score += 10
    return score


def _score_trigrams(word):
    score = 0
    for i in range(len(word) - 2):
        if word[i:i + 3] in COMMON_TRIGRAMS:
            score += 18
    return score


def _score_vowel_pattern(word):
    vowels = sum(1 for letter in word if letter in VOWELS)
    if vowels == 0:
        return -20

    ratio = vowels / len(word)

    if 0.25 <= ratio <= 0.6:
        return 15

    return 0


def _score_rare_letters(word):
    penalty = 0

    for letter in word:
        if letter in RARE_PENALTY:
            penalty += RARE_PENALTY[letter]

    return penalty


def _score_word(word, common_words):
    score = 0

    score += _score_letter_frequency(word)
    score += _score_bigrams(word)
    score += _score_trigrams(word)
    score += _score_vowel_pattern(word)
    score += _score_rare_letters(word)

    if word.endswith(COMMON_ENDINGS):
        score += 8

    if word in common_words:
        score += 500

    return score


def _is_consistent_with_mapping(word, cipher_word, mapping):
    plain_to_cipher = {v: k for k, v in mapping.items()}

    for cipher_letter, plain_letter in zip(cipher_word.upper(), word.upper()):
        if cipher_letter in mapping and mapping[cipher_letter] != plain_letter:
            return False

        if (
            plain_letter in plain_to_cipher
            and plain_to_cipher[plain_letter] != cipher_letter
        ):
            return False

    return True


class PatternDictionary:
    def __init__(self):
        self.patterns = {}
        self.pattern_stats = {}
        self.pattern_words = {}
        self.common_words = set()

    def load(self, filename, common_words_path=None):
        if common_words_path is None:
            common_words_path = Path(filename).parent / "common_words.txt"

        try:
            with open(common_words_path, encoding="utf-8") as f:
                self.common_words = {
                    line.strip().upper()
                    for line in f
                    if line.strip()
                }
        except FileNotFoundError:
            self.common_words = set()

        with open(filename, encoding="utf-8") as file:
            for line in file:
                word = line.strip().upper()

                if not word or not word.isalpha():
                    continue

                pattern = word_pattern(word)

                candidate = {
                    "word": word,
                    "length": len(word),
                    "pattern": pattern,
                    "score": _score_word(word, self.common_words),
                }

                if pattern not in self.patterns:
                    self.patterns[pattern] = []
                    self.pattern_words[pattern] = set()
                    self.pattern_stats[pattern] = {
                        "pattern": pattern,
                        "length": len(word),
                        "count": 0,
                    }

                if word in self.pattern_words[pattern]:
                    continue

                self.pattern_words[pattern].add(word)
                self.patterns[pattern].append(candidate)
                self.pattern_stats[pattern]["count"] += 1

        for pattern, candidates in self.patterns.items():
            candidates.sort(
                key=lambda c: (-c["score"], c["length"], c["word"])
            )

    def find_matches(self, cipher_word, limit=20, mapping=None):
        pattern = word_pattern(cipher_word.strip().upper())
        matches = self.patterns.get(pattern, [])

        if mapping:
            matches = [
                match
                for match in matches
                if _is_consistent_with_mapping(
                    match["word"],
                    cipher_word,
                    mapping,
                )
            ]

        results = [
            {
                "word": match["word"],
                "pattern": match["pattern"],
                "length": match["length"],
            }
            for match in matches
        ]

        if limit is None:
            return results

        return results[:limit]

    def find_partial_matches(self, pattern, limit=None):
        pattern = pattern.upper()
        results = []

        for candidates in self.patterns.values():
            for candidate in candidates:
                word = candidate["word"]

                if len(word) != len(pattern):
                    continue

                if all(
                    p == "_" or p == c
                    for p, c in zip(pattern, word)
                ):
                    results.append(
                        {
                            "word": word,
                            "pattern": candidate["pattern"],
                            "length": candidate["length"],
                        }
                    )

        if limit is None:
            return results

        return results[:limit]

    def get_pattern_stats(self, pattern):
        return self.pattern_stats.get(
            pattern,
            {
                "pattern": pattern,
                "length": len(pattern),
                "count": 0,
            },
        )