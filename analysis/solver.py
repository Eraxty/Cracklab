from analysis.mapping import create_mapping, merge_mappings


def solve(cipher_words, dictionary):
    """Find the first mapping-consistent candidate word combination.

    cipher_words is expected to be a list of uppercase cipher words.
    dictionary must provide find_matches(word), returning ranked candidates
    whose plaintext word is stored under the "word" key.
    """

    word_items = []
    for index, cipher_word in enumerate(cipher_words):
        candidates = dictionary.find_matches(cipher_word)
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

            # A None merge means this plaintext word contradicts an earlier
            # choice, so backtracking skips it and tries the next candidate.
            if merged_mapping is None:
                continue

            solved_words[item["index"]] = plain_word
            result = backtrack(index + 1, merged_mapping)

            if result is not None:
                return result

            solved_words[item["index"]] = None

        return None

    return backtrack(0, {})
