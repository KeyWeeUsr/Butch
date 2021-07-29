"""Characters used for assembling a command of Batch language."""

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
DELIM_WHITE = frozenset((DELIM_SPACE, DELIM_TAB))
DELIMS = frozenset(list(DELIM_WHITE) + [
    DELIM_SEMI,
    DELIM_COMMA,
    DELIM_EQ,
    DELIM_VERTAB,
    DELIM_FORMFEED,
    DELIM_WTF
])

SPECIAL_CR = "\r"
SPECIAL_CARRET = "^"
SPECIAL_LPAREN = "("
SPECIAL_RPAREN = ")"
SPECIAL_AT = "@"
SPECIAL_AMP = "&"
SPECIAL_PIPE = "|"
SPECIAL_LT = "<"
SPECIAL_GT = ">"
SPECIAL_COLON = ":"
SPECIAL_REDIR = frozenset((
    SPECIAL_LT,
    SPECIAL_GT
))
SPECIAL_SPLITTERS = frozenset(
    [
        SPECIAL_AMP,
        SPECIAL_PIPE
    ] + list(SPECIAL_REDIR)
)
SPECIAL_LF = "\n"
SPECIALS = frozenset(
    [
        SPECIAL_CR,
        SPECIAL_CARRET,
        SPECIAL_LPAREN,
        SPECIAL_RPAREN,
        SPECIAL_AT,
        SPECIAL_LF,
        SPECIAL_COLON
    ] + list(SPECIAL_SPLITTERS) + list(DELIMS)
)

QUOTE_DOUBLE = '"'
TOKENS = frozenset(list(SPECIALS) + [QUOTE_DOUBLE])
