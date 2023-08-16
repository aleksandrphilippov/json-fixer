import json
import re

from .utils import (
    codeAsterisk,
    codeBackslash,
    codeCloseParenthesis,
    codeClosingBrace,
    codeClosingBracket,
    codeColon,
    codeComma,
    codeDot,
    codeDoubleQuote,
    codeLowercaseE,
    codeMinus,
    codeNewline,
    codeOpeningBrace,
    codeOpeningBracket,
    codeOpenParenthesis,
    codePlus,
    codeSemicolon,
    codeSlash,
    codeUppercaseE,
    codeZero,
    ends_with_comma_or_newline,
    insert_before_last_whitespace,
    is_control_character,
    is_delimiter,
    is_digit,
    is_double_quote,
    is_double_quote_like,
    is_hex,
    is_non_zero_digit,
    is_quote,
    is_single_quote_like,
    is_special_whitespace,
    is_start_of_value,
    is_valid_string_character,
    is_whitespace,
    strip_last_occurrence,
    remove_at_index,
)


class JSONFixError(Exception):
    def __init__(self, message, position):
        super().__init__(f"{message} at position {position}")
        self.position = position


control_characters = {
    '\b': '\\b',
    '\f': '\\f',
    '\n': '\\n',
    '\r': '\\r',
    '\t': '\\t'
}

escape_characters = {
    '"': '"',
    '\\': '\\',
    '/': '/',
    'b': '\b',
    'f': '\f',
    'n': '\n',
    'r': '\r',
    't': '\t'
}


