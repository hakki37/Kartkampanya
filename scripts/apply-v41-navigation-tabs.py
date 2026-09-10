from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')


def class_end(src, start):
    brace = src.find('{', start)
    if brace < 0:
        raise SystemExit('class brace not found')
    depth = 0
    quote = None
    esc = False
    for i in range(brace, len(src)):
        ch = src[i]
        if quote:
            if esc:
                esc = False
            elif ch == '\\':
                esc = True
            elif ch == quote:
                quote = None
        elif ch in "'\"":
            quote = ch
        elif ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return i + 1
    raise SystemExit('unbalanced Dart class')


def remove_all_classes(src, marker):
    positions = []
    pos = 0
    while True:
        i = src.find(marker, pos)
        if i < 0:
            break
        positions.append(i)
        pos = i + 1
    for i in reversed(positions):
        src = src[:i] + src[class_end(src, i):]
    return src


def replace_class(src, name, replacement):
    start = src.find('class ' + name)
    if start < 0:
        raise SystemExit(f'{name} not found')
    brace = src.find('{', start)
    depth = 0
    quote = None
    esc = False
    for i in range(brace, len(src)):
        ch = src[i]
        if quote:
            if esc:
                esc = False
            elif ch == '\\':
                esc = True
            elif ch == quote:
                quote = None
        elif ch in "'\"":
            quote = ch
        elif ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return src[:start] + replacement + src[i + 1:]
    raise SystemExit(f'{name} end not found')

# Remove stale shell state(s) before replacing MainShell. The previous shell
# replacement only replaced the widget class, leaving its old State class behind.
s = remove_all_classes(s, 'class _MainShellState extends State<MainShell> {')

shell = r'''class MainShell extends StatefulWidget {
  const MainShell({super.key});

  @override
  State<MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<MainShell> {
  int index = 0;
  final cards = <UserCard>[];

  @override
  void initState() {
    super.initState();
    loadCards();
  }

  Future<void> loadCards() async {
    final uid = Supabase.instance.client.auth.currentUser!.id;
    final rows = await Supabase.instance.client
        .from('user_cards')
        .select()
        .eq('user_id', uid)
        .order('created_at');
    if (!mounted) return;
    setState(() {
      cards
        ..clear()
        ..addAll(
          List<Map<String, dynamic>>.from(rows).map(
            (m) => UserCard(
              id: '${m['id']}',
              bank: '${m['bank_name']}',
              card: '${m['card_name']}',
              network: '${m['network']}',
              customerType: '${m['customer_type'] ?? 'Bireysel'}',
              cardType: '${m['card_type'] ?? 'Kredi'}',
            ),
          ),
        );
    });
  }

  Future<void> addCard(UserCard card) async {
    final uid = Supabase.instance.client.auth.currentUser!.id;
    await Supabase.instance.client.from('user_cards').insert({
      'user_id': uid,
      'bank_name': card.bank,
      'card_name': card.card,
      'network': card.network,
      'customer_type': card.customerType,
      'card_type': card.cardType,
    });
    await loadCards();
  }

  Future<void> deleteCard(UserCard card) async {
    await Supabase.instance.client.from('user_cards').delete().eq('id', card.id);
    await loadCards();
  }

  @override
  Widget build(BuildContext context) {
    final pages = <Widget>[
      CampaignsPage(cards: cards, mode: 'home'),
      CampaignsPage(cards: cards, mode: 'all'),
      MyCardsPage(cards: cards, onAdd: addCard, onDelete: deleteCard),
      const CategoriesPage(),
      const ProfilePage(),
    ];

    return Scaffold(
      backgroundColor: const Color(0xFFF8F7FC),
      body: SafeArea(child: IndexedStack(index: index, children: pages)),
      bottomNavigationBar: NavigationBar(
        height: 78,
        backgroundColor: Colors.white,
        indicatorColor: const Color(0xFFE9DEFF),
        selectedIndex: index,
        onDestinationSelected: (value) => setState(() => index = value),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home_rounded),
            label: 'Ana Sayfa',
          ),
          NavigationDestination(
            icon: Icon(Icons.local_offer_outlined),
            selectedIcon: Icon(Icons.local_offer_rounded),
            label: 'Kampanyalar',
          ),
          NavigationDestination(
            icon: Icon(Icons.credit_card_outlined),
            selectedIcon: Icon(Icons.credit_card_rounded),
            label: 'Kartlarım',
          ),
          NavigationDestination(
            icon: Icon(Icons.grid_view_outlined),
            selectedIcon: Icon(Icons.grid_view_rounded),
            label: 'Kategoriler',
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outline_rounded),
            selectedIcon: Icon(Icons.person_rounded),
            label: 'Profil',
          ),
        ],
      ),
    );
  }
}
'''

