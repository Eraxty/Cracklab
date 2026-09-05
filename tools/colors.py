import sys
import colorama
from colorama import Fore, Style

colorama.init()

if sys.stdout.isatty():
    reset = Style.RESET_ALL
    bold = Style.BRIGHT
    dim = Style.DIM
    red = Fore.RED
    green = Fore.GREEN
    yellow = Fore.YELLOW
    cyan = Fore.CYAN
else:
    reset = bold = dim = red = green = yellow = cyan = ""
