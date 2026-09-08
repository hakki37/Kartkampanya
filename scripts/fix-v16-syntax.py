from pathlib import Path
import re

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')
s = s.replace('campaignConditions(c)', 'campaignConditions(campaign)')

mm = re.search(r'class\s+MyCardsPage\b[^\n{]*\{', s)
cm = re.search(r'class\s+CategoriesPage\s+extends\s+StatelessWidget\s*\{', s)
if mm and cm and cm.start() > mm.start():
    ms, me = mm.start(), cm.start()
    my = """class MyCardsPage extends StatefulWidget {
  final List<UserCard> cards;
  final Future<void> Function(UserCard) onAdd;
  final Future<void> Function(UserCard) onDelete;
  const MyCardsPage({super.key, required this.cards, required this.onAdd, required this.onDelete});
  @override State<MyCardsPage> createState() => _MyCardsPageState();
}

class _MyCardsPageState extends State<MyCardsPage> with SingleTickerProviderStateMixin {
  late final TabController tab = TabController(length: 2, vsync: this);
  @override void dispose() { tab.dispose(); super.dispose(); }
  Future<void> addCard() async { await widget.onAdd(UserCard(id: '', bank: 'Akbank', card: 'Axess', network: 'Visa', customerType: 'Bireysel', cardType: 'Kredi')); }
  @override Widget build(BuildContext c) => Scaffold(
    appBar: AppBar(title: const Text('Bendeki Kartlar', style: TextStyle(fontSize: 23, fontWeight: FontWeight.w900)), actions: [IconButton(onPressed: addCard, icon: const Icon(Icons.add_circle_outline_rounded))], bottom: PreferredSize(preferredSize: const Size.fromHeight(52), child: Padding(padding: const EdgeInsets.fromLTRB(14,0,14,8), child: TabBar(controller: tab, indicator: BoxDecoration(color: const Color(0xFF5B3DF5), borderRadius: BorderRadius.circular(13)), tabs: const [Tab(text: 'Kartlarım'), Tab(text: 'Kart Ekle')])))),
    body: TabBarView(controller: tab, children: [
      widget.cards.isEmpty ? const Center(child: Text('Henüz kart eklemedin.')) : ListView(padding: const EdgeInsets.all(14), children: widget.cards.map((x) => ListTile(leading: CatalogLogo(label: x.bank), title: Text(x.bank), subtitle: Text('${x.card} • ${x.network}'), trailing: IconButton(onPressed: () => widget.onDelete(x), icon: const Icon(Icons.delete_outline)))).toList()),
      Center(child: FilledButton.icon(onPressed: addCard, icon: const Icon(Icons.add), label: const Text('Kart Ekle'))),
    ]),
  );
}
"""
    s = s[:ms] + my + s[me:]

