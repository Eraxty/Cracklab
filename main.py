from pathlib import Path
import re
import argparse
import sys

from analysis.dict import PatternDictionary
from analysis.iterative_solver import solve, decrypt, score_text
from analysis.report import generate_report

ROOT = Path(__file__).resolve().parent
INPUT_FILE = ROOT / "crack.txt"
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

    raise FileNotFoundError(f"No word list found at {wordlist_path} or {FALLBACK_WORDLIST}")


def _save_results(plaintext):
    results_path = ROOT / "results.txt"
    results_path.write_text(plaintext + "\n")

def _parse_args():
    parser = argparse.ArgumentParser(prog="CrackLab", description="Cipher analysis pipeline")
    parser.add_argument("input_file", nargs="?", default=str(INPUT_FILE), help="ciphertext file")
    parser.add_argument("--wordlist", default=str(WORDLIST_FILE), help="dictionary word list")
    return parser.parse_args()

def main():
    args = _parse_args()

    try:
        dictionary = _load_dictionary(Path(args.wordlist))
        text = Path(args.input_file).read_text(encoding="utf-8", errors="ignore")
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    report = generate_report(text, dictionary)
    classification = report["classification"]

    cipher_name = classification["cipher"].replace(" Substitution", "")
    print("CrackLab")
    print(f"Cipher: {cipher_name} ({classification['confidence']}%)")
    print(f"IOC: {report['ioc']:.4f}  Entropy: {report['entropy']:.2f}")

    print("\nLetters")
    for item in report["top_letters"]:
        print(f"{item['letter']} {item['percent']:.2f}%")

    print("\nBigrams")
    ranked_bigrams = sorted(report["bigrams"].items(), key=lambda x: (-x[1], x[0]))[:10]
    for gram, count in ranked_bigrams:
        print(f"{gram} {count}")
    print()

    if classification["cipher"] == "Monoalphabetic Substitution":
        cipher_words = re.findall(r"[A-Z]+", text.upper())
        mapping = solve(cipher_words, dictionary)
        plaintext = decrypt(cipher_words, mapping)
        score = score_text(plaintext)
        _save_results(plaintext)
    else:
        print(f"\nNo solver available for: {classification['cipher']}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
