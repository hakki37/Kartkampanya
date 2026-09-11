from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

# FINAL catalog pass: earlier scripts may alter colors/layout, so this pass
# restores the reference presentation last while preserving app behavior.

def replace_class(src, name, replacement):
    marker = f'class {name}'
    start = src.find(marker)
    if start < 0:
        raise SystemExit(f'{name} not found')
    brace = src.find('{', start)
    if brace < 0:
        raise SystemExit(f'{name} opening brace not found')
    depth = 0
    for i in range(brace, len(src)):
        if src[i] == '{':
            depth += 1
        elif src[i] == '}':
            depth -= 1
            if depth == 0:
                return src[:start] + replacement + src[i + 1:]
    raise SystemExit(f'{name} end not found')

# ---------- Theme ----------
theme_start = s.find('      theme: ThemeData(')
theme_end = s.find('      home:', theme_start)
if theme_start < 0 or theme_end < 0:
    raise SystemExit('App theme boundary not found')
theme = s[theme_start:theme_end]
theme = theme.replace('brightness: Brightness.light,', 'brightness: Brightness.dark,', 1)
theme = theme.replace('scaffoldBackgroundColor: const Color(0xFFF7F5FC),', 'scaffoldBackgroundColor: const Color(0xFF081120),', 1)
theme = theme.replace('backgroundColor: const Color(0xFFF7F5FC),', 'backgroundColor: const Color(0xFF081120),', 1)
theme = theme.replace('foregroundColor: Color(0xFF211B2D),', 'foregroundColor: Colors.white,', 1)
s = s[:theme_start] + theme + s[theme_end:]

