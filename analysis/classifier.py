from encoding.base import decode_base32, decode_base64

from encoding.morse_more import decode_morse, decode_binary, decode_hex

def classify(report, text): # Trying formats that can be identified directly
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
        "vigenere": 0,
    }



    if ioc >= 0.06: # IOC helps separate ciphers based on how much letter frequency is preserved
        scores["substitution"] += 24
        scores["caesar"] += 18
    
    elif ioc >= 0.055:
        scores["substitution"] += 15
        scores["caesar"] += 12
    
    elif ioc >= 0.045:
        scores["substitution"] += 6
        scores["caesar"] += 5
        scores["vigenere"] += 8
    
    elif ioc >= 0.038:
        scores["vigenere"] += 18

    
    if entropy <= 4.0:
        scores["substitution"] += 12
        scores["caesar"] += 10
    elif entropy <= 4.5:
        scores["substitution"] += 4
        scores["vigenere"] += 6
    elif entropy <= 5.2:
        scores["vigenere"] += 10

    if frequency:
        peak = max(data["percent"] for data in frequency.values())

        if peak >= 11:
            scores["substitution"] += 14
            scores["caesar"] += 12
        elif peak >= 8:
            scores["substitution"] += 4
            scores["vigenere"] += 4
        elif peak < 8:
            scores["vigenere"] += 10


    if bigrams:
        counts = list(bigrams.values())
        bigram_peak = max(counts) / sum(counts)

        if bigram_peak >= 0.08:
            scores["substitution"] += 8
            scores["caesar"] += 6
        elif bigram_peak < 0.04:
            scores["vigenere"] += 8


    if patterns:
        unique = len(set(patterns.values()))

        if unique <= 3:
            scores["substitution"] += 10
            scores["caesar"] += 10
        else:
            scores["vigenere"] += 6

    cipher = max(scores, key=scores.get)

    names = {
        "substitution": "Monoalphabetic Substitution",
        "caesar": "Caesar Cipher",
        "vigenere": "Vigenere Cipher",
    }

    return {
        "cipher": names[cipher],
        "confidence": min(99, 55 + scores[cipher]),
    }