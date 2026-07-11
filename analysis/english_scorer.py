import re
from pathlib import Path

COMMON_WORDS = {
    "THE", "OF", "TO", "AND", "A", "IN", "IS", "IT", "YOU", "THAT",
    "HE", "WAS", "FOR", "ON", "ARE", "WITH", "AS", "I", "HIS", "THEY",
    "BE", "AT", "ONE", "HAVE", "THIS", "FROM", "OR", "HAD", "BY", "HOT",
    "BUT", "SOME", "WHAT", "THERE", "WE", "CAN", "OUT", "OTHER", "WERE",
    "ALL", "YOUR", "WHEN", "UP", "USE", "WORD", "HOW", "SAID", "AN",
    "EACH", "SHE", "WHICH", "DO", "THEIR", "TIME", "IF", "WILL", "WAY",
    "ABOUT", "MANY", "THEN", "THEM", "WOULD", "WRITE", "LIKE", "SO",
    "THESE", "HER", "LONG", "MAKE", "THING", "SEE", "HIM", "TWO", "HAS",
    "LOOK", "MORE", "DAY", "COULD", "GO", "COME", "DID", "MY", "SOUND",
    "NO", "MOST", "NUMBER", "WHO", "OVER", "KNOW", "WATER", "THAN",
    "CALL", "FIRST", "PEOPLE", "MAY", "DOWN", "SIDE", "BEEN", "NOW",
    "FIND", "ANY", "NEW", "WORK", "PART", "TAKE", "GET", "PLACE", "MADE",
    "LIVE", "WHERE", "AFTER", "BACK", "LITTLE", "ONLY", "ROUND", "MAN",
    "YEAR", "CAME", "SHOW", "EVERY", "GOOD", "ME", "GIVE", "OUR", "UNDER",
    "NAME", "VERY", "THROUGH", "JUST", "FORM", "MUCH", "GREAT", "THINK",
    "SAY", "HELP", "LOW", "LINE", "BEFORE", "TURN", "CAUSE", "SAME",
    "MEAN", "DIFFER", "MOVE", "RIGHT", "BOY", "OLD", "TOO", "DOES",
    "TELL", "SENTENCE", "SET", "THREE", "WANT", "AIR", "WELL", "ALSO",
    "PLAY", "SMALL", "END", "PUT", "HOME", "READ", "HAND", "PORT",
    "LARGE", "SPELL", "ADD", "EVEN", "LAND", "HERE", "MUST", "BIG",
    "HIGH", "SUCH", "FOLLOW", "ACT", "WHY", "ASK", "MEN", "CHANGE",
    "WENT", "LIGHT", "KIND", "OFF", "NEED", "HOUSE", "PICTURE", "TRY",
    "US", "AGAIN", "ANIMAL", "POINT", "MOTHER", "WORLD", "NEAR", "BUILD",
    "SELF", "EARTH", "FATHER", "HEAD", "STAND", "OWN", "PAGE", "SHOULD",
    "COUNTRY", "FOUND", "ANSWER", "SCHOOL", "GROW", "STUDY", "STILL",
    "LEARN", "PLANT", "COVER", "FOOD", "SUN", "FOUR", "THOUGHT", "LET",
    "KEEP", "EYE", "NEVER", "LAST", "DOOR", "BETWEEN", "CITY", "CROSS",
    "SINCE", "HARD", "START", "MIGHT", "STORY", "SAW", "FAR", "SEA",
    "DRAW", "LEFT", "LATE", "RUN", "DON'T", "WHILE", "PRESS", "CLOSE",
    "NIGHT", "REAL", "LIFE", "FEW", "STOP", "OPEN", "SEEM", "TOGETHER",
    "NEXT", "WHITE", "CHILDREN", "BEGIN", "GOT", "WALK", "EXAMPLE",
    "EASE", "PAPER", "OFTEN", "ALWAYS", "MUSIC", "THOSE", "BOTH", "MARK",
    "BOOK", "LETTER", "UNTIL", "MILE", "RIVER", "CAR", "FEET", "CARE",
    "SECOND", "GROUP", "CARRY", "TOOK", "RAIN", "EAT", "ROOM", "FRIEND",
    "BEGAN", "IDEA", "FISH", "MOUNTAIN", "NORTH", "ONCE", "BASE", "HEAR",
    "HORSE", "CUT", "SURE", "WATCH", "COLOR", "FACE", "WOOD", "MAIN",
    "ENOUGH", "PLAIN", "GIRL", "USUAL", "YOUNG", "READY", "ABOVE", "EVER",
    "RED", "LIST", "THOUGH", "FEEL", "TALK", "BIRD", "SOON", "BODY",
    "DOG", "FAMILY", "DIRECT", "POSE", "LEAVE", "SONG", "MEASURE",
    "STATE", "PRODUCT", "BLACK", "SHORT", "NUMERAL", "CLASS", "WIND",
    "QUESTION", "HAPPEN", "COMPLETE", "SHIP", "AREA", "HALF", "ROCK",
    "ORDER", "FIRE", "SOUTH", "PROBLEM", "PIECE", "TOLD", "KNEW", "PASS",
    "FARM", "TOP", "WHOLE", "KING", "SIZE", "HEARD", "BEST", "HOUR",
    "BETTER", "TRUE", "DURING", "HUNDRED", "AM", "REMEMBER", "STEP",
    "EARLY", "HOLD", "WEST", "GROUND", "INTEREST", "REACH", "FAST",
    "FIVE", "SING", "LISTEN", "SIX", "TABLE", "TRAVEL", "LESS", "MORNING",
    "TEN", "SIMPLE", "SEVERAL", "VOWEL", "TOWARD", "WAR", "LAY",
    "AGAINST", "PATTERN", "SLOW", "CENTER", "LOVE", "PERSON", "MONEY",
    "SERVE", "APPEAR", "ROAD", "MAP", "SCIENCE", "RULE", "GOVERN",
    "PULL", "COLD", "NOTICE", "VOICE", "FALL", "POWER", "TOWN", "FINE",
    "CERTAIN", "FLY", "UNIT", "LEAD", "CRY", "DARK", "MACHINE", "NOTE",
    "WAIT", "PLAN", "FIGURE", "STAR", "BOX", "NOUN", "FIELD", "REST",
    "CORRECT", "ABLE", "POUND", "DONE", "BEAUTY", "DRIVE", "STOOD",
    "CONTAIN", "FRONT", "TEACH", "WEEK", "FINAL", "GAVE", "GREEN", "OH",
    "QUICK", "DEVELOP", "SLEEP", "WARM", "FREE", "MINUTE", "STRONG",
    "SPECIAL", "MIND", "BEHIND", "CLEAR", "TAIL", "PRODUCE", "FACT",
    "STREET", "INCH", "LOT", "NOTHING", "COURSE", "STAY", "WHEEL",
    "FULL", "FORCE", "BLUE", "OBJECT", "DECIDE", "SURFACE", "DEEP",
    "MOON", "ISLAND", "FOOT", "YET", "BUSY", "TEST", "RECORD", "BOAT",
    "COMMON", "GOLD", "POSSIBLE", "PLANE", "AGE", "DRY", "WONDER",
    "LAUGH", "THOUSAND", "AGO", "RAN", "CHECK", "GAME", "SHAPE", "YES",
    "MISS", "BROUGHT", "HEAT", "SNOW", "BED", "BRING", "SIT", "PERHAPS",
    "FILL", "EAST", "WEIGHT", "LANGUAGE", "AMONG",
}

