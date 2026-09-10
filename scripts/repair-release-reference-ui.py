from pathlib import Path

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

# 2) Keep campaignSection callable from every widget. Some earlier repair scripts
# can remove/rewrite the class member, so provide a small safe top-level helper.
if 'String campaignSection(Map<String, dynamic> campaign)' not in s:
    marker = "class UserCard {"
    helper = '''String campaignSection(Map<String, dynamic> campaign) {
  final explicit = '${campaign['category'] ?? ''}'.trim();
  if (explicit.isNotEmpty) return explicit;

  final primary = _norm([
    campaign['merchant'],
    campaign['title'],
  ].where((x) => x != null).join(' '));

  const sections = <String, List<String>>{
    'Akaryakıt': ['benzin', 'motorin', 'mazot', 'lpg', 'akaryakıt', 'akaryakit', 'shell', 'opet', 'petrol ofisi', 'bp'],
    'Otomotiv': ['lastik', 'jant', 'oto servis', 'otomotiv', 'araç bakım', 'arac bakim', 'yedek parça', 'yedek parca'],
    'Market': ['market', 'migros', 'carrefour', 'bim', 'a101', 'şok'],
    'Restoran': ['restoran', 'restaurant', 'yemek', 'hamburger', 'burger', 'pizza', 'döner', 'doner', 'kebap', 'lahmacun', 'pide', 'cafe', 'kafe'],
    'E-ticaret': ['trendyol', 'hepsiburada', 'amazon', 'n11', 'çiçeksepeti', 'ciceksepeti', 'e-ticaret', 'eticaret', 'online alışveriş', 'online alisveris'],
    'Elektronik': ['telefon', 'iphone', 'samsung', 'xiaomi', 'tablet', 'laptop', 'bilgisayar', 'televizyon', 'teknoloji', 'mediamarkt', 'teknosa', 'vatan'],
    'Giyim': ['giyim', 'kıyafet', 'kiyafet', 'ayakkabı', 'ayakkabi', 'zara', 'mavi', 'boyner', 'defacto', 'lc waikiki'],
    'Ev & Yaşam': ['mobilya', 'koltuk', 'mutfak', 'banyo', 'dekorasyon', 'ikea', 'koçtaş', 'koctas', 'english home'],
    'Seyahat': ['uçak', 'ucak', 'uçuş', 'ucus', 'otel', 'tatil', 'seyahat', 'thy', 'pegasus', 'booking'],
    'Eğlence': ['sinema', 'film', 'tiyatro', 'konser', 'biletix', 'netflix', 'spotify', 'steam'],
    'Sağlık & Kişisel Bakım': ['eczane', 'ilaç', 'ilac', 'kozmetik', 'parfüm', 'parfum', 'kuaför', 'kuafor', 'berber'],
    'Spor': ['spor', 'fitness', 'gym', 'spor salonu', 'bisiklet'],
  };

  for (final entry in sections.entries) {
    if (entry.value.any(primary.contains)) return entry.key;
  }
  return 'Diğer Kampanyalar';
}

'''
    if marker not in s:
        raise SystemExit('UserCard marker not found while restoring campaignSection')
    s = s.replace(marker, helper + marker, 1)

# 3) Make the existing class implementation less eager when its source text is present.
old = """  final text = _norm([\n    campaign['title'],\n    campaign['merchant'],\n    campaign['campaign_text'],\n    campaign['conditions'],\n    campaign['terms'],\n    campaign['description'],\n  ].where((x) => x != null).join(' '));"""
new = """  final primaryText = _norm([\n    campaign['merchant'],\n    campaign['title'],\n  ].where((x) => x != null).join(' '));\n  final text = _norm([\n    campaign['title'],\n    campaign['merchant'],\n    campaign['campaign_text'],\n    campaign['conditions'],\n    campaign['terms'],\n    campaign['description'],\n  ].where((x) => x != null).join(' '));"""
s = s.replace(old, new, 1)
old_match = """  for (final entry in sections.entries) {\n    if (entry.value.any(text.contains)) {\n      return entry.key;\n    }\n  }"""
new_match = """  for (final entry in sections.entries) {\n    if (entry.value.any(primaryText.contains)) {\n      return entry.key;\n    }\n  }\n\n  for (final entry in sections.entries) {\n    if (entry.value.any(text.contains)) {\n      return entry.key;\n    }\n  }"""
s = s.replace(old_match, new_match, 1)

# 4) Never allow the generated build to silently drift back to the old dark theme.
if 'brightness: Brightness.dark,' in s.split('class AuthGate', 1)[0]:
    raise SystemExit('Reference UI repair failed: dark theme remains in app theme')
if '0xFF081120' in s.split('class AuthGate', 1)[0]:
    raise SystemExit('Reference UI repair failed: old dark background remains in app theme')

p.write_text(s, encoding='utf-8')
print('Release reference UI repaired: light palette, safe campaign helper, safer category priority.')
