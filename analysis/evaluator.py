from analysis.iterative_solver import decrypt

def build_mapping(cipher_word, old_pattern, candidate):
    mapping = {}

    for c, old, new in zip(cipher_word, old_pattern, candidate):
        if old == "_":
            mapping[c] = new

    return mapping

def merge_mapping(current_mapping, new_mapping):
    merged = current_mapping.copy()
    merged.update(new_mapping)
    return merged

def evaluate_candidate(
    cipher_words,
    current_mapping,
    cipher_word,
    old_pattern,
    candidate,
):
    new_mapping = build_mapping(
        cipher_word,
        old_pattern,
        candidate,
    )
    merged_mapping = merge_mapping(
        current_mapping,
        new_mapping,
    )
    plaintext = decrypt(
        cipher_words,
        merged_mapping,
    )
    return plaintext, merged_mapping