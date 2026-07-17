import math
import re

from analysis.classifier import classify
from analysis.frequency import analyze_frequency
from analysis.ngrams import count_ngrams
from analysis.patterns import word_pattern


def _normalize_text(text):
    return text.upper()

def _top_letters(frequency, limit=10):
    ranked = sorted(
        frequency.items(),
        key=lambda item: (-item[1]["count"], item[0]),
    )
    return [
        {"letter": letter, "count": data["count"], "percent": data["percent"]}
        for letter, data in ranked[:limit]
        if data["count"] > 0
    ]

def _word_patterns(text):
    words = re.findall(r"[A-Z]+", text.upper())
    patterns = {}
    for word in words:
        pattern = word_pattern(word)
        patterns[pattern] = patterns.get(pattern, 0) + 1
    return patterns

def _index_of_coincidence(frequency):
    counts = [data["count"] for data in frequency.values() if data["count"] > 0]
    total = sum(counts)
    if total < 2:
        return 0.0
    numerator = sum(count * (count - 1) for count in counts)
    denominator = total * (total - 1)
    return numerator / denominator if denominator else 0.0

def _shannon_entropy(frequency):
    counts = [data["count"] for data in frequency.values() if data["count"] > 0]
    total = sum(counts)
    if not total:
        return 0.0
    entropy = 0.0
    for count in counts:
        probability = count / total
        entropy -= probability * math.log2(probability)
    return entropy

def generate_report(text, dictionary):
    normalized = _normalize_text(text)
    frequency = analyze_frequency(normalized)
    report = {
        "frequency": frequency,
        "top_letters": _top_letters(frequency, limit=10),
        "bigrams": count_ngrams(normalized, 2),
        "trigrams": count_ngrams(normalized, 3),
        "ioc": _index_of_coincidence(frequency),
        "entropy": _shannon_entropy(frequency),
        "patterns": _word_patterns(normalized),
    }
    report["classification"] = classify(report, text)
    return report
