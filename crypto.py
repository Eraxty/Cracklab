import base64
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def generate_key():
    return AESGCM.generate_key(bit_length=256)


def encrypt(message, key):
    nonce = os.urandom(12)
    aes = AESGCM(key)
    ciphertext = aes.encrypt(nonce,message.encode("utf-8"),None,)
    encrypted = nonce + ciphertext
    return base64.urlsafe_b64encode(encrypted).decode("utf-8")

def decrypt(encrypted_text, key):
    encrypted = base64.urlsafe_b64decode(encrypted_text)
    nonce = encrypted[:12]
    ciphertext = encrypted[12:]
    aes = AESGCM(key)
    plaintext = aes.decrypt(nonce,ciphertext,None,)
    return plaintext.decode("utf-8")