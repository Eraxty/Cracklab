from pathlib import Path
import re

from analysis.dict import PatternDictionary
from analysis.solver import solve
from analysis.report import generate_report


ROOT = Path(__file__).resolve().parent
INPUT_FILE = ROOT / "crack.txt"
WORDLIST_FILE = ROOT / "data" / "cleaned_words.txt"


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


def _print_solver_result(solution):
    print("\nSolver Result\n")

    if solution is None:
        print("No mapping-consistent solution found.")
        return

    print("Mapping:")
    for cipher_letter in sorted(solution["mapping"]):
        print(f"{cipher_letter} -> {solution['mapping'][cipher_letter]}")

    print("\nRecovered Words:")
    print(" ".join(solution["words"]))


def main():
    dictionary = PatternDictionary()
    dictionary.load(WORDLIST_FILE)

    text = INPUT_FILE.read_text()
    report = generate_report(text, dictionary)
    classification = report["classification"]

    _print_header()
    print(f"Input File:\n{INPUT_FILE.name}\n")
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
        solution = solve(cipher_words, dictionary)
        _print_solver_result(solution)
    else:
        print("\nSolver for this cipher has not been implemented yet.")


if __name__ == "__main__":
    main()
