import re

from pathlib import Path

from analysis.dict import PatternDictionary
from analysis.iterative_solver import solve, decrypt, score_text
from analysis.report import generate_report
from ciphers.caesar import crack as crack_caesar
from ciphers.vigenere import solve as crack_vigenere
from encoding.base import solve as solve_base
from encoding.morse_more import decode_morse, decode_binary, decode_hex
from rich.console import Console
from rich.panel import Panel
from tools.colors import red, cyan, dim, reset
from tools.prompts import prompt


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


def show_result(plaintext, *extra):
    console.print(panel(plaintext, "green"))

    for line in extra:
        console.print(line)


def show_analysis(report):
    classification = report["classification"]
    cipher = classification["cipher"]

    console.print(panel(
        f"[cyan]{cipher.replace(' Substitution', '')}[/cyan] ({classification['confidence']}%)\n"
        f"IoC: {report['ioc']:.4f}  Entropy: {report['entropy']:.2f}"
    ))

    console.print(f"\n{cyan}Letters{reset}")

    for item in report["top_letters"]:
        console.print(f"  {item['letter']}  {item['percent']:.2f}%")

    console.print(f"\n{cyan}Bigrams{reset}")

    ranked = sorted(
        report["bigrams"].items(),
        key = lambda entry: (-entry[1], entry[0]),
    )

    for gram, count in ranked[:10]:
        console.print(f"  {gram}  {count}")

    console.print()


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


def solve_cipher(text, cipher, dictionary):
    # base encodings decode or they don't, try them first
    decoded, encoding = solve_base(text)

    if decoded:
        show_result(decoded, f"Encoding: {encoding}")

    elif cipher == "Monoalphabetic Substitution":
        handle_substitution(text, dictionary)

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
    show_analysis(report)

    solve_cipher(text, report["classification"]["cipher"], dictionary)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())