_common_words_path = Path(__file__).parent.parent / "data" / "common_words.txt"
if _common_words_path.exists():
    with open(_common_words_path) as _f:
        COMMON_SET = {line.strip().upper() for line in _f if line.strip()}
else:
    COMMON_SET = set(COMMON_WORDS)

_cleaned_path = Path(__file__).parent.parent / "data" / "cleaned_words.txt"
if _cleaned_path.exists():
    with open(_cleaned_path) as _f:
        WORD_SET = {line.strip().upper() for line in _f if line.strip()}
else:
    WORD_SET = COMMON_SET

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

COMMON_LETTERS = "ETAOINSHRDLCUMWFGYPBVKJXQZ"

VOWELS = {"A", "E", "I", "O", "U"}

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


def _clean_word(word):
    return re.sub(r"[^A-Z]", "", word.upper())


def _score_words(text):
    words = text.split()
    dictionary_score = 0
    unknown_penalty = 0
    consecutive_bonus = 0
    valid_count = 0
    invalid_count = 0
    prev_valid = False

    for word in words:
        clean = _clean_word(word)
        if not clean:
            continue
        if clean in COMMON_SET:
            dictionary_score += 40
            valid_count += 1
            if prev_valid:
                consecutive_bonus += 10
            prev_valid = True
        elif clean in WORD_SET:
            dictionary_score += 15
            valid_count += 1
            if prev_valid:
                consecutive_bonus += 10
            prev_valid = True
        elif len(clean) >= 4:
            unknown_penalty -= 3 * len(clean)
            invalid_count += 1
            prev_valid = False
        else:
            prev_valid = False

    return dictionary_score, unknown_penalty, consecutive_bonus, valid_count, invalid_count


