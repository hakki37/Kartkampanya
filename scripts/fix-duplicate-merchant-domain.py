from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')
marker = 'String? _merchantDomain(String merchant) {'
positions = []
start = 0
while True:
    pos = s.find(marker, start)
    if pos < 0:
        break
    positions.append(pos)
    start = pos + len(marker)

if len(positions) <= 1:
    print('merchant domain declarations OK')
else:
    for pos in reversed(positions[1:]):
        brace = s.find('{', pos)
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
        s = s[:pos] + s[end:]
    p.write_text(s, encoding='utf-8')
    print(f'removed {len(positions) - 1} duplicate merchant domain declaration(s)')
