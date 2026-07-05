from analysis.mapping import create_mapping, merge_mappings


def solve(cipher_words, dictionary):
    """Find the first mapping-consistent candidate word combination.

    cipher_words is expected to be a list of uppercase cipher words.
    dictionary must provide find_matches(word), returning ranked candidates
    whose plaintext word is stored under the "word" key.
    """

    def backtrack(index, current_mapping, solved_words):
        # Base case: every cipher word has a selected plaintext candidate.
        # At this point the accumulated mapping is valid because every step
        # reached this point through merge_mappings().
        if index == len(cipher_words):
            return {
                "mapping": current_mapping,
                "words": solved_words,
            }

        cipher_word = cipher_words[index]
        candidates = dictionary.find_matches(cipher_word)

        # Try the dictionary's ranked candidates in order. Each candidate
        # creates a small word-level mapping, then we ask merge_mappings()
        # whether it is compatible with everything chosen so far.
        for candidate in candidates:
            plain_word = candidate["word"]
            candidate_mapping = create_mapping(cipher_word, plain_word)

            if candidate_mapping is None:
                continue

            merged_mapping = merge_mappings(current_mapping, candidate_mapping)

            # A None merge means this plaintext word contradicts an earlier
            # choice, so backtracking skips it and tries the next candidate.
            if merged_mapping is None:
                continue

            # Recurse with the compatible mapping and the candidate word added
            # to the partial solution. If deeper words cannot be solved, the
            # loop naturally continues with the next candidate here.
            result = backtrack(
                index + 1,
                merged_mapping,
                solved_words + [plain_word],
            )

            if result is not None:
                return result

        # No candidate for this word could lead to a full solution.
        return None

    return backtrack(0, {}, [])
