from pathlib import Path
import runpy

# The previous V2 pass was a recolor/reconstruction mix. Keep this final hook
# deterministic: first rebuild the readable campaign card, then rebuild the
# catalog screen layout. Both run after every older UI transform.
runpy.run_path('scripts/reference-card-v3.py', run_name='__main__')
runpy.run_path('scripts/reference-catalog-v3.py', run_name='__main__')

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')
# Final safety net for the authenticated catalog canvas and Material defaults.
s = s.replace('brightness: Brightness.light,', 'brightness: Brightness.dark,')
s = s.replace('scaffoldBackgroundColor: const Color(0xFFF7F5FC),', 'scaffoldBackgroundColor: const Color(0xFF081120),')
s = s.replace('scaffoldBackgroundColor: const Color(0xFFF8F7FC),', 'scaffoldBackgroundColor: const Color(0xFF081120),')
p.write_text(s, encoding='utf-8')
print('Final dark reference V3 locked')
