import subprocess
import sys
import readline
from crypto import generate_key, encrypt, decrypt

def main():
    while True:
        print("=============================")
        print("CrackLab")
        print("=============================")
        print("1. Crack cipher")
        print("2. Encrypt")
        print("3. Decrypt")
        print("4. Exit")

        choice = input("> ").strip()

        if choice == "1":
            subprocess.run([sys.executable, "main.py"])

        elif choice == "2":
                    message = input("\nMessage: ")
                    key = generate_key()
                    encrypted_text = encrypt(message, key)
                    print("\nEncrypted:")
                    print(encrypted_text)
                    print("\nKey:")
                    print(key.hex())

        elif choice == "3":
            encrypted_text = input("\nEncrypted text: ").strip()
            key_hex = input("Key: ").strip()
            try:
                key = bytes.fromhex(key_hex)
                plaintext = decrypt(encrypted_text, key)
                print("\nDecrypted: ")
                print(plaintext)

            except Exception:
                print("Invalid key")
        
        elif choice == "4":
            break

        else:
            continue

if __name__ == "__main__":
    main()