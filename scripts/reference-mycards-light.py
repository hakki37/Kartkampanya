from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')
# The existing reference card-management implementation already has the required
# selectable fields. Keep its behavior, but convert its presentation from the
# old dark palette to the light reference palette.
s = s.replace('Color(0xFF0B1B31)', 'Colors.white')
s = s.replace('Color(0xFF294263)', 'Color(0xFFE5E1EF)')
s = s.replace('Color(0xFFB7C1D5)', 'Color(0xFF777187)')
# Keep the selected controls in the same vivid purple family as the reference.
s = s.replace('Color(0xFF5B3DF5)', 'Color(0xFF6D3DF5)')
s = s.replace('Color(0xFF7653FF)', 'Color(0xFF8B5CF6)')
p.write_text(s, encoding='utf-8')
print('Reference card palette applied')
