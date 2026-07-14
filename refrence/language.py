from refrence.english import ENGLISH

def score_language(letter_frequency):
    score = 0

    # Sort ciphertext letters by frequency
    cipher_letters = sorted(
        letter_frequency.items(),
        key=lambda item: item[1]["percent"],
        reverse=True
    )

    # Sort letters by frequency
    english_letters = sorted(
        ENGLISH["letters"].items(),
        key=lambda item: item[1],
        reverse=True
    )

    # Compare
    for i in range(min(len(cipher_letters), len(english_letters))):
        cipher_letter = cipher_letters[i][0]
        english_letter = english_letters[i][0]

        score += abs(
            letter_frequency[cipher_letter]["percent"]
            - ENGLISH["letters"][english_letter]
        )
    return score
