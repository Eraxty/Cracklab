def _num(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

def _add(scores, evidence, note, **points):
    for cipher, value in points.items():
        scores[cipher] += value
    if note and note not in evidence:
        evidence.append(note)

def _frequency_peak(frequency):
    if not isinstance(frequency, dict) or not frequency:
        return None

    percents = []
    for data in frequency.values():
        if isinstance(data, dict):
            percent = _num(data.get("percent"))
            if percent is not None:
                percents.append(percent)
    return max(percents) if percents else None

def _bigram_peak(bigrams):
    if not isinstance(bigrams, dict) or not bigrams:
        return None
    counts = [count for count in bigrams.values() if isinstance(count, int) and count > 0]
    if not counts:
        return None
    total = sum(counts)
    return max(counts) / total if total else None

def _patterns_present(patterns):
    if isinstance(patterns, dict):
        if not patterns:
            return False
        if any(isinstance(value, dict) and value.get("count", 0) > 1 for value in patterns.values()):
            return True
        return True
    return bool(patterns)

def classify(report):
    scores = {
        "substitution": 0,
        "caesar": 0,
        "vigenere": 0,
        "unknown": 8,
    }
    evidence = []

    ioc = _num(report.get("ioc"))
    entropy = _num(report.get("entropy"))
    frequency = report.get("frequency")
    bigrams = report.get("bigrams")
    patterns = report.get("patterns")

    # High IOC monoalphabetic cipher.
    if ioc is not None:
        if ioc >= 0.06:
            _add(scores, evidence, "High Index of Coincidence", substitution=24, caesar=18)
        elif ioc >= 0.048:
            _add(scores, evidence, "Moderate Index of Coincidence", substitution=15, caesar=12, vigenere=4)
        else:
            _add(scores, evidence, "Low Index of Coincidence", vigenere=20, unknown=6)

    if entropy is not None:
        if entropy <= 4.2:
            _add(scores, evidence, "Letter entropy resembles English", substitution=12, caesar=10)
        elif entropy >= 4.5:
            _add(scores, evidence, "Flattened letter entropy", vigenere=18, unknown=4)
        else:
            _add(scores, evidence, "Midrange letter entropy", substitution=4, caesar=4, vigenere=4)

    peak = _frequency_peak(frequency)
    if peak is not None:
        if peak >= 11:
            _add(scores, evidence, "Letter frequencies resemble English", substitution=14, caesar=12)
        elif peak <= 8:
            _add(scores, evidence, "Flattened letter frequencies", vigenere=14, unknown=4)

    bigram_peak = _bigram_peak(bigrams)
    if bigram_peak is not None:
        if bigram_peak >= 0.08:
            _add(scores, evidence, "Repeated digram structure preserved", substitution=8, caesar=6)
        elif bigram_peak <= 0.05:
            _add(scores, evidence, "Bigram distribution is diffuse", vigenere=8)

    if _patterns_present(patterns):
        _add(scores, evidence, "Repeated word patterns preserved", substitution=10, caesar=10)

    if max(scores["substitution"], scores["caesar"], scores["vigenere"]) < 20:
        scores["unknown"] += 12

    priority = {"unknown": 3, "substitution": 2, "caesar": 1, "vigenere": 0}
    cipher = max(scores, key=lambda name: (scores[name], priority[name]))

    return {
        "cipher": {
            "substitution": "Monoalphabetic Substitution",
            "caesar": "Caesar Cipher",
            "vigenere": "Vigenère Cipher",
            "unknown": "Unknown",
        }[cipher],
        "confidence": min(100, int(scores[cipher])),
        "score": scores,
        "evidence": evidence,
    }