def _score_phrases(text):
    total = 0
    for phrase, bonus in PHRASE_BONUSES.items():
        if phrase in text:
            total += bonus
    return total


def score_bigrams(text):
    letters = "".join(c for c in text if c.isalpha())
    score = 0
    streak = 0
    for i in range(len(letters) - 1):
        bigram = letters[i:i + 2]
        if bigram in COMMON_BIGRAMS:
            streak += 1
            score += COMMON_BIGRAMS[bigram] * streak
        else:
            streak = 0
    return score


def score_trigrams(text):
    letters = "".join(c for c in text if c.isalpha())
    score = 0
    streak = 0
    for i in range(len(letters) - 2):
        trigram = letters[i:i + 3]
        if trigram in COMMON_TRIGRAMS:
            streak += 1
            score += COMMON_TRIGRAMS[trigram] * streak
        else:
            streak = 0
    return score


def score_frequency(text):
    score = 0
    for letter in text:
        if not letter.isalpha():
            continue
        if letter in COMMON_LETTERS:
            score += len(COMMON_LETTERS) - COMMON_LETTERS.index(letter)
    return score


def score_vowels(text):
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0
    vowels = sum(1 for letter in letters if letter in VOWELS)
    vowel_ratio = vowels / len(letters)
    if 0.30 <= vowel_ratio <= 0.55:
        return 12
    if vowels == 0:
        return -20
    return 0


def score_double_letters(text):
    score = 0
    for i in range(len(text) - 1):
        pair = text[i:i + 2]
        if not pair.isalpha():
            continue
        if pair in COMMON_DOUBLES:
            score += 5
        elif pair[0] == pair[1]:
            score -= 2
    return score


def score_quadgrams(text):
    letters = "".join(c for c in text if c.isalpha())
    score = 0
    streak = 0
    for i in range(len(letters) - 3):
        quad = letters[i:i + 4]
        if quad in COMMON_QUADGRAMS:
            streak += 1
            score += COMMON_QUADGRAMS[quad] * streak
        else:
            streak = 0
    return score


def score_rare_bigrams(text):
    letters = "".join(c for c in text if c.isalpha())
    score = 0
    for i in range(len(letters) - 1):
        bigram = letters[i:i + 2]
        if bigram in RARE_BIGRAMS:
            score -= 10
    return score


def score_text(text):
    text = text.upper()

    dictionary_score, unknown_penalty, consecutive_bonus, _, _ = _score_words(text)
    phrase_bonus = _score_phrases(text)

    num_letters = max(1, len([c for c in text if c.isalpha()]))
    bigrams = round(score_bigrams(text) / num_letters * 10)
    trigrams = round(score_trigrams(text) / num_letters * 10)
    quadgrams = round(score_quadgrams(text) / num_letters * 10)
    frequency = round(score_frequency(text) / num_letters * 10)
    vowels = score_vowels(text)
    doubles = score_double_letters(text)
    rare = score_rare_bigrams(text)

    return (dictionary_score + unknown_penalty + consecutive_bonus + phrase_bonus
            + bigrams + trigrams + quadgrams
            + frequency + vowels + doubles + rare)
