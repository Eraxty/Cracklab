from collections import Counter

def prepare_words(cipher_words, dictionary):
    counts = Counter(cipher_words)
    words = []
    for word in cipher_words:
        if any(item["word"] == word for item in words):
            continue
        matches = dictionary.find_matches(word, limit=None)
        words.append({
            "word": word,
            "length": len(word),
            "count": counts[word],
            "candidate_count": len(matches),
        })
    words.sort(
        key=lambda x: (
            x["candidate_count"],
            -x["length"],
            -x["count"],
        )
    )
    return words

def print_prepared(words):
    print("Prepared Words\n")
    print("WORD\tLEN\tCOUNT\tCANDIDATES")

    for item in words:
        print(
            f"{item['word']}\t"
            f"{item['length']}\t"
            f"{item['count']}\t"
            f"{item['candidate_count']}"
        )