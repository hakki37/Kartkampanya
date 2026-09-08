from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

old = "SizedBox(width: double.infinity, child: FilledButton.icon(onPressed: () => onOpenUrl(detailUrl), icon: const Icon(Icons.open_in_new_rounded), label: const Text('Kampanyaya Git')),\n              ],"
new = "SizedBox(width: double.infinity, child: FilledButton.icon(onPressed: () => onOpenUrl(detailUrl), icon: const Icon(Icons.open_in_new_rounded), label: const Text('Kampanyaya Git'))),\n              ],"

if old in s:
    s = s.replace(old, new, 1)
else:
    if new not in s:
        raise SystemExit('v15 detail button syntax pattern not found')

p.write_text(s, encoding='utf-8')
print('v15 syntax fixed')
