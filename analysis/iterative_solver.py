import re
from collections import Counter
from dataclasses import dataclass

from analysis.eng_words import (
    BI_WEIGHT,
    COMMON_BIGRAMS,
    COMMON_LETTERS,
    COMMON_QUADGRAMS,
    COMMON_SET,
    COMMON_TRIGRAMS,
    COMMON_WORD_WEIGHT,
    DICTIONARY_WORD_WEIGHT,
    ENGLISH_FREQUENCIES,
    IMPOSSIBLE_BIGRAMS,
    LETTER_FREQUENCY_WEIGHT,
    RARE_BIGRAMS,
    RARE_BIGRAM_PENALTY,
    SHORT_UNKNOWN_WORD_PENALTY,
    TRI_WEIGHT,
    UNKNOWN,
    UNKNOWN_BI_PENALTY,
    UNKNOWN_QUAD_PENALTY,
    UNKNOWN_TRI_PENALTY,
    UNKNOWN_WORD_LETTER_PENALTY,
    WORD_SET,
    WORD_UNDERSCORE_PENALTY,
    WORD_UNKNOWN_PENALTY,
    WORST_WORD_COUNT,
    QUAD_WEIGHT,
)
from analysis.partial_words import build_remember
from analysis.mapping import create_mapping
from analysis.patterns import word_pattern


MAX_CANDIDATES_PER_WORD = 20


@dataclass(frozen=True)
class CandidateEvaluation:
    cipher_word: str
    old_candidate: str
    new_candidate: str
    mapping: dict
    plaintext: str
    score: int
    improvement: int
    new_valid_words: int
    new_common_words: int
    new_valid_distinct: int
    more_complete_words: int
    letters_revealed: int
    common_bigrams: int
    common_trigrams: int
    common_quadgrams: int
    broken_valid_words: int
    new_invalid_words: int
    rare_bigrams: int
    impossible_bigrams: int


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
    cipher_word = cipher_word.upper()
    pattern = word_pattern(cipher_word)
    matches = dictionary.find_matches(
        cipher_word,
        limit=MAX_CANDIDATES_PER_WORD,
        mapping=current_mapping,
    )
    candidates = []

    for match in matches:
        candidate_word = match["word"].upper()
        if word_pattern(candidate_word) != pattern:
            continue
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
    return score_plaintext(plaintext), plaintext


@dataclass(frozen=True)
class PlaintextStats:
    valid_words: tuple
    common_words: tuple
    known_letters: int
    common_bigrams: int
    common_trigrams: int
    common_quadgrams: int
    rare_bigrams: int
    impossible_bigrams: int


def _count_common_ngrams(words, size, scores):
    return sum(
        1
        for word in words
        for index in range(len(word) - size + 1)
        if UNKNOWN not in word[index:index + size]
        and word[index:index + size] in scores
    )


def _count_bigrams(words, candidates):
    return sum(
        1
        for word in words
        for index in range(len(word) - 1)
        if UNKNOWN not in word[index:index + 2]
        and word[index:index + 2] in candidates
    )


def _plaintext_stats(plaintext):
    words = plaintext.upper().split()
    valid_words = tuple(
        word for word in words
        if UNKNOWN not in word and word in WORD_SET
    )
    common_words = tuple(
        word for word in words
        if UNKNOWN not in word and word in COMMON_SET
    )

    return PlaintextStats(
        valid_words=valid_words,
        common_words=common_words,
        known_letters=sum(
            1 for word in words for letter in word if letter != UNKNOWN
        ),
        common_bigrams=_count_common_ngrams(words, 2, COMMON_BIGRAMS),
        common_trigrams=_count_common_ngrams(words, 3, COMMON_TRIGRAMS),
        common_quadgrams=_count_common_ngrams(words, 4, COMMON_QUADGRAMS),
        rare_bigrams=_count_bigrams(words, RARE_BIGRAMS),
        impossible_bigrams=_count_bigrams(words, IMPOSSIBLE_BIGRAMS),
    )