def fix_json(text):
    i = 0  # current index in text
    output = ''  # generated output

    def parse_value():
        nonlocal i, output
        parse_whitespace_and_skip_comments()
        processed = parse_object() or parse_array() or parse_string() or parse_number() or parse_keywords() or parse_unquoted_string()
        parse_whitespace_and_skip_comments()
        return processed

    def parse_whitespace_and_skip_comments():
        nonlocal i, output
        start = i
        parse_whitespace()
        changed = parse_comment()
        if changed:
            changed = parse_whitespace()
        while changed:
            changed = parse_comment()
            if changed:
                changed = parse_whitespace()
        return i > start

    def parse_whitespace():
        nonlocal i, output
        whitespace = ''
        while i < len(text) and (is_whitespace(ord(text[i])) or is_special_whitespace(ord(text[i]))):
            if i < len(text) and is_whitespace(ord(text[i])):
                whitespace += text[i]
            else:
                # repair special whitespace
                whitespace += ' '
            i += 1
        if len(whitespace) > 0:
            output += whitespace
            return True
        return False

    def parse_comment():
        nonlocal i
        # find a block comment '/* ... */'
        if i < len(text) and ord(text[i]) == codeSlash and ord(text[i + 1]) == codeAsterisk:
            # repair block comment by skipping it
            while i < len(text) and not at_end_of_block_comment(text, i):
                i += 1
            i += 2
            return True

        # find a line comment '// ...'
        if i < len(text) and ord(text[i]) == codeSlash and ord(text[i + 1]) == codeSlash:
            # repair line comment by skipping it
            while i < len(text) and ord(text[i]) != codeNewline:
                i += 1
            return True
        return False

    def parse_character(code: int):
        nonlocal i, output
        if i < len(text) and ord(text[i]) == code:
            output += text[i]
            i += 1
            return True
        return False

    def skip_character(code: int):
        nonlocal i
        if i < len(text) and ord(text[i]) == code:
            i += 1
            return True
        return False

    def skip_escape_character():
        return skip_character(codeBackslash)

    # Parse an object like '{"key": "value"}'
    def parse_object():
        nonlocal i, output
        if i < len(text) and ord(text[i]) == codeOpeningBrace:
            output += '{'
            i += 1
            parse_whitespace_and_skip_comments()

            initial = True
            while i < len(text) and ord(text[i]) != codeClosingBrace:
                processed_comma = False
                if not initial:
                    processed_comma = parse_character(codeComma)
                    if not processed_comma:
                        # repair missing comma
                        output = insert_before_last_whitespace(output, ',')
                    parse_whitespace_and_skip_comments()
                else:
                    processed_comma = True
                    initial = False

                processed_key = parse_string() or parse_unquoted_string()
                if not processed_key:
                    if i < len(text) and (ord(text[i]) in [codeClosingBrace, codeOpeningBrace, codeClosingBracket,
                                                           codeOpeningBracket]) or (i >= len(text)):

                        # repair trailing comma
                        output = strip_last_occurrence(output, ',')
                    else:
                        raise JSONFixError('Object key expected', i)
                    break

                parse_whitespace_and_skip_comments()
                processed_colon = parse_character(codeColon)
                if not processed_colon:
                    if i < len(text) and is_start_of_value(text[i]):
                        # repair missing colon
                        output = insert_before_last_whitespace(output, ':')
                    else:
                        raise JSONFixError('Colon expected', i)

                processed_value = parse_value()
                if not processed_value:
                    if processed_colon:
                        # repair missing object value
                        output += 'null'
                    else:
                        raise JSONFixError('Colon expected', i)

            if i < len(text) and ord(text[i]) == codeClosingBrace:
                output += '}'
                i += 1
            else:
                # repair missing end bracket
                output = insert_before_last_whitespace(output, '}')
            return True
        return False

    # Parse an array like '["item1", "item2", ...]'
    def parse_array():
        nonlocal i, output
        if i < len(text) and ord(text[i]) == codeOpeningBracket:
            output += '['
            i += 1
            parse_whitespace_and_skip_comments()

            initial = True
            while i < len(text) and ord(text[i]) != codeClosingBracket:
                if not initial:
                    processed_comma = parse_character(codeComma)
                    if not processed_comma:
                        # repair missing comma
                        output = insert_before_last_whitespace(output, ',')
                else:
                    initial = False

                processed_value = parse_value()
                if not processed_value:
                    # repair trailing comma
                    output = strip_last_occurrence(output, ',')
                    break

            if i < len(text) and ord(text[i]) == codeClosingBracket:
                output += ']'
                i += 1
            else:
                # repair missing closing array bracket
                output = insert_before_last_whitespace(output, ']')
            return True
        return False

    # Parse and repair Newline Delimited JSON (NDJSON):
    # multiple JSON objects separated by a newline character
    def parse_newline_delimited_json():
        # repair NDJSON
        nonlocal i, output
        initial = True
        processed_value = True
        while processed_value:
            if not initial:
                # parse optional comma, insert when missing
                processed_comma = parse_character(codeComma)
                if not processed_comma:
                    # repair: add missing comma
                    output = insert_before_last_whitespace(output, ',')
            else:
                initial = False

            processed_value = parse_value()

        if not processed_value:
            # repair: remove trailing comma
            output = strip_last_occurrence(output, ',')

        # repair: wrap the output inside array brackets
        output = '[\n' + output + '\n]'

    # Parse a string enclosed by double quotes "...". Can contain escaped quotes
    # Repair strings enclosed in single quotes or special quotes
    # Repair an escaped string
    def parse_string():
        nonlocal i, output
        skip_escape_chars = i < len(text) and ord(text[i]) == codeBackslash
        if skip_escape_chars:
            # repair: remove the first escape character
            i += 1
            skip_escape_chars = True

        if i < len(text) and is_quote(ord(text[i])):
            is_end_quote = i < len(text) and is_single_quote_like \
                if is_single_quote_like(ord(text[i])) else is_double_quote \
                if is_double_quote(ord(text[i])) else is_double_quote_like

            output += '"'
            i += 1

            while i < len(text) and not is_end_quote(ord(text[i])):
                if i < len(text) and ord(text[i]) == codeBackslash:
                    char = text[i + 1]
                    escape_char = escape_characters.get(char)
                    if escape_char is not None:
                        output += text[i:i + 2]
                        i += 2
                    elif char == 'u':
                        if i < len(text) and is_hex(ord(text[i + 2])) \
                                and is_hex(ord(text[i + 3])) \
                                and is_hex(ord(text[i + 4])) \
                                and is_hex(ord(text[i + 5])):
                            output += text[i:i + 6]
                            i += 6
                        else:
                            end_chars = i + 2
                            while re.match(r'\w', text[end_chars]):
                                end_chars += 1
                            chars = text[i:end_chars]
                            raise JSONFixError(f'Invalid unicode character "{chars}"', i)
                    else:
                        # repair invalid escape character: remove it
                        output += char
                        i += 2
                else:
                    char = text[i]
                    code = ord(text[i])
                    if code == codeDoubleQuote and ord(text[i - 1]) != codeBackslash:
                        # repair unescaped double quote
                        output += '\\' + char
                        i += 1
                    elif is_control_character(code):
                        # unescaped control character
                        output += control_characters[char]
                        i += 1
                    else:
                        if not is_valid_string_character(code):
                            raise JSONFixError('Invalid character ' + repr(char), i)
                        output += char
                        i += 1
                if skip_escape_chars:
                    skip_escape_character()
            if i < len(text) and is_quote(ord(text[i])):
                if i < len(text) and ord(text[i]) != codeDoubleQuote:
                    # repair non-normalized quote
                    pass
                output += '"'
                i += 1
            else:
                # repair missing end quote
                output += '"'
            parse_concatenated_string()
            return True
        return False

    # Repair concatenated strings like "hello" + "world", change this into "helloworld"
    def parse_concatenated_string():
        nonlocal i, output
        processed = False
        parse_whitespace_and_skip_comments()
        while i < len(text) and ord(text[i]) == codePlus:
            processed = True
            i += 1
            parse_whitespace_and_skip_comments()

            # repair: remove the end quote of the first string
            output = strip_last_occurrence(output, '"', True)
            start = len(output)
            parse_string()

            # repair: remove the start quote of the second string
            output = remove_at_index(output, start, 1)
        return processed

    # Parse a number like 2.4 or 2.4e6
    def parse_number():
        nonlocal i, output
        start = i
        if i < len(text) and ord(text[i]) == codeMinus:
            i += 1
            if expect_digit_or_repair(start):
                return True

        if i < len(text) and ord(text[i]) == codeZero:
            i += 1
        elif i < len(text) and is_non_zero_digit(ord(text[i])):
            i += 1
            while i < len(text) and is_digit(ord(text[i])):
                i += 1

        if i < len(text) and ord(text[i]) == codeDot:
            i += 1
            if expect_digit_or_repair(start):
                return True
            while i < len(text) and is_digit(ord(text[i])):
                i += 1

        if i < len(text) and ord(text[i]) in [codeLowercaseE, codeUppercaseE]:
            i += 1
            if i < len(text) and ord(text[i]) in [codeMinus, codePlus]:
                i += 1
            if expect_digit_or_repair(start):
                return True
            while i < len(text) and is_digit(ord(text[i])):
                i += 1

        if i > start:
            output += text[start:i]
            return True
        return False

    # Parse keywords true, false, null
    # Repair Python keywords True, False, None
    def parse_keywords():
        return parse_keyword('true', 'true') \
            or parse_keyword('false', 'false') \
            or parse_keyword('null', 'null') \
            or parse_keyword('True', 'true') \
            or parse_keyword('False', 'false') \
            or parse_keyword('None', 'null')

    def parse_keyword(name: str, value: str):
        nonlocal i, output
        if text[i:i + len(name)] == name:
            output += value
            i += len(name)
            return True
        return False

    # Repair and unquoted string by adding quotes around it
    # Repair a MongoDB function call like NumberLong("2")
    # Repair a JSONP function call like callback({...});
    def parse_unquoted_string():
        # note that the symbol can end with whitespaces: we stop at the next delimiter
        nonlocal i, output
        start = i
        while i < len(text) and not is_delimiter(text[i]):
            i += 1

        if i > start:
            if i < len(text) and ord(text[i]) == codeOpenParenthesis:
                # repair a MongoDB function call like NumberLong("2")
                # repair a JSONP function call like callback({...});
                i += 1

                parse_value()

                if i < len(text) and ord(text[i]) == codeCloseParenthesis:
                    # repair: skip close bracket of function call
                    i += 1
                    if i < len(text) and ord(text[i]) == codeSemicolon:
                        # repair: skip semicolon after JSONP call
                        i += 1
                return True
            else:
                # repair unquoted string

                # first, go back to prevent getting trailing whitespaces in the string
                while i - 1 < len(text) and is_whitespace(ord(text[i - 1])) and i > 0:
                    i -= 1
                symbol = text[start:i]
                output += 'null' if symbol == 'undefined' else json.dumps(symbol)
                return True

    def expect_digit(start: int):
        if i < len(text) and not is_digit(ord(text[i])):
            num_so_far = text[start:i]
            raise JSONFixError(f'Invalid number "{num_so_far}", expecting a digit but got "{text[i]}"', i)

    def expect_digit_or_repair(start):
        nonlocal i, output
        if i >= len(text):
            # repair numbers cut off at the end
            # this will only be called when we end after a '.', '-', or 'e' and does not
            # change the number more than it needs to make it valid JSON
            output += text[start:i] + '0'
            return True
        else:
            expect_digit(start)
            return False

    def at_end_of_block_comment(block_text: str, block_i: int):
        return block_text[block_i] == '*' and block_text[block_i + 1] == '/'

    def throw_unexpected_end():
        raise JSONFixError('Unexpected end of json string', len(text))

    def throw_unexpected_character():
        raise JSONFixError('Unexpected character ' + repr(text[i]), i)

    processed = parse_value()
    if not processed:
        throw_unexpected_end()

    processed_comma = parse_character(codeComma)
    if processed_comma:
        parse_whitespace_and_skip_comments()

    if i < len(text) and is_start_of_value(text[i]) and ends_with_comma_or_newline(output):
        # start of a new value after end of the root level object: looks like
        # newline delimited JSON -> turn into a root level array
        if not processed_comma:
            # repair missing comma
            output = insert_before_last_whitespace(output, ',')
        parse_newline_delimited_json()
    elif processed_comma:
        # repair: remove trailing comma
        output = strip_last_occurrence(output, ',')

    if i >= len(text):
        # reached the end of the document properly
        return output

    throw_unexpected_character()
