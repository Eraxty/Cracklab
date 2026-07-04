def is_mapping_valid(mapping):
    cipher_to_plain = {}
    plain_to_cipher = {}

    for cipher_letter, plain_letter in mapping.items():
        if cipher_to_plain.get(cipher_letter) not in (None, plain_letter):
            return False

        if plain_to_cipher.get(plain_letter) not in (None, cipher_letter):
            return False

        cipher_to_plain[cipher_letter] = plain_letter
        plain_to_cipher[plain_letter] = cipher_letter

    return True


def create_mapping(cipher_word, plain_word):
    cipher_word = cipher_word.upper()
    plain_word = plain_word.upper()

    if len(cipher_word) != len(plain_word):
        return None

    mapping = {}

    for cipher_letter, plain_letter in zip(cipher_word, plain_word):
        existing_plain = mapping.get(cipher_letter)

        if existing_plain is not None and existing_plain != plain_letter:
            return None

        mapping[cipher_letter] = plain_letter

    if not is_mapping_valid(mapping):
        return None

    return mapping


def merge_mappings(map1, map2):
    merged = dict(map1)

    for cipher_letter, plain_letter in map2.items():
        existing_plain = merged.get(cipher_letter)

        if existing_plain is not None and existing_plain != plain_letter:
            return None

        merged[cipher_letter] = plain_letter

    if not is_mapping_valid(merged):
        return None

    return merged
