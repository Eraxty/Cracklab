import re

from analysis.eng_words import (
    COMMON_SET,
    WORD_SET,
    COMMON_LETTERS,
    COMMON_BIGRAMS,
    COMMON_TRIGRAMS,
    COMMON_QUADGRAMS,
    COMMON_DOUBLES,
    RARE_BIGRAMS,
    PHRASE_BONUSES,
    VOWELS,
)

def _clean_word(word):
    return re.sub(r"[^A-Z]", "", word.upper())


def _score_words(text):
    words = text.split()
    dictionary_score = 0
    unknown_penalty = 0
    consecutive_bonus = 0
    valid_count = 0
    invalid_count = 0
    prev_valid = False

    for word in words:
        clean = _clean_word(word)
        if not clean:
            continue
        if clean in COMMON_SET:
            dictionary_score += 40
            valid_count += 1
            if prev_valid:
                consecutive_bonus += 10
            prev_valid = True
        elif clean in WORD_SET:
            dictionary_score += 15
            valid_count += 1
            if prev_valid:
                consecutive_bonus += 10
            prev_valid = True
        elif len(clean) >= 4:
            unknown_penalty -= 3 * len(clean)
            invalid_count += 1
            prev_valid = False
        else:
            prev_valid = False

    return dictionary_score, unknown_penalty, consecutive_bonus, valid_count, invalid_count


def _score_phrases(text):
    total = 0
    for phrase, bonus in PHRASE_BONUSES.items():
        if phrase in text:
            total += bonus
    return total


def score_bigrams(text):
    letters = "".join(c for c in text if c.isalpha())
    score = 0
    streak = 0
    for i in range(len(letters) - 1):
        bigram = letters[i:i + 2]
        if bigram in COMMON_BIGRAMS:
            streak += 1
            score += COMMON_BIGRAMS[bigram] * streak
        else:
            streak = 0
    return score


def score_trigrams(text):
    letters = "".join(c for c in text if c.isalpha())
    score = 0
    streak = 0
    for i in range(len(letters) - 2):
        trigram = letters[i:i + 3]
        if trigram in COMMON_TRIGRAMS:
            streak += 1
            score += COMMON_TRIGRAMS[trigram] * streak
        else:
            streak = 0
    return score


def score_frequency(text):
    score = 0
    for letter in text:
        if not letter.isalpha():
            continue
        if letter in COMMON_LETTERS:
            score += len(COMMON_LETTERS) - COMMON_LETTERS.index(letter)
    return score


def score_vowels(text):
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0
    vowels = sum(1 for letter in letters if letter in VOWELS)
    vowel_ratio = vowels / len(letters)
    if 0.30 <= vowel_ratio <= 0.55:
        return 12
    if vowels == 0:
        return -20
    return 0


def score_double_letters(text):
    score = 0
    for i in range(len(text) - 1):
        pair = text[i:i + 2]
        if not pair.isalpha():
            continue
        if pair in COMMON_DOUBLES:
            score += 5
        elif pair[0] == pair[1]:
            score -= 2
    return score


def score_quadgrams(text):
    letters = "".join(c for c in text if c.isalpha())
    score = 0
    streak = 0
    for i in range(len(letters) - 3):
        quad = letters[i:i + 4]
        if quad in COMMON_QUADGRAMS:
            streak += 1
            score += COMMON_QUADGRAMS[quad] * streak
        else:
            streak = 0
    return score


def score_rare_bigrams(text):
    letters = "".join(c for c in text if c.isalpha())
    score = 0
    for i in range(len(letters) - 1):
        bigram = letters[i:i + 2]
        if bigram in RARE_BIGRAMS:
            score -= 10
    return score


def score_text(text):
    text = text.upper()

    dictionary_score, unknown_penalty, consecutive_bonus, _, _ = _score_words(text)
    phrase_bonus = _score_phrases(text)

    num_letters = max(1, len([c for c in text if c.isalpha()]))
    bigrams = round(score_bigrams(text) / num_letters * 10)
    trigrams = round(score_trigrams(text) / num_letters * 10)
    quadgrams = round(score_quadgrams(text) / num_letters * 10)
    frequency = round(score_frequency(text) / num_letters * 10)
    vowels = score_vowels(text)
    doubles = score_double_letters(text)
    rare = score_rare_bigrams(text)

    return (dictionary_score + unknown_penalty + consecutive_bonus + phrase_bonus
            + bigrams + trigrams + quadgrams
            + frequency + vowels + doubles + rare)
