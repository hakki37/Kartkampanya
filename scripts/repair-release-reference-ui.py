from pathlib import Path
import re

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

# 1) Restore the requested light white/lilac reference theme without touching OAuth.
s = s.replace('brightness: Brightness.dark,', 'brightness: Brightness.light,', 1)
s = s.replace('scaffoldBackgroundColor: const Color(0xFF081120),', 'scaffoldBackgroundColor: const Color(0xFFF4F3FB),', 1)
s = s.replace('backgroundColor: const Color(0xFF081120),', 'backgroundColor: const Color(0xFFF4F3FB),', 1)

# The reference AppBar is light; only fix the first theme-level foreground value.
needle = "appBarTheme: const AppBarTheme(\n          elevation: 0,\n          backgroundColor: const Color(0xFFF4F3FB),\n          foregroundColor: Colors.white,"
replacement = "appBarTheme: const AppBarTheme(\n          elevation: 0,\n          backgroundColor: const Color(0xFFF4F3FB),\n          foregroundColor: Color(0xFF1E1B3A),"
s = s.replace(needle, replacement, 1)

# 2) Remove the redundant global campaignSection forwarding function.
# Keep the real implementation on KartKampanyaApp.
global_helper = re.compile(
    r"\nString campaignSection\(Map<String, dynamic> campaign\) \{\n"
    r"\s*return KartKampanyaApp\(\)\.campaignSection\(campaign\);\n\}\n",
    re.MULTILINE,
)
s = global_helper.sub('\n', s, count=1)

# 3) Make category matching less eager: explicit category wins; otherwise use
# merchant/title before long descriptions so incidental words do not hijack a card.
old = """  final text = _norm([\n    campaign['title'],\n    campaign['merchant'],\n    campaign['campaign_text'],\n    campaign['conditions'],\n    campaign['terms'],\n    campaign['description'],\n  ].where((x) => x != null).join(' '));"""
new = """  final primaryText = _norm([\n    campaign['merchant'],\n    campaign['title'],\n  ].where((x) => x != null).join(' '));\n  final text = _norm([\n    campaign['title'],\n    campaign['merchant'],\n    campaign['campaign_text'],\n    campaign['conditions'],\n    campaign['terms'],\n    campaign['description'],\n  ].where((x) => x != null).join(' '));"""
s = s.replace(old, new, 1)
s = s.replace("if (entry.value.any(text.contains)) {\n      return entry.key;\n    }", "if (entry.value.any(primaryText.contains)) {\n      return entry.key;\n    }\n  }\n\n  for (final entry in sections.entries) {\n    if (entry.value.any(text.contains)) {\n      return entry.key;\n    }", 1)

# 4) Never allow the generated build to silently drift back to the old dark theme.
if 'brightness: Brightness.dark,' in s.split('class AuthGate', 1)[0]:
    raise SystemExit('Reference UI repair failed: dark theme remains in app theme')
if '0xFF081120' in s.split('class AuthGate', 1)[0]:
    raise SystemExit('Reference UI repair failed: old dark background remains in app theme')

p.write_text(s, encoding='utf-8')
print('Release reference UI repaired: light palette, clean campaign helper, safer category priority.')