def _global_improvement(old_plaintext, new_plaintext, old_stats=None):
    old_words = old_plaintext.upper().split()
    new_words = new_plaintext.upper().split()
    if old_stats is None:
        old_stats = _plaintext_stats(old_plaintext)
    new_stats = _plaintext_stats(new_plaintext)

    new_valid_words = sum(
        old_word not in WORD_SET and new_word in WORD_SET
        for old_word, new_word in zip(old_words, new_words)
        if UNKNOWN not in new_word
    )
    new_common_words = sum(
        old_word not in COMMON_SET and new_word in COMMON_SET
        for old_word, new_word in zip(old_words, new_words)
        if UNKNOWN not in new_word
    )
    new_valid_distinct = len(
        set(new_stats.valid_words) - set(old_stats.valid_words)
    )
    more_complete_words = sum(
        new_word.count(UNKNOWN) < old_word.count(UNKNOWN)
        for old_word, new_word in zip(old_words, new_words)
        if new_word not in WORD_SET
    )
    broken_valid_words = sum(
        old_word in WORD_SET and new_word not in WORD_SET
        for old_word, new_word in zip(old_words, new_words)
    )
    new_invalid_words = sum(
        UNKNOWN not in new_word
        and new_word not in WORD_SET
        and UNKNOWN in old_word
        for old_word, new_word in zip(old_words, new_words)
    )

    delta = {
        "new_valid_words": new_valid_words,
        "new_common_words": new_common_words,
        "new_valid_distinct": new_valid_distinct,
        "more_complete_words": more_complete_words,
        "letters_revealed": new_stats.known_letters - old_stats.known_letters,
        "common_bigrams": new_stats.common_bigrams - old_stats.common_bigrams,
        "common_trigrams": new_stats.common_trigrams - old_stats.common_trigrams,
        "common_quadgrams": new_stats.common_quadgrams - old_stats.common_quadgrams,
        "broken_valid_words": broken_valid_words,
        "new_invalid_words": new_invalid_words,
        "rare_bigrams": new_stats.rare_bigrams - old_stats.rare_bigrams,
        "impossible_bigrams": (
            new_stats.impossible_bigrams - old_stats.impossible_bigrams
        ),
    }
    delta["score"] = (
        delta["new_common_words"] * 1000
        + delta["new_valid_words"] * 350
        + delta["new_valid_distinct"] * 250
        + delta["more_complete_words"] * 15
        + delta["letters_revealed"]
        + delta["common_bigrams"] * 8
        + delta["common_trigrams"] * 20
        + delta["common_quadgrams"] * 45
        - delta["broken_valid_words"] * 1200
        - delta["new_invalid_words"] * 250
        - delta["rare_bigrams"] * 30
        - delta["impossible_bigrams"] * 300
    )
    return delta


def evaluate_candidate(
    cipher_words,
    cipher_word,
    old_candidate,
    candidate_word,
    candidate_mapping,
    current_plaintext=None,
    current_stats=None,
):
    score, plaintext = evaluate_mapping(cipher_words, candidate_mapping)
    if current_plaintext is None:
        _, current_plaintext = evaluate_mapping(cipher_words, {})
    delta = _global_improvement(current_plaintext, plaintext, current_stats)
    return CandidateEvaluation(
        cipher_word=cipher_word,
        old_candidate=old_candidate,
        new_candidate=candidate_word,
        mapping=candidate_mapping,
        plaintext=plaintext,
        score=score,
        improvement=delta["score"],
        new_valid_words=delta["new_valid_words"],
        new_common_words=delta["new_common_words"],
        new_valid_distinct=delta["new_valid_distinct"],
        more_complete_words=delta["more_complete_words"],
        letters_revealed=delta["letters_revealed"],
        common_bigrams=delta["common_bigrams"],
        common_trigrams=delta["common_trigrams"],
        common_quadgrams=delta["common_quadgrams"],
        broken_valid_words=delta["broken_valid_words"],
        new_invalid_words=delta["new_invalid_words"],
        rare_bigrams=delta["rare_bigrams"],
        impossible_bigrams=delta["impossible_bigrams"],
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
        key=lambda item: (
            UNKNOWN not in item.plaintext_word,
            item.score,
            item.cipher_word,
            item.plaintext_word,
            item.index,
        ),
    )
    return ranked[:limit]


def choose_best_candidate(cipher_words, mapping, dictionary, weak_words, current_score):
    best = None
    _, current_plaintext = evaluate_mapping(cipher_words, mapping)
    current_stats = _plaintext_stats(current_plaintext)
    best_improvement = 0
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
                current_plaintext,
                current_stats,
            )

            print(f"{cipher_word} = {candidate_word}")

            if evaluation.improvement > best_improvement:
                best = evaluation
                best_improvement = evaluation.improvement

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
        print(
            f"+{improvement.improvement}  {improvement.cipher_word}: "
            f"{improvement.old_candidate} -> {improvement.new_candidate}"
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