fs = s.find('class _CatalogFilterPageState extends State<CatalogFilterPage>')
fe = s.find('class _FD', fs)
if fs >= 0 and fe >= 0:
    flt = """class _CatalogFilterPageState extends State<CatalogFilterPage> {
  late String category;
  late double? spend;
  String network = '';
  String bank = 'Tümü';
  String card = 'Tümü';
  String type = 'Taksit';
  final cats = const ['Otomotiv','E-ticaret','Elektronik','Market','Akaryakıt','Seyahat','Restoran','Giyim'];
  @override void initState() { super.initState(); category = widget.initialCategory; spend = widget.initialSpend; }
  @override Widget build(BuildContext c) => Scaffold(
    appBar: AppBar(leading: IconButton(onPressed: () => Navigator.pop(c), icon: const Icon(Icons.arrow_back_rounded)), title: const Text('Filtrele', style: TextStyle(fontWeight: FontWeight.w900)), actions: [TextButton(onPressed: () => setState(() { category=''; spend=null; network=''; bank='Tümü'; card='Tümü'; type='Taksit'; }), child: const Text('Temizle'))]),
    body: ListView(padding: const EdgeInsets.fromLTRB(14,4,14,100), children: [
      _FD('Kategori', category.isEmpty ? 'Tümü' : category, ['Tümü', ...cats], (v) => setState(() => category = v == 'Tümü' ? '' : v)), const SizedBox(height:14),
      _FD('Banka', bank, const ['Tümü','Akbank','Garanti BBVA','Yapı Kredi','İş Bankası','Ziraat Bankası','Halkbank','QNB','TEB'], (v) => setState(() => bank=v)), const SizedBox(height:14),
      _FD('Kart Programı', card, const ['Tümü','Axess','Bonus','World','Maximum','Paraf','Bankkart','CardFinans'], (v) => setState(() => card=v)), const SizedBox(height:18), const Text('Kart Ağı', style: TextStyle(fontWeight: FontWeight.w800)),
      Row(children: ['Visa','Mastercard','Troy'].map((x) => Expanded(child: ChoiceChip(label: CatalogLogo(label:x), selected:network==x, onSelected:(_)=>setState(()=>network=network==x?'':x)))).toList()), const SizedBox(height:18),
      Wrap(spacing:7, children:['TL Ödül','Taksit','İndirim','Diğer'].map((x)=>ChoiceChip(label:Text(x),selected:type==x,onSelected:(_)=>setState(()=>type=x))).toList()), const SizedBox(height:18),
      TextField(keyboardType:TextInputType.number,decoration:const InputDecoration(hintText:'Min TL'),onChanged:(v)=>spend=double.tryParse(v)),
    ]),
    bottomSheet: SafeArea(child: Padding(padding:const EdgeInsets.all(14),child:SizedBox(width:double.infinity,height:52,child:FilledButton(onPressed:()=>Navigator.pop(c,{'category':category,'spend':spend,'network':network,'bank':bank,'card':card,'type':type}),child:const Text('Uygula'))))),
  );
}
"""
    s = s[:fs] + flt + s[fe:]

# Catalog-style brand strip: BANK | CARD PROGRAM | NETWORK.
smart = s.find('class SmartCampaignCard extends StatelessWidget {')
if smart >= 0:
    helper = """class _CatalogBrandStrip extends StatelessWidget {
  final String bank; final String card; final String network;
  const _CatalogBrandStrip({required this.bank, required this.card, required this.network});
  @override Widget build(BuildContext context) {
    final items=<Widget>[];
    Widget item(String v)=>Expanded(child:Center(child:CatalogLogo(label:v)));
    if(bank.isNotEmpty) items.add(item(bank));
    if(card.isNotEmpty){if(items.isNotEmpty)items.add(const SizedBox(width:12));items.add(item(card));}
    if(network.isNotEmpty){if(items.isNotEmpty)items.add(const SizedBox(width:12));items.add(item(network));}
    if(items.isEmpty)return const SizedBox.shrink();
    return Padding(padding:const EdgeInsets.only(top:8,bottom:4),child:Row(children:items));
  }
}

"""
    if 'class _CatalogBrandStrip' not in s: s=s[:smart]+helper+s[smart:]
    if 'final displayNetwork = network.isNotEmpty' not in s[smart:smart+12000]:
        m=s.find('final network = decodeHtmlEntities(',smart)
        if m>=0:
            semi=s.find(';',m)
            if semi>=0:
                s=s[:semi+1]+"\n\n    final displayNetwork = network.isNotEmpty ? network : (cards.isNotEmpty ? cards.first.network : '');"+s[semi+1:]
    if '_CatalogBrandStrip(bank: bankName' not in s[smart:smart+16000]:
        cat=s.find('if (category.isNotEmpty)',smart)
        if cat>=0: s=s[:cat]+"_CatalogBrandStrip(bank: bankName, card: cardName, network: displayNetwork),\n\n            "+s[cat:]

p.write_text(s, encoding='utf-8')
print('v16 syntax + bank | card | network strip fixed')
