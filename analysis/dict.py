from analysis.patterns import word_pattern
from pathlib import Path

COMMON_LETTERS = "ETAOINSHRDLCUMWFGYPBVKJXQZ"
COMMON_BIGRAMS = {
    "TH", "HE", "IN", "ER", "AN", "RE", "ON", "AT", "EN", "ND",
    "TI", "ES", "OR", "TE", "OF", "ED", "IS", "IT", "AL", "AR",
    "ST", "TO", "NT", "NG", "SE", "HA", "AS", "OU", "IO", "LE",
    "VE", "CO", "ME", "DE", "HI", "RI", "RO", "IC", "NE", "EA",
    "LL", "LO", "EL",
}
COMMON_TRIGRAMS = {
    "THE", "AND", "ING", "ION", "ENT", "HER", "FOR", "THA", "NTH",
    "INT", "ERE", "TIO", "TER", "EST", "ERS", "ATI", "HAT", "ATE",
    "ALL", "ELL",
}
COMMON_WORDS = {
    "A", "I",
    "ABOUT", "AFTER", "AGAIN", "ALSO", "BECAUSE", "BEEN", "BEFORE",
    "BEING", "BELLY", "BETTER", "BETWEEN", "BOTH", "COULD", "EVERY",
    "FIRST", "FOUND", "FROM", "GOOD", "GREAT", "HELLO", "HERE",
    "HOUSE", "INTO", "JUST", "KNOW", "LARGE", "LITTLE", "MADE",
    "MANY", "MORE", "MOST", "OTHER", "OVER", "PEOPLE", "PLACE",
    "RIGHT", "SAID", "SAME", "SHOULD", "SMALL", "SOME", "STILL",
    "SUCH", "TAKE", "THAN", "THAT", "THEIR", "THEM", "THEN",
    "THERE", "THESE", "THEY", "THING", "THINK", "THIS", "THOSE",
    "THREE", "TIME", "UNDER", "VERY", "WANT", "WATER", "WELL",
    "WERE", "WHAT", "WHEN", "WHERE", "WHICH", "WHILE",
    "WITH", "WORD", "WORK", "WORLD", "WOULD", "WRITE", "YEAR",
}
COMMON_ENDINGS = ("E", "ED", "ER", "ES", "ING", "ION", "LY", "S", "Y")
VOWELS = set("AEIOUY")

RARE_PENALTY = {"Q": -30, "X": -25, "Z": -30, "J": -20}


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


def _score_word(word, common_words_set):
    score = _score_letter_frequency(word)
    score += _score_bigrams(word)
    score += _score_trigrams(word)
    score += _score_vowel_pattern(word)
    score += _score_rare_letters(word)

    if word.endswith(COMMON_ENDINGS):
        score += 8

    if word in common_words_set:
        score += 500

    return score


def _is_consistent_with_mapping(word, cipher_word, mapping):
    plain_to_cipher = {v: k for k, v in mapping.items()}
    for cipher_letter, plain_letter in zip(cipher_word.upper(), word.upper()):
        if cipher_letter in mapping and mapping[cipher_letter] != plain_letter:
            return False
        if plain_letter in plain_to_cipher and plain_to_cipher[plain_letter] != cipher_letter:
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
            common_words_path = str(Path(filename).parent / "common_words.txt")

        try:
            with open(common_words_path) as f:
                self.common_words = {line.strip().upper() for line in f if line.strip()}
        except FileNotFoundError:
            self.common_words = set()

        with open(filename) as file:
            for line in file:
                word = line.strip().upper()
                if not word or not word.isalpha():
                    continue

                pattern = word_pattern(word)
                score = _score_word(word, self.common_words)
                candidate = {
                    "word": word,
                    "length": len(word),
                    "pattern": pattern,
                    "score": score,
                }

                if pattern not in self.patterns:
                    self.patterns[pattern] = []
                    self.pattern_words[pattern] = set()
                    self.pattern_stats[pattern] = {
                        "pattern": pattern,
                        "length": len(word),
                        "count": 0,
                    }

                if word not in self.pattern_words[pattern]:
                    self.patterns[pattern].append(candidate)
                    self.pattern_words[pattern].add(word)
                    self.pattern_stats[pattern]["count"] += 1

        for pattern in self.patterns:
            self.patterns[pattern] = sorted(
                self.patterns[pattern],
                key=lambda c: (-c["score"], c["length"], c["word"]),
            )

    def find_matches(self, cipher_word, limit=20, mapping=None):
        pattern = word_pattern(cipher_word.strip().upper())
        matches = self.patterns.get(pattern, [])

        if mapping:
            matches = [
                m for m in matches
                if _is_consistent_with_mapping(m["word"], cipher_word, mapping)
            ]

        if limit is None:
            return [{"word": m["word"], "pattern": m["pattern"], "length": m["length"]}
                    for m in matches]

        return [{"word": m["word"], "pattern": m["pattern"], "length": m["length"]}
                for m in matches[:limit]]

    def find_partial_matches(self, pattern, limit=None):
        results = []
        pattern = pattern.upper()

        for words in self.patterns.values():
            for entry in words:
                word = entry["word"]
                if len(word) != len(pattern):
                    continue
                ok = True
                
                for a, b in zip(pattern, word):
                    if a != "_" and a != b:
                        ok = False
                        break

                if ok:
                    results.append({
                        "word": word,
                        "pattern": entry["pattern"],
                        "length": entry["length"],
                    })

        if limit is not None:
            return results[:limit]

        return results

    def get_pattern_stats(self, pattern):
        return self.pattern_stats.get(pattern, {
            "pattern": pattern,
            "length": len(pattern),
            "count": 0,
        })
