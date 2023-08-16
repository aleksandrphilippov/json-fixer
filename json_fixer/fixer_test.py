import unittest

from json_fixer.fixer import JSONFixError
from json_fixer.fixer import fix_json


class TestJSONFixValidJSON(unittest.TestCase):
    def assert_fix(self, text: str):
        self.assertEqual(fix_json(text), text)

    def test_full_JSON_object(self):
        text = '{"a":2.3e100,"b":"str","c":null,"d":false,"e":[1,2,3]}'
        parsed = fix_json(text)
        self.assertEqual(parsed, text, "Should parse a JSON object correctly")

    def test_parse_whitespace(self):
        self.assert_fix('  { \n } \t ')

    def test_parse_object(self):
        self.assert_fix('{}')
        self.assert_fix('{"a": {}}')
        self.assert_fix('{"a": "b"}')
        self.assert_fix('{"a": 2}')

    def test_parse_array(self):
        self.assert_fix('[]')
        self.assert_fix('[{}]')
        self.assert_fix('{"a":[]}')
        self.assert_fix('[1, "hi", true, false, null, {}, []]')

    def test_parse_number(self):
        self.assert_fix('23')
        self.assert_fix('0')
        self.assert_fix('0e+2')
        self.assert_fix('0.0')
        self.assert_fix('-0')
        self.assert_fix('2.3')
        self.assert_fix('2300e3')
        self.assert_fix('2300e+3')
        self.assert_fix('2300e-3')
        self.assert_fix('-2')
        self.assert_fix('2e-3')
        self.assert_fix('2.3e-3')

    def test_parse_string(self):
        self.assert_fix('"str"')
        self.assert_fix('"\\"\\\\\\/\\b\\f\\n\\r\\t"')
        self.assert_fix('"\\u260E"')

    def test_parse_keywords(self):
        self.assert_fix('true')
        self.assert_fix('false')
        self.assert_fix('null')

    def test_correctly_handle_strings_equaling_a_json_delimiter(self):
        self.assert_fix('""')
        self.assert_fix('"["')
        self.assert_fix('"]"')
        self.assert_fix('"{"')
        self.assert_fix('"}"')
        self.assert_fix('":"')
        self.assert_fix('","')

    def test_supports_unicode_characters_in_a_string(self):
        self.assert_fix('"★"')
        self.assert_fix('"\u2605"')
        self.assert_fix('"😀"')
        self.assert_fix('"\ud83d\ude00"')
        self.assert_fix('"йнформация"')

    def test_supports_escaped_unicode_characters_in_a_string(self):
        self.assert_fix('"\\u2605"')
        self.assert_fix('"\\ud83d\\ude00"')
        self.assert_fix('"\\u0439\\u043d\\u0444\\u043e\\u0440\\u043c\\u0430\\u0446\\u0438\\u044f"')

    def test_supports_unicode_characters_in_a_key(self):
        self.assert_fix('{"★":true}')
        self.assert_fix('{"\u2605":true}')
        self.assert_fix('{"😀":true}')
        self.assert_fix('{"\ud83d\ude00":true}')


