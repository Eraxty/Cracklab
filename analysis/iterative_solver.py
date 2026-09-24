from analysis.eng_words import COMMON_SET, UNKNOWN, WORD_SET
from analysis.mapping import create_mapping
from analysis.patterns import word_pattern


def decrypt(cipher_words, mapping):
    return " ".join(
        "".join(mapping.get(letter, UNKNOWN) for letter in word.upper())
        for word in cipher_words
    )


def score_text(text):
    total = 0

    for word in text.upper().split():
        if UNKNOWN not in word:
            total += 90 if word in COMMON_SET else 35 if word in WORD_SET else 0

    return total


def _merge(cipher_word, plain_word, mapping):
    merged = dict(mapping)

    for letter in cipher_word.upper():
        merged.pop(letter, None)

    added = create_mapping(cipher_word, plain_word)

    if added is None:
        return None

    merged.update(added)

    return merged


def solve(cipher_words, dictionary, initial_mapping = None):
    mapping = dict(initial_mapping or {})
    done = set()

    while True:
        before = score_text(decrypt(cipher_words, mapping))
        best_mapping = None
        best_gain = 0

        for cipher_word in {word.upper() for word in cipher_words} - done:
            done.add(cipher_word)

            for match in dictionary.find_matches(cipher_word, limit = 20, mapping = mapping):
                plain_word = match["word"].upper()

                if word_pattern(plain_word) != word_pattern(cipher_word):
                    continue

                merged = _merge(cipher_word, plain_word, mapping)

                if merged is None:
                    continue

                gain = score_text(decrypt(cipher_words, merged)) - before

                if gain > best_gain:
                    best_gain = gain
                    best_mapping = merged

        if best_mapping is None:
            break

        mapping = best_mapping

    return mapping