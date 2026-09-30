import re
from analysis.mapping import create_mapping
from analysis.patterns import word_pattern

from analysis.eng_words import (
    COMMON_BIGRAMS,
    COMMON_QUADGRAMS,
    COMMON_SET,
    COMMON_TRIGRAMS,
    RARE_BIGRAMS,
    UNKNOWN,
    WORD_SET,
)


NGRAMS = ((4, COMMON_QUADGRAMS, 10), (3, COMMON_TRIGRAMS, 5), (2, COMMON_BIGRAMS, 2))
UNKNOWN_NGRAM_PENALTY = -8
UNKNOWN_WORD_PENALTY = -25
RARE_BIGRAM_PENALTY = -20


def decrypt(cipher_words, mapping):
    return " ".join(
        "".join(mapping.get(letter, UNKNOWN) for letter in word.upper())
        for word in cipher_words
    )


def score_text(text):
    total = 0
    stream = "".join(char for char in text.upper() if char.isalpha() or char == UNKNOWN)

    for size, table, weight in NGRAMS:
        for index in range(len(stream) - size + 1):
            gram = stream[index:index + size]

            if UNKNOWN in gram:
                total += UNKNOWN_NGRAM_PENALTY
                continue

            total += table.get(gram, -1) * weight

            if size == 2 and gram in RARE_BIGRAMS:
                total += RARE_BIGRAM_PENALTY

    for raw in text.upper().split():
        word = re.sub(r"[^A-Z_]", "", raw)

        if not word:
            continue

        if UNKNOWN in word:
            total += UNKNOWN_WORD_PENALTY * word.count(UNKNOWN)
        elif word in COMMON_SET:
            total += 90
        elif word in WORD_SET:
            total += 35

    return total


def merge(cipher_word, plain_word, mapping):
    merged = dict(mapping)

    for letter in cipher_word.upper():
        merged.pop(letter, None)

    added = create_mapping(cipher_word, plain_word)

    if added is None:
        return None

    merged.update(added)

    return merged


MAX_PASSES = 20


def solve(cipher_words, dictionary, initial_mapping = None):
    mapping = dict(initial_mapping or {})
    words = sorted({word.upper() for word in cipher_words})

    best_score = score_text(decrypt(cipher_words, mapping))

    for _ in range(MAX_PASSES):
        move = None
        move_score = best_score

        for cipher_word in words:
            for match in dictionary.find_matches(cipher_word, limit = 20, mapping = mapping):
                plain_word = match["word"].upper()

                if word_pattern(plain_word) != word_pattern(cipher_word):
                    continue

                merged = merge(cipher_word, plain_word, mapping)

                if merged is None:
                    continue

                score = score_text(decrypt(cipher_words, merged))

                if score > move_score:
                    move_score = score
                    move = merged

        if move is None:
            break

        mapping = move
        best_score = move_score

    return mapping
