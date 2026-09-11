from pathlib import Path
import runpy

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

# Keep campaignSection as a real top-level helper so every widget can call it.
start = s.find('String campaignSection(Map<String, dynamic> campaign) {')
if start == -1:
    raise SystemExit('top-level campaignSection not found')
end = s.find('\n}\n\nclass UserCard', start)
if end == -1:
    raise SystemExit('campaignSection boundary not found')
helper = '''String campaignSection(Map<String, dynamic> campaign) {
  final existing = '${campaign['category'] ?? ''}'.trim();
  if (existing.isNotEmpty) return existing;

  final text = _norm([
    campaign['title'],
    campaign['merchant'],
    campaign['campaign_text'],
    campaign['conditions'],
    campaign['terms'],
    campaign['description'],
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
    if (entry.value.any(text.contains)) return entry.key;
  }
  return 'Diğer Kampanyalar';
}'''
s = s[:start] + helper + s[end + 2:]

# Remove the duplicate class method; the top-level helper is the single source of truth.
class_start = s.find('class KartKampanyaApp extends StatelessWidget {')
method_start = s.find('String campaignSection(Map<String, dynamic> campaign) {', class_start)
if method_start != -1:
    method_end = s.find('\n  }\n\n  @override', method_start)
    if method_end == -1:
        raise SystemExit('class campaignSection boundary not found')
    s = s[:method_start] + s[method_end + 4:]

# Make the global theme permanently light; this is intentionally limited to theme values.
s = s.replace('brightness: Brightness.dark,', 'brightness: Brightness.light,', 1)
s = s.replace('scaffoldBackgroundColor: const Color(0xFF081120),', 'scaffoldBackgroundColor: const Color(0xFFF7F5FC),', 1)
s = s.replace("backgroundColor: const Color(0xFF081120),\n          foregroundColor: Colors.white,", "backgroundColor: const Color(0xFFF7F5FC),\n          foregroundColor: Color(0xFF211B2D),", 1)

# Replace only MainShell's bottom bar. No campaign/card/category logic is touched.
main_start = s.find('class MainShell extends StatefulWidget {')
nav_start = s.find('      bottomNavigationBar: NavigationBar(', main_start)
nav_end = s.find('\n      ),\n    );', nav_start)
if main_start == -1 or nav_start == -1 or nav_end == -1:
    raise SystemExit('MainShell navigation block not found')
nav_end += len('\n      ),')
new_nav = '''      bottomNavigationBar: Container(
        decoration: const BoxDecoration(
          color: Colors.white,
          border: Border(top: BorderSide(color: Color(0xFFE9E4F1))),
        ),
        child: SafeArea(
          top: false,
          child: SizedBox(
            height: 64,
            child: Row(
              children: [
                _BottomItem(index: 0, current: index, icon: Icons.home_outlined, selectedIcon: Icons.home_rounded, label: 'Ana Sayfa', onTap: () => setState(() => index = 0)),
                _BottomItem(index: 1, current: index, icon: Icons.auto_awesome_outlined, selectedIcon: Icons.auto_awesome, label: 'Kartıma Uygun', onTap: () => setState(() => index = 1)),
                _BottomItem(index: 2, current: index, icon: Icons.apps_outlined, selectedIcon: Icons.apps_rounded, label: 'Kampanyalar', onTap: () => setState(() => index = 2)),
                _BottomItem(index: 3, current: index, icon: Icons.credit_card_outlined, selectedIcon: Icons.credit_card, label: 'Kartlarım', onTap: () => setState(() => index = 3)),
                _BottomItem(index: 4, current: index, icon: Icons.category_outlined, selectedIcon: Icons.category_rounded, label: 'Kategoriler', onTap: () => setState(() => index = 4)),
              ],
            ),
          ),
        ),
      ),'''
s = s[:nav_start] + new_nav + s[nav_end:]

# Add a compact reusable item immediately before CampaignsPage.
marker = 'class CampaignsPage extends StatefulWidget {'
if '_BottomItem extends StatelessWidget' not in s:
    item = '''class _BottomItem extends StatelessWidget {
  final int index;
  final int current;
  final IconData icon;
  final IconData selectedIcon;
  final String label;
  final VoidCallback onTap;

  const _BottomItem({
    required this.index,
    required this.current,
    required this.icon,
    required this.selectedIcon,
    required this.label,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final selected = index == current;
    final color = selected ? const Color(0xFF6D3DF5) : const Color(0xFF77717F);
    return Expanded(
      child: InkWell(
        onTap: onTap,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(selected ? selectedIcon : icon, size: 21, color: color),
            const SizedBox(height: 3),
            Text(
              label,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(fontSize: 10, fontWeight: selected ? FontWeight.w800 : FontWeight.w600, color: color),
            ),
          ],
        ),
      ),
    );
  }
}

'''
    if marker not in s:
        raise SystemExit('CampaignsPage marker not found')
    s = s.replace(marker, item + marker, 1)

p.write_text(s, encoding='utf-8')

# This script runs late in the workflow, so apply the final matching/data repair now.
runpy.run_path('scripts/fix-card-match-and-campaign-data.py', run_name='__main__')
print('Reference bottom navigation and compile helper repaired')
