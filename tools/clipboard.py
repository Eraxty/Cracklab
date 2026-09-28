try:
    import pyperclip
except ImportError:
    pyperclip = None


def copy_text(text):
    if pyperclip is None:
        return False

    try:
        pyperclip.copy(text)
        return True
    except pyperclip.PyperclipException:
        return False
