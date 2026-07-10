from analysis.mapping import create_mapping, merge_mappings
from analysis.english_scorer import score_text
from analysis.prepare import prepare_words

def decrypt_partial(cipher_words, mapping):
    plaintext = []
    for word in cipher_words:
        decrypted = ""
        for letter in word:
            decrypted += mapping.get(letter, "_")
        plaintext.append(decrypted)
    return " ".join(plaintext)

def evaluate_mapping(cipher_words, mapping):
    plaintext = decrypt_partial(cipher_words, mapping)
    return score_text(plaintext)

def generate_candidates(cipher_word, mapping, dictionary, limit=100):
    return dictionary.find_matches(cipher_word, limit=limit, mapping=mapping)

def evaluate_candidate(cipher_word, plain_word, mapping, cipher_words):
    candidate_mapping = create_mapping(cipher_word, plain_word)
    if candidate_mapping is None:
        return None
    merged = merge_mappings(mapping, candidate_mapping)
    if merged is None:
        return None
    plaintext = decrypt_partial(cipher_words, merged)
    score = score_text(plaintext)
    return {
        "mapping": merged,
        "score": score,
        "plaintext": plaintext,
    }

def choose_best_candidate(item, mapping, cipher_words, dictionary, verbose=False, limit=100):
    cipher_word = item["word"]
    candidates = generate_candidates(cipher_word, mapping, dictionary, limit=limit)
    if not candidates:
        return None

    best = None

    if verbose:
        print(f"\n  Cipher word: {cipher_word}")
        print(f"  Candidates: {len(candidates)}")
        print(f"  Trying candidates...")
    for candidate in candidates:
        plain_word = candidate["word"]
        result = evaluate_candidate(cipher_word, plain_word, mapping, cipher_words)
        if result is None:
            continue
        if verbose:
            print(f"    {plain_word:15s}  score {result['score']}")
        if best is None or result["score"] > best["score"]:
            best = {
                "candidate": plain_word,
                "mapping": result["mapping"],
                "score": result["score"],
                "plaintext": result["plaintext"],
            }

    if verbose and best:
        print(f"  Chosen: {best['candidate']}")
        print(f"  Current score: {best['score']}")

    return best

def run_pass(prepared, mapping, cipher_words, dictionary, pass_num, verbose=False):
    if verbose:
        print(f"\n{'='*40}")
        print(f"Pass {pass_num}")
        print(f"{'='*40}")

    current_mapping = dict(mapping)

    for item in prepared:
        if item["candidate_count"] == 0:
            continue

        result = choose_best_candidate(
            item, current_mapping, cipher_words, dictionary, verbose=verbose
        )

        if result is not None and result["mapping"] is not None:
            if result["mapping"] != current_mapping:
                current_mapping = result["mapping"]

    final_score = evaluate_mapping(cipher_words, current_mapping)
    plaintext = decrypt_partial(cipher_words, current_mapping)
    improved = final_score > evaluate_mapping(cipher_words, mapping)

    if verbose:
        print(f"\n  Pass {pass_num} score: {final_score}")
        print(f"  Plaintext: {plaintext}")

    return current_mapping, final_score, improved

def solve(cipher_words, dictionary, verbose=True):
    prepared = prepare_words(cipher_words, dictionary)
    mapping = {}
    pass_num = 0
    scores = []

    while True:
        pass_num += 1
        new_mapping, new_score, improved = run_pass(
            prepared, mapping, cipher_words, dictionary, pass_num, verbose=verbose
        )
        scores.append(new_score)
        if not improved:
            if verbose:
                print(f"\n{'='*40}")
                print(f"No improvement. Finished after {pass_num - 1} passes.")
                print(f"{'='*40}")
            break
        mapping = new_mapping
    final_plaintext = decrypt_partial(cipher_words, mapping)
    final_score = evaluate_mapping(cipher_words, mapping)

    if verbose and scores:
        print(f"\nPass scores: {scores}")

    return {
        "mapping": mapping,
        "plaintext": final_plaintext,
        "score": final_score,
    }