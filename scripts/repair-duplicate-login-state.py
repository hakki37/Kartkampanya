from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

def class_end(src, start):
    brace = src.find('{', start)
    if brace < 0:
        raise SystemExit('Login state opening brace not found')
    depth = 0
    quote = None
    escape = False
    for i in range(brace, len(src)):
        ch = src[i]
        if quote:
            if escape:
                escape = False
            elif ch == '\\':
                escape = True
            elif ch == quote:
                quote = None
            continue
        if ch in ("'", '"'):
            quote = ch
        elif ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return i + 1
    raise SystemExit('Login state class end not found')

needle = 'class _LoginPageState extends State<LoginPage> {'
starts = []
pos = 0
while True:
    i = s.find(needle, pos)
    if i < 0:
        break
    starts.append(i)
    pos = i + len(needle)

if len(starts) > 1:
    # lock-reference-login-v2 replaces LoginPage with a new widget + state,
    # but the old state can remain immediately after it. Keep the new first
    # definition and remove every duplicate definition.
    for start in reversed(starts[1:]):
        end = class_end(s, start)
        s = s[:start] + s[end:]
    p.write_text(s, encoding='utf-8')
    print(f'Removed {len(starts) - 1} duplicate _LoginPageState definition(s)')
else:
    print('No duplicate _LoginPageState definition found')
