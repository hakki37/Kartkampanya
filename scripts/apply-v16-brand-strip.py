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

# Separate campaign tabs: home keeps the catalog feed, while the new
# "Kartıma Uygun" and "Tüm Kampanyalar" tabs have explicit behavior.
old_shell = '''    final pages = <Widget>[
      CampaignsPage(cards: cards),
      MyCardsPage(
        cards: cards,
        onAdd: addCard,
        onDelete: deleteCard,
      ),
      const CategoriesPage(),
    ];'''
new_shell = '''    final pages = <Widget>[
      CampaignsPage(cards: cards, mode: 'home'),
      CampaignsPage(cards: cards, mode: 'matched'),
      CampaignsPage(cards: cards, mode: 'all'),
      MyCardsPage(
        cards: cards,
        onAdd: addCard,
        onDelete: deleteCard,
      ),
      const CategoriesPage(),
    ];'''
if old_shell in s:
    s = s.replace(old_shell, new_shell, 1)
else:
    print('MainShell pages block not found')

old_nav = '''        destinations: const [
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
new_nav = '''        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home),
            label: 'Ana Sayfa',
          ),
          NavigationDestination(
            icon: Icon(Icons.auto_awesome_outlined),
            selectedIcon: Icon(Icons.auto_awesome),
            label: 'Kartıma Uygun',
          ),
          NavigationDestination(
            icon: Icon(Icons.apps_outlined),
            selectedIcon: Icon(Icons.apps),
            label: 'Tüm Kampanyalar',
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
if old_nav in s:
    s = s.replace(old_nav, new_nav, 1)
else:
    print('Navigation destinations block not found')

old_ctor = '''class CampaignsPage extends StatefulWidget {
  final List<UserCard> cards;

  const CampaignsPage({
    super.key,
    required this.cards,
  });'''
new_ctor = '''class CampaignsPage extends StatefulWidget {
  final List<UserCard> cards;
  final String mode; // home | matched | all

  const CampaignsPage({
    super.key,
    required this.cards,
    this.mode = 'home',
  });'''
if old_ctor in s:
    s = s.replace(old_ctor, new_ctor, 1)
else:
    print('CampaignsPage constructor block not found')

old_init = '''  void initState() {
    super.initState();
    future = fetchCampaigns();
    _loadUserState();
  }'''
new_init = '''  void initState() {
    super.initState();
    showAllCampaigns = widget.mode == 'all';
    future = fetchCampaigns();
    _loadUserState();
  }'''
if old_init in s:
    s = s.replace(old_init, new_init, 1)
else:
    print('CampaignsPage initState block not found')

old_match = '''      if (widget.cards.isNotEmpty &&
          matchingCards.isEmpty &&
          !showAllCampaigns) {
        continue;
      }'''
new_match = '''      // Dedicated tabs have strict, predictable semantics:
      // Kartıma Uygun = only campaigns matching at least one saved card.
      // Tüm Kampanyalar = never hide a campaign because of saved cards.
      if (widget.mode == 'matched' &&
          (widget.cards.isEmpty || matchingCards.isEmpty)) {
        continue;
      }

      if (widget.mode == 'home' &&
          widget.cards.isNotEmpty &&
          matchingCards.isEmpty &&
          !showAllCampaigns) {
        continue;
      }'''
if old_match in s:
    s = s.replace(old_match, new_match, 1)
else:
    print('card matching block not found')

old_title = '''        title: const Text(
          'Kart Kampanya',
          style: TextStyle(fontWeight: FontWeight.w800),
        ),'''
new_title = '''        title: Text(
          widget.mode == 'matched'
              ? 'Kartıma Uygun'
              : widget.mode == 'all'
                  ? 'Tüm Kampanyalar'
                  : 'Kart Kampanya',
          style: const TextStyle(fontWeight: FontWeight.w800),
        ),'''
if old_title in s:
    s = s.replace(old_title, new_title, 1)
else:
    print('Campaign app bar title block not found')

# Fix the visible v16 "0 TL" fallback. Percentage campaigns show their
# percentage, installment campaigns show installments, and free benefits
# do not pretend to be a zero-lira cash reward.
marker = "String _catalogBenefitText(Map<String, dynamic> campaign) {"
if marker not in s:
    helper = r'''String _catalogBenefitText(Map<String, dynamic> campaign) {
  final title = decodeHtmlEntities('${campaign['title'] ?? ''}');
  final text = _norm('${campaign['title'] ?? ''} ${campaign['campaign_text'] ?? ''} ${campaign['conditions'] ?? ''}');

  if (text.contains('ucretsiz') && text.contains('park')) return 'Ücretsiz park';

  final percent = RegExp(r'%\s*(\d+(?:[\.,]\d+)?)').firstMatch(text);
  if (percent != null) return '%${percent.group(1)!.replaceAll(',', '.')} indirim';

  final installment = RegExp(r'\b(\d{1,2})\s*taksit\b').firstMatch(text);
  if (installment != null) return '${installment.group(1)} taksit';

  final reward = double.tryParse('${campaign['reward_amount'] ?? 0}') ?? 0;
  final max = double.tryParse('${campaign['max_reward'] ?? 0}') ?? 0;
  final value = max > 0 ? max : reward;
  if (value > 0) return '${value.toStringAsFixed(0)} TL';

  if (title.toLowerCase().contains('ücretsiz')) return 'Ücretsiz';
  return 'Detaylar için kampanyaya bak';
}
'''
    insert_at = s.find('class SmartCampaignCard extends StatelessWidget {')
    if insert_at >= 0:
        s = s[:insert_at] + helper + '\n' + s[insert_at:]
    else:
        print('SmartCampaignCard marker not found for benefit helper')

old_benefit = "Padding(padding: const EdgeInsets.only(top: 8), child: Text('💰 Tahmini avantaj: ${hasMoney ? '${(reward as num).toDouble().toStringAsFixed(0)} TL' : installment != null ? '$installment taksit' : '0 TL'}', style: TextStyle(fontWeight: FontWeight.w800, color: hasMoney || installment != null ? Colors.amber : null))),"
new_benefit = "Padding(padding: const EdgeInsets.only(top: 8), child: Text('💰 Tahmini avantaj: ${_catalogBenefitText(campaign)}', style: const TextStyle(fontWeight: FontWeight.w800, color: Colors.amber))),"
if old_benefit in s:
    s = s.replace(old_benefit, new_benefit)
else:
    print('v16 benefit widget not found; leaving existing benefit renderer')

p.write_text(s, encoding='utf-8')
