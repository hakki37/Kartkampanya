from pathlib import Path
import re

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

# FINAL REFERENCE V2: this pass is intentionally last. It reconstructs the
# authenticated catalog presentation instead of recoloring an older screen.

def replace_class(src, name, replacement):
    start = src.find('class ' + name)
    if start < 0:
        raise SystemExit(name + ' not found')
    brace = src.find('{', start)
    if brace < 0:
        raise SystemExit(name + ' opening brace not found')
    depth = 0
    quote = None
    esc = False
    i = brace
    while i < len(src):
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
        i += 1
    raise SystemExit(name + ' end not found')


def replace_build(src, state_name, replacement):
    state = src.find('class ' + state_name)
    if state < 0:
        raise SystemExit(state_name + ' not found')
    start = src.find('  @override\n  Widget build(BuildContext context) {', state)
    if start < 0:
        raise SystemExit(state_name + ' build not found')
    brace = src.find('{', start)
    depth = 0
    quote = None
    esc = False
    i = brace
    while i < len(src):
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
        i += 1
    raise SystemExit(state_name + ' build end not found')

# Catalog palette: dark navy canvas, readable white foregrounds, purple
# selection, and restrained blue borders. Login keeps its own light colors.
theme_start = s.find('      theme: ThemeData(')
theme_end = s.find('      home:', theme_start)
if theme_start < 0 or theme_end < 0:
    raise SystemExit('Theme boundary not found')
theme = '''      theme: ThemeData(\n        useMaterial3: true,\n        brightness: Brightness.dark,\n        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF6D4AFF), brightness: Brightness.dark),\n        scaffoldBackgroundColor: const Color(0xFF081120),\n        appBarTheme: const AppBarTheme(elevation: 0, scrolledUnderElevation: 0, backgroundColor: Color(0xFF081120), foregroundColor: Colors.white),\n        inputDecorationTheme: const InputDecorationTheme(\n          filled: true, fillColor: Color(0xFF0E1A2D),\n          border: OutlineInputBorder(borderRadius: BorderRadius.all(Radius.circular(18)), borderSide: BorderSide(color: Color(0xFF29415F))),\n          enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.all(Radius.circular(18)), borderSide: BorderSide(color: Color(0xFF29415F))),\n          focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.all(Radius.circular(18)), borderSide: BorderSide(color: Color(0xFF7657FF), width: 1.5)),\n          hintStyle: TextStyle(color: Color(0xFF8291AA)),\n        ),\n        cardTheme: CardThemeData(elevation: 0, margin: EdgeInsets.zero, color: Color(0xFF0D1728), surfaceTintColor: Colors.transparent),\n      ),\n'''
s = s[:theme_start] + theme + s[theme_end:]

