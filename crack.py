from pathlib import Path
import re

from analysis.dict import PatternDictionary
from analysis.iterative_solver import solve, decrypt, score_text
from analysis.report import generate_report
from analysis.ml_classifier import classify as ml_classify
from ciphers.caesar import crack as crack_caesar
from ciphers.vigenere import solve as crack_vigenere
from encoding.base import solve as solve_base
from encoding.morse_more import decode_morse, decode_binary, decode_hex
from rich.console import Console
from rich.panel import Panel
from tools.prompts import prompt
from tools.colors import green, red, cyan, dim, reset


console = Console()

ROOT = Path(__file__).resolve().parent
WORDLIST_FILE = ROOT / "data" / "cleaned_words.txt"
FALLBACK_WORDLIST = ROOT / "data" / "words.txt"


def panel(content, border = "cyan"):
    return Panel(content, border_style = border, expand = False)


def load_dictionary():
    path = WORDLIST_FILE if WORDLIST_FILE.exists() else FALLBACK_WORDLIST

    if not path.exists():
        raise FileNotFoundError(f"no wordlist at {WORDLIST_FILE} or {FALLBACK_WORDLIST}")

    dictionary = PatternDictionary()
    dictionary.load(path)
    return dictionary


def save(plaintext):
    (ROOT / "results.txt").write_text(plaintext + "\n")


def show_result(plaintext, *extra):
    save(plaintext)
    console.print(panel(plaintext, "green"))

    for line in extra:
        console.print(line)


def handle_substitution(text, dictionary):
    words = re.findall(r"[A-Z]+", text.upper())

    console.print(f"{dim}running substitution solver...{reset}")
    mono_plain = decrypt(words, solve(words, dictionary))
    mono_score = score_text(mono_plain)

    console.print(f"{dim}running vigenere solver...{reset}")
    vig = crack_vigenere(text)
    vig_score = score_text(vig["plaintext"])

    if vig_score > mono_score:
        show_result(vig["plaintext"], f"Key: {vig['key']}")
    else:
        show_result(mono_plain, f"Score: {mono_score}")


def main():
    try:
        dictionary = load_dictionary()
    except FileNotFoundError as exc:
        console.print(f"{red}Error: {exc}{reset}")
        return 1

    text = prompt("\nEnter ciphertext:\n> ")

    if not text:
        console.print(f"{red}No ciphertext entered.{reset}")
        return 1

    report = generate_report(text, dictionary)
    cls = ml_classify(text)
    cipher = cls["cipher"]

    console.print(panel(
        f"[cyan]{cipher.replace(' Substitution', '')}[/cyan] ({cls['confidence']}%)\n"
        f"IoC: {report['ioc']:.4f}  Entropy: {report['entropy']:.2f}"
    ))

    console.print(f"\n{cyan}Letters{reset}")
    for item in report["top_letters"]:
        console.print(f"  {item['letter']}  {item['percent']:.2f}%")

    console.print(f"\n{cyan}Bigrams{reset}")
    bigrams = sorted(report["bigrams"].items(), key = lambda x: (-x[1], x[0]))[:10]
    for gram, count in bigrams:
        console.print(f"  {gram}  {count}")

    console.print()

    decoded, encoding = solve_base(text)

    if cipher == "Monoalphabetic Substitution":
        handle_substitution(text, dictionary)

    elif decoded:
        show_result(decoded, f"Encoding: {encoding}")

    elif cipher == "Caesar Cipher":
        console.print(f"{dim}brute forcing 26 shifts...{reset}")
        plaintext, shift = crack_caesar(text)
        show_result(plaintext, f"Shift: {shift}")

    elif cipher == "Vigenere Cipher":
        console.print(f"{dim}analyzing key length...{reset}")
        result = crack_vigenere(text)
        show_result(result["plaintext"], f"Key: {result['key']}")

    elif cipher == "Morse":
        show_result(decode_morse(text))

    elif cipher == "Binary":
        show_result(decode_binary(text))

    elif cipher == "Hex":
        show_result(decode_hex(text))

    else:
        console.print(f"{red}No solver available for: {cipher}{reset}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
