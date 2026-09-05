import subprocess
import sys
import readline
from ciphers.crypto import generate_key, encrypt, decrypt
from tools.visualize import console, menu_table, clear, LOGO
from rich.panel import Panel
from rich.console import Group
from tools.prompts import prompt
from tools.colors import green, red, cyan, reset


def main():
    while True:
        clear()
        content = Group(LOGO, "", menu_table([
            ("1.", "Crack cipher"),
            ("2.", "Encrypt"),
            ("3.", "Decrypt"),
            ("0.", "Exit"),
        ]))
        console.print(Panel(content, border_style = "cyan"))

        choice = prompt("\nChoice: ")

        if choice == "1":
            subprocess.run([sys.executable, "main.py"])

        elif choice == "2":
            message = prompt("\nMessage: ")
            key = generate_key()
            encrypted_text = encrypt(message, key)
            console.print(Panel(f"{green}{encrypted_text}{reset}", border_style = "green", expand = False))
            console.print(f"Key: {cyan}{key.hex()}{reset}")

        elif choice == "3":
            encrypted_text = prompt("\nEncrypted text: ")
            key_hex = prompt("Key: ")
            try:
                key = bytes.fromhex(key_hex)
                plaintext = decrypt(encrypted_text, key)
                console.print(Panel(f"{green}{plaintext}{reset}", border_style = "green", expand = False))
            except Exception:
                console.print(f"{red}invalid key{reset}")

        elif choice == "0":
            console.print(f"\n{cyan}byee.{reset}")
            break

        else:
            continue

        prompt("\n[enter]")


if __name__ == "__main__":
    main()
