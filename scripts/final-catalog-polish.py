from pathlib import Path
import re

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

# Compact home categories: 4 columns, 2 rows like the reference catalog.
old = re.search(r"        SizedBox\(height:92,child:ListView\.separated.*?\),\n        if\(category\.isNotEmpty", s, re.S)
if old:
    cats = '''        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: 8,
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 4,
            crossAxisSpacing: 8,
            mainAxisSpacing: 8,
            childAspectRatio: 1.12,
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
                    Text(x[1], maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 11.5, fontWeight: FontWeight.w800)),
                  ],
                ),
              ),
            );
          },
        ),
        if(category.isNotEmpty'''
    s = s[:old.start()] + cats + s[old.end():]
    print('compact home categories applied')

# Clean catalog wordmarks and merchant marks. No blank favicon boxes.
lo = s.find('class CatalogLogo extends StatelessWidget')
ld = s.find('\n\nclass CampaignDetailPage', lo)
if lo >= 0 and ld > lo:
    logo = r'''class CatalogLogo extends StatelessWidget {
  final String label;
  final bool big;
  const CatalogLogo({super.key, required this.label, this.big = false});
  @override
  Widget build(BuildContext context) {
    final n = _norm(label);
    final w = big ? 108.0 : 82.0;
    final h = big ? 48.0 : 30.0;
    if (n.contains('ispark')) return SizedBox(width:w,height:h,child:Center(child:Text('İSPARK',style:TextStyle(fontSize:big?19:12,fontWeight:FontWeight.w900,color:const Color(0xFF159447)))));
    if (n == 'n11' || n.contains('n11')) return SizedBox(width:w,height:h,child:Center(child:Text('n11',style:TextStyle(fontSize:big?30:21,fontWeight:FontWeight.w900,color:const Color(0xFF5D35D5)))));
    if (n.contains('mediamarkt')) return SizedBox(width:w,height:h,child:Center(child:Text('MediaMarkt',style:TextStyle(fontSize:big?16:12,fontWeight:FontWeight.w900,color:const Color(0xFFE30613)))));
    if (n == 'akbank') return SizedBox(width:w,height:h,child:Center(child:Text('AKBANK',style:TextStyle(fontSize:big?21:16,fontWeight:FontWeight.w900,color:const Color(0xFFE30613)))));
    if (n == 'axess') return SizedBox(width:w,height:h,child:Center(child:RichText(text:TextSpan(children:[TextSpan(text:'a',style:TextStyle(fontSize:big?30:23,color:Colors.white)),TextSpan(text:'x',style:TextStyle(fontSize:big?30:23,fontWeight:FontWeight.w900,color:const Color(0xFFF5A623))),TextSpan(text:'ess',style:TextStyle(fontSize:big?30:23,color:Colors.white))]))));
    if (n == 'visa') return SizedBox(width:w,height:h,child:Center(child:Text('VISA',style:TextStyle(fontSize:big?27:20,fontWeight:FontWeight.w900,fontStyle:FontStyle.italic,color:const Color(0xFF1677FF)))));
    if (n == 'mastercard') return SizedBox(width:w,height:h,child:Center(child:Row(mainAxisAlignment:MainAxisAlignment.center,children:[Container(width:big?28:20,height:big?28:20,decoration:const BoxDecoration(shape:BoxShape.circle,color:Color(0xFFE9283F))),Container(margin:const EdgeInsets.only(left:-9),width:big?28:20,height:big?28:20,decoration:const BoxDecoration(shape:BoxShape.circle,color:Color(0xFFFFA500)))])));
    if (n == 'troy') return SizedBox(width:w,height:h,child:Center(child:Text('troy',style:TextStyle(fontSize:big?24:18,fontWeight:FontWeight.w900,color:const Color(0xFF27C5D9)))));
    const sizes = {'garanti bbva':16.0,'bonus':19.0,'yapı kredi':16.0,'world':19.0,'iş bankası':16.0,'maximum':19.0,'ziraat bankası':14.0,'bankkart':18.0,'halkbank':16.0,'paraf':19.0,'qnb':19.0,'cardfinans':16.0,'teb':19.0,'vakıfbank':16.0,'sağlam kart':15.0,'türkiye finans':14.0,'ing':20.0,'hsbc':20.0,'odeabank':16.0};
    return SizedBox(width:w,height:h,child:Center(child:Text(label,maxLines:1,overflow:TextOverflow.ellipsis,textAlign:TextAlign.center,style:TextStyle(fontSize:sizes[n]??14,fontWeight:FontWeight.w900,color:Colors.white))));
  }
}'''
    s = s[:lo] + logo + s[ld:]
    print('catalog logos polished')

