from pathlib import Path
import re

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

# v16 occasionally emits this call with the wrong local variable name.
s = s.replace('campaignConditions(c)', 'campaignConditions(campaign)')

# Replace the generated My Cards page regardless of whether the generator used
# StatefulWidget/StatelessWidget formatting or spacing around the opening brace.
mm = re.search(r'class\s+MyCardsPage\b[^\n{]*\{', s)
cm = re.search(r'class\s+CategoriesPage\s+extends\s+StatelessWidget\s*\{', s)
if not mm or not cm or cm.start() <= mm.start():
    raise SystemExit('MyCardsPage/CategoriesPage markers not found after v16 UI patch')
ms = mm.start()
me = cm.start()

my = r'''class MyCardsPage extends StatefulWidget {
  final List<UserCard> cards;
  final Future<void> Function(UserCard) onAdd;
  final Future<void> Function(UserCard) onDelete;
  const MyCardsPage({super.key, required this.cards, required this.onAdd, required this.onDelete});
  @override State<MyCardsPage> createState() => _MyCardsPageState();
}

class _MyCardsPageState extends State<MyCardsPage> with SingleTickerProviderStateMixin {
  late final TabController tab = TabController(length: 2, vsync: this);
  @override void dispose() { tab.dispose(); super.dispose(); }
  Future<void> addCard() async {
    await widget.onAdd(UserCard(id: '', bank: 'Akbank', card: 'Axess', network: 'Visa', customerType: 'Bireysel', cardType: 'Kredi'));
  }
  @override
  Widget build(BuildContext c) => Scaffold(
    appBar: AppBar(
      title: const Text('Bendeki Kartlar', style: TextStyle(fontSize: 23, fontWeight: FontWeight.w900)),
      actions: [IconButton(onPressed: addCard, icon: const Icon(Icons.add_circle_outline_rounded))],
      bottom: PreferredSize(
        preferredSize: const Size.fromHeight(52),
        child: Padding(
          padding: const EdgeInsets.fromLTRB(14, 0, 14, 8),
          child: TabBar(
            controller: tab,
            indicator: BoxDecoration(color: const Color(0xFF5B3DF5), borderRadius: BorderRadius.circular(13)),
            tabs: const [Tab(text: 'Kartlarım'), Tab(text: 'Kart Ekle')],
          ),
        ),
      ),
    ),
    body: TabBarView(
      controller: tab,
      children: [
        widget.cards.isEmpty
            ? const Center(child: Text('Henüz kart eklemedin.'))
            : ListView(
                padding: const EdgeInsets.all(14),
                children: widget.cards.map((x) => ListTile(
                  leading: CatalogLogo(label: x.bank),
                  title: Text(x.bank),
                  subtitle: Text('${x.card} • ${x.network}'),
                  trailing: IconButton(onPressed: () => widget.onDelete(x), icon: const Icon(Icons.delete_outline)),
                )).toList(),
              ),
        Center(child: FilledButton.icon(onPressed: addCard, icon: const Icon(Icons.add), label: const Text('Kart Ekle'))),
      ],
    ),
  );
}
'''
s = s[:ms] + my + s[me:]

# Fix the filter state using initState so widget.* values are not read in field initializers.
fs = s.find('class _CatalogFilterPageState extends State<CatalogFilterPage>')
fe = s.find('class _FD', fs)
if fs < 0 or fe < 0:
    raise SystemExit('filter markers not found after v16 UI patch')

flt = r'''class _CatalogFilterPageState extends State<CatalogFilterPage> {
  late String category;
  late double? spend;
  String network = '';
  String bank = 'Tümü';
  String card = 'Tümü';
  String type = 'Taksit';
  final cats = const ['Otomotiv','E-ticaret','Elektronik','Market','Akaryakıt','Seyahat','Restoran','Giyim'];

  @override
  void initState() {
    super.initState();
    category = widget.initialCategory;
    spend = widget.initialSpend;
  }

  @override
  Widget build(BuildContext c) => Scaffold(
    appBar: AppBar(
      leading: IconButton(onPressed: () => Navigator.pop(c), icon: const Icon(Icons.arrow_back_rounded)),
      title: const Text('Filtrele', style: TextStyle(fontWeight: FontWeight.w900)),
      actions: [TextButton(onPressed: () => setState(() { category = ''; spend = null; network = ''; bank = 'Tümü'; card = 'Tümü'; type = 'Taksit'; }), child: const Text('Temizle'))],
    ),
    body: ListView(
      padding: const EdgeInsets.fromLTRB(14, 4, 14, 100),
      children: [
        _FD('Kategori', category.isEmpty ? 'Tümü' : category, ['Tümü', ...cats], (v) => setState(() => category = v == 'Tümü' ? '' : v)),
        const SizedBox(height: 14),
        _FD('Banka', bank, const ['Tümü','Akbank','Garanti BBVA','Yapı Kredi','İş Bankası','Ziraat Bankası','Halkbank','QNB','TEB'], (v) => setState(() => bank = v)),
        const SizedBox(height: 14),
        _FD('Kart Programı', card, const ['Tümü','Axess','Bonus','World','Maximum','Paraf','Bankkart','CardFinans'], (v) => setState(() => card = v)),
        const SizedBox(height: 18),
        const Text('Kart Ağı', style: TextStyle(fontWeight: FontWeight.w800)),
        Row(children: ['Visa','Mastercard','Troy'].map((x) => Expanded(child: ChoiceChip(label: CatalogLogo(label: x), selected: network == x, onSelected: (_) => setState(() => network = network == x ? '' : x)))).toList()),
        const SizedBox(height: 18),
        Wrap(spacing: 7, children: ['TL Ödül','Taksit','İndirim','Diğer'].map((x) => ChoiceChip(label: Text(x), selected: type == x, onSelected: (_) => setState(() => type = x))).toList()),
        const SizedBox(height: 18),
        TextField(keyboardType: TextInputType.number, decoration: const InputDecoration(hintText: 'Min TL'), onChanged: (v) => spend = double.tryParse(v)),
      ],
    ),
    bottomSheet: SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: SizedBox(width: double.infinity, height: 52, child: FilledButton(onPressed: () => Navigator.pop(c, {'category': category, 'spend': spend, 'network': network, 'bank': bank, 'card': card, 'type': type}), child: const Text('Uygula'))),
      ),
    ),
  );
}
'''
s = s[:fs] + flt + s[fe:]
p.write_text(s, encoding='utf-8')
print('v16 syntax fixed')
