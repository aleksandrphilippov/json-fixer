# Import the re module for regular expressions
import re

# Constants analogous to the ones in stringUtils.ts
codeBackslash = 0x5c  # "\\"
codeSlash = 0x2f  # "/"
codeAsterisk = 0x2a  # "*"
codeOpeningBrace = 0x7b  # "{"
codeClosingBrace = 0x7d  # "}"
codeOpeningBracket = 0x5b  # "["
codeClosingBracket = 0x5d  # "]"
codeOpenParenthesis = 0x28  # "("
codeCloseParenthesis = 0x29  # ")"
codeSpace = 0x20  # " "
codeNewline = 0xa  # "\n"
codeTab = 0x9  # "\t"
codeReturn = 0xd  # "\r"
codeBackspace = 0x08  # "\b"
codeFormFeed = 0x0c  # "\f"
codeDoubleQuote = 0x0022  # "\"
codePlus = 0x2b  # "+"
codeMinus = 0x2d  # "-"
codeQuote = 0x27  # "'"
codeZero = 0x30
codeOne = 0x31
codeNine = 0x39
codeComma = 0x2c  # ","
codeDot = 0x2e  # "." (dot, period)
codeColon = 0x3a  # ":"
codeSemicolon = 0x3b  # ";"
codeUppercaseA = 0x41  # "A"
codeLowercaseA = 0x61  # "a"
codeUppercaseE = 0x45  # "E"
codeLowercaseE = 0x65  # "e"
codeUppercaseF = 0x46  # "F"
codeLowercaseF = 0x66  # "f"

# Special whitespace characters
codeNonBreakingSpace = 0xa0
codeEnQuad = 0x2000
codeHairSpace = 0x200a
codeNarrowNoBreakSpace = 0x202f
codeMediumMathematicalSpace = 0x205f
codeIdeographicSpace = 0x3000

# Special quote characters
codeDoubleQuoteLeft = 0x201c  # “
codeDoubleQuoteRight = 0x201d  # ”
codeQuoteLeft = 0x2018  # ‘
codeQuoteRight = 0x2019  # ’
codeGraveAccent = 0x0060  # `
codeAcuteAccent = 0x00b4  # ´

regex_delimiter = re.compile(r'^[,:[\]{}()\n]$')

# alpha, number, minus, or opening bracket or brace
regex_start_of_value = re.compile(r'^[\[{\w-]$')


# Utility Functions
def is_hex(code: int):
    return ((code >= codeZero and code <= codeNine) or
            (code >= codeUppercaseA and code <= codeUppercaseF) or
            (code >= codeLowercaseA and code <= codeLowercaseF))


def is_digit(code: int):
    return code >= codeZero and code <= codeNine


def is_non_zero_digit(code: int):
    return code >= codeOne and code <= codeNine


def is_valid_string_character(code: int):
    return code >= 0x20 and code <= 0x10ffff


def is_delimiter(char: str):
    return bool(regex_delimiter.match(char)) or (char and is_quote(ord(char[0])))


def is_start_of_value(char: str):
    return bool(regex_start_of_value.match(char)) or (char and is_quote(ord(char[0])))


def is_control_character(code: int):
    return (
            code == codeNewline or
            code == codeReturn or
            code == codeTab or
            code == codeBackspace or
            code == codeFormFeed
    )


def is_whitespace(code: int):
    return code == codeSpace or code == codeNewline or code == codeTab or code == codeReturn


def is_special_whitespace(code: int):
    return (
            code == codeNonBreakingSpace or
            (code >= codeEnQuad and code <= codeHairSpace) or
            code == codeNarrowNoBreakSpace or
            code == codeMediumMathematicalSpace or
            code == codeIdeographicSpace
    )


def is_quote(code: int):
    # the first check double quotes, since that occurs most often
    return is_double_quote_like(code) or is_single_quote_like(code)


def is_double_quote_like(code: int):
    # the first check double quotes, since that occurs most often
    return code == codeDoubleQuote or code == codeDoubleQuoteLeft or code == codeDoubleQuoteRight


def is_double_quote(code: int):
    return code == codeDoubleQuote


def is_single_quote_like(code: int):
    return (
            code == codeQuote or
            code == codeQuoteLeft or
            code == codeQuoteRight or
            code == codeGraveAccent or
            code == codeAcuteAccent
    )


def strip_last_occurrence(text: str, text_to_strip: str, strip_remaining_text: bool = False):
    index = text.rfind(text_to_strip)
    return text[:index] + (text[index + 1:] if not strip_remaining_text else '') if index != -1 else text


def insert_before_last_whitespace(text: str, text_to_insert: str):
    index = len(text)

    if not is_whitespace(ord(text[index - 1])):
        # no trailing whitespaces
        return text + text_to_insert

    while is_whitespace(ord(text[index - 1])) and index > 0:
        index -= 1

    return text[:index] + text_to_insert + text[index:]


def remove_at_index(text: str, start: int, count: int):
    return text[:start] + text[start + count:]


def ends_with_comma_or_newline(text: str):
    return bool(re.search(r'[,\n][ \t\r]*$', text))
