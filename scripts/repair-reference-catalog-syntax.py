from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

state = s.find('class _CampaignsPageState')
if state < 0:
    raise SystemExit('_CampaignsPageState not found')
start = s.find('  @override\n  Widget build(BuildContext context) {', state)
if start < 0:
    raise SystemExit('campaign build not found')
brace = s.find('{', start)
depth = 0
quote = None
esc = False
end = None
for i in range(brace, len(s)):
    ch = s[i]
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
            end = i + 1
            break
if end is None:
    raise SystemExit('campaign build end not found')

build = r'''  @override
  Widget build(BuildContext context) {
    const categories = <List<String>>[
      ['🍴', 'Restoran'], ['🛒', 'Market'], ['⛽', 'Akaryakıt'],
      ['🧳', 'Seyahat'], ['👕', 'Giyim'], ['🛋️', 'Ev & Yaşam'],
      ['▦', 'Tümü'], ['📱', 'Elektronik'],
    ];

    Widget categoryTile(String icon, String label) {
      final selected = label == 'Tümü' ? category.isEmpty : category == label;
      return InkWell(
        onTap: () => setState(() => category = label == 'Tümü' ? '' : label),
        borderRadius: BorderRadius.circular(16),
        child: Container(
          width: 94,
          height: 72,
          margin: const EdgeInsets.only(right: 9),
          decoration: BoxDecoration(
            color: selected ? const Color(0xFF6847F4) : const Color(0xFF0D1A2D),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: selected ? const Color(0xFF8066FF) : const Color(0xFF294361)),
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(icon, style: const TextStyle(fontSize: 22)),
              const SizedBox(height: 4),
              Text(label, maxLines: 1, overflow: TextOverflow.ellipsis,
                style: const TextStyle(color: Colors.white, fontSize: 10.5, fontWeight: FontWeight.w800)),
            ],
          ),
        ),
      );
    }

    return Scaffold(
      backgroundColor: const Color(0xFF081120),
      body: FutureBuilder<List<Map<String, dynamic>>>(
        future: future,
        builder: (context, snapshot) {
          var rows = snapshot.data ?? <Map<String, dynamic>>[];
          final q = _norm(search.text);
          if (q.isNotEmpty) {
            rows = rows.where((c) => _norm([
              c['title'], c['merchant'], c['category'], c['description'], c['campaign_text']
            ].where((x) => x != null).join(' ')).contains(q)).toList();
          }
          if (category.isNotEmpty) {
            rows = rows.where((c) => campaignSection(c) == category || '${c['category'] ?? ''}' == category).toList();
          }
          if (showFavoritesOnly) {
            rows = rows.where((c) => favoriteIds.contains(campaignId(c))).toList();
          }
          if (widget.mode == 'matched') {
            rows = rows.where((c) => widget.cards.any((card) => cardMatches(c, card))).toList();
          }

          final content = <Widget>[];
          final groups = <String, List<Map<String, dynamic>>>{};
          for (final row in rows) {
            final key = campaignSection(row).isEmpty ? 'Diğer' : campaignSection(row);
            groups.putIfAbsent(key, () => <Map<String, dynamic>>[]).add(row);
          }
          for (final entry in groups.entries) {
            content.add(Padding(
              padding: const EdgeInsets.only(bottom: 7),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(child: Text('${emoji(entry.key)}  ${entry.key}', style: const TextStyle(color: Colors.white, fontSize: 21, fontWeight: FontWeight.w900))),
                      Text('${entry.value.length} kampanya', style: const TextStyle(color: Color(0xFFAAB6C8), fontSize: 11, fontWeight: FontWeight.w700)),
                    ],
                  ),
                  const SizedBox(height: 9),
                ],
              ),
            ));
            for (final c in entry.value) {
              content.add(SmartCampaignCard(
                campaign: c,
                isFavorite: favoriteIds.contains(campaignId(c)),
                isCompared: compareIds.contains(campaignId(c)),
                showAllCampaigns: showAllCampaigns,
                expiringSoon: isExpiringSoon(c),
                daysRemaining: daysLeft(c),
                onFavorite: () => toggleFavorite(c),
                onCompare: () => toggleCompare(c),
                onOpenUrl: openCampaignUrl,
                requiredSteps: requiredSteps(c),
                completedSteps: campaignProgress[campaignId(c)] ?? 0,
                onProgressChange: (v) => setState(() => campaignProgress[campaignId(c)] = v),
              ));
            }
          }

          Widget stateMessage(String text) => Padding(
            padding: const EdgeInsets.all(28),
            child: Text(text, textAlign: TextAlign.center, style: const TextStyle(color: Color(0xFFB8C2D2))),
          );

          return RefreshIndicator(
            color: const Color(0xFF7956FF),
            backgroundColor: const Color(0xFF0D1728),
            onRefresh: () async {
              setState(() => future = fetchCampaigns());
              await future;
            },
            child: ListView(
              padding: const EdgeInsets.fromLTRB(16, 14, 16, 94),
              children: [
                Row(
                  children: [
                    Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: const [
                      Text('Kart Kampanya', style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.w900)),
                      SizedBox(height: 2),
                      Text('Tüm banka kampanyaları tek yerde!', style: TextStyle(color: Color(0xFFAAB6C8), fontSize: 12, fontWeight: FontWeight.w600)),
                    ])),
                    IconButton(onPressed: () => setState(() => future = fetchCampaigns()), icon: const Icon(Icons.refresh_rounded, color: Colors.white, size: 26)),
                  ],
                ),
                const SizedBox(height: 13),
                TextField(
                  controller: search,
                  onChanged: (_) => setState(() {}),
                  onSubmitted: (_) => searchNow(),
                  decoration: const InputDecoration(
                    prefixIcon: Icon(Icons.search_rounded, color: Color(0xFF9AA8BD)),
                    hintText: 'Örn. Trendyol 3000 TL',
                    suffixIcon: Icon(Icons.arrow_forward_rounded, color: Color(0xFF9AA8BD)),
                  ),
                ),
                const SizedBox(height: 15),
                SizedBox(height: 72, child: ListView(scrollDirection: Axis.horizontal, children: categories.map((x) => categoryTile(x[0], x[1])).toList())),
                const SizedBox(height: 13),
                Wrap(spacing: 9, runSpacing: 8, children: [
                  _refFilter('★', 'Favoriler', showFavoritesOnly, () => setState(() => showFavoritesOnly = !showFavoritesOnly)),
                  _refFilter('▣', 'Kartıma uygun', widget.mode == 'matched', () => setState(() {})),
                ]),
                const SizedBox(height: 22),
                if (snapshot.connectionState == ConnectionState.waiting)
                  const SizedBox(height: 260, child: Center(child: CircularProgressIndicator()))
                else if (snapshot.hasError)
                  stateMessage('Kampanyalar yüklenemedi. Aşağı çekerek tekrar dene.')
                else if (groups.isEmpty)
                  stateMessage('Bu filtreye uygun kampanya bulunamadı.')
                else
                  ...content,
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _refFilter(String icon, String label, bool selected, VoidCallback onTap) => InkWell(
    onTap: onTap,
    borderRadius: BorderRadius.circular(12),
    child: Container(
      padding: const EdgeInsets.symmetric(horizontal: 13, vertical: 9),
      decoration: BoxDecoration(
        color: selected ? const Color(0xFF20163D) : const Color(0xFF111A29),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: selected ? const Color(0xFF7A5AFF) : const Color(0xFF3B4050)),
      ),
      child: Row(mainAxisSize: MainAxisSize.min, children: [
        Text(icon, style: const TextStyle(color: Color(0xFFC7B8FF), fontSize: 18, fontWeight: FontWeight.w900)),
        const SizedBox(width: 7),
        Text(label, style: const TextStyle(color: Color(0xFFE6EAF2), fontSize: 13, fontWeight: FontWeight.w800)),
      ]),
    ),
  );
'''

s = s[:start] + build + s[end:]
p.write_text(s, encoding='utf-8')
print('Final reference catalog syntax rebuilt with explicit widget list')
