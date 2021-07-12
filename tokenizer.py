# consecutive delims should be treated as one
# no delims within a quoted string
DELIM_SPACE = " "
DELIM_TAB = "\t"
DELIM_SEMI = ";"
DELIM_COMMA = ","
DELIM_EQ = "="
DELIM_VERTAB = "\x0B"
DELIM_FORMFEED = "\x0C"
DELIM_WTF = "\xff"
DELIMS = [
    DELIM_SPACE,
    DELIM_TAB,
    DELIM_SEMI,
    DELIM_COMMA,
    DELIM_EQ,
    DELIM_VERTAB,
    DELIM_FORMFEED,
    DELIM_WTF
]

SPECIAL_CR = "\r"
SPECIAL_CARRET = "^"
SPECIAL_LPAREN = "("
SPECIAL_AT = "@"
SPECIAL_AMP = "&"
SPECIAL_PIPE = "|"
SPECIAL_LT = "<"
SPECIAL_GT = ">"
SPECIAL_LF = "\n"
SPECIALS = [
    SPECIAL_CR,
    SPECIAL_CARRET,
    SPECIAL_LPAREN,
    SPECIAL_AT,
    SPECIAL_AMP,
    SPECIAL_PIPE,
    SPECIAL_LT,
    SPECIAL_GT,
    SPECIAL_LF
] + DELIMS

def tokenize(text: str) -> list:
    output = []

    idx = 0
    text_len = len(text)
    while idx < text_len:
        char = text[idx]
        if char == SPECIAL_CR:
            pass
        idx += 1
    return output
