from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

# v29 builds the reference look on top of the existing working logic.
# Data, Supabase, campaign matching and card persistence remain untouched.

# Replace MainShell with a clean five-tab shell matching the reference.
start = s.find('class _MainShellState extends State<MainShell> {')
end = s.find('class CampaignsPage extends StatefulWidget {', start)
if start < 0 or end < 0:
    raise SystemExit('MainShell anchors not found')

shell = r'''class _MainShellState extends State<MainShell> {
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
        ..addAll(List<Map<String, dynamic>>.from(rows).map((m) => UserCard(
          id: '${m['id']}',
          bank: '${m['bank_name']}',
          card: '${m['card_name']}',
          network: '${m['network']}',
          customerType: '${m['customer_type'] ?? 'Bireysel'}',
          cardType: '${m['card_type'] ?? 'Kredi'}',
        )));
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
      CampaignsPage(cards: cards, mode: 'matched'),
    ];

    return Scaffold(
      backgroundColor: const Color(0xFFF7F6FC),
      body: SafeArea(child: IndexedStack(index: index, children: pages)),
      bottomNavigationBar: NavigationBar(
        selectedIndex: index,
        onDestinationSelected: (v) => setState(() => index = v),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home_rounded), label: 'Ana Sayfa'),
          NavigationDestination(icon: Icon(Icons.local_offer_outlined), selectedIcon: Icon(Icons.local_offer_rounded), label: 'Kampanyalar'),
          NavigationDestination(icon: Icon(Icons.credit_card_outlined), selectedIcon: Icon(Icons.credit_card_rounded), label: 'Kartlarım'),
          NavigationDestination(icon: Icon(Icons.grid_view_outlined), selectedIcon: Icon(Icons.grid_view_rounded), label: 'Kategoriler'),
          NavigationDestination(icon: Icon(Icons.person_outline_rounded), selectedIcon: Icon(Icons.person_rounded), label: 'Profil'),
        ],
      ),
    );
  }
}

'''
s = s[:start] + shell + s[end:]

# Reference-style five-column category grid on the home screen.
start = s.find('            GridView.builder(')
end = s.find('            const SizedBox(height: 14),', start)
if start < 0 or end < 0:
    raise SystemExit('quick category grid anchors not found')

grid = r'''            SizedBox(
              height: 92,
              child: GridView.builder(
                physics: const NeverScrollableScrollPhysics(),
                itemCount: 10,
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 5,
                  crossAxisSpacing: 8,
                  mainAxisSpacing: 8,
                  childAspectRatio: .92,
                ),
                itemBuilder: (_, i) {
                  const data = [
                    ['▦', 'Tümü', 0xFFE9DEFF, 0xFF6D3DF5],
                    ['⛽', 'Akaryakıt', 0xFFFFE8E8, 0xFFE53E3E],
                    ['🛒', 'Market', 0xFFE1F8EF, 0xFF159A68],
                    ['🍴', 'Restoran', 0xFFFFEAD8, 0xFFE76F00],
                    ['🛍', 'E-Ticaret', 0xFFE8E1FF, 0xFF6D3DF5],
                    ['📱', 'Elektronik', 0xFFE1EEFF, 0xFF2176E8],
                    ['✈', 'Seyahat', 0xFFFFE8D8, 0xFFEA6B1F],
                    ['🚗', 'Otomotiv', 0xFFE1F5F4, 0xFF168B8B],
                    ['👕', 'Giyim', 0xFFFFE2F1, 0xFFD93686],
                    ['⌂', 'Ev & Yaşam', 0xFFE3F4E9, 0xFF159A68],
                  ];
                  final x = data[i];
                  final name = x[1] as String;
                  final selected = name == 'Tümü' ? category.isEmpty : category == name;
                  final bg = Color(x[2] as int);
                  final fg = Color(x[3] as int);
                  return InkWell(
                    borderRadius: BorderRadius.circular(16),
                    onTap: () => setState(() => category = name == 'Tümü' ? '' : name),
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 160),
                      decoration: BoxDecoration(
                        color: selected ? fg : bg,
                        borderRadius: BorderRadius.circular(16),
                        boxShadow: selected ? const [BoxShadow(color: Color(0x1F6D3DF5), blurRadius: 10, offset: Offset(0, 4))] : null,
                      ),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(x[0] as String, style: TextStyle(fontSize: 20, color: selected ? Colors.white : fg, fontWeight: FontWeight.w900)),
                          const SizedBox(height: 3),
                          Text(name, maxLines: 1, overflow: TextOverflow.ellipsis, style: TextStyle(fontSize: 9.5, color: selected ? Colors.white : const Color(0xFF353146), fontWeight: FontWeight.w800)),
                        ],
                      ),
                    ),
                  );
                },
              ),
            ),
'''
s = s[:start] + grid + s[end:]

# Compact reference-like home header and banner.
start = s.find('      appBar: AppBar(', s.find('class _CampaignsPageState'))
end = s.find('      body: RefreshIndicator(', start)
if start < 0 or end < 0:
    raise SystemExit('campaign appbar anchors not found')
