COMMON_WORDS = {
    "THE", "AND", "THIS", "THAT", "YOU",
    "HAVE", "WITH", "FOR", "NOT", "ARE",
    "FROM", "HELLO", "WORLD",
}

COMMON_TRIGRAMS = {
    "THE",
    "AND",
    "ING",
    "ENT",
    "ION",
}


def score_dictionary(text):
    score = 0

    for word in text.split():
        if word in COMMON_WORDS:
            score += 20

    return score


def score_bigrams(text):
    score = 0

    for i in range(len(text) - 1):
        bigram = text[i:i + 2]

        if bigram in COMMON_BIGRAMS:
            score += 3

    return score


def score_trigrams(text):
    score = 0

    for i in range(len(text) - 2):
        trigram = text[i:i + 3]

        if trigram in COMMON_TRIGRAMS:
            score += 5

    return score


def score_frequency(text):
    score = 0

    for letter in text:
        if letter in COMMON_LETTERS:
            score += len(COMMON_LETTERS) - COMMON_LETTERS.index(letter)

    return score


def score_vowels(text):
    vowels = sum(1 for letter in text if letter in VOWELS)

    if vowels == 0:
        return -20

    vowel_ratio = vowels / len(text)

    if 0.25 <= vowel_ratio <= 0.6:
        return 12

    return 0


def score_double_letters(text):
    score = 0

    for i in range(len(text) - 1):
        if text[i] == text[i + 1]:
            score += 5

    return score


def score_text(text):
    text = text.upper()

    score = 0
    score += score_dictionary(text)
    score += score_bigrams(text)
    score += score_trigrams(text)
    score += score_frequency(text)
    score += score_vowels(text)
    score += score_double_letters(text)

    return score