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
    if quote is not None:
        if esc:
            esc = False
        elif ch == '\\':
            esc = True
        elif ch == quote:
            quote = None
    elif ch in ("'", '"'):
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
    const names = <String>['Restoran', 'Market', 'Akaryakıt', 'Seyahat', 'Giyim', 'Ev & Yaşam', 'Tümü', 'Elektronik'];
    const icons = <String>['🍴', '🛒', '⛽', '🧳', '👕', '🛋️', '▦', '📱'];

    return Scaffold(
      backgroundColor: const Color(0xFF081120),
      body: FutureBuilder<List<Map<String, dynamic>>>(
        future: future,
        builder: (context, snapshot) {
          var rows = snapshot.data ?? <Map<String, dynamic>>[];
          final query = _norm(search.text);
          if (query.isNotEmpty) {
            rows = rows.where((c) {
              final text = _norm('${c['title'] ?? ''} ${c['merchant'] ?? ''} ${c['description'] ?? ''} ${c['campaign_text'] ?? ''}');
              return text.contains(query);
            }).toList();
          }
          if (category.isNotEmpty) {
            rows = rows.where((c) => '${c['category'] ?? ''}' == category || campaignSection(c) == category).toList();
          }
          if (showFavoritesOnly) {
            rows = rows.where((c) => favoriteIds.contains(campaignId(c))).toList();
          }
          if (widget.mode == 'matched') {
            rows = rows.where((c) => widget.cards.any((card) => cardMatches(c, card))).toList();
          }

          final children = <Widget>[];
          for (final c in rows) {
            children.add(SmartCampaignCard(
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

          return RefreshIndicator(
            onRefresh: () async {
              setState(() { future = fetchCampaigns(); });
              await future;
            },
            child: ListView(
              padding: const EdgeInsets.fromLTRB(16, 14, 16, 100),
              children: <Widget>[
                Row(
                  children: <Widget>[
                    const Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: <Widget>[
                          Text('Kart Kampanya', style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.w900)),
                          SizedBox(height: 3),
                          Text('Tüm banka kampanyaları tek yerde!', style: TextStyle(color: Color(0xFFAAB6C8), fontSize: 12)),
                        ],
                      ),
                    ),
                    IconButton(onPressed: () { setState(() { future = fetchCampaigns(); }); }, icon: const Icon(Icons.refresh, color: Colors.white)),
                  ],
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: search,
                  onChanged: (_) { setState(() {}); },
                  decoration: const InputDecoration(
                    prefixIcon: Icon(Icons.search, color: Color(0xFF9AA8BD)),
                    hintText: 'Kampanya ara...',
                  ),
                ),
                const SizedBox(height: 14),
                SizedBox(
                  height: 72,
                  child: ListView.builder(
                    scrollDirection: Axis.horizontal,
                    itemCount: names.length,
                    itemBuilder: (context, index) {
                      final name = names[index];
                      final selected = name == 'Tümü' ? category.isEmpty : category == name;
                      return InkWell(
                        onTap: () { setState(() { category = name == 'Tümü' ? '' : name; }); },
                        child: Container(
                          width: 94,
                          margin: const EdgeInsets.only(right: 9),
                          decoration: BoxDecoration(
                            color: selected ? const Color(0xFF6847F4) : const Color(0xFF0D1A2D),
                            borderRadius: BorderRadius.circular(16),
                            border: Border.all(color: selected ? const Color(0xFF8066FF) : const Color(0xFF294361)),
                          ),
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: <Widget>[
                              Text(icons[index], style: const TextStyle(fontSize: 21)),
                              const SizedBox(height: 4),
                              Text(name, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.w800)),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),
                const SizedBox(height: 14),
                if (snapshot.connectionState == ConnectionState.waiting)
                  const SizedBox(height: 240, child: Center(child: CircularProgressIndicator()))
                else if (snapshot.hasError)
                  const Padding(padding: EdgeInsets.all(28), child: Text('Kampanyalar yüklenemedi.', textAlign: TextAlign.center, style: TextStyle(color: Color(0xFFB8C2D2))))
                else if (children.isEmpty)
                  const Padding(padding: EdgeInsets.all(28), child: Text('Bu filtreye uygun kampanya bulunamadı.', textAlign: TextAlign.center, style: TextStyle(color: Color(0xFFB8C2D2))))
                else
                  ...children,
              ],
            ),
          );
        },
      ),
    );
  }
'''

s = s[:start] + build + s[end:]
p.write_text(s, encoding='utf-8')
print('Final reference catalog builder simplified to syntax-safe Dart')