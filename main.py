from pathlib import Path
import re
import sys
import readline

from analysis.dict import PatternDictionary
from analysis.iterative_solver import solve, decrypt, score_text
from analysis.report import generate_report
from ciphers.caesar import crack as crack_caesar
from ciphers.vigenere import solve as crack_vigenere
from encoding.base import solve as solve_base
from encoding.morse_more import decode_morse, decode_binary, decode_hex
from tools.visualize import console, panel, banner, menu_table, clear
from tools.prompts import prompt
from tools.colors import green, red, cyan, yellow, dim, reset

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
        console.print(f"{red}Error: {exc}{reset}")
        return 1

    clear()
    banner()

    text = prompt("\nEnter ciphertext:\n> ")

    if not text:
        console.print(f"{red}No ciphertext entered.{reset}")
        return 1

    report = generate_report(text, dictionary)
    classification = report["classification"]
    cipher_name = classification["cipher"].replace(" Substitution", "")

    console.print(panel(
        f"Cipher: {cyan}{cipher_name}{reset} ({classification['confidence']}%)\n"
        f"IoC: {report['ioc']:.4f}  Entropy: {report['entropy']:.2f}"
    ))

    console.print(f"\n{cyan}Letters{reset}")
    for item in report["top_letters"]:
        console.print(f"  {item['letter']}  {item['percent']:.2f}%")

    console.print(f"\n{cyan}Bigrams{reset}")
    ranked_bigrams = sorted(
        report["bigrams"].items(),
        key=lambda x: (-x[1], x[0]),
    )[:10]
    for gram, count in ranked_bigrams:
        console.print(f"  {gram}  {count}")

    console.print()

    decoded, encoding = solve_base(text)

    if classification["cipher"] == "Monoalphabetic Substitution":
        cipher_words = re.findall(r"[A-Z]+", text.upper())
        console.print(f"{dim}running substitution solver...{reset}")
        mapping = solve(cipher_words, dictionary)
        mono_plain = decrypt(cipher_words, mapping)
        mono_score = score_text(mono_plain)

        console.print(f"{dim}running vigenere solver...{reset}")
        vig_result = crack_vigenere(text)
        vig_plain = vig_result["plaintext"]
        vig_score = score_text(vig_plain)

        if vig_score > mono_score:
            _save_results(vig_plain)
            console.print(panel(f"{green}{vig_plain}{reset}", "green"))
            console.print(f"Key: {vig_result['key']}")
        else:
            _save_results(mono_plain)
            console.print(panel(f"{green}{mono_plain}{reset}", "green"))
            console.print(f"Score: {mono_score}")

    elif decoded:
        _save_results(decoded)
        console.print(panel(f"{green}{decoded}{reset}", "green"))
        console.print(f"Encoding: {encoding}")

    elif classification["cipher"] == "Caesar Cipher":
        console.print(f"{dim}brute-forcing 26 shifts...{reset}")
        plaintext, shift = crack_caesar(text)
        _save_results(plaintext)
        console.print(panel(f"{green}{plaintext}{reset}", "green"))
        console.print(f"Shift: {shift}")

    elif classification["cipher"] == "Vigenere Cipher":
        console.print(f"{dim}analyzing key length...{reset}")
        result = crack_vigenere(text)
        plaintext = result["plaintext"]
        key = result["key"]
        _save_results(plaintext)
        console.print(panel(f"{green}{plaintext}{reset}", "green"))
        console.print(f"Key: {key}")

    elif classification["cipher"] == "Morse":
        plaintext = decode_morse(text)
        _save_results(plaintext)
        console.print(panel(f"{green}{plaintext}{reset}", "green"))

    elif classification["cipher"] == "Binary":
        plaintext = decode_binary(text)
        _save_results(plaintext)
        console.print(panel(f"{green}{plaintext}{reset}", "green"))

    elif classification["cipher"] == "Hex":
        plaintext = decode_hex(text)
        _save_results(plaintext)
        console.print(panel(f"{green}{plaintext}{reset}", "green"))

    else:
        console.print(f"{red}No solver available for: {classification['cipher']}{reset}")

    prompt("\n[enter]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
