from analysis.mapping import create_mapping, merge_mappings
from analysis.english_scorer import score_text
from analysis.prepare import prepare_words

DEBUG = True


def decrypt_partial(cipher_words, mapping):
    plaintext = []
    for word in cipher_words:
        decrypted = ""
        for letter in word:
            decrypted += mapping.get(letter, "_")
        plaintext.append(decrypted)
    return " ".join(plaintext)


def _debug_first_word(cipher_word, state, cipher_words, dictionary):
    from analysis.english_scorer import COMMON_SET

    print(f"\nDEBUG {cipher_word}")
    if state["mapping"]:
        for k, v in sorted(state["mapping"].items()):
            print(f"    {k} -> {v}")
    else:
        print("    (empty)")
    candidates = dictionary.find_matches(cipher_word, limit=None, mapping=state["mapping"])
    print(f"candidates: {len(candidates)}")
    results = []
    for candidate in candidates:
        candidate_mapping = create_mapping(cipher_word, candidate["word"])
        if candidate_mapping is None:
            continue
        merged = merge_mappings(state["mapping"], candidate_mapping)
        if merged is None:
            continue
        plaintext = decrypt_partial(cipher_words, merged)
        score = score_text(plaintext)
        results.append({
            "candidate": candidate["word"],
            "score": score,
            "plaintext": plaintext,
            "is_common": candidate["word"] in COMMON_SET,
        })

    results.sort(key=lambda x: x["score"], reverse=True)

    print(f"top {len(results)}")
    for i, r in enumerate(results):
        suffix = " [COMMON]" if r["is_common"] else ""
        if i == 0:
            suffix += " <- best"
        print(f"  {r['candidate']:15s} {r['score']:>6d}{suffix}")

    if not results:
        print("  (no candidates)")
        return

    winner = results[0]
    print(f"winner: {winner['candidate']}")
    common_words_in_results = [r for r in results if r["is_common"]]
    if common_words_in_results:
        best_common = common_words_in_results[0]
        if best_common["candidate"] != winner["candidate"]:
            print(f"best common: {best_common['candidate']}")

    if state["mapping"]:
        used = set(state["mapping"].values())
        print(f"used: {sorted(used)}")
        if winner["candidate"] == "THE":
            conflict = {"T", "H", "E"} & used
            if conflict:
                print(f"conflict: {sorted(conflict)}")

    the_result = next((r for r in results if r["candidate"] == "THE"), None)
    if the_result and the_result["candidate"] != winner["candidate"]:
        rank = results.index(the_result) + 1
        print(f"THE #{rank} {the_result['score']}")
        print(f"gap {winner['score'] - the_result['score']}")


def solve(cipher_words, dictionary, beam_width=20):
    prepared = prepare_words(cipher_words, dictionary)
    debug_done = False
    debugged_word = None
    first_cipher_word = cipher_words[0] if cipher_words else None

    beam = [{"mapping": {}, "score": 0, "plaintext": ""}]

    for item in prepared:
        if item["candidate_count"] == 0:
            continue

        cipher_word = item["word"]

        if DEBUG:
            print(f"Pass: {cipher_word} (unfiltered candidates: {item['candidate_count']})")

        if DEBUG and not debug_done:
            test_candidates = dictionary.find_matches(
                cipher_word, limit=None, mapping=beam[0]["mapping"]
            )
            if test_candidates:
                debug_done = True
                debugged_word = cipher_word
                _debug_first_word(cipher_word, beam[0], cipher_words, dictionary)

        if DEBUG and cipher_word == first_cipher_word and cipher_word != debugged_word:
            _debug_first_word(cipher_word, beam[0], cipher_words, dictionary)

        next_states = []

        for state in beam:
            candidates = dictionary.find_matches(
                cipher_word, limit=None, mapping=state["mapping"]
            )

            for candidate in candidates:
                candidate_mapping = create_mapping(cipher_word, candidate["word"])
                if candidate_mapping is None:
                    continue
                merged = merge_mappings(state["mapping"], candidate_mapping)
                if merged is None:
                    continue
                plaintext = decrypt_partial(cipher_words, merged)
                next_states.append({
                    "mapping": merged,
                    "score": score_text(plaintext),
                    "plaintext": plaintext,
                })

        if next_states:
            next_states.sort(key=lambda x: x["score"], reverse=True)
            beam = next_states[:beam_width]

    return beam