# Delete only the current user's card, then update the visible list immediately.
dm = re.search(r'  Future<void> deleteCard\(UserCard card\) async \{.*?\n  \}', s, re.S)
if dm:
    delete = '''  Future<void> deleteCard(UserCard card) async {
    final uid = Supabase.instance.client.auth.currentUser!.id;
    if (card.id.isEmpty) return;
    await Supabase.instance.client
        .from('user_cards')
        .delete()
        .eq('id', card.id)
        .eq('user_id', uid);
    if (!mounted) return;
    setState(() => cards.removeWhere((x) => x.id == card.id));
  }'''
    s = s[:dm.start()] + delete + s[dm.end():]
    print('card deletion hardened')

# Replace the previous fragile card-management page with a readable,
# reference-style segmented page. Keep all widgets expanded so Dart syntax is stable.
ms = s.find('class MyCardsPage extends StatefulWidget')
me = s.find('class CategoriesPage extends StatelessWidget', ms)
if ms >= 0 and me > ms:
    my = r'''class MyCardsPage extends StatefulWidget {
  final List<UserCard> cards;
  final Future<void> Function(UserCard) onAdd;
  final Future<void> Function(UserCard) onDelete;
  const MyCardsPage({super.key, required this.cards, required this.onAdd, required this.onDelete});
  @override
  State<MyCardsPage> createState() => _MyCardsPageState();
}

class _MyCardsPageState extends State<MyCardsPage> {
  int tab = 0;
  String bank = 'Akbank';
  String program = 'Axess';
  String network = 'Visa';
  String cardType = 'Kredi Kartı';
  String usage = 'Bireysel';
  bool saving = false;

  static const banks = [
    'Akbank','Garanti BBVA','Yapı Kredi','İş Bankası','QNB','Ziraat Bankası',
    'Halkbank','TEB','VakıfBank','DenizBank','ING','HSBC','Kuveyt Türk',
    'Türkiye Finans','Odeabank'
  ];
  static const programs = [
    'Axess','Bonus','World','Maximum','Paraf','Bankkart','CardFinans',
    'Sağlam Kart','CEPTETEB','Maximum Genç','Bankkart Genç'
  ];
  static const networks = ['Visa','Mastercard','Troy'];
  static const cardTypes = ['Kredi Kartı','Banka Kartı'];
  static const usages = ['Bireysel','Ticari'];

  Future<void> save() async {
    setState(() => saving = true);
    try {
      await widget.onAdd(UserCard(
        id: '',
        bank: bank,
        card: program,
        network: network,
        customerType: usage,
        cardType: cardType,
      ));
      if (!mounted) return;
      setState(() => tab = 0);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Kart eklendi')),
      );
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Kart eklenemedi: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => saving = false);
    }
  }

  Widget dropdownField(String label, String value, List<String> items, ValueChanged<String> onChanged) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800)),
        const SizedBox(height: 7),
        DropdownButtonFormField<String>(
          value: value,
          isExpanded: true,
          items: items.map((x) => DropdownMenuItem<String>(value: x, child: Text(x))).toList(),
          onChanged: (x) { if (x != null) onChanged(x); },
          decoration: InputDecoration(
            filled: true,
            fillColor: const Color(0xFF0B1B31),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Color(0xFF294263)),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Color(0xFF294263)),
            ),
          ),
        ),
      ],
    );
  }

  Widget choiceRow(List<String> items, String selected, ValueChanged<String> onChanged) {
    return Row(
      children: items.asMap().entries.map((entry) {
        final i = entry.key;
        final x = entry.value;
        return Expanded(
          child: Padding(
            padding: EdgeInsets.only(right: i == items.length - 1 ? 0 : 7),
            child: InkWell(
              borderRadius: BorderRadius.circular(12),
              onTap: () => onChanged(x),
              child: Container(
                height: 50,
                decoration: BoxDecoration(
                  color: selected == x ? const Color(0xFF5B3DF5) : const Color(0xFF0B1B31),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: selected == x ? const Color(0xFF7653FF) : const Color(0xFF294263),
                  ),
                ),
                child: Center(
                  child: x == 'Visa' || x == 'Mastercard' || x == 'Troy'
                      ? CatalogLogo(label: x)
                      : Text(x, style: const TextStyle(fontWeight: FontWeight.w800)),
                ),
              ),
            ),
          ),
        );
      }).toList(),
    );
  }

  Widget cardRow(UserCard x) {
    return Container(
      margin: const EdgeInsets.only(bottom: 9),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF0B1B31),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFF294263)),
      ),
      child: Row(
        children: [
          SizedBox(width: 48, child: CatalogLogo(label: x.bank)),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(x.bank, style: const TextStyle(fontWeight: FontWeight.w900)),
                Text(x.card, style: const TextStyle(color: Color(0xFFB7C1D5), fontSize: 12)),
              ],
            ),
          ),
          SizedBox(width: 58, child: CatalogLogo(label: x.network)),
          IconButton(
            tooltip: 'Kartı sil',
            onPressed: () => widget.onDelete(x),
            icon: const Icon(Icons.delete_outline_rounded),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Bendeki Kartlar', style: TextStyle(fontSize: 22, fontWeight: FontWeight.w900)),
        actions: [
          IconButton(
            onPressed: () => setState(() => tab = 1),
            icon: const Icon(Icons.add_circle_outline_rounded, size: 25),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(14, 2, 14, 100),
        children: [
          Container(
            padding: const EdgeInsets.all(3),
            decoration: BoxDecoration(
              color: const Color(0xFF0B1B31),
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: const Color(0xFF294263)),
            ),
            child: Row(
              children: [
                Expanded(
                  child: InkWell(
                    borderRadius: BorderRadius.circular(11),
                    onTap: () => setState(() => tab = 0),
                    child: Container(
                      padding: const EdgeInsets.symmetric(vertical: 13),
                      decoration: BoxDecoration(
                        color: tab == 0 ? const Color(0xFF5B3DF5) : Colors.transparent,
                        borderRadius: BorderRadius.circular(11),
                      ),
                      child: const Center(child: Text('Kartlarım', style: TextStyle(fontWeight: FontWeight.w900))),
                    ),
                  ),
                ),
                Expanded(
                  child: InkWell(
                    borderRadius: BorderRadius.circular(11),
                    onTap: () => setState(() => tab = 1),
                    child: Container(
                      padding: const EdgeInsets.symmetric(vertical: 13),
                      decoration: BoxDecoration(
                        color: tab == 1 ? const Color(0xFF5B3DF5) : Colors.transparent,
                        borderRadius: BorderRadius.circular(11),
                      ),
                      child: const Center(child: Text('Kart Ekle', style: TextStyle(fontWeight: FontWeight.w900))),
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),
          if (tab == 0) ...[
            if (widget.cards.isEmpty)
              const Padding(
                padding: EdgeInsets.all(35),
                child: Center(child: Text('Henüz kart eklemedin.')),
              ),
            ...widget.cards.map(cardRow),
          ],
          if (tab == 1) ...[
            dropdownField('Banka', bank, banks, (v) => setState(() => bank = v)),
            const SizedBox(height: 14),
            dropdownField('Kart Programı', program, programs, (v) => setState(() => program = v)),
            const SizedBox(height: 16),
            const Text('Kart Ağı', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800)),
            const SizedBox(height: 8),
            choiceRow(networks, network, (v) => setState(() => network = v)),
            const SizedBox(height: 16),
            const Text('Kart Türü', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800)),
            const SizedBox(height: 8),
            choiceRow(cardTypes, cardType, (v) => setState(() => cardType = v)),
            const SizedBox(height: 16),
            const Text('Kullanım', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800)),
            const SizedBox(height: 8),
            choiceRow(usages, usage, (v) => setState(() => usage = v)),
            const SizedBox(height: 24),
            SizedBox(
              height: 52,
              width: double.infinity,
              child: FilledButton(
                onPressed: saving ? null : save,
                child: Text(saving ? 'Kaydediliyor...' : 'Kartı Kaydet'),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
'''
    s = s[:ms] + my + s[me:]
    print('reference-style MyCardsPage applied safely')
else:
    print('MyCardsPage/CategoriesPage boundaries not found')

p.write_text(s, encoding='utf-8')
print('final catalog polish complete')
