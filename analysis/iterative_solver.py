import re
from collections import Counter
from dataclasses import dataclass

from analysis.english_scorer import (
    COMMON_BIGRAMS,
    COMMON_LETTERS,
    COMMON_QUADGRAMS,
    COMMON_SET,
    COMMON_TRIGRAMS,
    RARE_BIGRAMS,
    WORD_SET,
)
from analysis.mapping import create_mapping
from analysis.patterns import word_pattern

UNKNOWN = "_"

QUAD_WEIGHT = 80
TRI_WEIGHT = 24
BI_WEIGHT = 8
COMMON_WORD_WEIGHT = 90
DICTIONARY_WORD_WEIGHT = 35
LETTER_FREQUENCY_WEIGHT = 6

UNKNOWN_QUAD_PENALTY = -35
UNKNOWN_TRI_PENALTY = -10
UNKNOWN_BI_PENALTY = -3
UNKNOWN_WORD_LETTER_PENALTY = -2
WORD_UNDERSCORE_PENALTY = -35
SHORT_UNKNOWN_WORD_PENALTY = -180
WORD_UNKNOWN_PENALTY = -45
RARE_BIGRAM_PENALTY = -35
WORST_WORD_COUNT = 20

ENGLISH_FREQUENCIES = {
    "E": 12.70,
    "T": 9.06,
    "A": 8.17,
    "O": 7.51,
    "I": 6.97,
    "N": 6.75,
    "S": 6.33,
    "H": 6.09,
    "R": 5.99,
    "D": 4.25,
    "L": 4.03,
    "C": 2.78,
    "U": 2.76,
    "M": 2.41,
    "W": 2.36,
    "F": 2.23,
    "G": 2.02,
    "Y": 1.97,
    "P": 1.93,
    "B": 1.49,
    "V": 0.98,
    "K": 0.77,
    "J": 0.15,
    "X": 0.15,
    "Q": 0.10,
    "Z": 0.07,
}


@dataclass(frozen=True)
class CandidateEvaluation:
    cipher_word: str
    old_candidate: str
    new_candidate: str
    mapping: dict
    plaintext: str
    score: int


@dataclass(frozen=True)
class WordEvaluation:
    cipher_word: str
    plaintext_word: str
    score: int
    index: int


def decrypt(cipher_words, mapping):
    plaintext = []
    for word in cipher_words:
        plaintext.append("".join(mapping.get(letter, UNKNOWN) for letter in word.upper()))
    return " ".join(plaintext)


def _known_mapping_count(mapping):
    return sum(1 for letter in mapping.values() if letter != UNKNOWN)


def _is_mapping_valid(mapping):
    plain_to_cipher = {}
    for cipher_letter, plain_letter in mapping.items():
        if not cipher_letter.isalpha() or not plain_letter.isalpha():
            return False
        existing_cipher = plain_to_cipher.get(plain_letter)
        if existing_cipher is not None and existing_cipher != cipher_letter:
            return False
        plain_to_cipher[plain_letter] = cipher_letter
    return True


def _merge_replacing_word(current_mapping, cipher_word, candidate_word):
    candidate_mapping = create_mapping(cipher_word, candidate_word)
    if candidate_mapping is None:
        return None

    merged = dict(current_mapping)
    for cipher_letter in cipher_word.upper():
        merged.pop(cipher_letter, None)
    merged.update(candidate_mapping)

    if not _is_mapping_valid(merged):
        return None
    return merged

def generate_candidates(cipher_word, current_mapping, dictionary):
    pattern = word_pattern(cipher_word.upper())
    matches = sorted(dictionary.patterns.get(pattern, []), key=lambda match: match["word"])
    candidates = []

    for match in matches:
        candidate_word = match["word"].upper()
        merged = _merge_replacing_word(current_mapping, cipher_word, candidate_word)
        if merged is None:
            continue
        candidates.append((candidate_word, merged))

    return candidates


def _ngram_stream(text):
    return "".join(c for c in text.upper() if c.isalpha() or c == UNKNOWN)

def _score_ngram(stream, size, score, weight,unknown_penalty):
    total = 0 
    for i in range(len(stream) -size + 1):
        gram = stream[i:i+size]
        if UNKNOWN in gram:
            total += unknown_penalty
        else:
            total += scores.get(gram , unknown_penalty) * weight
    return total

