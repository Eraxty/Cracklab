def word_pattern(word: str):
    word = word.upper()

    pattern = []
    letter_map = {}
    next_id = 0

    for letter in word:
        if letter not in letter_map:
            letter_map[letter] = str(next_id)
            next_id += 1

        pattern.append(letter_map[letter])

    return "".join(pattern)