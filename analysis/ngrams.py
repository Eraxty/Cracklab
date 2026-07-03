import string

CHARS = string.ascii_uppercase

def count_ngrams(text: str, n: int):
    text = text.upper()

    # Remove unnecessary characters
    clean_text = "".join(char for char in text if char in CHARS)

    ngrams = {}

    for i in range(len(clean_text) - n + 1):
        gram = clean_text[i:i + n]
        if gram in ngrams:
            ngrams[gram] += 1
        else:
            ngrams[gram] = 1
    return ngrams