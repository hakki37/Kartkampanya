from pathlib import Path
import re

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

pattern = r"    Future<void> openDetails\(\) async \{.*?\n    \}\n    return Card"
replacement = "    Future<void> openDetails() async {\n      if (detailUrl.isNotEmpty) {\n        await onOpenUrl(detailUrl);\n      }\n    }\n    return Card"

s2, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('v14 openDetails block not found')

p.write_text(s2, encoding='utf-8')
print('v14 syntax fixed')