card = r'''class SmartCampaignCard extends StatelessWidget {
  final Map<String, dynamic> campaign;
  final bool isFavorite, isCompared, showAllCampaigns, expiringSoon;
  final int daysRemaining, requiredSteps, completedSteps;
  final VoidCallback onFavorite, onCompare;
  final Future<void> Function(String url) onOpenUrl;
  final ValueChanged<int> onProgressChange;
  const SmartCampaignCard({super.key, required this.campaign, required this.isFavorite, required this.isCompared, required this.showAllCampaigns, required this.expiringSoon, required this.daysRemaining, required this.onFavorite, required this.onCompare, required this.onOpenUrl, required this.requiredSteps, required this.completedSteps, required this.onProgressChange});

  String clean(dynamic value) {
    if (value == null) return '';
    var x = decodeHtmlEntities('$value').replaceAll(RegExp(r'<[^>]*>'), ' ').replaceAll(RegExp(r'\s+'), ' ').trim();
    x = x.replaceAll(RegExp(r'^(-->)+'), '').trim();
    return x;
  }
  String first(List<String> keys) { for (final k in keys) { final v = clean(campaign[k]); if (v.isNotEmpty) return v; } return ''; }
  String merchantDomain(String value) {
    final m = _norm(value);
    const d = {'migros':'migros.com.tr','carrefour':'carrefoursa.com','trendyol':'trendyol.com','hepsiburada':'hepsiburada.com','amazon':'amazon.com.tr','a101':'a101.com.tr','bim':'bim.com.tr','sok':'sokmarket.com.tr','opet':'opet.com.tr','shell':'shell.com.tr','petrol ofisi':'petrolofisi.com.tr','mediamarkt':'mediamarkt.com.tr','teknosa':'teknosa.com','boyner':'boyner.com.tr','mavi':'mavi.com','ikea':'ikea.com.tr','ispark':'ispark.istanbul'};
    for (final e in d.entries) { if (m.contains(e.key)) return e.value; }
    return '';
  }
  String bankDomain(String value) {
    final m = _norm(value);
    const d = {'akbank':'akbank.com','axess':'axess.com.tr','garanti':'garantibbva.com.tr','bonus':'bonus.com.tr','vakifbank':'vakifbank.com.tr','world':'worldcard.com.tr','yapi kredi':'worldcard.com.tr','qnb':'qnb.com.tr','cardfinans':'cardfinans.com.tr','teb':'teb.com.tr','cepteteb':'teb.com.tr','hsbc':'hsbc.com','isbank':'isbank.com.tr','maximum':'maximum.com.tr','ziraat':'ziraatbank.com.tr','denizbank':'denizbank.com','enpara':'enpara.com','kuveytturk':'kuveytturk.com.tr','ing':'ing.com.tr'};
    for (final e in d.entries) { if (m.contains(e.key)) return e.value; }
    return '';
  }
  String logo(String domain) => domain.isEmpty ? '' : 'https://cdn.brandfetch.io/$domain/w/600/h/180/logo';

  Widget logoBox(String value) {
    final d = bankDomain(value);
    return Container(width: 84, height: 40, padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 5), decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(9)), alignment: Alignment.center, child: d.isEmpty ? Text(value, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(color: Color(0xFF172033), fontSize: 10, fontWeight: FontWeight.w900)) : Image.network(logo(d), fit: BoxFit.contain, filterQuality: FilterQuality.high, errorBuilder: (_, __, ___) => Text(value, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(color: Color(0xFF172033), fontSize: 10, fontWeight: FontWeight.w900))));
  }

  @override
  Widget build(BuildContext context) {
    final title = first(['title','name']);
    final merchant = first(['merchant','brand']);
    final category = first(['category']).isNotEmpty ? first(['category']) : campaignSection(campaign);
    final bank = first(['bank_name','bank','card_bank']);
    final description = first(['description','campaign_text','summary','details','content']);
    final benefit = first(['benefit','benefit_label','advantage_label','reward','reward_amount','cashback','discount']);
    final minSpend = first(['min_spend','minimum_spend']);
    final userCards = (campaign['_cards'] as List?)?.whereType<UserCard>().toList() ?? <UserCard>[];
    final labels = <String>[];
    for (final c in userCards) { for (final v in [bank.isNotEmpty ? bank : c.bank, c.card, c.network]) { if (v.trim().isNotEmpty && !labels.contains(v.trim())) labels.add(v.trim()); } }

    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(color: const Color(0xFF0D1728), borderRadius: BorderRadius.circular(22), border: Border.all(color: const Color(0xFF243A57), width: 1.15)),
      child: InkWell(
        borderRadius: BorderRadius.circular(18),
        onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => CampaignDetailPage(campaign: campaign))),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Container(width: 82, height: 64, padding: const EdgeInsets.all(7), decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(12)), alignment: Alignment.center, child: merchantDomain(merchant).isNotEmpty ? Image.network(logo(merchantDomain(merchant)), fit: BoxFit.contain, errorBuilder: (_, __, ___) => Text(merchant.isEmpty ? 'KAMPANYA' : merchant, maxLines: 2, overflow: TextOverflow.ellipsis, textAlign: TextAlign.center, style: const TextStyle(color: Color(0xFF172033), fontWeight: FontWeight.w900, fontSize: 11))) : Text(merchant.isEmpty ? 'KAMPANYA' : merchant, maxLines: 2, overflow: TextOverflow.ellipsis, textAlign: TextAlign.center, style: const TextStyle(color: Color(0xFF172033), fontWeight: FontWeight.w900, fontSize: 11))),
            const SizedBox(width: 11),
            Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(title.isEmpty ? 'Kampanya' : title, maxLines: 3, overflow: TextOverflow.ellipsis, style: const TextStyle(color: Colors.white, fontSize: 16, height: 1.16, fontWeight: FontWeight.w900)),
              if (merchant.isNotEmpty) ...[const SizedBox(height: 4), Text(merchant, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(color: Color(0xFFAAB6C8), fontSize: 12, fontWeight: FontWeight.w600))],
              if (benefit.isNotEmpty) ...[const SizedBox(height: 7), Text('💰 Tahmini avantaj: $benefit', maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(color: Color(0xFFFFD166), fontSize: 12.5, fontWeight: FontWeight.w900))],
            ])),
            Column(children: [IconButton(visualDensity: VisualDensity.compact, padding: EdgeInsets.zero, constraints: const BoxConstraints(minWidth: 32,minHeight: 32), onPressed: onFavorite, icon: Icon(isFavorite ? Icons.star_rounded : Icons.star_border_rounded, color: isFavorite ? const Color(0xFFC5B5FF) : const Color(0xFF7E8CA3), size: 27)), IconButton(visualDensity: VisualDensity.compact, padding: EdgeInsets.zero, constraints: const BoxConstraints(minWidth: 32,minHeight: 32), onPressed: onCompare, icon: Icon(Icons.compare_arrows_rounded, color: isCompared ? const Color(0xFFC5B5FF) : const Color(0xFF7E8CA3), size: 25))]),
          ]),
          if (labels.isNotEmpty) ...[const SizedBox(height: 11), SizedBox(height: 40, child: ListView.separated(scrollDirection: Axis.horizontal, itemCount: labels.length > 4 ? 4 : labels.length, separatorBuilder: (_, __) => const SizedBox(width: 7), itemBuilder: (_, i) => logoBox(labels[i])))],
          if (description.isNotEmpty) ...[const SizedBox(height: 9), Text(description, maxLines: 2, overflow: TextOverflow.ellipsis, style: const TextStyle(color: Color(0xFFAAB6C8), fontSize: 12.5, height: 1.25))],
          if (minSpend.isNotEmpty) ...[const SizedBox(height: 6), Text('Minimum harcama: $minSpend', maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(color: Color(0xFFDCE5F2), fontSize: 12, fontWeight: FontWeight.w700))],
          const SizedBox(height: 10),
          Row(children: [Container(constraints: const BoxConstraints(maxWidth: 145), padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6), decoration: BoxDecoration(color: const Color(0xFF172943), borderRadius: BorderRadius.circular(15), border: Border.all(color: const Color(0xFF2A4668))), child: Text(category, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(color: Color(0xFFD6CCFF), fontSize: 11, fontWeight: FontWeight.w800))), const SizedBox(width: 8), Expanded(child: Text(userCards.isNotEmpty ? 'Kayıtlı kartlarınla eşleşiyor' : 'Kayıtlı kartlarınla eşleşmiyor', maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(color: Color(0xFF7F8DA4), fontSize: 10.5, fontWeight: FontWeight.w600))), const Icon(Icons.chevron_right_rounded, color: Color(0xFF93A1B6), size: 23)]),
        ]),
      ),
    );
  }
}
'''
s = replace_class(s, 'SmartCampaignCard', card)

