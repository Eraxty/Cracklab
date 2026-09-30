import re

from analysis.eng_words import WORD_SET
from ciphers.caesar import crack as crack_caesar
from encoding.base import decode_base32, decode_base64
from encoding.morse_more import decode_morse, decode_binary, decode_hex


def detect_caesar(text):
    plaintext, _ = crack_caesar(text)
    words = re.findall(r"[A-Z]+", plaintext)

    if not words:
        return False

    known = 0

    for word in words:
        if word in WORD_SET:
            known += 1

    return known / len(words) >= 0.8



def classify(report, text):
    direct = (
        ("Base32", decode_base32),
        ("Base64", decode_base64),
        ("Morse", decode_morse),
        ("Binary", decode_binary),
        ("Hex", decode_hex),
    )

    for name, decoder in direct:
        if decoder(text):
            return {"cipher": name, "confidence": 99}

    ioc = report["ioc"]
    entropy = report["entropy"]
    frequency = report["frequency"]
    bigrams = report["bigrams"]
    patterns = report["patterns"]

    scores = {
        "substitution": 0,
        "vigenere": 0,
    }

    if ioc >= 0.06:
        scores["substitution"] += 24

    elif ioc >= 0.055:
        scores["substitution"] += 15

    elif ioc >= 0.045:
        scores["substitution"] += 6
        scores["vigenere"] += 8
    
    elif ioc >= 0.038:
        scores["vigenere"] += 18


    if entropy <= 4.0:
        scores["substitution"] += 12

    elif entropy <= 4.5:
        scores["substitution"] += 4
        scores["vigenere"] += 6

    elif entropy <= 5.2:
        scores["vigenere"] += 10

    if frequency:
        peak = max(data["percent"] for data in frequency.values())

        if peak >= 11:
            scores["substitution"] += 14

        elif peak >= 8:
            scores["substitution"] += 4
            scores["vigenere"] += 4

        else:
            scores["vigenere"] += 10

    if bigrams:
        counts = list(bigrams.values())
        bigram_peak = max(counts) / sum(counts)

        if bigram_peak >= 0.08:
            scores["substitution"] += 8
        elif bigram_peak < 0.04:
            scores["vigenere"] += 8

    if patterns:
        unique = len(set(patterns.values()))

        if unique <= 3:
            scores["substitution"] += 10
        else:
            scores["vigenere"] += 6

    if ioc >= 0.06 and detect_caesar(text):
        return {"cipher": "Caesar Cipher", "confidence": 99}

    cipher = max(scores, key = scores.get)

    names = {
        "substitution": "Monoalphabetic Substitution",
        "vigenere": "Vigenere Cipher",
    }

    return {
        "cipher": names[cipher],
        "confidence": min(99, 55 + scores[cipher]),
    }