class TestJSONFixInValidJSON(unittest.TestCase):
    def test_should_add_missing_quotes(self):
        self.assertEqual(fix_json('abc'), '"abc"')
        self.assertEqual(fix_json('hello   world'), '"hello   world"')
        self.assertEqual(fix_json('{a:2}'), '{"a":2}')
        self.assertEqual(fix_json('{a: 2}'), '{"a": 2}')
        self.assertEqual(fix_json('{2: 2}'), '{"2": 2}')
        self.assertEqual(fix_json('{true: 2}'), '{"true": 2}')
        self.assertEqual(fix_json('{\n  a: 2\n}'), '{\n  "a": 2\n}')
        self.assertEqual(fix_json('[a,b]'), '["a","b"]')
        self.assertEqual(fix_json('[\na,\nb\n]'), '[\n"a",\n"b"\n]')

    def test_should_add_missing_end_quote(self):
        self.assertEqual(fix_json('"abc'), '"abc"')
        self.assertEqual(fix_json("'abc"), '"abc"')
        self.assertEqual(fix_json('\u2018abc'), '"abc"')

    def test_should_replace_single_quotes_with_double_quotes(self):
        self.assertEqual(fix_json("{'a':2}"), '{"a":2}')
        self.assertEqual(fix_json("{'a':'foo'}"), '{"a":"foo"}')
        self.assertEqual(fix_json('{"a":\'foo\'}'), '{"a":"foo"}')
        self.assertEqual(fix_json("{a:'foo',b:'bar'}"), '{"a":"foo","b":"bar"}')

    def test_should_replace_special_quotes_with_double_quotes(self):
        self.assertEqual(fix_json('{“a”:“b”}'), '{"a":"b"}')
        self.assertEqual(fix_json('{‘a’:‘b’}'), '{"a":"b"}')
        self.assertEqual(fix_json('{`a´:`b´}'), '{"a":"b"}')

    def test_should_not_replace_special_quotes_inside_a_normal_string(self):
        self.assertEqual(fix_json('"Rounded “ quote"'), '"Rounded “ quote"')

    def test_should_leave_string_content_untouched(self):
        self.assertEqual(fix_json('"{a:b}"'), '"{a:b}"')

    def test_should_add_or_remove_escape_characters(self):
        self.assertEqual(fix_json('"foo\'bar"'), '"foo\'bar"')
        self.assertEqual(fix_json('"foo\\"bar"'), '"foo\\"bar"')
        self.assertEqual(fix_json("'foo\"bar'"), '"foo\\"bar"')
        self.assertEqual(fix_json("'foo\\'bar'"), '"foo\'bar"')
        self.assertEqual(fix_json('"foo\\\'bar"'), '"foo\'bar"')
        self.assertEqual(fix_json('"\\a"'), '"a"')

    def test_should_fix_a_missing_object_value(self):
        self.assertEqual(fix_json('{"a":}'), '{"a":null}')
        self.assertEqual(fix_json('{"a":,"b":2}'), '{"a":null,"b":2}')
        self.assertEqual(fix_json('{"a":'), '{"a":null}')

    def test_should_fix_undefined_values(self):
        self.assertEqual(fix_json('{"a":undefined}'), '{"a":null}')
        self.assertEqual(fix_json('[undefined]'), '[null]')
        self.assertEqual(fix_json('undefined'), 'null')

    def test_should_escape_unescaped_control_characters(self):
        self.assertEqual(fix_json('"hello\bworld"'), '"hello\\bworld"')
        self.assertEqual(fix_json('"hello\fworld"'), '"hello\\fworld"')
        self.assertEqual(fix_json('"hello\nworld"'), '"hello\\nworld"')
        self.assertEqual(fix_json('"hello\rworld"'), '"hello\\rworld"')
        self.assertEqual(fix_json('"hello\tworld"'), '"hello\\tworld"')
        self.assertEqual(fix_json('{"value\n": "dc=hcm,dc=com"}'), '{"value\\n": "dc=hcm,dc=com"}')

    def test_should_replace_special_white_space_characters(self):
        self.assertEqual(fix_json('{"a":\u00a0"foo\u00a0bar"}'), '{"a": "foo\u00a0bar"}')
        self.assertEqual(fix_json('{"a":\u202F"foo"}'), '{"a": "foo"}')
        self.assertEqual(fix_json('{"a":\u205F"foo"}'), '{"a": "foo"}')
        self.assertEqual(fix_json('{"a":\u3000"foo"}'), '{"a": "foo"}')

    def test_should_replace_non_normalized_left_or_right_quotes(self):
        self.assertEqual(fix_json('\u2018foo\u2019'), '"foo"')
        self.assertEqual(fix_json('\u201Cfoo\u201D'), '"foo"')
        self.assertEqual(fix_json('\u0060foo\u00B4'), '"foo"')
        self.assertEqual(fix_json("\u0060foo'"), '"foo"')
        self.assertEqual(fix_json("\u0060foo'"), '"foo"')

    def test_should_remove_block_comments(self):
        self.assertEqual(fix_json('/* foo */ {}'), ' {}')
        self.assertEqual(fix_json('{} /* foo */ '), '{}  ')
        self.assertEqual(fix_json('{} /* foo '), '{} ')
        self.assertEqual(fix_json('\n/* foo */\n{}'), '\n\n{}')
        self.assertEqual(fix_json('{"a":"foo",/*hello*/"b":"bar"}'), '{"a":"foo","b":"bar"}')

    def test_should_remove_line_comments(self):
        self.assertEqual(fix_json('{} // comment'), '{} ')
        self.assertEqual(fix_json('{\n"a":"foo",//hello\n"b":"bar"\n}'), '{\n"a":"foo",\n"b":"bar"\n}')

    def test_should_not_remove_comments_inside_a_string(self):
        self.assertEqual(fix_json('"/* foo */"'), '"/* foo */"')

    def test_should_strip_jsonp_notation(self):
        self.assertEqual(fix_json('callback_123({});'), '{}')
        self.assertEqual(fix_json('callback_123([]);'), '[]')
        self.assertEqual(fix_json('callback_123(2);'), '2')
        self.assertEqual(fix_json('callback_123("foo");'), '"foo"')
        self.assertEqual(fix_json('callback_123(null);'), 'null')
        self.assertEqual(fix_json('callback_123(true);'), 'true')
        self.assertEqual(fix_json('callback_123(false);'), 'false')
        self.assertEqual(fix_json('callback({}'), '{}')
        self.assertEqual(fix_json('/* foo bar */ callback_123 ({})'), ' {}')
        self.assertEqual(fix_json('/* foo bar */ callback_123 ({})'), ' {}')
        self.assertEqual(fix_json('/* foo bar */\ncallback_123({})'), '\n{}')
        self.assertEqual(fix_json('/* foo bar */ callback_123 (  {}  )'), '   {}  ')
        self.assertEqual(fix_json('  /* foo bar */   callback_123({});  '), '     {}  ')
        self.assertEqual(fix_json('\n/* foo\nbar */\ncallback_123 ({});\n\n'), '\n\n{}\n\n')

        with self.assertRaises(JSONFixError):
            fix_json('callback {}')

    def test_should_fix_escaped_string_contents(self):
        self.assertEqual(fix_json('\\"hello world\\"'), '"hello world"')
        self.assertEqual(fix_json('\\"hello world\\'), '"hello world"')
        self.assertEqual(fix_json('\\"hello \\\\"world\\\\"\\"'), '"hello \\"world\\""')
        self.assertEqual(fix_json('[\\"hello \\\\"world\\\\"\\"]'), '["hello \\"world\\""]')
        self.assertEqual(
            fix_json('{\\"stringified\\": \\"hello \\\\"world\\\\"\\"}'),
            '{"stringified": "hello \\"world\\""}'
        )
        self.assertEqual(fix_json('[\\"hello\\, \\"world\\"]'), '["hello, ","world\\\\","]"]')
        self.assertEqual(fix_json('\\"hello"'), '"hello"')

    def test_should_strip_trailing_commas_from_an_array(self):
        self.assertEqual(fix_json('[1,2,3,]'), '[1,2,3]')
        self.assertEqual(fix_json('[1,2,3,\n]'), '[1,2,3\n]')
        self.assertEqual(fix_json('[1,2,3,  \n  ]'), '[1,2,3  \n  ]')
        self.assertEqual(fix_json('[1,2,3,/*foo*/]'), '[1,2,3]')
        self.assertEqual(fix_json('{"array":[1,2,3,]}'), '{"array":[1,2,3]}')
        self.assertEqual(fix_json('"[1,2,3,]"'), '"[1,2,3,]"')

    def test_should_strip_trailing_commas_from_an_object(self):
        self.assertEqual(fix_json('{"a":2,}'), '{"a":2}')
        self.assertEqual(fix_json('{"a":2  ,  }'), '{"a":2    }')
        self.assertEqual(fix_json('{"a":2  , \n }'), '{"a":2   \n }')
        self.assertEqual(fix_json('{"a":2/*foo*/,/*foo*/}'), '{"a":2}')
        self.assertEqual(fix_json('"{a:2,}"'), '"{a:2,}"')

    def test_should_strip_trailing_comma_at_the_end(self):
        self.assertEqual(fix_json('4,'), '4')
        self.assertEqual(fix_json('4 ,'), '4 ')
        self.assertEqual(fix_json('4 , '), '4  ')
        self.assertEqual(fix_json('{"a":2},'), '{"a":2}')
        self.assertEqual(fix_json('[1,2,3],'), '[1,2,3]')

    def test_should_add_a_missing_closing_bracket_for_an_object(self):
        self.assertEqual(fix_json('{'), '{}')
        self.assertEqual(fix_json('{"a":2'), '{"a":2}')
        self.assertEqual(fix_json('{"a":2,'), '{"a":2}')
        self.assertEqual(fix_json('{"a":{"b":2}'), '{"a":{"b":2}}')
        self.assertEqual(fix_json('{\n  "a":{"b":2\n}'), '{\n  "a":{"b":2\n}}')
        self.assertEqual(fix_json('[{"b":2]'), '[{"b":2}]')
        self.assertEqual(fix_json('[{"b":2\n]'), '[{"b":2}\n]')
        self.assertEqual(fix_json('[{"i":1{"i":2}]'), '[{"i":1},{"i":2}]')
        self.assertEqual(fix_json('[{"i":1,{"i":2}]'), '[{"i":1},{"i":2}]')

    def test_should_add_a_missing_closing_bracket_for_an_array(self):
        self.assertEqual(fix_json('['), '[]')
        self.assertEqual(fix_json('[1,2,3'), '[1,2,3]')
        self.assertEqual(fix_json('[1,2,3,'), '[1,2,3]')
        self.assertEqual(fix_json('[[1,2,3,'), '[[1,2,3]]')
        self.assertEqual(fix_json('{\n"values":[1,2,3\n}'), '{\n"values":[1,2,3]\n}')
        self.assertEqual(fix_json('{\n"values":[1,2,3\n'), '{\n"values":[1,2,3]}\n')

    def test_should_strip_mongo_db_data_types(self):
        self.assertEqual(fix_json('NumberLong("2")'), '"2"')
        self.assertEqual(fix_json('{"_id":ObjectId("123")}'), '{"_id":"123"}')

        mongo_document = '''{
"_id" : ObjectId("123"),
"isoDate" : ISODate("2012-12-19T06:01:17.171Z"),
"regularNumber" : 67,
"long" : NumberLong("2"),
"long2" : NumberLong(2),
"int" : NumberInt("3"),
"int2" : NumberInt(3),
"decimal" : NumberDecimal("4"),
"decimal2" : NumberDecimal(4)
}'''
        expected_json = '''{
"_id" : "123",
"isoDate" : "2012-12-19T06:01:17.171Z",
"regularNumber" : 67,
"long" : "2",
"long2" : 2,
"int" : "3",
"int2" : 3,
"decimal" : "4",
"decimal2" : 4
}'''
        self.assertEqual(expected_json, fix_json(mongo_document))

    def test_should_replace_python_constants_none_true_false(self):
        self.assertEqual(fix_json('True'), 'true')
        self.assertEqual(fix_json('False'), 'false')
        self.assertEqual(fix_json('None'), 'null')

    def test_should_turn_unknown_symbols_into_a_string(self):
        self.assertEqual(fix_json('foo'), '"foo"')
        self.assertEqual(fix_json('[1,foo,4]'), '[1,"foo",4]')
        self.assertEqual(fix_json('{foo: bar}'), '{"foo": "bar"}')

        self.assertEqual(fix_json('foo 2 bar'), '"foo 2 bar"')
        self.assertEqual(fix_json('{greeting: hello world}'), '{"greeting": "hello world"}')
        self.assertEqual(
            fix_json('{greeting: hello world\nnext: "line"}'),
            '{"greeting": "hello world",\n"next": "line"}'
        )
        self.assertEqual(fix_json('{greeting: hello world!}'), '{"greeting": "hello world!"}')

    def test_should_concatenate_strings(self):
        self.assertEqual(fix_json('"hello" + " world"'), '"hello world"')
        self.assertEqual(fix_json('"hello" +\n " world"'), '"hello world"')
        self.assertEqual(fix_json('"a"+"b"+"c"'), '"abc"')
        self.assertEqual(fix_json('"hello" + /*comment*/ " world"'), '"hello world"')
        self.assertEqual(fix_json("{\n  \"greeting\": 'hello' +\n 'world'\n}"), '{\n  "greeting": "helloworld"\n}')

    def test_should_fix_missing_comma_between_array_items(self):
        self.assertEqual(fix_json('{"array": [{}{}]}'), '{"array": [{},{}]}')
        self.assertEqual(fix_json('{"array": [{} {}]}'), '{"array": [{}, {}]}')
        self.assertEqual(fix_json('{"array": [{}\n{}]}'), '{"array": [{},\n{}]}')
        self.assertEqual(fix_json('{"array": [\n{}\n{}\n]}'), '{"array": [\n{},\n{}\n]}')
        self.assertEqual(fix_json('{"array": [\n1\n2\n]}'), '{"array": [\n1,\n2\n]}')
        self.assertEqual(fix_json('{"array": [\n"a"\n"b"\n]}'), '{"array": [\n"a",\n"b"\n]}')
        self.assertEqual(fix_json('[\n{},\n{}\n]'), '[\n{},\n{}\n]')

    def test_should_fix_missing_comma_between_object_properties(self):
        self.assertEqual(fix_json('{"a":2\n"b":3\nc:4}'), '{"a":2,\n"b":3,\n"c":4}')

    def test_should_fix_numbers_at_the_end(self):
        self.assertEqual(fix_json('{"a":2.'), '{"a":2.0}')
        self.assertEqual(fix_json('{"a":2e'), '{"a":2e0}')
        self.assertEqual(fix_json('{"a":2e-'), '{"a":2e-0}')
        self.assertEqual(fix_json('{"a":-'), '{"a":-0}')

    def test_should_fix_missing_colon_between_object_key_and_value(self):
        self.assertEqual(fix_json('{"a" "b"}'), '{"a": "b"}')
        self.assertEqual(fix_json('{"a" 2}'), '{"a": 2}')
        self.assertEqual(fix_json('{\n"a" "b"\n}'), '{\n"a": "b"\n}')
        self.assertEqual(fix_json('{"a" \'b\'}'), '{"a": "b"}')
        self.assertEqual(fix_json("{'a' 'b'}"), '{"a": "b"}')
        self.assertEqual(fix_json('{“a” “b”}'), '{"a": "b"}')
        self.assertEqual(fix_json("{a 'b'}"), '{"a": "b"}')
        self.assertEqual(fix_json('{a “b”}'), '{"a": "b"}')

    def test_should_fix_missing_a_combination_of_comma_quotes_and_brackets(self):
        self.assertEqual(fix_json('{"array": [\na\nb\n]}'), '{"array": [\n"a",\n"b"\n]}')
        self.assertEqual(fix_json('1\n2'), '[\n1,\n2\n]')
        self.assertEqual(fix_json('[a,b\nc]'), '["a","b",\n"c"]')

    def test_should_fix_newline_separated_json(self):
        text = '' + '/* 1 */\n' + '{}\n' + '\n' + '/* 2 */\n' + '{}\n' + '\n' + '/* 3 */\n' + '{}\n'
        expected = '[\n\n{},\n\n\n{},\n\n\n{}\n\n]'
        self.assertEqual(fix_json(text), expected)

    def test_should_fix_newline_separated_json_having_commas(self):
        text = '' + '/* 1 */\n' + '{},\n' + '\n' + '/* 2 */\n' + '{},\n' + '\n' + '/* 3 */\n' + '{}\n'
        expected = '[\n\n{},\n\n\n{},\n\n\n{}\n\n]'
        self.assertEqual(fix_json(text), expected)

    def test_should_fix_newline_separated_json_having_commas_and_trailing_comma(self):
        text = '' + '/* 1 */\n' + '{},\n' + '\n' + '/* 2 */\n' + '{},\n' + '\n' + '/* 3 */\n' + '{},\n'
        expected = '[\n\n{},\n\n\n{},\n\n\n{}\n\n]'
        self.assertEqual(fix_json(text), expected)

    def test_should_fix_a_comma_separated_list_with_value(self):
        self.assertEqual(fix_json('1,2,3'), '[\n1,2,3\n]')
        self.assertEqual(fix_json('1,2,3,'), '[\n1,2,3\n]')
        self.assertEqual(fix_json('1\n2\n3'), '[\n1,\n2,\n3\n]')
        self.assertEqual(fix_json('a\nb'), '[\n"a",\n"b"\n]')
        self.assertEqual(fix_json('a,b'), '[\n"a","b"\n]')


