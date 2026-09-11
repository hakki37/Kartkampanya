from pathlib import Path

# Compatibility-only step.
# Authentication and application logic are preserved in lib/main.dart.
# UI is now split into dedicated screen/widget files; this script must never
# regenerate or overwrite the catalog/login UI.
p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')
if 'class KartKampanyaApp extends StatelessWidget {' not in s:
    raise SystemExit('KartKampanyaApp not found')
if 'class MainShell extends StatefulWidget {' not in s:
    raise SystemExit('MainShell not found')
print('Auth/app compatibility check passed; no UI code regenerated.')
