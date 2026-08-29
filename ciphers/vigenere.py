import string
from collections import Counter

ALPHA = string.ascii_uppercase

FREQ = {
    'A': 8.17, 'B': 1.49, 'C': 2.78, 'D': 4.25, 'E': 12.70, 'F': 2.23,
    'G': 2.02, 'H': 6.09, 'I': 6.97, 'J': 0.15, 'K': 0.77, 'L': 4.03,
    'M': 2.41, 'N': 6.75, 'O': 7.51, 'P': 1.93, 'Q': 0.10, 'R': 5.99,
    'S': 6.33, 'T': 9.06, 'U': 2.76, 'V': 0.98, 'W': 2.36, 'X': 0.15,
    'Y': 1.97, 'Z': 0.07
}


def _clean(s):
    return ''.join(c for c in s.upper() if c in ALPHA)


def encrypt(text, key):
    key = _clean(key)
    out = []
    ki = 0

    for c in text:
        if c.isalpha():
            shift = ALPHA.index(key[ki % len(key)])
            base = 65 if c.isupper() else 97
            out.append(chr((ord(c) - base + shift) % 26 + base))
            ki += 1
    
        else:
            out.append(c)
    return ''.join(out)


def decrypt(text, key):
    key = _clean(key)
    out = []
    ki = 0
    
    for c in text:
        if c.isalpha():
            shift = ALPHA.index(key[ki % len(key)])
            base = 65 if c.isupper() else 97
            out.append(chr((ord(c) - base - shift) % 26 + base))
            ki += 1
        else:
            out.append(c)
    return ''.join(out)


def _chi2(text):
    n = len(text)
    
    if n == 0:
        return float('inf')
    
    counts = Counter(text)
    total = 0.0
    
    for l in ALPHA:
        exp = FREQ[l] / 100 * n
        obs = counts.get(l, 0)
        total += (obs - exp) ** 2 / exp
    return total


def _repeats(text, n):
    seen = {}
    for i in range(len(text) - n + 1):
        seg = text[i:i + n]
        seen.setdefault(seg, []).append(i)
    dists = []
    
    for idxs in seen.values():
        if len(idxs) > 1:
            for a, b in zip(idxs, idxs[1:]):
                dists.append(b - a)
    return dists


def _factors(n, cap):
    return [f for f in range(2, cap + 1) if n % f == 0]


def guess_keylen(text, cap=20):
    dists = []
    
    for n in (3, 4, 5):
        dists += _repeats(text, n)

    if not dists:
        return list(range(1, cap + 1))

    counts = Counter()
    
    for d in dists:
        for f in _factors(d, cap):
            counts[f] += 1

    ranked = [f for f, _ in counts.most_common()]
    
    for f in range(1, cap + 1):
        if f not in ranked:
            ranked.append(f)
    return ranked


def _crack_column(col):
    best_shift, best_score = 0, float('inf')
    
    for shift in range(26):
        shifted = ''.join(ALPHA[(ALPHA.index(c) - shift) % 26] for c in col)
        score = _chi2(shifted)
    
        if score < best_score:
            best_score, best_shift = score, shift
    return ALPHA[best_shift]


def solve(ciphertext, max_key_len=20, tries=8):
    text = _clean(ciphertext)
    lens = guess_keylen(text, max_key_len)[:tries]

    best = None
    
    for kl in lens:
        cols = [text[i::kl] for i in range(kl)]
        key = ''.join(_crack_column(c) for c in cols)
        plain = decrypt(text, key)
        score = _chi2(plain)
    
        if best is None or score < best[2]:
            best = (key, plain, score)

    key, plain, score = best
  
    return {
        'cipher': 'vigenere',
        'key': key,
        'plaintext': plain,
        'score': score
    }
