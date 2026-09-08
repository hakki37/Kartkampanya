from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

# 1) Make the catalog consistently dark and readable.
s = s.replace("brightness: Brightness.light,", "brightness: Brightness.dark,")
s = s.replace("scaffoldBackgroundColor: const Color(0xFFF6F7FB),", "scaffoldBackgroundColor: const Color(0xFF081120),")
s = s.replace("backgroundColor: Colors.transparent,\n        ),", "backgroundColor: const Color(0xFF081120),\n          foregroundColor: Colors.white,\n        ),", 1)
s = s.replace("fillColor: Colors.white,", "fillColor: const Color(0xFF0B1B31),")

# 2) Five clear bottom-navigation destinations.
pages_old = '''    final pages = <Widget>[
      CampaignsPage(cards: cards),
      MyCardsPage(
        cards: cards,
        onAdd: addCard,
        onDelete: deleteCard,
      ),
      const CategoriesPage(),
    ];'''
pages_new = '''    final pages = <Widget>[
      CampaignsPage(cards: cards, mode: 'home'),
      CampaignsPage(cards: cards, mode: 'matched'),
      CampaignsPage(cards: cards, mode: 'all'),
      MyCardsPage(cards: cards, onAdd: addCard, onDelete: deleteCard),
      const CategoriesPage(),
    ];'''
s = s.replace(pages_old, pages_new, 1)

nav_old = '''        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home),
            label: 'Ana Sayfa',
          ),
          NavigationDestination(
            icon: Icon(Icons.credit_card_outlined),
            selectedIcon: Icon(Icons.credit_card),
            label: 'Bendeki Kartlar',
          ),
          NavigationDestination(
            icon: Icon(Icons.category_outlined),
            selectedIcon: Icon(Icons.category),
            label: 'Kategoriler',
          ),
        ],'''
nav_new = '''        destinations: const [
          NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home), label: 'Ana Sayfa'),
          NavigationDestination(icon: Icon(Icons.auto_awesome_outlined), selectedIcon: Icon(Icons.auto_awesome), label: 'Kartıma Uygun'),
          NavigationDestination(icon: Icon(Icons.apps_outlined), selectedIcon: Icon(Icons.apps), label: 'Tüm Kampanyalar'),
          NavigationDestination(icon: Icon(Icons.credit_card_outlined), selectedIcon: Icon(Icons.credit_card), label: 'Bendeki Kartlar'),
          NavigationDestination(icon: Icon(Icons.category_outlined), selectedIcon: Icon(Icons.category), label: 'Kategoriler'),
        ],'''
s = s.replace(nav_old, nav_new, 1)

# 3) CampaignsPage mode keeps the three campaign views independent.
ctor_old = '''class CampaignsPage extends StatefulWidget {
  final List<UserCard> cards;

  const CampaignsPage({
    super.key,
    required this.cards,
  });'''
ctor_new = '''class CampaignsPage extends StatefulWidget {
  final List<UserCard> cards;
  final String mode; // home | matched | all

  const CampaignsPage({
    super.key,
    required this.cards,
    this.mode = 'home',
  });'''
s = s.replace(ctor_old, ctor_new, 1)
init_old = '''  void initState() {
    super.initState();
    future = fetchCampaigns();
    _loadUserState();
  }'''
init_new = '''  void initState() {
    super.initState();
    showAllCampaigns = widget.mode == 'all';
    future = fetchCampaigns();
    _loadUserState();
  }'''
s = s.replace(init_old, init_new, 1)

# 4) Compact catalog-style 4x2 category grid. It avoids chip wrapping/overflow.
start = s.find('''            Wrap(
              spacing: 6,
              runSpacing: 6,
              children: [
                ...(showAllQuickCategories ? quick : quick.take(6)).map<Widget>''')
