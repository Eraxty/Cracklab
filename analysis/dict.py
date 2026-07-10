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


def load_common_words(filepath):
    words = set()
    try:
        with open(filepath, "r") as f:
            for line in f:
                w = line.strip().upper()
                if w.isalpha():
                    words.add(w)
    except FileNotFoundError:
        pass
    return words


def normalize_word(word):
    return word.strip().upper()


def filter_short_words(word):
    return len(word) >= 1


def is_consistent_with_mapping(word, cipher_word, mapping):
    plain_to_cipher = {v: k for k, v in mapping.items()}
    for cipher_letter, plain_letter in zip(cipher_word.upper(), word.upper()):
        if cipher_letter in mapping and mapping[cipher_letter] != plain_letter:
            return False
        if plain_letter in plain_to_cipher and plain_to_cipher[plain_letter] != cipher_letter:
            return False
    return True


def score_letter_frequency(word):
    score = 0
    for letter in word:
        if letter in COMMON_LETTERS:
            score += len(COMMON_LETTERS) - COMMON_LETTERS.index(letter)
    return score


def score_bigrams(word):
    score = 0
    for i in range(len(word) - 1):
        if word[i:i + 2] in COMMON_BIGRAMS:
            score += 10
    return score


def score_trigrams(word):
    score = 0
    for i in range(len(word) - 2):
        if word[i:i + 3] in COMMON_TRIGRAMS:
            score += 18
    return score


def score_vowel_pattern(word):
    vowels = sum(1 for letter in word if letter in VOWELS)
    if vowels == 0:
        return -20
    ratio = vowels / len(word)
    if 0.25 <= ratio <= 0.6:
        return 15
    return 0


def score_rare_letters(word):
    penalty = 0
    for letter in word:
        if letter in RARE_PENALTY:
            penalty += RARE_PENALTY[letter]
    return penalty


def score_word(word, common_words_set):
    base = score_letter_frequency(word)
    base += score_bigrams(word)
    base += score_trigrams(word)
    base += score_vowel_pattern(word)
    base += score_rare_letters(word)

    if word.endswith(COMMON_ENDINGS):
        base += 8

    if word in common_words_set:
        base += 500

    return base


def rank_candidate(word, common_words_set):
    return score_word(word, common_words_set)


def build_candidate(word, pattern, common_words_set):
    return {
        "word": word,
        "length": len(word),
        "pattern": pattern,
        "score": rank_candidate(word, common_words_set),
    }


def public_candidate(candidate):
    return {
        "word": candidate["word"],
        "pattern": candidate["pattern"],
        "length": candidate["length"],
    }


class PatternDictionary:
    def __init__(self):
        self.patterns = {}
        self.pattern_stats = {}
        self.pattern_words = {}
        self.common_words = set()

    def load(self, filename, common_words_path=None):
        if common_words_path is None:
            common_words_path = str(
                Path(filename).parent / "common_words.txt"
            )
        self.common_words = load_common_words(common_words_path)

        with open(filename, "r") as file:
            for word in file:
                word = normalize_word(word)

                if not filter_short_words(word):
                    continue

                if not word.isalpha():
                    continue

                pattern = word_pattern(word)
                candidate = build_candidate(word, pattern, self.common_words)

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
            self.patterns[pattern] = rank_candidates(self.patterns[pattern])

    def find_matches(self, cipher_word, limit=20, mapping=None):
        pattern = word_pattern(normalize_word(cipher_word))
        matches = self.patterns.get(pattern, [])

        if mapping:
            matches = [
                m for m in matches
                if is_consistent_with_mapping(m["word"], cipher_word, mapping)
            ]

        if limit is None:
            return [public_candidate(match) for match in matches]

        return [public_candidate(match) for match in matches[:limit]]

    def get_pattern_stats(self, pattern):
        return self.pattern_stats.get(pattern, {
            "pattern": pattern,
            "length": len(pattern),
            "count": 0,
        })


def rank_candidates(candidates):
    return sorted(
        candidates,
        key=lambda candidate: (
            -candidate["score"],
            candidate["length"],
            candidate["word"],
        ),
    )


def debug_find_matches(dictionary, cipher_word, mapping=None, limit=15):
    pattern = word_pattern(normalize_word(cipher_word))
    all_matches = dictionary.patterns.get(pattern, [])

    print(f"Cipher: {cipher_word}")
    print(f"Pattern: {pattern}")
    print(f"{len(all_matches)} pattern matches")

    if mapping:
        after_mapping = [
            m for m in all_matches
            if is_consistent_with_mapping(m["word"], cipher_word, mapping)
        ]
        print(f"After mapping filter: {len(after_mapping)}")
        candidates = after_mapping
    else:
        candidates = all_matches

    print(f"\nTop ranked candidates:")
    for m in candidates[:limit]:
        in_common = " [COMMON]" if m["word"] in dictionary.common_words else ""
        print(f"  {m['word']:15s}  score={m['score']:4d}{in_common}")

    return [public_candidate(m) for m in candidates[:limit]]
