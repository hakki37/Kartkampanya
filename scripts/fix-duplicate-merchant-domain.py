from pathlib import Path
import re

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

# V15 can leave one nullable and one non-nullable helper. Remove every
# duplicate declaration after the first, regardless of return type.
pattern = re.compile(r'String\??\s+_merchantDomain\s*\(\s*String\s+merchant\s*\)\s*\{')
matches = list(pattern.finditer(s))

if len(matches) <= 1:
    print('merchant domain declarations OK')
    raise SystemExit(0)

# Keep the first declaration and remove later complete function blocks.
for m in reversed(matches[1:]):
    brace = s.find('{', m.start(), m.end())
    if brace < 0:
        raise SystemExit('merchant domain opening brace not found')
    depth = 0
    end = None
    for i in range(brace, len(s)):
        if s[i] == '{':
            depth += 1
        elif s[i] == '}':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end is None:
        raise SystemExit('merchant domain closing brace not found')
    while end < len(s) and s[end] in '\r\n':
        end += 1
    s = s[:m.start()] + s[end:]

p.write_text(s, encoding='utf-8')
print(f'removed {len(matches) - 1} duplicate merchant domain declaration(s)')
