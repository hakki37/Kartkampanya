from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

# v16 currently uses Google favicon squares for banks/cards. Replace that
# renderer with clean catalog-style wordmarks, matching the supplied target:
# AKBANK | axess | VISA. No external image host is needed.
start = s.find('class CatalogLogo extends StatelessWidget{')
end = s.find('\n\nclass CampaignDetailPage', start)
if start >= 0 and end > start:
    logo = r'''class CatalogLogo extends StatelessWidget {
  final String label;
  final bool big;
  const CatalogLogo({super.key, required this.label, this.big = false});
  @override
  Widget build(BuildContext context) {
    final n = label.trim().toLowerCase();
    final w = big ? 108.0 : 92.0;
    final h = big ? 42.0 : 32.0;
    if (n == 'akbank') {
      return SizedBox(width: w, height: h, child: Center(child: Text('AKBANK', style: TextStyle(fontSize: big ? 21 : 17, fontWeight: FontWeight.w900, letterSpacing: .2, color: const Color(0xFFE30613)))));
    }
    if (n == 'axess') {
      return SizedBox(width: w, height: h, child: Center(child: RichText(text: TextSpan(children: [TextSpan(text: 'a', style: TextStyle(fontSize: big ? 31 : 24, fontWeight: FontWeight.w300, color: Colors.white)), TextSpan(text: 'x', style: TextStyle(fontSize: big ? 31 : 24, fontWeight: FontWeight.w900, color: const Color(0xFFF5A623))), TextSpan(text: 'ess', style: TextStyle(fontSize: big ? 31 : 24, fontWeight: FontWeight.w300, color: Colors.white))]))));
    }
    if (n == 'visa') {
      return SizedBox(width: w, height: h, child: Center(child: Text('VISA', style: TextStyle(fontSize: big ? 28 : 22, fontWeight: FontWeight.w900, fontStyle: FontStyle.italic, letterSpacing: -1.0, color: const Color(0xFF1677FF)))));
    }
    if (n == 'mastercard') {
      return SizedBox(width: w, height: h, child: Center(child: Row(mainAxisAlignment: MainAxisAlignment.center, children: [Container(width: big ? 30 : 24, height: big ? 30 : 24, decoration: const BoxDecoration(shape: BoxShape.circle, color: Color(0xFFE9283F))), Container(margin: const EdgeInsets.only(left: -9), width: big ? 30 : 24, height: big ? 30 : 24, decoration: const BoxDecoration(shape: BoxShape.circle, color: Color(0xFFFFA500))), const SizedBox(width: 7), Text('mastercard', style: TextStyle(fontSize: big ? 11 : 9, fontWeight: FontWeight.w800, color: Colors.white))])));
    }
    if (n == 'troy') {
      return SizedBox(width: w, height: h, child: Center(child: Text('troy', style: TextStyle(fontSize: big ? 25 : 20, fontWeight: FontWeight.w900, color: const Color(0xFF27C5D9)))));
    }
    const brandSizes = <String, double>{
      'garanti bbva': 16, 'bonus': 20, 'yapı kredi': 16, 'world': 20,
      'iş bankası': 16, 'maximum': 20, 'ziraat bankası': 15, 'bankkart': 18,
      'halkbank': 16, 'paraf': 20, 'qnb': 19, 'cardfinans': 17, 'teb': 20,
      'vakıfbank': 16, 'sağlam kart': 16, 'türkiye finans': 14, 'ing': 21,
      'hsbc': 20, 'odeabank': 17,
    };
    final fs = brandSizes[n] ?? (big ? 17.0 : 14.0);
    return SizedBox(width: w, height: h, child: Center(child: Text(label, maxLines: 1, overflow: TextOverflow.ellipsis, textAlign: TextAlign.center, style: TextStyle(fontSize: fs, fontWeight: FontWeight.w900, color: Colors.white, letterSpacing: .1))));
  }
}'''
    s = s[:start] + logo + s[end:]
    print('CatalogLogo replaced with catalog-style wordmarks')
else:
    print('CatalogLogo class not found; keeping existing renderer')

old = "Wrap(spacing:4,runSpacing:2,children:[if(b.isNotEmpty)CatalogLogo(label:b),if(card.isNotEmpty)CatalogLogo(label:card),if(n.isNotEmpty)CatalogLogo(label:n)])"
new = "Wrap(spacing:2,runSpacing:2,children:[if(b.isNotEmpty)CatalogLogo(label:b),if(b.isNotEmpty&&card.isNotEmpty)const Padding(padding:EdgeInsets.symmetric(horizontal:5),child:Text('|',style:TextStyle(color:Color(0xFF8090A8),fontSize:20,fontWeight:FontWeight.w300))),if(card.isNotEmpty)CatalogLogo(label:card),if(card.isNotEmpty&&n.isNotEmpty)const Padding(padding:EdgeInsets.symmetric(horizontal:5),child:Text('|',style:TextStyle(color:Color(0xFF8090A8),fontSize:20,fontWeight:FontWeight.w300))),if(n.isNotEmpty)CatalogLogo(label:n)])"
count = s.count(old)
if count:
    s = s.replace(old, new)
    print(f'catalog bank | card | network separators applied ({count})')

detail_old = "Center(child:Wrap(alignment:WrapAlignment.center,spacing:5,children:[if(b.isNotEmpty)CatalogLogo(label:b),if(card.isNotEmpty)CatalogLogo(label:card),if(n.isNotEmpty)CatalogLogo(label:n)]))"
detail_new = "Center(child:Wrap(alignment:WrapAlignment.center,spacing:2,children:[if(b.isNotEmpty)CatalogLogo(label:b),if(b.isNotEmpty&&card.isNotEmpty)const Padding(padding:EdgeInsets.symmetric(horizontal:5),child:Text('|',style:TextStyle(color:Color(0xFF8090A8),fontSize:20,fontWeight:FontWeight.w300))),if(card.isNotEmpty)CatalogLogo(label:card),if(card.isNotEmpty&&n.isNotEmpty)const Padding(padding:EdgeInsets.symmetric(horizontal:5),child:Text('|',style:TextStyle(color:Color(0xFF8090A8),fontSize:20,fontWeight:FontWeight.w300))),if(n.isNotEmpty)CatalogLogo(label:n)]))"
if detail_old in s:
    s = s.replace(detail_old, detail_new)
    print('detail bank | card | network separators applied')

p.write_text(s, encoding='utf-8')
