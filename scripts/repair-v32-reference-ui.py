from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')


def replace_class(src, name, replacement):
    start = src.find('class ' + name)
    if start < 0:
        raise SystemExit(name + ' not found')
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
    raise SystemExit(name + ' end not found')


def replace_build(src, state_name, replacement):
    state = src.find('class ' + state_name)
    if state < 0:
        raise SystemExit(state_name + ' not found')
    start = src.find('Widget build(', state)
    if start < 0:
        raise SystemExit('build not found')
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
    raise SystemExit('build end not found')


campaign_build = r'''Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8F7FC),
      body: FutureBuilder<List<Map<String, dynamic>>>(
        future: future,
        builder: (context, snapshot) {
          var rows = snapshot.data ?? <Map<String, dynamic>>[];
          final q = search.text.trim();
          if (q.isNotEmpty) {
            final nq = _norm(q);
            rows = rows.where((c) => _norm([
              c['title'], c['merchant'], c['category'],
              c['description'], c['campaign_text'],
            ].where((x) => x != null).join(' ')).contains(nq)).toList();
          }
          if (category.isNotEmpty) {
            rows = rows.where((c) => campaignSection(c) == category || '${c['category'] ?? ''}' == category).toList();
          }
          if (showFavoritesOnly) {
            rows = rows.where((c) => favoriteIds.contains(campaignId(c))).toList();
          }
          if (widget.mode == 'matched' && widget.cards.isNotEmpty) {
            rows = rows.where((c) => widget.cards.any((card) => cardMatches(c, card))).toList();
          }
          return RefreshIndicator(
            onRefresh: () async {
              setState(() { future = fetchCampaigns(); });
              await future;
            },
            child: ListView(
              padding: const EdgeInsets.fromLTRB(16, 14, 16, 30),
              children: [
                Row(children: [
                  Container(width: 40, height: 40, decoration: BoxDecoration(gradient: const LinearGradient(colors: [Color(0xFF8B5CF6), Color(0xFF5B21B6)]), borderRadius: BorderRadius.circular(12)), child: const Icon(Icons.credit_card_rounded, color: Colors.white, size: 24)),
                  const SizedBox(width: 10),
                  const Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                    Text('Kart Kampanya', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900, color: Color(0xFF211D2D))),
                    Text('Tüm Banka Kampanyaları Tek Uygulamada', style: TextStyle(fontSize: 10, color: Color(0xFF777187))),
                  ])),
                  IconButton(onPressed: () => setState(() => future = fetchCampaigns()), icon: const Icon(Icons.refresh_rounded)),
                ]),
                const SizedBox(height: 12),
                TextField(controller: search, onChanged: (_) => setState(() {}), decoration: const InputDecoration(prefixIcon: Icon(Icons.search_rounded), hintText: 'Kampanya, marka veya kategori ara...')),
                const SizedBox(height: 11),
                SingleChildScrollView(scrollDirection: Axis.horizontal, child: Row(children: [
                  _pill('▦', 'Tümü', category.isEmpty && !showFavoritesOnly, () => setState(() => category = '')),
                  _pill('✧', 'Bana Uygun', widget.mode == 'matched', () {}),
                  _pill('♥', 'Favoriler', showFavoritesOnly, () => setState(() => showFavoritesOnly = !showFavoritesOnly)),
                  _pill('◷', 'Son Eklenen', false, () {}),
                ])),
                if (widget.mode == 'home') ...[
                  const SizedBox(height: 14),
                  Container(height: 145, padding: const EdgeInsets.all(17), decoration: BoxDecoration(gradient: const LinearGradient(colors: [Color(0xFF5424CF), Color(0xFF8C62F7)]), borderRadius: BorderRadius.circular(23)), child: Stack(children: [
                    const Positioned(right: 10, top: 2, child: Text('☀️', style: TextStyle(fontSize: 28))),
                    const Positioned(right: 12, bottom: 0, child: Text('🏖️', style: TextStyle(fontSize: 40))),
                    Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                      const Text('Yaz Fırsatları\nDevam Ediyor!', style: TextStyle(color: Colors.white, fontSize: 23, height: 1.0, fontWeight: FontWeight.w900)),
                      const SizedBox(height: 8),
                      const Text('Alışverişte kazancının\ntam zamanını yakala.', style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.w700)),
                      const Spacer(),
                      Container(padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 6), decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(13)), child: const Text('Tüm Kampanyalar  →', style: TextStyle(color: Color(0xFF5B21B6), fontSize: 10, fontWeight: FontWeight.w900))),
                    ]),
                  ])),
                  const SizedBox(height: 16),
                  const Text('Kategoriler', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: Color(0xFF211D2D))),
                  const SizedBox(height: 9),
                  GridView.count(shrinkWrap: true, physics: const NeverScrollableScrollPhysics(), crossAxisCount: 4, crossAxisSpacing: 8, mainAxisSpacing: 8, childAspectRatio: 1.02, children: const [
                    _HomeCat('⛽', 'Akaryakıt', 0xFFFFE4E8), _HomeCat('🛒', 'Market', 0xFFE1F8EF), _HomeCat('🍴', 'Restoran', 0xFFFFEAD8), _HomeCat('🛍', 'E-Ticaret', 0xFFE8E1FF),
                    _HomeCat('📱', 'Elektronik', 0xFFE1EEFF), _HomeCat('✈', 'Seyahat', 0xFFFFE8D8), _HomeCat('👕', 'Giyim', 0xFFFFE2F1), _HomeCat('⌂', 'Ev & Yaşam', 0xFFE3F4E9),
                  ]),
                ],
                if (snapshot.connectionState == ConnectionState.waiting) const Padding(padding: EdgeInsets.all(35), child: Center(child: CircularProgressIndicator())),
                if (snapshot.hasError) const Padding(padding: EdgeInsets.all(25), child: Text('Kampanyalar yüklenemedi.\nAşağı çekerek tekrar dene.', textAlign: TextAlign.center)),
                if (snapshot.connectionState != ConnectionState.waiting && !snapshot.hasError && rows.isEmpty) const Padding(padding: EdgeInsets.all(25), child: Text('Bu filtreye uygun kampanya bulunamadı.', textAlign: TextAlign.center)),
                if (snapshot.connectionState != ConnectionState.waiting && !snapshot.hasError) ...rows.map((c) => SmartCampaignCard(
                  campaign: c,
                  isFavorite: favoriteIds.contains(campaignId(c)),
                  isCompared: compareIds.contains(campaignId(c)),
                  showAllCampaigns: widget.mode != 'matched',
                  expiringSoon: isExpiringSoon(c),
                  daysRemaining: daysLeft(c),
                  onFavorite: () => toggleFavorite(c),
                  onCompare: () => toggleCompare(c),
                  onOpenUrl: openCampaignUrl,
                  requiredSteps: requiredSteps(c),
                  completedSteps: campaignProgress[campaignId(c)] ?? 0,
                  onProgressChange: (v) => setState(() => campaignProgress[campaignId(c)] = v),
                )),
              ],
            ),
          );
        },
      ),
    );
  }
'''

