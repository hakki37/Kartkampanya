from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')
# Colors.white is already a const Color; `const Colors.white` is invalid Dart syntax.
s = s.replace('const Colors.white', 'Colors.white')
p.write_text(s, encoding='utf-8')
print('Fixed invalid const Colors.white expressions')
