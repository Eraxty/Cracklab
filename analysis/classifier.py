from base import decode_base32, decode_base64
from morse_more import decode_morse, decode_binary, decode_hex


def classify(report, text):
    if decode_base32(text):
        return {
            "cipher": "Base32",
            "confidence": 99,
        }

    if decode_base64(text):
        return {
            "cipher": "Base64",
            "confidence": 99,
        }
    
    if decode_morse(text):
        return {"cipher":"Morse",
                "confidence": 99
        }
    
    if decode_binary(text):
        return {"cipher": "Binary",
                "confidence":99
        }

    if decode_hex(text):
        return {"cipher": "Hex",
                "confidence":99
        }

    ioc = report["ioc"]
    entropy = report["entropy"]
    frequency = report["frequency"]
    bigrams = report["bigrams"]
    patterns = report["patterns"]

    scores = {
        "substitution": 0,
        "caesar": 0,
    }

    if ioc >= 0.06:
        scores["substitution"] += 24
        scores["caesar"] += 18
    elif ioc >= 0.048:
        scores["substitution"] += 15
        scores["caesar"] += 12

    if entropy <= 4.2:
        scores["substitution"] += 12
        scores["caesar"] += 10

    if frequency:
        peak = max(data["percent"] for data in frequency.values())

        if peak >= 11:
            scores["substitution"] += 14
            scores["caesar"] += 12

    if bigrams:
        counts = list(bigrams.values())
        bigram_peak = max(counts) / sum(counts)

        if bigram_peak >= 0.08:
            scores["substitution"] += 8
            scores["caesar"] += 6

    if patterns:
        scores["substitution"] += 10
        scores["caesar"] += 10

    cipher = max(scores, key=scores.get)

    names = {
        "substitution": "Monoalphabetic Substitution",
        "caesar": "Caesar Cipher",
    }

    return {
        "cipher": names[cipher],
        "confidence": min(99, 55 + scores[cipher]),
    }