s = replace_build(s, '_CampaignsPageState', campaign_build)

categories = r'''class CategoriesPage extends StatelessWidget {
  const CategoriesPage({super.key});
  static const data = [
    ['▦', 'Tümü', 0xFFEDE7FF], ['⛽', 'Akaryakıt', 0xFFFFE4E8], ['🛒', 'Market', 0xFFE1F8EF],
    ['🍴', 'Restoran', 0xFFFFEAD8], ['🛍', 'E-Ticaret', 0xFFE8E1FF], ['👕', 'Giyim', 0xFFFFE2F1],
    ['📱', 'Elektronik', 0xFFE1EEFF], ['✈', 'Seyahat', 0xFFFFE8D8], ['🚗', 'Otomotiv', 0xFFE2F2EE],
    ['⌂', 'Ev & Yaşam', 0xFFE3F4E9], ['💄', 'Sağlık & Güzellik', 0xFFFFE1F0], ['🎮', 'Eğlence', 0xFFFFE5E5],
    ['🎓', 'Eğitim', 0xFFFFE5F2], ['🏦', 'Finans', 0xFFE2E9FF], ['✦', 'Diğer', 0xFFE9EBF4],
  ];
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8F7FC),
      appBar: AppBar(title: const Text('Kategoriler', style: TextStyle(fontWeight: FontWeight.w900)), actions: [IconButton(onPressed: () {}, icon: const Icon(Icons.search_rounded))]),
      body: GridView.builder(
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 30),
        itemCount: data.length,
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 3, crossAxisSpacing: 10, mainAxisSpacing: 10, childAspectRatio: 1.02),
        itemBuilder: (_, i) {
          final x = data[i];
          return Container(decoration: BoxDecoration(color: Color(x[2] as int), borderRadius: BorderRadius.circular(18)), child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [Text(x[0] as String, style: const TextStyle(fontSize: 25)), const SizedBox(height: 7), Padding(padding: const EdgeInsets.symmetric(horizontal: 4), child: Text(x[1] as String, maxLines: 2, textAlign: TextAlign.center, style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: Color(0xFF353146))))]));
        },
      ),
    );
  }
}
'''
s = replace_class(s, 'CategoriesPage', categories)
p.write_text(s, encoding='utf-8')
print('v32 reference UI parser repair applied')
