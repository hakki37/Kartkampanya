from pathlib import Path
import re

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')
s = s.replace('campaignConditions(c)', 'campaignConditions(campaign)')

# The v16 generator emits a compact two-button selector with one missing
# closing parenthesis. Keep the selector but make the generated Dart valid.
s = s.replace(
"Expanded(child: GestureDetector(onTap: () => setState(() => showAllCampaigns = false), child: AnimatedContainer(duration: const Duration(milliseconds: 160), padding: const EdgeInsets.symmetric(vertical: 12), decoration: BoxDecoration(color: !showAllCampaigns ? const Color(0xFF5B3DF5) : Colors.transparent, borderRadius: BorderRadius.circular(13)), child: Row(mainAxisAlignment: MainAxisAlignment.center, children: [const Icon(Icons.credit_card_rounded, size: 18), const SizedBox(width: 7), Text('Kartıma Uygun', style: TextStyle(fontWeight: FontWeight.w900, color: !showAllCampaigns ? Colors.white : const Color(0xFFB7C1D5)))]))),",
"Expanded(child: GestureDetector(onTap: () => setState(() => showAllCampaigns = false), child: AnimatedContainer(duration: const Duration(milliseconds: 160), padding: const EdgeInsets.symmetric(vertical: 12), decoration: BoxDecoration(color: !showAllCampaigns ? const Color(0xFF5B3DF5) : Colors.transparent, borderRadius: BorderRadius.circular(13)), child: Row(mainAxisAlignment: MainAxisAlignment.center, children: [const Icon(Icons.credit_card_rounded, size: 18), const SizedBox(width: 7), Text('Kartıma Uygun', style: TextStyle(fontWeight: FontWeight.w900, color: !showAllCampaigns ? Colors.white : const Color(0xFFB7C1D5)))]))))),",
)
s = s.replace(
"Expanded(child: GestureDetector(onTap: () => setState(() => showAllCampaigns = true), child: AnimatedContainer(duration: const Duration(milliseconds: 160), padding: const EdgeInsets.symmetric(vertical: 12), decoration: BoxDecoration(color: showAllCampaigns ? const Color(0xFF5B3DF5) : Colors.transparent, borderRadius: BorderRadius.circular(13)), child: Row(mainAxisAlignment: MainAxisAlignment.center, children: [const Icon(Icons.grid_view_rounded, size: 18), const SizedBox(width: 7), Text('Tüm Kampanyalar', style: TextStyle(fontWeight: FontWeight.w900, color: showAllCampaigns ? Colors.white : const Color(0xFFB7C1D5)))]))),",
"Expanded(child: GestureDetector(onTap: () => setState(() => showAllCampaigns = true), child: AnimatedContainer(duration: const Duration(milliseconds: 160), padding: const EdgeInsets.symmetric(vertical: 12), decoration: BoxDecoration(color: showAllCampaigns ? const Color(0xFF5B3DF5) : Colors.transparent, borderRadius: BorderRadius.circular(13)), child: Row(mainAxisAlignment: MainAxisAlignment.center, children: [const Icon(Icons.grid_view_rounded, size: 18), const SizedBox(width: 7), Text('Tüm Kampanyalar', style: TextStyle(fontWeight: FontWeight.w900, color: showAllCampaigns ? Colors.white : const Color(0xFFB7C1D5)))]))))),",
)

