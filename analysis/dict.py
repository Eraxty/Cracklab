from analysis.patterns import word_pattern

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


def normalize_word(word):
    return word.strip().upper()


def filter_short_words(word):
    return len(word) >= 1


def common_letter_score(word):
    score = 0

    for letter in word:
        if letter in COMMON_LETTERS:
            score += len(COMMON_LETTERS) - COMMON_LETTERS.index(letter)

    return score


def rank_candidate(word):
    score = common_letter_score(word)
    vowels = sum(1 for letter in word if letter in VOWELS)

    if word in COMMON_WORDS:
        score += 80

    if vowels == 0:
        score -= 20
    else:
        vowel_ratio = vowels / len(word)
        if 0.25 <= vowel_ratio <= 0.6:
            score += 12

    for index in range(len(word) - 1):
        if word[index:index + 2] in COMMON_BIGRAMS:
            score += 10

    for index in range(len(word) - 2):
        if word[index:index + 3] in COMMON_TRIGRAMS:
            score += 18

    if word.endswith(COMMON_ENDINGS):
        score += 8

    for rare_letter in "QXZJ":
        if rare_letter in word:
            score -= 12

    return score


def build_candidate(word, pattern):
    return {
        "word": word,
        "length": len(word),
        "pattern": pattern,
        "score": rank_candidate(word),
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

    def load(self, filename):
        with open(filename, "r") as file:
            for word in file:
                word = normalize_word(word)

                if not filter_short_words(word):
                    continue

                if not word.isalpha():
                    continue

                pattern = word_pattern(word)
                candidate = build_candidate(word, pattern)

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

    def find_matches(self, cipher_word, limit=20):
        pattern = word_pattern(normalize_word(cipher_word))
        matches = self.patterns.get(pattern, [])
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
