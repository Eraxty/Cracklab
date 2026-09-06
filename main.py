import subprocess
import sys
import readline
import os
from ciphers.crypto import generate_key, encrypt, decrypt
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from tools.prompts import prompt
from tools.colors import green, red, cyan, reset

console = Console()

LOGO = r"""
 ██████╗ ██████╗   █████╗  ██████╗██╗  ██╗██╗      █████╗ ██████╗
██╔════╝ ██╔══██╗ ██╔══██╗██╔════╝██║ ██╔╝██║     ██╔══██╗██╔══██╗
██║      ██████╔╝ ███████║██║     █████╔╝ ██║     ███████║██████╔╝
██║      ██╔══██╗ ██╔══██║██║     ██╔═██╗ ██║     ██╔══██║██╔══██╗
╚██████╗ ██║  ██║ ██║  ██║╚██████╗██║  ██╗███████╗██║  ██║██████╔╝
 ╚═════╝ ╚═╝  ╚═╝ ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝
"""


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def menu_table(rows):
    table = Table(show_header = False, box = None, padding = (0, 2))
    table.add_column("num", style = "bold cyan", width = 3)
    table.add_column("label", style = "white")
    
    for num, label in rows:
        table.add_row(num, label)
    return table


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
            subprocess.run([sys.executable, "crack.py"])

        elif choice == "2":
            message = prompt("\nMessage: ")
            key = generate_key()
            encrypted_text = encrypt(message, key)
            console.print(Panel(f"[green]{encrypted_text}[/green]", border_style = "green", expand = False))
            console.print(f"Key: [cyan]{key.hex()}[/cyan]")

        elif choice == "3":
            encrypted_text = prompt("\nEncrypted text: ")
            key_hex = prompt("Key: ")
            try:
                key = bytes.fromhex(key_hex)
                plaintext = decrypt(encrypted_text, key)
                console.print(Panel(f"[green]{plaintext}[/green]", border_style = "green", expand = False))
            except Exception:
                console.print("[red]invalid key[/red]")

        elif choice == "0":
            console.print(f"\n{cyan}byee.{reset}")
            break

        else:
            continue

        prompt("\n[enter]")


if __name__ == "__main__":
    main()
