from analysis.mapping import create_mapping, merge_mappings
from analysis.solver import decrypt_partial
from analysis.english_scorer import score_text


def choose_best_candidate(item, mapping, cipher_words, dictionary):
    cipher_word = item["word"]
    candidates = dictionary.find_matches(cipher_word, limit=None)

    best_candidate = None
    best_mapping = None
    best_score = float("-inf")
    best_plaintext = None

    for candidate in candidates:
        plain_word = candidate["word"]

        candidate_mapping = create_mapping(cipher_word, plain_word)
        if candidate_mapping is None:
            continue

        merged = merge_mappings(mapping, candidate_mapping)
        if merged is None:
            continue

        plaintext = decrypt_partial(cipher_words, merged)
        score = score_text(plaintext)

        if score > best_score:
            best_score = score
            best_candidate = plain_word
            best_mapping = merged
            best_plaintext = plaintext

    return {
        "candidate": best_candidate,
        "mapping": best_mapping,
        "score": best_score,
        "plaintext": best_plaintext,
    }
