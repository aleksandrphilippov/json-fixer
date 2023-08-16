from json_fixer import fix_json, JSONFixError

try:
    json_text = "{name: 'John',}"
    repaired = fix_json(json_text)
    print(repaired)
except JSONFixError as err:
    print(err)