s = replace_class(s, 'MainShell', shell)

# The existing reference MyCardsPage is intentionally tabbed. Keep its behavior,
# but recolor its explicitly dark surfaces to match the open white/purple design.
start = s.find('class MyCardsPage extends StatefulWidget')
end = s.find('class CategoriesPage extends StatelessWidget', start)
if start >= 0 and end > start:
    block = s[start:end]
    block = block.replace('const Color(0xFF0B1B31)', 'Colors.white')
    block = block.replace('const Color(0xFF294263)', 'const Color(0xFFE3DEEC)')
    block = block.replace('const Color(0xFFB7C1D5)', 'const Color(0xFF777187)')
    block = block.replace('const Color(0xFF7653FF)', 'const Color(0xFF8A63F5)')
    block = block.replace('const Color(0xFF5B3DF5)', 'const Color(0xFF6D3DF5)')
    s = s[:start] + block + s[end:]
else:
    raise SystemExit('MyCardsPage boundaries not found')

# Keep the campaign date parser at top level and before the generated card.
if 'DateTime? parseCampaignDate(' not in s:
    helper = r'''DateTime? parseCampaignDate(String value) {
  final text = value.trim();
  final direct = DateTime.tryParse(text);
  if (direct != null) return direct;
  final m = RegExp(r'(\d{1,2})[./-](\d{1,2})[./-](\d{4})').firstMatch(text);
  if (m == null) return null;
  return DateTime.tryParse('${m.group(3)}-${m.group(2)!.padLeft(2, '0')}-${m.group(1)!.padLeft(2, '0')}');
}

'''
    marker = 'class SmartCampaignCard extends StatelessWidget {'
    if marker not in s:
        raise SystemExit('SmartCampaignCard marker not found for date helper')
    s = s.replace(marker, helper + marker, 1)

# MyCardsPage uses CatalogLogo for bank/network identity.
if 'class CatalogLogo extends StatelessWidget' not in s:
    logo = r'''class CatalogLogo extends StatelessWidget {
  final String label;
  const CatalogLogo({super.key, required this.label});

  String _domain() {
    final x = label.toLowerCase().replaceAll(' ', '');
    if (x == 'visa') return 'visa.com';
    if (x == 'mastercard') return 'mastercard.com';
    if (x == 'troy') return 'troy.com.tr';
    if (x.contains('akbank')) return 'akbank.com';
    if (x.contains('garanti')) return 'garantibbva.com.tr';
    if (x.contains('yapi') || x.contains('yapıkredi')) return 'yapikredi.com.tr';
    if (x.contains('isbank') || x.contains('işbank')) return 'isbank.com.tr';
    if (x.contains('qnb') || x.contains('cardfinans')) return 'qnb.com.tr';
    if (x.contains('teb')) return 'teb.com.tr';
    if (x.contains('ziraat')) return 'ziraatbank.com.tr';
    if (x.contains('halk')) return 'halkbank.com.tr';
    if (x.contains('vakif')) return 'vakifbank.com.tr';
    if (x.contains('deniz')) return 'denizbank.com';
    if (x.contains('ing')) return 'ing.com.tr';
    return '';
  }

  @override
  Widget build(BuildContext context) {
    final domain = _domain();
    if (domain.isEmpty) {
      return Text(label, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 11));
    }
    return Image.network(
      'https://www.google.com/s2/favicons?domain=$domain&sz=128',
      width: 34,
      height: 34,
      fit: BoxFit.contain,
      errorBuilder: (_, __, ___) => Text(label, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 11)),
    );
  }
}

'''
    marker = 'class UserCard {'
    if marker not in s:
        raise SystemExit('UserCard marker not found for CatalogLogo')
    s = s.replace(marker, logo + marker, 1)

p.write_text(s, encoding='utf-8')
print('Reference navigation repaired: duplicate shell state removed; campaign date/logo helpers guaranteed')
