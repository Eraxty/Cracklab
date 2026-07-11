def build_remember(cipher_words, plaintext):
    plain_words = plaintext.split()
    remember = {}
    for cipher, plain in zip(cipher_words, plain_words):
        remember[cipher] = plain
    return remember