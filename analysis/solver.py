from analysis.mapping import create_mapping, merge_mappings
from analysis.english_scorer import score_text

def decrypt_partial(cipher_words, mapping):
    plaintext = []
    for word in cipher_words:
        decrypted = ""
        for letter in word:
            decrypted += mapping.get(letter, "_")
        plaintext.append(decrypted)
    return " ".join(plaintext)

def score_mapping(cipher_words, mapping):
    plaintext = decrypt_partial(cipher_words, mapping)
    return score_text(plaintext)

def solve(cipher_words, dictionary):
    unique_words = sorted(
        set(cipher_words),
        key=lambda word: (
            len(dictionary.find_matches(word, limit=None)),
            -len(word),
        ),
    )

    beam = [({}, 0)]
    for cipher_word in unique_words:
        matches = dictionary.find_matches(cipher_word, limit=30)
        if not matches:
          continue
        
        next_beam = []
        for mapping, _ in beam:
            for candidate in matches:
                plain_word = candidate["word"]
                candidate_mapping = create_mapping(cipher_word, plain_word)
          
                if candidate_mapping is None:
                    continue
                merged = merge_mappings(mapping, candidate_mapping)

                if merged is None:
                    continue
                score = score_mapping(cipher_words, merged)
                next_beam.append((merged, score))

        if not next_beam:
            break

        next_beam.sort(
            key=lambda item: item[1],
            reverse=True,
        )
        beam = next_beam[:10]

    if not beam:
        return None
    best_mapping, best_score = beam[0]
    return {
        "mapping": best_mapping,
        "plaintext": decrypt_partial(cipher_words, best_mapping),
        "score": best_score,
    }