# Replace the generated card page with a real selector instead of the old
# hard-coded Akbank/Axess/Visa action. The user chooses bank, card program,
# network, customer type and card type before the row is inserted into Supabase.
mm = re.search(r'class\s+MyCardsPage\b[^\n{]*\{', s)
cm = re.search(r'class\s+CategoriesPage\s+extends\s+StatelessWidget\s*\{', s)
if mm and cm and cm.start() > mm.start():
    ms, me = mm.start(), cm.start()
    my = r'''class MyCardsPage extends StatefulWidget {
  final List<UserCard> cards;
  final Future<void> Function(UserCard) onAdd;
  final Future<void> Function(UserCard) onDelete;
  const MyCardsPage({super.key, required this.cards, required this.onAdd, required this.onDelete});
  @override State<MyCardsPage> createState() => _MyCardsPageState();
}

class _MyCardsPageState extends State<MyCardsPage> {
  Future<void> addCard() async {
    String bank = 'Akbank';
    String card = 'Axess';
    String network = 'Visa';
    String customerType = 'Bireysel';
    String cardType = 'Kredi';
    const banks = ['Akbank','Garanti BBVA','Yapı Kredi','İş Bankası','Ziraat Bankası','Halkbank','QNB','TEB','VakıfBank','DenizBank','ING','HSBC','Kuveyt Türk','Türkiye Finans'];
    const cards = ['Axess','Bonus','World','Maximum','Paraf','Bankkart','CardFinans','Sağlam Kart','CEPTETEB','Maximum Genç','Bankkart Genç'];
    const networks = ['Visa','Mastercard','Troy'];
    final result = await showDialog<Map<String,String>>(
      context: context,
      builder: (dialogContext) => StatefulBuilder(builder: (context, setDialog) => AlertDialog(
        title: const Text('Kart Ekle'),
        content: SingleChildScrollView(child: Column(mainAxisSize: MainAxisSize.min, children: [
          DropdownButtonFormField<String>(value: bank, decoration: const InputDecoration(labelText: 'Banka'), items: banks.map((x)=>DropdownMenuItem(value:x,child:Text(x))).toList(), onChanged:(v){if(v!=null)setDialog(()=>bank=v);}),
          const SizedBox(height: 10),
          DropdownButtonFormField<String>(value: card, decoration: const InputDecoration(labelText: 'Kart Programı'), items: cards.map((x)=>DropdownMenuItem(value:x,child:Text(x))).toList(), onChanged:(v){if(v!=null)setDialog(()=>card=v);}),
          const SizedBox(height: 10),
          DropdownButtonFormField<String>(value: network, decoration: const InputDecoration(labelText: 'Kart Ağı'), items: networks.map((x)=>DropdownMenuItem(value:x,child:Text(x))).toList(), onChanged:(v){if(v!=null)setDialog(()=>network=v);}),
          const SizedBox(height: 10),
          DropdownButtonFormField<String>(value: customerType, decoration: const InputDecoration(labelText: 'Müşteri Tipi'), items: const ['Bireysel','Ticari'].map((x)=>DropdownMenuItem(value:x,child:Text(x))).toList(), onChanged:(v){if(v!=null)setDialog(()=>customerType=v);}),
          const SizedBox(height: 10),
          DropdownButtonFormField<String>(value: cardType, decoration: const InputDecoration(labelText: 'Kart Tipi'), items: const ['Kredi','Banka'].map((x)=>DropdownMenuItem(value:x,child:Text(x))).toList(), onChanged:(v){if(v!=null)setDialog(()=>cardType=v);}),
        ])),
        actions: [TextButton(onPressed:()=>Navigator.pop(dialogContext),child:const Text('İptal')),FilledButton(onPressed:()=>Navigator.pop(dialogContext,{'bank':bank,'card':card,'network':network,'customerType':customerType,'cardType':cardType}),child:const Text('Kaydet'))],
      )),
    );
    if (result == null || !mounted) return;
    try {
      await widget.onAdd(UserCard(id:'', bank:result['bank']!, card:result['card']!, network:result['network']!, customerType:result['customerType']!, cardType:result['cardType']!));
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Kart eklendi')));
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Kart eklenemedi: $e')));
    }
  }
  @override Widget build(BuildContext c) => Scaffold(
    appBar: AppBar(title: const Text('Bendeki Kartlar', style: TextStyle(fontSize: 23, fontWeight: FontWeight.w900)), actions: [IconButton(onPressed: addCard, icon: const Icon(Icons.add_circle_outline_rounded))],
    body: widget.cards.isEmpty ? Center(child: FilledButton.icon(onPressed:addCard,icon:const Icon(Icons.add),label:const Text('Kart Ekle'))) : ListView(padding:const EdgeInsets.all(14),children:widget.cards.map((x)=>Card(child:ListTile(leading:CatalogLogo(label:x.bank),title:Text('${x.bank} • ${x.card}'),subtitle:Text('${x.network} • ${x.customerType} • ${x.cardType}'),trailing:IconButton(onPressed:()=>widget.onDelete(x),icon:const Icon(Icons.delete_outline)))).toList()),
    floatingActionButton: FloatingActionButton(onPressed:addCard,child:const Icon(Icons.add)),
  );
}
'''
    s = s[:ms] + my + s[me:]

# Give the main shell dedicated bottom-navigation destinations for the two
# campaign views. This avoids mixing the semantics of the old in-page toggle.
mainm = re.search(r'class\s+MainShell\s+extends\s+StatefulWidget', s)
if mainm:
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
    if pages_old in s: s=s.replace(pages_old,pages_new,1)
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
    if nav_old in s:s=s.replace(nav_old,nav_new,1)

# Add mode to CampaignsPage and make matched mode strict.
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
if ctor_old in s:s=s.replace(ctor_old,ctor_new,1)
init_old='''  void initState() {
    super.initState();
    future = fetchCampaigns();
    _loadUserState();
  }'''
init_new='''  void initState() {
    super.initState();
    showAllCampaigns = widget.mode == 'all';
    future = fetchCampaigns();
    _loadUserState();
  }'''
if init_old in s:s=s.replace(init_old,init_new,1)
match_old='''      if (widget.cards.isNotEmpty &&
          matchingCards.isEmpty &&
          !showAllCampaigns) {
        continue;
      }'''
match_new='''      if (widget.mode == 'matched' &&
          (widget.cards.isEmpty || matchingCards.isEmpty)) {
        continue;
      }
      if (widget.mode == 'home' &&
          widget.cards.isNotEmpty &&
          matchingCards.isEmpty &&
          !showAllCampaigns) {
        continue;
      }'''
if match_old in s:s=s.replace(match_old,match_new,1)

# The page itself already has the in-page selector; make its title mode-aware.
s=s.replace("title: const Text('Kart Kampanya', style: TextStyle(fontWeight: FontWeight.w900)),", "title: Text(widget.mode == 'matched' ? 'Kartıma Uygun' : widget.mode == 'all' ? 'Tüm Kampanyalar' : 'Kart Kampanya', style: const TextStyle(fontWeight: FontWeight.w900)),")

p.write_text(s, encoding='utf-8')
print('v16 syntax fixed; card add is interactive; campaign tabs are separated')
