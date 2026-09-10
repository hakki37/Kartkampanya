from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

# The generated reference chain leaves one extra closing brace at EOF.
# Remove exactly one final brace; do not touch any other braces.
stripped = s.rstrip()
if not stripped.endswith('}'):
    raise SystemExit('main.dart does not end with a closing brace')

fixed = stripped[:-1].rstrip() + '\n'
p.write_text(fixed, encoding='utf-8')
print('removed one trailing generated brace')
