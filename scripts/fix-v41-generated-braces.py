from pathlib import Path

p = Path('lib/main.dart')
lines = p.read_text(encoding='utf-8').splitlines()

# The current reference generators leave two standalone closing braces at these
# generated boundaries. Remove only the exact standalone braces, bottom-up.
for target in (2254, 1610):
    i = target - 1
    if 0 <= i < len(lines) and lines[i].strip() == '}':
        lines.pop(i)
    else:
        raise SystemExit(f'Expected generated brace at line {target}')

p.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print('v41 generated brace repair applied')
