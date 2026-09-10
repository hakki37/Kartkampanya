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
    for start in reversed(starts[1:]):
        end = class_end(s, start)
        s = s[:start] + s[end:]
    print(f'Removed {len(starts) - 1} duplicate _LoginPageState definition(s)')
else:
    print('No duplicate _LoginPageState definition found')

# Compact the home screen to match the supplied reference: the banner,
# search box and especially the 4x2 quick-category tiles must not dominate
# the first viewport.
replacements = {
    "padding: const EdgeInsets.fromLTRB(16, 8, 16, 24)": "padding: const EdgeInsets.fromLTRB(14, 4, 14, 18)",
    "padding: const EdgeInsets.fromLTRB(20, 20, 20, 22)": "padding: const EdgeInsets.fromLTRB(16, 14, 16, 16)",
    "borderRadius: BorderRadius.circular(26)": "borderRadius: BorderRadius.circular(20)",
    "fontSize: 25,\n                      fontWeight: FontWeight.w800": "fontSize: 21,\n                      fontWeight: FontWeight.w800",
    "style: TextStyle(color: Colors.white70, fontSize: 14)": "style: TextStyle(color: Colors.white70, fontSize: 12.5)",
    "contentPadding: const EdgeInsets.symmetric(\n                  horizontal: 18,\n                  vertical: 16,\n                )": "contentPadding: const EdgeInsets.symmetric(\n                  horizontal: 16,\n                  vertical: 10,\n                )",
    "fontSize: 18,\n                fontWeight: FontWeight.bold": "fontSize: 16,\n                fontWeight: FontWeight.w800",
    "crossAxisSpacing: 8,\n                mainAxisSpacing: 8,\n                childAspectRatio: 1.05": "crossAxisSpacing: 7,\n                mainAxisSpacing: 7,\n                childAspectRatio: 1.48",
    "Text(x[0], style: const TextStyle(fontSize: 23))": "Text(x[0], style: const TextStyle(fontSize: 18))",
    "const SizedBox(height: 3),\n                        Text(x[1]": "const SizedBox(height: 2),\n                        Text(x[1]",
    "style: const TextStyle(fontSize: 11.5, fontWeight: FontWeight.w800)": "style: const TextStyle(fontSize: 10.5, fontWeight: FontWeight.w800)",
}

changed = 0
for old, new in replacements.items():
    if old in s:
        s = s.replace(old, new, 1)
        changed += 1

# Keep the category tiles compact and clearly distinct from the campaign cards.
if "'Hızlı kategoriler'" not in s or 'crossAxisCount: 4' not in s:
    raise SystemExit('Home quick-category grid not found')

p.write_text(s, encoding='utf-8')
print(f'Compact home reference applied ({changed} layout adjustments)')
