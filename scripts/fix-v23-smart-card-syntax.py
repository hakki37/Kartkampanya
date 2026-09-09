from pathlib import Path
p=Path('lib/main.dart')
s=p.read_text(encoding='utf-8')
start=s.find('class SmartCampaignCard extends StatelessWidget {')
if start<0: raise SystemExit('SmartCampaignCard not found')
brace=s.find('{',start); depth=0
for i in range(brace,len(s)):
    if s[i]=='{': depth+=1
    elif s[i]=='}':
        depth-=1
        if depth==0:
            end=i+1; break
else: raise SystemExit('SmartCampaignCard end not found')
new=r'''class SmartCampaignCard extends StatelessWidget {
  final Map<String, dynamic> campaign;
  final bool isFavorite;
  final bool isCompared;
  final bool showAllCampaigns;
  final bool expiringSoon;
  final int daysRemaining;
  final VoidCallback onFavorite;
  final VoidCallback onCompare;
  final Future<void> Function(String url) onOpenUrl;
  final int requiredSteps;
  final int completedSteps;
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

  String _t(dynamic value) => value == null ? '' : '$value'.trim();

  String _domain(String value) {
    final m = _norm(value);
    const map = <String, String>{
      'ispark': 'ispark.istanbul',
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
      'akbank': 'akbank.com',
      'axess': 'axess.com.tr',
      'garanti': 'garantibbva.com.tr',
      'bonus': 'bonus.com.tr',
      'vakifbank': 'vakifbank.com.tr',
      'world': 'worldcard.com.tr',
      'qnb': 'qnb.com.tr',
      'teb': 'teb.com.tr',
      'hsbc': 'hsbc.com.tr',
      'isbank': 'isbank.com.tr',
      'maximum': 'maximum.com.tr',
      'ziraat': 'ziraatbank.com.tr',
    };
    for (final entry in map.entries) {
      if (m.contains(entry.key)) return entry.value;
    }
    return '';
  }

  String _logo(String domain) => domain.isEmpty ? '' : 'https://cdn.brandfetch.io/$domain/w/600/h/180/logo';

  @override
  Widget build(BuildContext context) {
    final merchant = _t(campaign['merchant']);
    final title = _t(campaign['title']).isEmpty ? 'Kampanya' : _t(campaign['title']);
    final category = _t(campaign['category']).isEmpty ? campaignSection(campaign) : _t(campaign['category']);
    final detailUrl = _t(campaign['detail_url']).isNotEmpty ? _t(campaign['detail_url']) : _t(campaign['url']);
    final cards = (campaign['_cards'] as List?)?.whereType<UserCard>().toList() ?? <UserCard>[];
    final brandNames = <String>[];
    for (final card in cards) {
      for (final value in <String>[card.bank, card.card, card.network]) {
        if (value.trim().isNotEmpty && !brandNames.contains(value)) brandNames.add(value);
      }
    }
    final md = _domain(merchant);
    final benefit = _t(campaign['benefit']);
    final minSpend = _t(campaign['min_spend'] ?? campaign['minimum_spend']);

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: const Color(0xFF121A2A),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: const Color(0xFF34445E), width: 1.2),
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(24),
        onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => CampaignDetailPage(campaign: campaign))),
        child: Padding(
          padding: const EdgeInsets.fromLTRB(14, 14, 14, 16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  md.isNotEmpty
                      ? _CatalogLogo(_logo(md), size: 54)
                      : Container(
                          width: 132,
                          height: 54,
                          alignment: Alignment.center,
                          decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(10)),
                          child: Text(merchant.isEmpty ? 'KAMPANYA' : merchant, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(color: Color(0xFF172033), fontWeight: FontWeight.w900)),
                        ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: <Widget>[
                        Text(title, maxLines: 3, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 18, height: 1.12, fontWeight: FontWeight.w800, color: Colors.white)),
                        if (merchant.isNotEmpty) ...<Widget>[
                          const SizedBox(height: 5),
                          Text(merchant, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 13, color: Color(0xFFB8C2D8), fontWeight: FontWeight.w600)),
                        ],
                      ],
                    ),
                  ),
                  IconButton(onPressed: onFavorite, icon: Icon(isFavorite ? Icons.star_rounded : Icons.star_border_rounded, color: isFavorite ? const Color(0xFFC5B5FF) : Colors.white70)),
                  IconButton(onPressed: onCompare, icon: Icon(Icons.compare_arrows_rounded, color: isCompared ? const Color(0xFFC5B5FF) : Colors.white70)),
                ],
              ),
              if (brandNames.isNotEmpty) ...<Widget>[
                const SizedBox(height: 12),
                Wrap(
                  spacing: 7,
                  runSpacing: 7,
                  children: brandNames.take(5).map<Widget>((name) {
                    final domain = _domain(name);
                    if (domain.isEmpty) {
                      return Container(padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7), decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(9)), child: Text(name, style: const TextStyle(color: Color(0xFF172033), fontWeight: FontWeight.w800, fontSize: 12)));
                    }
                    return _CatalogLogo(_logo(domain), size: 34);
                  }).toList(),
                ),
              ],
              if (benefit.isNotEmpty) ...<Widget>[
                const SizedBox(height: 12),
                Text('💰  Tahmini avantaj: $benefit', maxLines: 2, overflow: TextOverflow.ellipsis, style: const TextStyle(color: Color(0xFFE8ECF5), fontSize: 14, fontWeight: FontWeight.w600)),
              ],
              if (minSpend.isNotEmpty) ...<Widget>[
                const SizedBox(height: 6),
                Text('💳  Minimum harcama: $minSpend', maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(color: Color(0xFFE8ECF5), fontSize: 14, fontWeight: FontWeight.w600)),
              ],
              const SizedBox(height: 12),
              Row(
                children: <Widget>[
                  Container(padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7), decoration: BoxDecoration(color: const Color(0xFF5D43E7).withOpacity(.25), borderRadius: BorderRadius.circular(18)), child: Text(category, style: const TextStyle(color: Color(0xFFD5CCFF), fontWeight: FontWeight.w700))),
                  const Spacer(),
                  if (detailUrl.isNotEmpty) IconButton(onPressed: () => onOpenUrl(detailUrl), icon: const Icon(Icons.arrow_forward_rounded, color: Colors.white70)),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
'''
s=s[:start]+new+s[end:]
p.write_text(s,encoding='utf-8')
print('v23 applied')