if start >= 0:
    end_marker = '''            const SizedBox(height: 14),'''
    end = s.find(end_marker, start)
    if end >= 0:
        grid = '''            GridView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: 8,
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 4,
                crossAxisSpacing: 8,
                mainAxisSpacing: 8,
                childAspectRatio: 1.05,
              ),
              itemBuilder: (_, i) {
                const data = [
                  ['🚗', 'Otomotiv'], ['🛍️', 'E-ticaret'], ['📱', 'Elektronik'], ['🛒', 'Market'],
                  ['⛽', 'Akaryakıt'], ['🧳', 'Seyahat'], ['👕', 'Giyim'], ['▦', 'Tümü'],
                ];
                final x = data[i];
                final selected = x[1] == 'Tümü' ? category.isEmpty : category == x[1];
                return InkWell(
                  borderRadius: BorderRadius.circular(15),
                  onTap: () => setState(() => category = x[1] == 'Tümü' ? '' : x[1]),
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 150),
                    decoration: BoxDecoration(
                      gradient: selected ? const LinearGradient(colors: [Color(0xFF5B3DF5), Color(0xFF7653FF)]) : null,
                      color: selected ? null : const Color(0xFF0B1B31),
                      borderRadius: BorderRadius.circular(15),
                      border: Border.all(color: selected ? const Color(0xFF6D59FF) : const Color(0xFF28415F)),
                    ),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(x[0], style: const TextStyle(fontSize: 23)),
                        const SizedBox(height: 3),
                        Text(x[1], maxLines: 1, overflow: TextOverflow.ellipsis,
                          style: const TextStyle(fontSize: 11.5, fontWeight: FontWeight.w800)),
                      ],
                    ),
                  ),
                );
              },
            ),

            const SizedBox(height: 14),'''
        s = s[:start] + grid + s[end + len(end_marker):]

# 5) Make the campaign card title/logo area robust on small phones.
s = s.replace("fontSize: 17,\n      fontWeight: FontWeight.bold,", "fontSize: 16,\n      fontWeight: FontWeight.bold,", 1)

# 6) Replace the generic card icon with a compact bank mark in My Cards.
old_icon = '''                    leading: Container(
                      width: 46,
                      height: 46,
                      decoration: BoxDecoration(
                        color: const Color(0xFFECE9FF),
                        borderRadius: BorderRadius.circular(14),
                      ),
                      child: const Icon(
                        Icons.credit_card_rounded,
                        color: Color(0xFF5B4BDB),
                      ),
                    ),'''
new_icon = '''                    leading: Container(
                      width: 46,
                      height: 46,
                      decoration: BoxDecoration(
                        color: const Color(0xFF162844),
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(color: const Color(0xFF294263)),
                      ),
                      alignment: Alignment.center,
                      child: Text(
                        c.bank.length > 7 ? c.bank.substring(0, 7) : c.bank,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(fontSize: 9, fontWeight: FontWeight.w900),
                      ),
                    ),'''
s = s.replace(old_icon, new_icon, 1)

# 7) Add a real CatalogLogo helper for any later reference-style widgets.
if 'class CatalogLogo extends StatelessWidget' not in s:
    marker = 'class CategoriesPage extends StatelessWidget {'
    logo = '''class CatalogLogo extends StatelessWidget {
  final String label;
  final bool big;
  const CatalogLogo({super.key, required this.label, this.big = false});

  @override
  Widget build(BuildContext context) {
    final n = _norm(label);
    final size = big ? 19.0 : 13.0;
    if (n == 'visa') return Text('VISA', style: TextStyle(fontSize: size + 2, fontWeight: FontWeight.w900, fontStyle: FontStyle.italic));
    if (n == 'mastercard') return const Icon(Icons.circle, size: 18);
    if (n == 'troy') return Text('troy', style: TextStyle(fontSize: size + 1, fontWeight: FontWeight.w900));
    if (n == 'akbank') return Text('AKBANK', style: TextStyle(fontSize: size, fontWeight: FontWeight.w900));
    if (n == 'teb') return Text('TEB', style: TextStyle(fontSize: size + 2, fontWeight: FontWeight.w900));
    return Text(label, maxLines: 1, overflow: TextOverflow.ellipsis, textAlign: TextAlign.center,
      style: TextStyle(fontSize: size, fontWeight: FontWeight.w900));
  }
}

'''
    if marker in s:
        s = s.replace(marker, logo + marker, 1)

p.write_text(s, encoding='utf-8')
print('catalog UI repair applied')
