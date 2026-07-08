from pathlib import Path
import re
import argparse
import sys

from analysis.dict import PatternDictionary
from analysis.solver import solve
from analysis.report import generate_report
from analysis.prepare import prepare_words, print_prepared
from analysis.english_scorer import score_text

ROOT = Path(__file__).resolve().parent
INPUT_FILE = ROOT / "crack.txt"
WORDLIST_FILE = ROOT / "data" / "cleaned_words.txt"
FALLBACK_WORDLIST = ROOT / "data" / "words.txt"


def _format_percent(value):
    return f"{value:.2f}%"


def _print_header():
    print("====================================")
    print("CrackLab")
    print("====================================\n")


def _print_top_letters(top_letters):
    if not top_letters:
        print("None")
        return

    for item in top_letters:
        print(f"{item['letter']} {_format_percent(item['percent'])}")


def _print_top_bigrams(bigrams, limit=10):
    if not bigrams:
        print("None")
        return

    ranked = sorted(bigrams.items(), key=lambda item: (-item[1], item[0]))[:limit]
    for gram, count in ranked:
        print(f"{gram} {count}")


def _load_dictionary(wordlist_path):
    dictionary = PatternDictionary()
    if wordlist_path.exists():
        dictionary.load(wordlist_path)
        return dictionary

    if FALLBACK_WORDLIST.exists():
        dictionary.load(FALLBACK_WORDLIST)
        return dictionary

    raise FileNotFoundError(f"No word list found at {wordlist_path} or {FALLBACK_WORDLIST}")


def _print_solver_result(solution):
    print("\nSolver Result\n")

    if solution is None:
        print("No mapping solution found.")
        return
    for cipher_letter in sorted(solution["mapping"]):
        print(f"{cipher_letter} -> {solution['mapping'][cipher_letter]}")

    print("\nPartial Plaintext:")
    print(solution["plaintext"])


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

    _print_header()
    print(f"Input File:\n{Path(args.input_file).name}\n")
    print(f"Detected Cipher:\n{classification['cipher']}\n")
    print(f"Confidence:\n{classification['confidence']}%\n")

    print("\nTop Letters:\n")
    _print_top_letters(report["top_letters"])

    print("\nTop Bigrams:\n")
    _print_top_bigrams(report["bigrams"])

    print(f"\nEntropy:\n{report['entropy']:.2f}\n")
    print(f"Index of Coincidence:\n{report['ioc']:.4f}\n")
    print("====================================")

    if classification["cipher"] == "Monoalphabetic Substitution":
        cipher_words = re.findall(r"[A-Z]+", text.upper())
        prepared = prepare_words(cipher_words, dictionary)
        print("Prepared Word List:\n")
        print_prepared(prepared)
        print()
        solution = solve(cipher_words, dictionary)
        _print_solver_result(solution)
    else:
        print("\nno solver for ts rn.")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
