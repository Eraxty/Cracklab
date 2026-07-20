MORSE = {
    ".-": "A", "-...": "B", "-.-.": "C", "-..": "D",
    ".": "E", "..-.": "F", "--.": "G", "....": "H",
    "..": "I", ".---": "J", "-.-": "K", ".-..": "L",
    "--": "M", "-.": "N", "---": "O", ".--.": "P",
    "--.-": "Q", ".-.": "R", "...": "S", "-": "T",
    "..-": "U", "...-": "V", ".--": "W", "-..-": "X",
    "-.--": "Y", "--..": "Z",
}

def decode_morse(text):
    try:
        words = text.split(" / ")
        result = []
        for word in words:
            letters = word.split()
            result.append("".join(MORSE[letter] for letter in letters))
        return " ".join(result)
    except:
        return None

def decode_binary(text):
    try:
        parts = text.split()
        return "".join(chr(int(part, 2)) for part in parts)
    except:
        return None

def decode_hex(text):
    try:
        return bytes.fromhex(text).decode()
    except:
        return None