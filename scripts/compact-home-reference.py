from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

# The reference screenshot is intentionally compact: less vertical space above
# the first campaign, while keeping the same 4x2 category catalog.
replacements = {
    "padding: const EdgeInsets.fromLTRB(16, 8, 16, 24)": "padding: const EdgeInsets.fromLTRB(14, 4, 14, 18)",
    "padding: const EdgeInsets.fromLTRB(20, 20, 20, 22)": "padding: const EdgeInsets.fromLTRB(16, 14, 16, 16)",
    "borderRadius: BorderRadius.circular(26)": "borderRadius: BorderRadius.circular(20)",
    "fontSize: 25,\n                      fontWeight: FontWeight.w800": "fontSize: 21,\n                      fontWeight: FontWeight.w800",
    "style: TextStyle(color: Colors.white70, fontSize: 14)": "style: TextStyle(color: Colors.white70, fontSize: 12.5)",
    "const SizedBox(height: 14),\n\n            TextField(": "const SizedBox(height: 9),\n\n            TextField(",
    "contentPadding: const EdgeInsets.symmetric(\n                  horizontal: 18,\n                  vertical: 16,\n                )": "contentPadding: const EdgeInsets.symmetric(\n                  horizontal: 16,\n                  vertical: 10,\n                )",
    "borderRadius: BorderRadius.circular(18)": "borderRadius: BorderRadius.circular(16)",
    "fontSize: 18,\n                fontWeight: FontWeight.bold": "fontSize: 16,\n                fontWeight: FontWeight.w800",
    "const SizedBox(height: 10),\n\n            GridView.builder(": "const SizedBox(height: 6),\n\n            GridView.builder(",
    "crossAxisSpacing: 8,\n                mainAxisSpacing: 8,\n                childAspectRatio: 1.05": "crossAxisSpacing: 7,\n                mainAxisSpacing: 7,\n                childAspectRatio: 1.48",
    "borderRadius: BorderRadius.circular(15)": "borderRadius: BorderRadius.circular(13)",
    "Text(x[0], style: const TextStyle(fontSize: 23))": "Text(x[0], style: const TextStyle(fontSize: 18))",
    "const SizedBox(height: 3),\n                        Text(x[1]": "const SizedBox(height: 2),\n                        Text(x[1]",
    "style: const TextStyle(fontSize: 11.5, fontWeight: FontWeight.w800)": "style: const TextStyle(fontSize: 10.5, fontWeight: FontWeight.w800)",
    "const SizedBox(height: 14),\n\n            Wrap(": "const SizedBox(height: 8),\n\n            Wrap(",
}

changed = 0
for old, new in replacements.items():
    if old in s:
        s = s.replace(old, new, 1)
        changed += 1

# Only the home quick-category grid should be compacted. Guard against an
# accidental replacement by requiring its heading and the 4-column grid.
if "'Hızlı kategoriler'" not in s or 'crossAxisCount: 4' not in s:
    raise SystemExit('Home quick-category grid not found')

p.write_text(s, encoding='utf-8')
print(f'Compact home reference applied ({changed} layout adjustments)')
