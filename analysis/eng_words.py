from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"


def _load_word_set(filename):
    path = DATA_DIR / filename
    return {
        line.strip().upper()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


COMMON_WORDS = _load_word_set("common_words.txt")
COMMON_SET = COMMON_WORDS
WORD_SET = _load_word_set("cleaned_words.txt")

COMMON_LETTERS = "ETAOINSHRDLCUMWFGYPBVKJXQZ"

COMMON_BIGRAMS = {
    "TH": 5, "HE": 5, "IN": 4, "ER": 4, "AN": 4, "RE": 4,
    "ON": 3, "AT": 3, "EN": 3, "ND": 3, "TI": 3, "ES": 3,
    "OR": 3, "TE": 3, "OF": 3, "ED": 3, "IS": 3, "IT": 3,
    "AL": 2, "AR": 2, "ST": 2, "TO": 2, "NT": 2, "NG": 2,
    "SE": 2, "HA": 2, "AS": 2, "OU": 2, "IO": 2, "LE": 2,
    "VE": 2, "CO": 2, "ME": 2, "DE": 2, "HI": 2, "RI": 2,
}

COMMON_TRIGRAMS = {
    "THE": 7, "AND": 6, "ING": 6, "HER": 5, "ERE": 5,
    "ENT": 5, "THA": 5, "NTH": 4, "WAS": 4, "ETH": 4,
    "FOR": 4, "DTH": 3, "HAT": 4, "ION": 5, "TIO": 5,
    "VER": 3, "TER": 4, "HES": 3, "ALL": 3, "OFT": 3,
}

COMMON_ENDINGS = (
    "S", "ES", "ED", "ER", "EST", "ING", "LY", "TION", "ION", "MENT", "NESS",
    "ABLE", "IBLE", "AL", "IC", "OUS", "IVE", "FUL", "LESS", "Y", "E",
)

VOWELS = {"A", "E", "I", "O", "U"}

RARE_PENALTY = {"J": -20, "Q": -30, "X": -25, "Z": -30, "K": -10}

IMPOSSIBLE_BIGRAMS = {
    "QJ", "QQ", "QX", "QY", "JQ", "JX", "JZ", "XQ", "XZ", "ZQ", "ZX", "ZJ",
}

COMMON_DOUBLES = {
    "LL", "EE", "SS", "OO",
    "TT", "RR", "NN", "FF",
    "PP", "MM",
}

COMMON_QUADGRAMS = {
    "TION": 7, "THER": 6, "THAT": 6, "WITH": 6, "MENT": 6,
    "OULD": 5, "IGHT": 5, "HAVE": 5, "HICH": 5, "WHIC": 5,
    "THIS": 5, "THIN": 5, "THEY": 5, "ATIN": 5, "HERE": 5,
    "OUGH": 5, "ENCE": 4, "ANCE": 4, "NESS": 4, "INGS": 4,
    "ABLE": 4, "IOUS": 4, "EVEL": 4, "FROM": 4, "WERE": 4,
    "ICAL": 4, "SOME": 4, "OUNT": 4, "ESTI": 4, "ATED": 3,
    "TING": 3, "RING": 3, "ALLY": 3, "NDER": 3, "EVER": 3,
    "INTE": 3, "OTHE": 3, "TTHE": 3, "SAND": 3,
}

RARE_BIGRAMS = {
    "QJ", "JQ", "QX", "XQ", "QZ", "ZQ", "ZX", "XZ",
    "JX", "XJ", "JZ", "ZJ", "QQ", "JJ", "ZZ", "XX",
    "VX", "XV", "BX", "XB", "WX", "XW", "VJ", "JV",
    "FQ", "QF", "GX", "XG", "HX", "XH", "KX", "XK",
    "WZ", "ZW", "VQ", "QV", "VZ", "ZV",
}

PHRASE_BONUSES = {
    "OF THE": 20, "IN THE": 20, "TO THE": 20, "AND THE": 20,
    "FOR THE": 20, "ON THE": 15, "AT THE": 15, "BY THE": 15,
    "FROM THE": 20, "WITH THE": 20, "THAT THE": 15,
    "IS A": 15, "IN A": 12, "OF A": 12, "TO A": 12,
    "AND A": 12, "IT IS": 15, "THAT IS": 15, "THIS IS": 15,
    "THERE IS": 15, "TO BE": 15, "CAN BE": 12, "WILL BE": 12,
    "HAS BEEN": 12, "HAVE BEEN": 12, "WOULD BE": 12,
    "COULD BE": 12, "SHOULD BE": 12, "HOW TO": 12,
}

UNKNOWN = "_"

QUAD_WEIGHT = 80
TRI_WEIGHT = 24
BI_WEIGHT = 8
COMMON_WORD_WEIGHT = 90
DICTIONARY_WORD_WEIGHT = 35
LETTER_FREQUENCY_WEIGHT = 6
UNKNOWN_QUAD_PENALTY = -35
UNKNOWN_TRI_PENALTY = -10
UNKNOWN_BI_PENALTY = -3
UNKNOWN_WORD_LETTER_PENALTY = -2
WORD_UNDERSCORE_PENALTY = -35
SHORT_UNKNOWN_WORD_PENALTY = -180
WORD_UNKNOWN_PENALTY = -45
RARE_BIGRAM_PENALTY = -35
WORST_WORD_COUNT = 20

ENGLISH_FREQUENCIES = {
    "E": 12.70,
    "T": 9.06,
    "A": 8.17,
    "O": 7.51,
    "I": 6.97,
    "N": 6.75,
    "S": 6.33,
    "H": 6.09,
    "R": 5.99,
    "D": 4.25,
    "L": 4.03,
    "C": 2.78,
    "U": 2.76,
    "M": 2.41,
    "W": 2.36,
    "F": 2.23,
    "G": 2.02,
    "Y": 1.97,
    "P": 1.93,
    "B": 1.49,
    "V": 0.98,
    "K": 0.77,
    "J": 0.15,
    "X": 0.15,
    "Q": 0.10,
    "Z": 0.07,
}

ENGLISH = {
    "letters": ENGLISH_FREQUENCIES,
    "bigrams": [
        "TH", "HE", "IN", "ER", "AN",
        "RE", "ON", "AT", "EN", "ND",
        "TI", "ES", "OR", "TE", "OF",
        "ED", "IS", "IT", "AL", "AR",
        "ST", "TO", "NT", "NG", "SE",
    ],
    "trigrams": [
        "THE", "ING", "AND", "HER", "ERE",
        "ENT", "THA", "NTH", "WAS", "ETH",
        "FOR", "DTH", "HAT", "ION", "TIO",
        "VER", "TER", "HES", "ATI", "ALL",
    ],
    "double_letters": [
        "LL", "EE", "SS", "OO", "TT",
        "FF", "RR", "NN", "PP", "CC",
    ],
    "one_letter_words": [
        "A",
        "I",
    ],
    "common_two_letter_words": [
        "OF", "TO", "IN", "IT", "IS",
        "BE", "AS", "AT", "SO", "WE",
        "HE", "BY", "OR", "ON", "DO",
        "IF", "ME", "MY", "UP", "AN",
    ],
    "common_three_letter_words": [
        "THE", "AND", "FOR", "ARE", "BUT",
        "NOT", "YOU", "ALL", "ANY", "CAN",
        "HAD", "HER", "WAS", "ONE", "OUR",
        "OUT", "DAY", "GET", "HAS", "HIM",
    ],
}
