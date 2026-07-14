from analysis.iterative_solver import decrypt

def build_mapping(cipher_word, old_pattern, candidate):
    mapping = {}

    for c, old, new in zip(cipher_word, old_pattern, candidate):
        if old == "_":
            mapping[c] = new

    return mapping

def is_valid_mapping(mapping):
    values = list(mapping.values())
    return len(values) == len(set(values))

def merge_mapping(current_mapping, new_mapping):
    merged = current_mapping.copy()
    merged.update(new_mapping)

    if not is_valid_mapping(merged):
        return None

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

    if merged_mapping is None:
        return None, None
        
    plaintext = decrypt(
        cipher_words,
        merged_mapping,
    )
    return plaintext, merged_mapping