appbar = r'''      appBar: AppBar(
        titleSpacing: 16,
        title: Row(
          children: [
            Container(
              width: 38, height: 38,
              decoration: BoxDecoration(
                gradient: const LinearGradient(colors: [Color(0xFF8B5CF6), Color(0xFF5B21B6)]),
                borderRadius: BorderRadius.circular(11),
              ),
              child: const Icon(Icons.credit_card_rounded, color: Colors.white, size: 23),
            ),
            const SizedBox(width: 10),
            const Text('Kart Kampanya', style: TextStyle(fontSize: 19, fontWeight: FontWeight.w900)),
          ],
        ),
        actions: [
          IconButton(icon: const Icon(Icons.notifications_none_rounded), onPressed: () {}),
        ],
      ),
'''
s = s[:start] + appbar + s[end:]

# Replace the first purple query hero with a reference-style promotional banner.
old_start = s.find("            Container(\n              padding: const EdgeInsets.fromLTRB(20, 20, 20, 22),")
old_end = s.find('            const SizedBox(height: 14),', old_start)
if old_start >= 0 and old_end > old_start:
    banner = r'''            Container(
              height: 145,
              padding: const EdgeInsets.fromLTRB(18, 16, 16, 14),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFF087CB5), Color(0xFF42B5C7), Color(0xFFF3C46B)],
                  begin: Alignment.centerLeft,
                  end: Alignment.centerRight,
                ),
                borderRadius: BorderRadius.circular(24),
              ),
              child: Stack(
                children: [
                  const Positioned(right: 12, top: 8, child: Text('☀️', style: TextStyle(fontSize: 34))),
                  const Positioned(right: 28, bottom: 0, child: Text('🏖️', style: TextStyle(fontSize: 50))),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Yaz Fırsatları\nDevam Ediyor!', style: TextStyle(color: Colors.white, fontSize: 23, height: 1.02, fontWeight: FontWeight.w900)),
                      const SizedBox(height: 8),
                      const Text('Alışverişte kazancının\ntam zamanını yakala.', style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.w600)),
                      const Spacer(),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 13, vertical: 7),
                        decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(14)),
                        child: const Text('Tüm Kampanyalar  →', style: TextStyle(color: Color(0xFF1767A4), fontSize: 11, fontWeight: FontWeight.w900)),
                      ),
                    ],
                  ),
                ],
              ),
            ),
'''
    s = s[:old_start] + banner + s[old_end:]

# Make CategoriesPage match the reference grid instead of a plain list.
start = s.find('class CategoriesPage extends StatelessWidget {')
if start >= 0:
    end = s.find('\n}', s.find('  }\n}', start) + 4)
    # Find the class's final closing brace robustly.
    brace = s.find('{', start)
    depth = 0
    class_end = None
    for i in range(brace, len(s)):
        if s[i] == '{': depth += 1
        elif s[i] == '}':
            depth -= 1
            if depth == 0:
                class_end = i + 1
                break
    if class_end is not None:
        categories = r'''class CategoriesPage extends StatelessWidget {
  const CategoriesPage({super.key});

  static const items = <List<Object>>[
    ['▦', 'Tümü', 0xFFE9DEFF, 0xFF6D3DF5], ['⛽', 'Akaryakıt', 0xFFFFE8E8, 0xFFE53E3E], ['🛒', 'Market', 0xFFE1F8EF, 0xFF159A68],
    ['🍴', 'Restoran', 0xFFFFEAD8, 0xFFE76F00], ['🛍', 'E-Ticaret', 0xFFE8E1FF, 0xFF6D3DF5], ['👕', 'Giyim', 0xFFFFE2F1, 0xFFD93686],
    ['📱', 'Elektronik', 0xFFE1EEFF, 0xFF2176E8], ['✈', 'Seyahat', 0xFFFFE8D8, 0xFFEA6B1F], ['🚗', 'Otomotiv', 0xFFE1F5F4, 0xFF168B8B],
    ['⌂', 'Ev & Yaşam', 0xFFE3F4E9, 0xFF159A68], ['✚', 'Sağlık & Güzellik', 0xFFE7F7EA, 0xFF2D9B52], ['🎬', 'Eğlence', 0xFFFFE0EC, 0xFFD93686],
    ['🎓', 'Eğitim', 0xFFFFE5F0, 0xFFE0005A], ['▥', 'Finans', 0xFFE1EEFF, 0xFF315FD1], ['••', 'Diğer', 0xFFE8EAF4, 0xFF6E7591],
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF7F6FC),
      appBar: AppBar(
        title: const Text('Kategoriler', style: TextStyle(fontSize: 25, fontWeight: FontWeight.w900)),
        actions: [IconButton(icon: const Icon(Icons.search_rounded), onPressed: () {})],
      ),
      body: GridView.builder(
        padding: const EdgeInsets.fromLTRB(18, 8, 18, 28),
        itemCount: items.length,
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 3, crossAxisSpacing: 10, mainAxisSpacing: 10, childAspectRatio: .98),
        itemBuilder: (_, i) {
          final x = items[i];
          final bg = Color(x[2] as int);
          final fg = Color(x[3] as int);
          return Container(
            decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(20)),
            child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
              Text(x[0] as String, style: TextStyle(fontSize: 29, color: fg, fontWeight: FontWeight.w900)),
              const SizedBox(height: 7),
              Text(x[1] as String, textAlign: TextAlign.center, style: const TextStyle(fontSize: 11, color: Color(0xFF302D40), fontWeight: FontWeight.w800)),
            ]),
          );
        },
      ),
    );
  }
}'''
        s = s[:start] + categories + s[class_end:]

p.write_text(s, encoding='utf-8')
print('v29 reference UI applied')
