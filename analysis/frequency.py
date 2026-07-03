import string

CHARS = string.ascii_uppercase

def analyze_frequency(text: str):
    text = text.upper()

    frequency = {char: 0 for char in CHARS}

    for char in text:
        if char in frequency:
            frequency[char] += 1

    total = sum(frequency.values())

    result = {}

    for char, count in frequency.items():
        percent = (count / total * 100) if total else 0

        result[char] = {
            "count": count,
            "percent": percent
        }

    return result