class TestJSONRaiseExceptionIfNonFixableIssue(unittest.TestCase):
    def test_should_throw_an_exception_in_case_of_non_fixable_issues(self):
        with self.assertRaises(JSONFixError) as cm:
            fix_json('')
        self.assertEqual(cm.exception.args[0], 'Unexpected end of json string at position 0')

        with self.assertRaises(JSONFixError) as cm:
            fix_json('{"a",')
        self.assertEqual(cm.exception.args[0], 'Colon expected at position 4')

        with self.assertRaises(JSONFixError) as cm:
            fix_json('{:2}')
        self.assertEqual(cm.exception.args[0], 'Object key expected at position 1')

        with self.assertRaises(JSONFixError) as cm:
            fix_json('{"a":2,]')
        self.assertEqual(cm.exception.args[0], 'Unexpected character \']\' at position 7')

        with self.assertRaises(JSONFixError) as cm:
            fix_json('{"a" ]')
        self.assertEqual(cm.exception.args[0], 'Colon expected at position 5')

        with self.assertRaises(JSONFixError) as cm:
            fix_json('{}}')
        self.assertEqual(cm.exception.args[0], 'Unexpected character \'}\' at position 2')

        with self.assertRaises(JSONFixError) as cm:
            fix_json('[2,}')
        self.assertEqual(cm.exception.args[0], 'Unexpected character \'}\' at position 3')

        with self.assertRaises(JSONFixError) as cm:
            fix_json('2.3.4')
        self.assertEqual(cm.exception.args[0], 'Unexpected character \'.\' at position 3')

        with self.assertRaises(JSONFixError) as cm:
            fix_json('2..3')
        self.assertEqual(cm.exception.args[0], 'Invalid number "2.", expecting a digit but got "." at position 2')

        with self.assertRaises(JSONFixError) as cm:
            fix_json('2e3.4')
        self.assertEqual(cm.exception.args[0], 'Unexpected character \'.\' at position 3')

        with self.assertRaises(JSONFixError) as cm:
            fix_json('[2e,')
        self.assertEqual(cm.exception.args[0], 'Invalid number "2e", expecting a digit but got "," at position 3')

        with self.assertRaises(JSONFixError) as cm:
            fix_json('[-,')
        self.assertEqual(cm.exception.args[0], 'Invalid number "-", expecting a digit but got "," at position 2')

        with self.assertRaises(JSONFixError) as cm:
            fix_json('foo [')
        self.assertEqual(cm.exception.args[0], 'Unexpected character \'[\' at position 4')

        with self.assertRaises(JSONFixError) as cm:
            fix_json('"\\u26"')
        self.assertEqual(cm.exception.args[0], 'Invalid unicode character "\\u26" at position 1')

        with self.assertRaises(JSONFixError) as cm:
            fix_json('"\\uZ000"')
        self.assertEqual(cm.exception.args[0], 'Invalid unicode character "\\uZ000" at position 1')


if __name__ == '__main__':
    unittest.main()
