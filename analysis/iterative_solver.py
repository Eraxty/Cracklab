import re
from collections import Counter
from dataclasses import dataclass
from analysis.partial_words import build_remember

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

def _score_ngrams(stream, size, scores, weight, unknown_penalty):
    total = 0
    for i in range(len(stream) - size + 1):
        gram = stream[i:i + size]
        if UNKNOWN in gram:
            total += unknown_penalty
        else:
            total += scores.get(gram, unknown_penalty) * weight
    return total



# UNDER THIS PART AI CODE i geniuenly couldnt make it work i had to resort to it
#PLZ forgive me 





def _score_word_ngrams(word):
    score = 0
    known_letters = "".join(letter for letter in word if letter != UNKNOWN)
    score += _score_ngrams(known_letters, 4, COMMON_QUADGRAMS, 10, -8)
    score += _score_ngrams(known_letters, 3, COMMON_TRIGRAMS, 5, -5)
    score += _score_ngrams(known_letters, 2, COMMON_BIGRAMS, 2, -3)

    for i in range(len(known_letters) - 1):
        if known_letters[i:i + 2] in RARE_BIGRAMS:
            score += RARE_BIGRAM_PENALTY

    return score


def score_word(word):
    word = re.sub(r"[^A-Z_]", "", word.upper())
    if not word:
        return 0

    if set(word) == {UNKNOWN}:
        return -80 - min(len(word), 6) * 15

    score = 0
    unknown_count = word.count(UNKNOWN)
    score += WORD_UNDERSCORE_PENALTY * min(unknown_count, 4)
    if unknown_count and len(word) <= 3:
        score += SHORT_UNKNOWN_WORD_PENALTY
    score += _score_word_ngrams(word)

    if UNKNOWN in word:
        return score

    if word in COMMON_SET:
        score += 140 + len(word) * 3
    elif word in WORD_SET:
        score += 65 + len(word) * 2
    elif len(word) >= 3:
        score += WORD_UNKNOWN_PENALTY - len(word) * 7

    for letter in word:
        if letter in COMMON_LETTERS:
            score += len(COMMON_LETTERS) - COMMON_LETTERS.index(letter)

    return score


def _score_complete_words(text):
    total = 0
    for raw_word in text.upper().split():
        if UNKNOWN in raw_word:
            total += UNKNOWN_WORD_LETTER_PENALTY * raw_word.count(UNKNOWN)
            continue

        word = re.sub(r"[^A-Z]", "", raw_word)
        if not word:
            continue
        if word in COMMON_SET:
            total += COMMON_WORD_WEIGHT + len(word)
        elif word in WORD_SET:
            total += DICTIONARY_WORD_WEIGHT + len(word)
        elif len(word) >= 4:
            total -= len(word) * 8

    return total


def _score_letter_frequencies(stream):
    letters = [c for c in stream if c.isalpha()]
    if not letters:
        return 0

    counts = {letter: 0 for letter in ENGLISH_FREQUENCIES}
    for letter in letters:
        counts[letter] += 1

    total_letters = len(letters)
    chi_square = 0.0
    for letter, expected_percent in ENGLISH_FREQUENCIES.items():
        expected = total_letters * expected_percent / 100
        observed = counts[letter]
        chi_square += ((observed - expected) ** 2) / max(expected, 0.01)

    rank_bonus = 0
    for letter in letters:
        if letter in COMMON_LETTERS:
            rank_bonus += len(COMMON_LETTERS) - COMMON_LETTERS.index(letter)

    return round(rank_bonus / total_letters * LETTER_FREQUENCY_WEIGHT - chi_square)


def score_plaintext(text):
    stream = _ngram_stream(text)
    quadgrams = _score_ngrams(
        stream, 4, COMMON_QUADGRAMS, QUAD_WEIGHT, UNKNOWN_QUAD_PENALTY
    )
    trigrams = _score_ngrams(
        stream, 3, COMMON_TRIGRAMS, TRI_WEIGHT, UNKNOWN_TRI_PENALTY
    )
    bigrams = _score_ngrams(
        stream, 2, COMMON_BIGRAMS, BI_WEIGHT, UNKNOWN_BI_PENALTY
    )
    words = _score_complete_words(text)
    frequency = _score_letter_frequencies(stream)

    return quadgrams + trigrams + bigrams + words + frequency


