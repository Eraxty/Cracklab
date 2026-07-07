from analysis.dict import COMMON_WORDS
from analysis.mapping import create_mapping, merge_mappings
from analysis.patterns import word_pattern

ENG_FREQ = "ETAOINSHRDLCUMWFGYPBVKJXQZ"

def _raw_candidates(dictionary, cipher_word, limit=50):
    pattern = word_pattern(cipher_word)
    matches = getattr(dictionary, "patterns", {}).get(pattern, [])
    return matches[:limit] if limit is not None else matches

def _complete_mapping(mapping, cipher_words):
    used = set(mapping.values())
    remaining = [letter for letter in ENG_FREQ if letter not in used]
    completed = dict(mapping)

    for cipher_letter in sorted({ch for word in cipher_words for ch in word}):
        if cipher_letter not in completed and remaining:
            completed[cipher_letter] = remaining.pop(0)

    return completed

def _decrypt_words(cipher_words, mapping):
    return [
        "".join(mapping.get(letter, "_") for letter in word)
        for word in cipher_words
    ]

def _exact_solve(cipher_words, dictionary):
    """Find the first mapping-consistent candidate word combination."""

    word_items = []
    for index, cipher_word in enumerate(cipher_words):
        candidates = _raw_candidates(dictionary, cipher_word, limit=50)
        if not candidates:
            return None
        word_items.append({
            "index": index,
            "cipher_word": cipher_word,
            "candidates": candidates,
        })

    word_items.sort(key=lambda item: (len(item["candidates"]), -len(item["cipher_word"])))

    solved_words = [None] * len(cipher_words)

    def backtrack(index, current_mapping):
        if index == len(word_items):
            return {
                "mapping": current_mapping,
                "words": solved_words[:],
            }

        item = word_items[index]
        cipher_word = item["cipher_word"]

        for candidate in item["candidates"]:
            plain_word = candidate["word"]
            candidate_mapping = create_mapping(cipher_word, plain_word)

            if candidate_mapping is None:
                continue

            merged_mapping = merge_mappings(current_mapping, candidate_mapping)

            if merged_mapping is None:
                continue

            solved_words[item["index"]] = plain_word
            result = backtrack(index + 1, merged_mapping)

            if result is not None:
                return result

            solved_words[item["index"]] = None

        return None

    return backtrack(0, {})

def _best_effort_solve(cipher_words, dictionary):
    counts = {}
    order = []
    for word in cipher_words:
        if word not in counts:
            counts[word] = 0
            order.append(word)
        counts[word] += 1

    candidates = []
    for word in order:
        matches = _raw_candidates(dictionary, word, limit=50)
        if 2 <= len(matches) <= 50:
            candidates.append((word, matches))

    candidates.sort(key=lambda item: (len(item[1]), -len(item[0]), -counts[item[0]]))
    candidates = candidates[:4]

    beam = [({}, 0)]
    for cipher_word, matches in candidates:
        next_beam = []
        for mapping, score in beam:
            for candidate in matches:
                plain_word = candidate["word"]
                candidate_mapping = create_mapping(cipher_word, plain_word)
                if candidate_mapping is None:
                    continue

                merged_mapping = merge_mappings(mapping, candidate_mapping)
                if merged_mapping is None:
                    continue

                new_letters = len(merged_mapping) - len(mapping)
                candidate_score = candidate.get("score", 0)
                if plain_word in COMMON_WORDS:
                    candidate_score += 25
                if len(plain_word) <= 3:
                    candidate_score += 10

                next_beam.append((
                    merged_mapping,
                    score + candidate_score + new_letters * 8,
                ))

        if not next_beam:
            break

        next_beam.sort(key=lambda item: (len(item[0]), item[1]), reverse=True)
        beam = next_beam[:400]

    if not beam:
        return None

    mapping, _ = max(beam, key=lambda item: (len(item[0]), item[1]))
    mapping = _complete_mapping(mapping, cipher_words)
    return {
        "mapping": mapping,
        "words": _decrypt_words(cipher_words, mapping),
    }

def solve(cipher_words, dictionary):
    result = _exact_solve(cipher_words, dictionary)
    if result is not None:
        return result
    return _best_effort_solve(cipher_words, dictionary)
