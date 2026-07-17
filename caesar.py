from analysis.english_scorer import score_text

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def decrypt(text, shift):
    result = ""
    for letter in text.upper():
        if letter in ALPHABET:
            position = ALPHABET.index(letter)
            new_position = (position - shift) % 26
            result += ALPHABET[new_position]
        else:
            result += letter
    return result

def crack(text):
    best_text = ""
    best_shift = 0
    best_score = float("-inf")
    for shift in range(26):
        decrypted = decrypt(text, shift)
        score = score_text(decrypted)
        if score > best_score:
            best_text = decrypted
            best_shift = shift
            best_score = score
    return best_text, best_shift