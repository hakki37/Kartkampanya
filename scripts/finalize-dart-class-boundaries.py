from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

# Some legacy repair passes can leave KartKampanyaApp's closing brace missing,
# causing AuthGate/LoginPage fields to be parsed as members of the app class.
app = s.find('class KartKampanyaApp extends StatelessWidget')
auth = s.find('class AuthGate extends StatelessWidget')
if app < 0 or auth < 0 or auth <= app:
    raise SystemExit('Expected KartKampanyaApp and AuthGate classes not found')

brace = s.find('{', app)
depth = 0
quote = None
escape = False
for i in range(brace, auth):
    ch = s[i]
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

if depth > 0:
    s = s[:auth] + '\n}\n\n' + s[auth:]
    print('Closed unterminated KartKampanyaApp before AuthGate')
else:
    print('Dart top-level class boundary already valid')

p.write_text(s, encoding='utf-8')
