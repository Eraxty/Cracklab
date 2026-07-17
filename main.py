from pathlib import Path
import re
import sys
import readline

from analysis.dict import PatternDictionary
from analysis.iterative_solver import solve, decrypt, score_text
from analysis.report import generate_report
from caesar import crack as crack_caesar
from base import solve as solve_base
from morse_more import decode_morse, decode_binary, decode_hex

ROOT = Path(__file__).resolve().parent
WORDLIST_FILE = ROOT / "data" / "cleaned_words.txt"
FALLBACK_WORDLIST = ROOT / "data" / "words.txt"


def _load_dictionary(wordlist_path):
    dictionary = PatternDictionary()

    if wordlist_path.exists():
        dictionary.load(wordlist_path)
        return dictionary

    if FALLBACK_WORDLIST.exists():
        dictionary.load(FALLBACK_WORDLIST)
        return dictionary

    raise FileNotFoundError(
        f"No word list found at {wordlist_path} or {FALLBACK_WORDLIST}"
    )


def _save_results(plaintext):
    results_path = ROOT / "results.txt"
    results_path.write_text(plaintext + "\n")


def main():
    try:
        dictionary = _load_dictionary(WORDLIST_FILE)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    text = input("\nEnter ciphertext:\n> ").strip()

    if not text:
        print("No ciphertext entered.")
        return 1

    report = generate_report(text, dictionary)
    classification = report["classification"]

    cipher_name = classification["cipher"].replace(" Substitution", "")

    print("\nCrackLab")
    print(f"Cipher: {cipher_name} ({classification['confidence']}%)")
    print(f"IOC: {report['ioc']:.4f}  Entropy: {report['entropy']:.2f}")

    print("\nLetters")
    for item in report["top_letters"]:
        print(f"{item['letter']} {item['percent']:.2f}%")

    print("\nBigrams")
    ranked_bigrams = sorted(
        report["bigrams"].items(),
        key=lambda x: (-x[1], x[0]),
    )[:10]

    for gram, count in ranked_bigrams:
        print(f"{gram} {count}")

    print()
    
    decoded, encoding = solve_base(text)
    if classification["cipher"] == "Monoalphabetic Substitution":
        cipher_words = re.findall(r"[A-Z]+", text.upper())
        mapping = solve(cipher_words, dictionary)
        plaintext = decrypt(cipher_words, mapping)
        score = score_text(plaintext)
        _save_results(plaintext)
        print("\nDecrypted:")
        print(plaintext)
        print(f"\nScore: {score}")

    
    elif decoded:
        _save_results(decoded)
        print(f"\nEncoding: {encoding}")
        print("\nDecoded:")
        print(decoded)

    elif classification["cipher"] == "Caesar Cipher":
        plaintext, shift = crack_caesar(text)
        _save_results(plaintext)
        print("\nDecrypted:")
        print(plaintext)
        print(f"\nShift: {shift}")

    elif classification["cipher"] == "Morse":
        plaintext = decode_morse(text)
        _save_results(plaintext)
        print("\nDecoded:")
        print(plaintext)

    elif classification["cipher"] == "Binary":
        plaintext = decode_binary(text)
        _save_results(plaintext)
        print("\nDecoded:")
        print(plaintext)

    elif classification["cipher"] == "Hex":
        plaintext = decode_hex(text)
        _save_results(plaintext)
        print("\nDecoded:")
        print(plaintext)

    else:
        print(f"\nNo solver available for: {classification['cipher']}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())