build = r'''  @override
  Widget build(BuildContext context) {
    final quickItems = showAllQuickCategories ? quick : quick.take(8).toList();
    return Scaffold(
      backgroundColor: const Color(0xFF081120),
      body: FutureBuilder<List<Map<String, dynamic>>>(
        future: future,
        builder: (context, snapshot) {
          var rows = snapshot.data ?? <Map<String, dynamic>>[];
          if (search.text.trim().isNotEmpty) { final q = _norm(search.text); rows = rows.where((c) => _norm([c['title'],c['merchant'],c['category'],c['description'],c['campaign_text']].where((x)=>x!=null).join(' ')).contains(q)).toList(); }
          if (category.isNotEmpty) rows = rows.where((c) => campaignSection(c) == category || '${c['category'] ?? ''}' == category).toList();
          if (showFavoritesOnly) rows = rows.where((c) => favoriteIds.contains(campaignId(c))).toList();
          if (widget.mode == 'matched') rows = rows.where((c) => widget.cards.any((card) => cardMatches(c, card))).toList();
          return RefreshIndicator(
            color: const Color(0xFF7657FF), backgroundColor: const Color(0xFF0D1728),
            onRefresh: () async { setState(() => future = fetchCampaigns()); await future; },
            child: ListView(padding: const EdgeInsets.fromLTRB(16, 14, 16, 92), children: [
              Row(children: [Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [const Text('Kart Kampanya', style: TextStyle(color: Colors.white, fontSize: 25, fontWeight: FontWeight.w900)), const SizedBox(height: 3), const Text('Tüm banka kampanyaları tek yerde!', style: TextStyle(color: Color(0xFFAAB6C8), fontSize: 12.5, fontWeight: FontWeight.w500))])), IconButton(onPressed: () => setState(() => future = fetchCampaigns()), icon: const Icon(Icons.refresh_rounded, color: Colors.white, size: 27)), IconButton(onPressed: () => Supabase.instance.client.auth.signOut(), icon: const Icon(Icons.logout_rounded, color: Colors.white, size: 26))]),
              const SizedBox(height: 14),
              TextField(controller: search, onChanged: (_) => setState(() {}), onSubmitted: (_) => searchNow(), decoration: const InputDecoration(prefixIcon: Icon(Icons.search_rounded, color: Color(0xFFAAB6C8)), hintText: 'Örn. Trendyol 3000 TL', suffixIcon: Icon(Icons.arrow_forward_rounded, color: Color(0xFFAAB6C8)))),
              const SizedBox(height: 15),
              GridView.builder(shrinkWrap: true, physics: const NeverScrollableScrollPhysics(), itemCount: quickItems.length, gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 4, crossAxisSpacing: 9, mainAxisSpacing: 9, childAspectRatio: .98), itemBuilder: (_, i) { final item = quickItems[i]; final selected = category == item[1]; return InkWell(onTap: () => setState(() => category = selected ? '' : item[1]), borderRadius: BorderRadius.circular(18), child: Container(decoration: BoxDecoration(color: selected ? const Color(0xFF6245EF) : const Color(0xFF0E1B30), borderRadius: BorderRadius.circular(18), border: Border.all(color: selected ? const Color(0xFF866FFF) : const Color(0xFF294664))), child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [Text(item[0], style: const TextStyle(fontSize: 25)), const SizedBox(height: 5), Text(item[1], maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(color: Colors.white, fontSize: 11.5, fontWeight: FontWeight.w800))]))); }),
              const SizedBox(height: 14),
              SingleChildScrollView(scrollDirection: Axis.horizontal, child: Row(children: [_catalogFilter('Tümü', !showFavoritesOnly && category.isEmpty, () => setState(() { category=''; showFavoritesOnly=false; })), _catalogFilter('✦  Bana Uygun', widget.mode == 'matched', () => setState(() { category=''; showFavoritesOnly=false; })), _catalogFilter('★  Favoriler', showFavoritesOnly, () => setState(() => showFavoritesOnly=!showFavoritesOnly)), _catalogFilter('Son Eklenen', false, () => setState(() => showAllCampaigns=true))])),
              const SizedBox(height: 20),
              if (snapshot.connectionState == ConnectionState.waiting) const Center(child: Padding(padding: EdgeInsets.all(35), child: CircularProgressIndicator(color: Color(0xFF7657FF))))
              else if (snapshot.hasError) const Center(child: Padding(padding: EdgeInsets.all(30), child: Text('Kampanyalar yüklenemedi. Aşağı çekerek tekrar dene.', textAlign: TextAlign.center, style: TextStyle(color: Color(0xFFB7C2D4))))
              else if (rows.isEmpty) const Center(child: Padding(padding: EdgeInsets.all(30), child: Text('Bu filtreye uygun kampanya bulunamadı.', textAlign: TextAlign.center, style: TextStyle(color: Color(0xFFB7C2D4))))
              else ...rows.map((c) => SmartCampaignCard(campaign:c,isFavorite:favoriteIds.contains(campaignId(c)),isCompared:compareIds.contains(campaignId(c)),showAllCampaigns:showAllCampaigns,expiringSoon:isExpiringSoon(c),daysRemaining:daysLeft(c),onFavorite:()=>toggleFavorite(c),onCompare:()=>toggleCompare(c),onOpenUrl:openCampaignUrl,requiredSteps:requiredSteps(c),completedSteps:campaignProgress[campaignId(c)]??0,onProgressChange:(_){}})),
            ]),
          );
        },
      ),
    );
  }

  Widget _catalogFilter(String label, bool selected, VoidCallback onTap) => Padding(padding: const EdgeInsets.only(right:8), child: InkWell(onTap:onTap,borderRadius:BorderRadius.circular(14),child:Container(padding:const EdgeInsets.symmetric(horizontal:13,vertical:9),decoration:BoxDecoration(color:selected?const Color(0xFF6245EF):const Color(0xFF101D31),borderRadius:BorderRadius.circular(14),border:Border.all(color:selected?const Color(0xFF806AFF):const Color(0xFF2A415D))),child:Text(label,style:TextStyle(color:selected?Colors.white:const Color(0xFFB8C3D4),fontSize:11.5,fontWeight:FontWeight.w800)))));
'''
s = replace_build(s, '_CampaignsPageState', build)

# Kill legacy light catalog backgrounds only inside CampaignsPage; login is outside.
s = re.sub(r'(class CampaignsPage extends StatefulWidget \{.*?)(?=class )', lambda m: m.group(1).replace('Color(0xFFF8F7FC)','Color(0xFF081120)').replace('Color(0xFFF7F5FC)','Color(0xFF081120)'), s, flags=re.S)

p.write_text(s, encoding='utf-8')
print('Final dark reference V2 locked')