# ---------- Campaign card ----------
card = r'''class SmartCampaignCard extends StatelessWidget {
  final Map<String, dynamic> campaign;
  final bool isFavorite, isCompared, showAllCampaigns, expiringSoon;
  final int daysRemaining, requiredSteps, completedSteps;
  final VoidCallback onFavorite, onCompare;
  final Future<void> Function(String url) onOpenUrl;
  final ValueChanged<int> onProgressChange;

  const SmartCampaignCard({
    super.key,
    required this.campaign,
    required this.isFavorite,
    required this.isCompared,
    required this.showAllCampaigns,
    required this.expiringSoon,
    required this.daysRemaining,
    required this.onFavorite,
    required this.onCompare,
    required this.onOpenUrl,
    required this.requiredSteps,
    required this.completedSteps,
    required this.onProgressChange,
  });

  String t(dynamic value) => value == null ? '' : '$value'.trim();

  String _merchantDomain(String value) {
    final m = _norm(value);
    const domains = <String, String>{
      'migros': 'migros.com.tr',
      'carrefour': 'carrefoursa.com',
      'trendyol': 'trendyol.com',
      'hepsiburada': 'hepsiburada.com',
      'amazon': 'amazon.com.tr',
      'a101': 'a101.com.tr',
      'bim': 'bim.com.tr',
      'sok': 'sokmarket.com.tr',
      'opet': 'opet.com.tr',
      'shell': 'shell.com.tr',
      'petrol ofisi': 'petrolofisi.com.tr',
      'mediamarkt': 'mediamarkt.com.tr',
      'teknosa': 'teknosa.com',
      'vatan': 'vatanbilgisayar.com',
      'boyner': 'boyner.com.tr',
      'mavi': 'mavi.com',
      'ikea': 'ikea.com.tr',
      'thy': 'turkishairlines.com',
      'pegasus': 'flypgs.com',
      'ispark': 'ispark.istanbul',
    };
    for (final entry in domains.entries) {
      if (m.contains(entry.key)) return entry.value;
    }
    return '';
  }

  String _brandDomain(String value) {
    final m = _norm(value);
    const domains = <String, String>{
      'akbank': 'akbank.com',
      'axess': 'axess.com.tr',
      'garanti': 'garantibbva.com.tr',
      'bonus': 'bonus.com.tr',
      'vakifbank': 'vakifbank.com.tr',
      'world': 'worldcard.com.tr',
      'yapi kredi': 'worldcard.com.tr',
      'qnb': 'qnb.com.tr',
      'cardfinans': 'cardfinans.com.tr',
      'teb': 'teb.com.tr',
      'cepteteb': 'teb.com.tr',
      'hsbc': 'hsbc.com',
      'isbank': 'isbank.com.tr',
      'maximum': 'maximum.com.tr',
      'ziraat': 'ziraatbank.com.tr',
      'denizbank': 'denizbank.com',
      'enpara': 'enpara.com',
      'kuveytturk': 'kuveytturk.com.tr',
      'ing': 'ing.com.tr',
    };
    for (final entry in domains.entries) {
      if (m.contains(entry.key)) return entry.value;
    }
    return '';
  }

  String _logoUrl(String domain) =>
      domain.isEmpty ? '' : 'https://cdn.brandfetch.io/$domain/w/600/h/180/logo';

  Widget _logoBox(String value, {double width = 78, double height = 42}) {
    final domain = _brandDomain(value);
    return Container(
      width: width,
      height: height,
      padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 6),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: const Color(0xFF263B58)),
      ),
      alignment: Alignment.center,
      child: domain.isEmpty
          ? Text(
              value,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              textAlign: TextAlign.center,
              style: const TextStyle(
                color: Color(0xFF172033),
                fontSize: 10,
                fontWeight: FontWeight.w900,
              ),
            )
          : Image.network(
              _logoUrl(domain),
              fit: BoxFit.contain,
              filterQuality: FilterQuality.high,
              errorBuilder: (_, __, ___) => Text(
                value,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  color: Color(0xFF172033),
                  fontSize: 10,
                  fontWeight: FontWeight.w900,
                ),
              ),
            ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final merchant = t(campaign['merchant']);
    final title = t(campaign['title']).isEmpty ? 'Kampanya' : t(campaign['title']);
    final category = t(campaign['category']).isEmpty
        ? campaignSection(campaign)
        : t(campaign['category']);
    final benefit = t(campaign['benefit']);
    final minSpend = t(campaign['min_spend'] ?? campaign['minimum_spend']);
    final description = t(campaign['description']);
    final cards = (campaign['_cards'] as List?)?.whereType<UserCard>().toList() ?? <UserCard>[];

    final brands = <String>[];
    for (final card in cards) {
      for (final value in [card.bank, card.card, card.network]) {
        if (value.trim().isNotEmpty && !brands.contains(value.trim())) {
          brands.add(value.trim());
        }
      }
    }

    final merchantDomain = _merchantDomain(merchant);

    return InkWell(
      borderRadius: BorderRadius.circular(22),
      onTap: () => Navigator.of(context).push(
        MaterialPageRoute(builder: (_) => CampaignDetailPage(campaign: campaign)),
      ),
      child: Container(
        margin: const EdgeInsets.only(bottom: 14),
        padding: const EdgeInsets.fromLTRB(14, 14, 10, 14),
        decoration: BoxDecoration(
          color: const Color(0xFF0D1728),
          borderRadius: BorderRadius.circular(22),
          border: Border.all(color: const Color(0xFF233B5A), width: 1.1),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 86,
                  height: 66,
                  padding: const EdgeInsets.all(7),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(13),
                  ),
                  alignment: Alignment.center,
                  child: merchantDomain.isNotEmpty
                      ? Image.network(
                          _logoUrl(merchantDomain),
                          fit: BoxFit.contain,
                          filterQuality: FilterQuality.high,
                          errorBuilder: (_, __, ___) => Text(
                            merchant.isEmpty ? 'KAMPANYA' : merchant,
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                            textAlign: TextAlign.center,
                            style: const TextStyle(
                              color: Color(0xFF172033),
                              fontWeight: FontWeight.w900,
                              fontSize: 11,
                            ),
                          ),
                        )
                      : Text(
                          merchant.isEmpty ? 'KAMPANYA' : merchant,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          textAlign: TextAlign.center,
                          style: const TextStyle(
                            color: Color(0xFF172033),
                            fontWeight: FontWeight.w900,
                            fontSize: 11,
                          ),
                        ),
                ),
                const SizedBox(width: 11),
                Expanded(
                  child: Padding(
                    padding: const EdgeInsets.only(top: 2),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          title,
                          maxLines: 3,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 16,
                            height: 1.15,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                        if (merchant.isNotEmpty) ...[
                          const SizedBox(height: 4),
                          Text(
                            merchant,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(
                              color: Color(0xFFAAB6C8),
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                        if (benefit.isNotEmpty) ...[
                          const SizedBox(height: 7),
                          Text(
                            '💰 Tahmini avantaj: $benefit',
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(
                              color: Color(0xFFFFD166),
                              fontSize: 12.5,
                              fontWeight: FontWeight.w800,
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                ),
                Column(
                  children: [
                    IconButton(
                      visualDensity: VisualDensity.compact,
                      padding: EdgeInsets.zero,
                      constraints: const BoxConstraints(minWidth: 34, minHeight: 34),
                      onPressed: onFavorite,
                      icon: Icon(
                        isFavorite ? Icons.star_rounded : Icons.star_border_rounded,
                        color: isFavorite ? const Color(0xFFC5B5FF) : const Color(0xFF8390A6),
                        size: 27,
                      ),
                    ),
                    IconButton(
                      visualDensity: VisualDensity.compact,
                      padding: EdgeInsets.zero,
                      constraints: const BoxConstraints(minWidth: 34, minHeight: 34),
                      onPressed: onCompare,
                      icon: Icon(
                        Icons.compare_arrows_rounded,
                        color: isCompared ? const Color(0xFFC5B5FF) : const Color(0xFF8390A6),
                        size: 25,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            if (brands.isNotEmpty) ...[
              const SizedBox(height: 11),
              SizedBox(
                height: 42,
                child: ListView.separated(
                  scrollDirection: Axis.horizontal,
                  itemCount: brands.length > 4 ? 4 : brands.length,
                  separatorBuilder: (_, __) => const SizedBox(width: 7),
                  itemBuilder: (_, index) => _logoBox(brands[index]),
                ),
              ),
            ],
            if (minSpend.isNotEmpty) ...[
              const SizedBox(height: 9),
              Text(
                'Minimum harcama: $minSpend',
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  color: Color(0xFFDCE5F2),
                  fontSize: 12.5,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ],
            if (description.isNotEmpty) ...[
              const SizedBox(height: 7),
              Text(
                description,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  color: Color(0xFFAAB6C8),
                  fontSize: 12.5,
                  height: 1.25,
                ),
              ),
            ],
            const SizedBox(height: 10),
            Row(
              children: [
                Container(
                  constraints: const BoxConstraints(maxWidth: 150),
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  decoration: BoxDecoration(
                    color: const Color(0xFF16263E),
                    borderRadius: BorderRadius.circular(15),
                    border: Border.all(color: const Color(0xFF28415F)),
                  ),
                  child: Text(
                    category,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      color: Color(0xFFD4CBFF),
                      fontSize: 11,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    cards.isNotEmpty
                        ? 'Kartınla eşleşiyor'
                        : 'Kayıtlı kartlarınla eşleşmiyor',
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      color: Color(0xFF7E8BA1),
                      fontSize: 10.5,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
                const Icon(Icons.chevron_right_rounded, color: Color(0xFF9AA8BC), size: 23),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
'''
s = replace_class(s, 'SmartCampaignCard', card)

