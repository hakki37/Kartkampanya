from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')
old = "'cepteteb': ['teb', 'cepteteb'],"
new = "'cepteteb': ['teb', 'cepteteb', 'bonus', 'bonus platinum', 'teb platinum'],\n        'bonus': ['bonus', 'cepteteb', 'bonus platinum', 'teb platinum'],"
if old not in s:
    raise SystemExit('CEPTETEB alias not found')
s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')
print('TEB Bonus/CEPTETEB matching alias applied')
