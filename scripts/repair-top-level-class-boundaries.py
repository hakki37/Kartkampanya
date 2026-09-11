from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')
marker = 'class AuthGate extends StatelessWidget {'
idx = s.find(marker)
if idx < 0:
    raise SystemExit('AuthGate marker not found')
prefix = s[:idx]
depth = 0
quote = None
escape = False
line_comment = False
block_comment = False
i = 0
while i < len(prefix):
    ch = prefix[i]
    nxt = prefix[i + 1] if i + 1 < len(prefix) else ''
    if line_comment:
        if ch == '\n': line_comment = False
        i += 1; continue
    if block_comment:
        if ch == '*' and nxt == '/': block_comment = False; i += 2; continue
        i += 1; continue
    if quote:
        if escape: escape = False
        elif ch == '\\': escape = True
        elif ch == quote: quote = None
        i += 1; continue
    if ch == '/' and nxt == '/': line_comment = True; i += 2; continue
    if ch == '/' and nxt == '*': block_comment = True; i += 2; continue
    if ch in ("'", '"'): quote = ch
    elif ch == '{': depth += 1
    elif ch == '}': depth -= 1
    i += 1
if depth < 0:
    raise SystemExit(f'Unexpected negative brace depth before AuthGate: {depth}')
if depth > 0:
    s = s[:idx] + ('}\n' * depth) + s[idx:]
    print(f'Closed {depth} leaked top-level Dart brace(s) before AuthGate')
else:
    print('Top-level class boundary already balanced before AuthGate')
p.write_text(s, encoding='utf-8')