# ---------- CampaignsPage build ----------
state = s.find('class _CampaignsPageState extends State<CampaignsPage> {')
if state < 0:
    raise SystemExit('Campaign state not found')
start = s.find('  @override\n  Widget build(BuildContext context) {', state)
if start < 0:
    raise SystemExit('Campaign build not found')
brace = s.find('{', start)
depth = 0
end = -1
for i in range(brace, len(s)):
    if s[i] == '{':
        depth += 1
    elif s[i] == '}':
        depth -= 1
        if depth == 0:
            end = i + 1
            break
if end < 0:
    raise SystemExit('Campaign build end not found')

build = r'''  @override
  Widget build(BuildContext context) {
    final quickItems = showAllQuickCategories ? quick : quick.take(8).toList();

    return FutureBuilder<List<Map<String, dynamic>>>(
      future: future,
      builder: (context, snapshot) {
        var campaigns = snapshot.data ?? <Map<String, dynamic>>[];

        if (search.text.trim().isNotEmpty) {
          final q = _norm(search.text);
          campaigns = campaigns.where((campaign) {
            final text = _norm([
              campaign['title'],
              campaign['merchant'],
              campaign['category'],
              campaign['description'],
              campaign['campaign_text'],
            ].where((value) => value != null).join(' '));
            return text.contains(q);
          }).toList();
        }

        if (category.isNotEmpty) {
          campaigns = campaigns.where((campaign) {
            return campaignSection(campaign) == category ||
                '${campaign['category'] ?? ''}' == category;
          }).toList();
        }

        if (showFavoritesOnly) {
          campaigns = campaigns
              .where((campaign) => favoriteIds.contains(campaignId(campaign)))
              .toList();
        }

        if (widget.mode == 'matched') {
          campaigns = campaigns.where((campaign) {
            final matched = campaign['_cards'];
            return matched is List && matched.isNotEmpty;
          }).toList();
        }

        final groups = <String, List<Map<String, dynamic>>>{};
        for (final campaign in campaigns) {
          groups.putIfAbsent(campaignSection(campaign), () => []).add(campaign);
        }

        Widget chip(String label, bool selected, VoidCallback onTap) {
          return Padding(
            padding: const EdgeInsets.only(right: 8),
            child: InkWell(
              borderRadius: BorderRadius.circular(18),
              onTap: onTap,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 13, vertical: 9),
                decoration: BoxDecoration(
                  color: selected ? const Color(0xFF6848F2) : const Color(0xFF0D1A2D),
                  borderRadius: BorderRadius.circular(18),
                  border: Border.all(
                    color: selected ? const Color(0xFF8069FF) : const Color(0xFF243D5B),
                  ),
                ),
                child: Text(
                  label,
                  style: TextStyle(
                    color: selected ? Colors.white : const Color(0xFFB5C1D5),
                    fontSize: 12,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ),
            ),
          );
        }

        return RefreshIndicator(
          onRefresh: () async {
            setState(() => future = fetchCampaigns());
            await future;
          },
          color: const Color(0xFF7A5CFF),
          backgroundColor: const Color(0xFF0D1728),
          child: CustomScrollView(
            slivers: [
              SliverPadding(
                padding: const EdgeInsets.fromLTRB(16, 14, 16, 0),
                sliver: SliverToBoxAdapter(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Expanded(
                            child: Text(
                              'Kart Kampanya',
                              style: TextStyle(
                                color: Colors.white,
                                fontSize: 25,
                                fontWeight: FontWeight.w900,
                              ),
                            ),
                          ),
                          IconButton(
                            onPressed: () => setState(() => future = fetchCampaigns()),
                            icon: const Icon(Icons.refresh_rounded, color: Colors.white, size: 27),
                          ),
                          IconButton(
                            onPressed: () => Supabase.instance.client.auth.signOut(),
                            icon: const Icon(Icons.logout_rounded, color: Colors.white, size: 26),
                          ),
                        ],
                      ),
                      const SizedBox(height: 11),
                      Container(
                        height: 86,
                        width: double.infinity,
                        decoration: BoxDecoration(
                          gradient: const LinearGradient(
                            colors: [Color(0xFF5B3CEB), Color(0xFF825BFF)],
                          ),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        padding: const EdgeInsets.symmetric(horizontal: 18),
                        child: Row(
                          children: [
                            const Expanded(
                              child: Text(
                                'Kartına özel kampanyaları keşfet',
                                style: TextStyle(
                                  color: Colors.white,
                                  fontSize: 19,
                                  fontWeight: FontWeight.w900,
                                ),
                              ),
                            ),
                            Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: Colors.white24,
                                shape: BoxShape.circle,
                              ),
                              child: const Icon(Icons.credit_card_rounded, color: Colors.white, size: 30),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 13),
                      TextField(
                        controller: search,
                        onChanged: (_) => setState(() {}),
                        style: const TextStyle(color: Color(0xFF172033), fontWeight: FontWeight.w700),
                        decoration: InputDecoration(
                          hintText: 'Örn. Trendyol 3000 TL',
                          hintStyle: const TextStyle(color: Color(0xFF9AA3B2), fontWeight: FontWeight.w700),
                          prefixIcon: const Icon(Icons.search_rounded, color: Color(0xFFA7AFBC), size: 28),
                          suffixIcon: const Icon(Icons.arrow_forward_rounded, color: Color(0xFFADB4BF), size: 28),
                          filled: true,
                          fillColor: const Color(0xFFF8F9FB),
                          contentPadding: const EdgeInsets.symmetric(vertical: 16),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(18),
                            borderSide: BorderSide.none,
                          ),
                        ),
                      ),
                      const SizedBox(height: 18),
                      const Text(
                        'Hızlı kategoriler',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 18,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      const SizedBox(height: 10),
                      GridView.builder(
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        itemCount: quickItems.length,
                        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                          crossAxisCount: 4,
                          crossAxisSpacing: 9,
                          mainAxisSpacing: 9,
                          childAspectRatio: .96,
                        ),
                        itemBuilder: (_, index) {
                          final item = quickItems[index];
                          final selected = category == item[1];
                          return InkWell(
                            borderRadius: BorderRadius.circular(18),
                            onTap: () => setState(() => category = selected ? '' : item[1]),
                            child: Container(
                              decoration: BoxDecoration(
                                color: selected ? const Color(0xFF6846F4) : const Color(0xFF0E1B30),
                                borderRadius: BorderRadius.circular(18),
                                border: Border.all(
                                  color: selected ? const Color(0xFF8268FF) : const Color(0xFF29435F),
                                ),
                              ),
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Text(item[0], style: const TextStyle(fontSize: 24)),
                                  const SizedBox(height: 4),
                                  Padding(
                                    padding: const EdgeInsets.symmetric(horizontal: 3),
                                    child: Text(
                                      item[1],
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                      textAlign: TextAlign.center,
                                      style: const TextStyle(
                                        color: Colors.white,
                                        fontSize: 10.5,
                                        fontWeight: FontWeight.w800,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          );
                        },
                      ),
                      if (quick.length > 8)
                        Align(
                          alignment: Alignment.center,
                          child: TextButton(
                            onPressed: () => setState(() => showAllQuickCategories = !showAllQuickCategories),
                            child: Text(showAllQuickCategories ? 'Daha az' : 'Tüm kategoriler'),
                          ),
                        ),
                      const SizedBox(height: 8),
                      SingleChildScrollView(
                        scrollDirection: Axis.horizontal,
                        child: Row(
                          children: [
                            chip('Tümü', !showFavoritesOnly && category.isEmpty, () {
                              setState(() {
                                category = '';
                                showFavoritesOnly = false;
                              });
                            }),
                            chip('Bana Uygun', widget.mode == 'matched', () {
                              setState(() {
                                showFavoritesOnly = false;
                              });
                            }),
                            chip('Favoriler', showFavoritesOnly, () {
                              setState(() => showFavoritesOnly = !showFavoritesOnly);
                            }),
                            chip('Son Eklenen', false, () {
                              setState(() => showAllCampaigns = true);
                            }),
                          ],
                        ),
                      ),
                      const SizedBox(height: 18),
                    ],
                  ),
                ),
              ),
              if (snapshot.connectionState == ConnectionState.waiting)
                const SliverFillRemaining(
                  hasScrollBody: false,
                  child: Center(child: CircularProgressIndicator()),
                )
              else if (snapshot.hasError)
                const SliverFillRemaining(
                  hasScrollBody: false,
                  child: Center(
                    child: Padding(
                      padding: EdgeInsets.all(24),
                      child: Text(
                        'Kampanyalar yüklenemedi. Aşağı çekerek tekrar dene.',
                        textAlign: TextAlign.center,
                        style: TextStyle(color: Color(0xFFAAB6C8)),
                      ),
                    ),
                  ),
                )
              else if (groups.isEmpty)
                const SliverFillRemaining(
                  hasScrollBody: false,
                  child: Center(
                    child: Text(
                      'Bu filtreye uygun kampanya bulunamadı.',
                      style: TextStyle(color: Color(0xFFAAB6C8)),
                    ),
                  ),
                )
              else
                ...groups.entries.map(
                  (entry) => SliverPadding(
                    padding: const EdgeInsets.fromLTRB(16, 0, 16, 4),
                    sliver: SliverToBoxAdapter(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Expanded(
                                child: Text(
                                  '${emoji(entry.key)}  ${entry.key}',
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontSize: 21,
                                    fontWeight: FontWeight.w900,
                                  ),
                                ),
                              ),
                              Text(
                                '${entry.value.length} kampanya',
                                style: const TextStyle(
                                  color: Color(0xFFAAB6C8),
                                  fontSize: 12,
                                  fontWeight: FontWeight.w700,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 9),
                          ...entry.value.map(
                            (campaign) => SmartCampaignCard(
                              campaign: campaign,
                              isFavorite: favoriteIds.contains(campaignId(campaign)),
                              isCompared: compareIds.contains(campaignId(campaign)),
                              showAllCampaigns: showAllCampaigns,
                              expiringSoon: isExpiringSoon(campaign),
                              daysRemaining: daysLeft(campaign),
                              onFavorite: () => toggleFavorite(campaign),
                              onCompare: () => toggleCompare(campaign),
                              onOpenUrl: openCampaignUrl,
                              requiredSteps: requiredSteps(campaign),
                              completedSteps: campaignProgress[campaignId(campaign)] ?? 0,
                              onProgressChange: (value) => changeProgress(campaign, value),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
            ],
          ),
        );
      },
    );
  }
'''
s = s[:start] + build + s[end:]