def score_text(text):
    return score_plaintext(text)


def evaluate_mapping(cipher_words, mapping):
    plaintext = decrypt(cipher_words, mapping)
    
    remember = build_remember(cipher_words, plaintext)
    print(remember)
    
    return score_plaintext(plaintext), plaintext


def evaluate_candidate(cipher_words, cipher_word, old_candidate, candidate_word, candidate_mapping):
    score, plaintext = evaluate_mapping(cipher_words, candidate_mapping)
    return CandidateEvaluation(
        cipher_word=cipher_word,
        old_candidate=old_candidate,
        new_candidate=candidate_word,
        mapping=candidate_mapping,
        plaintext=plaintext,
        score=score,
    )


def _has_dictionary_candidates(cipher_word, dictionary):
    pattern = word_pattern(cipher_word.upper())
    return bool(dictionary.patterns.get(pattern))


def find_worst_words(cipher_words, plaintext, dictionary, limit=WORST_WORD_COUNT):
    decrypted_words = plaintext.split()
    cipher_counts = Counter(word.upper() for word in cipher_words)
    scored_words = []

    for index, (cipher_word, plaintext_word) in enumerate(zip(cipher_words, decrypted_words)):
        cipher_word = cipher_word.upper()
        if not _has_dictionary_candidates(cipher_word, dictionary):
            continue

        plaintext_word = plaintext_word.upper()
        word_score = score_word(plaintext_word)
        word_score -= min(cipher_counts[cipher_word] - 1, 4) * 40
        scored_words.append(
            WordEvaluation(
                cipher_word=cipher_word,
                plaintext_word=plaintext_word,
                score=word_score,
                index=index,
            )
        )

    ranked = sorted(
        scored_words,
        key=lambda item: (item.score, item.cipher_word, item.plaintext_word, item.index),
    )
    return ranked[:limit]


def choose_best_candidate(cipher_words, mapping, dictionary, weak_words, current_score):
    best = None
    best_score = current_score
    evaluated_cipher_words = set()

    for weak_word in weak_words:
        cipher_word = weak_word.cipher_word
        if cipher_word in evaluated_cipher_words:
            continue
        evaluated_cipher_words.add(cipher_word)

        old_candidate = weak_word.plaintext_word
        for candidate_word, candidate_mapping in generate_candidates(
            cipher_word, mapping, dictionary
        ):
            evaluation = evaluate_candidate(
                cipher_words,
                cipher_word,
                old_candidate,
                candidate_word,
                candidate_mapping,
            )

            if evaluation.score > best_score:
                best = evaluation
                best_score = evaluation.score

    return best


def solve_iteration(cipher_words, mapping, dictionary):
    current_score, plaintext = evaluate_mapping(cipher_words, mapping)
    weak_words = find_worst_words(cipher_words, plaintext, dictionary)
    improvement = choose_best_candidate(
        cipher_words, mapping, dictionary, weak_words, current_score
    )
    return current_score, weak_words, improvement


def apply_improvement(mapping, improvement):
    if improvement is None:
        return mapping
    return improvement.mapping


def _print_iteration(iteration, current_score, weak_words, improvement, mapping):
    displayed_mapping = improvement.mapping if improvement is not None else mapping
    bad = ", ".join(item.plaintext_word for item in weak_words)
    print(f"Pass {iteration}")
    print(f"bad: {bad}")

    if improvement is None:
        print("stop")
    else:
        gain = improvement.score - current_score
        print(
            f"+{gain}  {improvement.cipher_word}: "
            f"{improvement.old_candidate} -> {improvement.new_candidate}  "
            f"{current_score} -> {improvement.score}"
        )

    print(f"map: {_known_mapping_count(displayed_mapping)}\n")


def solve(cipher_words, dictionary, initial_mapping=None):
    mapping = dict(initial_mapping or {})
    iterations = 0

    while True:
        current_score, weak_words, improvement = solve_iteration(
            cipher_words, mapping, dictionary
        )
        iterations += 1
        _print_iteration(iterations, current_score, weak_words, improvement, mapping)

        if improvement is None:
            break

        mapping = apply_improvement(mapping, improvement)

    final_score, _ = evaluate_mapping(cipher_words, mapping)
    print(f"Done. score: {final_score}  passes: {iterations}  map: {_known_mapping_count(mapping)}")

    return mapping
