from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

def class_ranges(src, name):
    needle = 'class ' + name
    ranges = []
    pos = 0
    while True:
        start = src.find(needle, pos)
        if start < 0:
            break
        brace = src.find('{', start)
        if brace < 0:
            break
        depth = 0
        quote = None
        escape = False
        i = brace
        while i < len(src):
            ch = src[i]
            if quote:
                if ch == quote and not escape:
                    quote = None
                escape = (ch == '\\' and not escape)
                if ch != '\\':
                    escape = False
                i += 1
                continue
            if ch in ("'", '"'):
                quote = ch
            elif ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    ranges.append((start, i + 1))
                    pos = i + 1
                    break
            i += 1
        else:
            break
    return ranges

ranges = class_ranges(s, '_LoginPageState')
if len(ranges) > 1:
    start, end = ranges[1]
    s = s[:start] + s[end:]
    print('removed duplicate _LoginPageState')
else:
    print('no duplicate _LoginPageState found')

p.write_text(s, encoding='utf-8')