# ---------- Quick category order ----------
old_data = """const data = [
                  ['🚗', 'Otomotiv'], ['🛍️', 'E-ticaret'], ['📱', 'Elektronik'], ['🛒', 'Market'],
                  ['⛽', 'Akaryakıt'], ['🧳', 'Seyahat'], ['👕', 'Giyim'], ['▦', 'Tümü'],
                ];"""
new_data = """const data = [
                  ['🍴', 'Restoran'], ['🛒', 'Market'], ['⛽', 'Akaryakıt'], ['🧳', 'Seyahat'],
                  ['👕', 'Giyim'], ['🛋️', 'Ev & Yaşam'], ['▦', 'Tümü'], ['📱', 'Elektronik'],
                ];"""
s = s.replace(old_data, new_data)

# ---------- Bottom navigation ----------
nav_start = s.find('bottomNavigationBar:')
if nav_start >= 0:
    nav_end = s.find('\n      ),', nav_start)
    if nav_end >= 0:
        nav = s[nav_start:nav_end]
        nav = nav.replace('backgroundColor: Colors.white,', 'backgroundColor: const Color(0xFF081120),')
        nav = nav.replace('color: Colors.white,', 'color: const Color(0xFF081120),')
        nav = nav.replace('Color(0xFFE9E4F1)', 'Color(0xFF182B43)')
        s = s[:nav_start] + nav + s[nav_end:]

p.write_text(s, encoding='utf-8')
print('Reference catalog rebuilt: readable layout, compact cards, logo row, category grid and preserved interactions.')
