import base64
import binascii

def decode_base64(text):
    try:
        decoded = base64.b64decode(text).decode("utf-8")
        return decoded
    except (ValueError, UnicodeDecodeError, binascii.Error):
        return None

def decode_base32(text):
    try:
        decoded = base64.b32decode(text).decode("utf-8")
        return decoded
    except (ValueError, UnicodeDecodeError, binascii.Error):
        return None

def solve(text):
    text = text.strip()
    decoded = decode_base32(text)
    if decoded:
        return decoded, "Base32"
    decoded = decode_base64(text)
    if decoded:
        return decoded, "Base64"
    return None, None