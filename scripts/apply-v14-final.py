from pathlib import Path
import re

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')
marker = 'class SmartCampaignCard extends StatelessWidget {'
if marker not in s:
    raise SystemExit('SmartCampaignCard marker not found')
helper = r'''class _V14Logo extends StatelessWidget {
  final String label;
  final bool merchant;
  const _V14Logo({required this.label, this.merchant = false});
  String? _domain(String value) {
    final n = _norm(value);
    const map = <String, String>{
      'akbank': 'akbank.com', 'garanti bbva': 'garantibbva.com.tr', 'yapı kredi': 'yapikredi.com.tr', 'iş bankası': 'isbank.com.tr',
      'qnb': 'qnb.com.tr', 'enpara': 'enpara.com', 'ziraat bankası': 'ziraatbank.com.tr', 'halkbank': 'halkbank.com.tr', 'vakıfbank': 'vakifbank.com.tr',
      'denizbank': 'denizbank.com', 'teb': 'teb.com.tr', 'cepteteb': 'cepteteb.com.tr', 'ing': 'ing.com.tr', 'kuveyt türk': 'kuveytturk.com.tr',
      'türkiye finans': 'turkiyefinans.com.tr', 'albaraka türk': 'albaraka.com.tr', 'fibabanka': 'fibabanka.com.tr', 'odeabank': 'odeabank.com.tr',
      'hsbc': 'hsbc.com.tr', 'şekerbank': 'sekerbank.com.tr', 'axess': 'axess.com.tr', 'bonus': 'bonus.com.tr', 'world': 'worldcard.com.tr',
      'maximum': 'maximum.com.tr', 'paraf': 'paraf.com.tr', 'bankkart': 'bankkart.com.tr', 'sağlam kart': 'kuveytturk.com.tr',
      'visa': 'visa.com', 'mastercard': 'mastercard.com', 'troy': 'troyodeme.com', 'migros': 'migros.com.tr', 'shell': 'shell.com.tr', 'opet': 'opet.com.tr',
      'petrol ofisi': 'petrolofisi.com.tr', 'n11': 'n11.com', 'trendyol': 'trendyol.com', 'hepsiburada': 'hepsiburada.com', 'amazon': 'amazon.com.tr',
      'boyner': 'boyner.com.tr', 'media markt': 'mediamarkt.com.tr', 'mediamarkt': 'mediamarkt.com.tr', 'teknosa': 'teknosa.com', 'vatan': 'vatanbilgisayar.com',
      'a101': 'a101.com.tr', 'bim': 'bim.com.tr', 'starbucks': 'starbucks.com.tr', 'nike': 'nike.com', 'apple': 'apple.com', 'mavi': 'mavi.com',
      'ikea': 'ikea.com.tr', 'enuygun': 'enuygun.com', 'muhiku': 'muhiku.com', 'spotify': 'spotify.com', 'netflix': 'netflix.com', 'steam': 'steampowered.com',
    };
    if (map.containsKey(n)) return map[n];
    for (final e in map.entries) { if (n.contains(e.key)) return e.value; }
    return null;
  }
  @override
  Widget build(BuildContext context) {
    final d = _domain(label);
    if (d == null || label.trim().isEmpty) return const SizedBox.shrink();
    final image = Image.network('https://www.google.com/s2/favicons?domain=$d&sz=128', fit: BoxFit.contain, errorBuilder: (_, __, ___) => const SizedBox.shrink());
    if (merchant) {
      return Container(width: 58, height: 58, padding: const EdgeInsets.all(6), decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(14)), child: image);
    }
    return SizedBox(width: 62, height: 30, child: image);
  }
}

'''
s = re.sub(r'class _V14Logo extends StatelessWidget \{.*?\n\}\n\n', '', s, count=1, flags=re.S)
s = s.replace(marker, helper + marker, 1)
start = s.find(marker)
end = s.find('class MyCardsPage extends StatefulWidget {', start)
if end < 0: raise SystemExit('MyCardsPage marker not found')
new_class = r'''class SmartCampaignCard extends StatelessWidget {
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
  const SmartCampaignCard({super.key, required this.campaign, required this.isFavorite, required this.isCompared, required this.showAllCampaigns, required this.expiringSoon, required this.daysRemaining, required this.onFavorite, required this.onCompare, required this.onOpenUrl, required this.requiredSteps, required this.completedSteps, required this.onProgressChange});
  @override
  Widget build(BuildContext context) {
    final cards = (campaign['_cards'] as List?)?.whereType<UserCard>().toList() ?? <UserCard>[];
    final merchant = decodeHtmlEntities('${campaign['merchant'] ?? ''}').trim();
    final title = decodeHtmlEntities('${campaign['title'] ?? ''}').trim();
    final category = decodeHtmlEntities('${campaign['category'] ?? ''}').trim();
    final bank = decodeHtmlEntities('${campaign['bank_name'] ?? ''}').trim();
    final card = decodeHtmlEntities('${campaign['card_name'] ?? ''}').trim();
    final network = decodeHtmlEntities('${campaign['network'] ?? ''}').trim();
    final min = campaign['min_spend'];
    final reward = campaign['_calculatedReward'] ?? campaign['_reward'] ?? campaign['reward_amount'] ?? campaign['max_reward'];
    final detailUrl = '${campaign['detail_url'] ?? campaign['url'] ?? ''}'.trim();
    final terms = campaignConditions(campaign);
    final searchable = '${campaign['title'] ?? ''} ${campaign['description'] ?? ''} ${campaign['reward_type'] ?? ''}';
    final taksit = RegExp(r'(\d+)\s*taksit', caseSensitive: false).firstMatch(searchable)?.group(1);
    final rewardType = '${campaign['reward_type'] ?? ''}'.toLowerCase();
    final isInstallment = taksit != null || rewardType.contains('taksit');
    String advantage = '0 TL';
    if (isInstallment) { advantage = taksit != null ? '$taksit taksit' : 'Taksit'; }
    else if (reward is num && reward != 0) { advantage = '${reward.toDouble().toStringAsFixed(0)} TL'; }
    else if (campaign['reward_percent'] is num && (campaign['reward_percent'] as num) > 0) { advantage = '%${(campaign['reward_percent'] as num).toDouble().toStringAsFixed(0)}'; }
    Future<void> openDetails() async {
      await showModalBottomSheet(context: context, isScrollControlled: true, showDragHandle: true, builder: (sheet) => SafeArea(child: SingleChildScrollView(padding: const EdgeInsets.fromLTRB(20, 8, 20, 28), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(title.isNotEmpty ? title : '$merchant Kampanyası', style: Theme.of(sheet).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w800)),
        const SizedBox(height: 14), if (bank.isNotEmpty) Text('Banka: $bank'), if (card.isNotEmpty) Text('Kart: $card'), if (network.isNotEmpty) Text('Kart ağı: $network'), if (category.isNotEmpty) Text('Kategori: $category'),
        const SizedBox(height: 10), Text('Avantaj: $advantage', style: const TextStyle(fontWeight: FontWeight.w800)), if (min != null) Text('Minimum harcama: $min TL'),
        if (terms.isNotEmpty) ...[const SizedBox(height: 12), const Text('Kampanya şartları', style: TextStyle(fontWeight: FontWeight.w800)), const SizedBox(height: 6), Text(terms, style: const TextStyle(height: 1.4))],
        if (detailUrl.isNotEmpty) ...[const SizedBox(height: 16), SizedBox(width: double.infinity, child: FilledButton.icon(onPressed: () => onOpenUrl(detailUrl), icon: const Icon(Icons.open_in_new_rounded), label: const Text('Kampanyaya Git'))],
      ]))));
    }
    return Card(margin: const EdgeInsets.only(bottom: 10), clipBehavior: Clip.antiAlias, child: InkWell(borderRadius: BorderRadius.circular(20), onTap: openDetails, child: Padding(padding: const EdgeInsets.fromLTRB(10, 10, 10, 11), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
        if (merchant.isNotEmpty) ...[_V14Logo(label: merchant, merchant: true), const SizedBox(width: 10)] else const Icon(Icons.local_offer_rounded, size: 30),
        Expanded(child: Text(title.isNotEmpty ? title : '$merchant Kampanyası', maxLines: 3, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 16, height: 1.2, fontWeight: FontWeight.w800))),
        IconButton(constraints: const BoxConstraints(minWidth: 36, minHeight: 36), padding: EdgeInsets.zero, tooltip: isFavorite ? 'Favoriden çıkar' : 'Favoriye ekle', onPressed: onFavorite, icon: Icon(isFavorite ? Icons.star_rounded : Icons.star_border_rounded)),
        IconButton(constraints: const BoxConstraints(minWidth: 36, minHeight: 36), padding: EdgeInsets.zero, tooltip: isCompared ? 'Karşılaştırmadan çıkar' : 'Karşılaştır', onPressed: onCompare, icon: Icon(isCompared ? Icons.check_circle_rounded : Icons.compare_arrows_rounded)),
      ]),
      if (bank.isNotEmpty || card.isNotEmpty || network.isNotEmpty) Padding(padding: const EdgeInsets.only(top: 5), child: Row(children: [if (bank.isNotEmpty) _V14Logo(label: bank), if (card.isNotEmpty) _V14Logo(label: card), if (network.isNotEmpty) _V14Logo(label: network)])),
      if (category.isNotEmpty) Padding(padding: const EdgeInsets.only(top: 5), child: Container(padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4), decoration: BoxDecoration(color: Theme.of(context).colorScheme.primaryContainer.withOpacity(.6), borderRadius: BorderRadius.circular(12)), child: Text(category, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700)))),
      if (cards.isEmpty && showAllCampaigns) Padding(padding: const EdgeInsets.only(top: 6), child: Text('ℹ️ Kayıtlı kartlarınla eşleşmiyor', style: TextStyle(fontSize: 12, color: Theme.of(context).colorScheme.onSurfaceVariant))),
      if (cards.isNotEmpty) Padding(padding: const EdgeInsets.only(top: 6), child: Text('🏆 Uygun kart: ${cards.map((c) => '${c.bank} • ${c.card} • ${c.network}').join('  |  ')}', maxLines: 2, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 12.5, fontWeight: FontWeight.w700))),
      Padding(padding: const EdgeInsets.only(top: 6), child: Text('💰 Tahmini avantaj: $advantage', style: TextStyle(fontWeight: FontWeight.w800, color: isInstallment ? Theme.of(context).colorScheme.secondary : null))),
      if (min != null) Padding(padding: const EdgeInsets.only(top: 4), child: Text('💳 Minimum harcama: $min TL', style: const TextStyle(fontSize: 12.5))),
      if (expiringSoon) Padding(padding: const EdgeInsets.only(top: 4), child: Text(daysRemaining == 0 ? '⚠️ Bugün bitiyor' : '⚠️ $daysRemaining gün kaldı', style: const TextStyle(fontSize: 12.5, fontWeight: FontWeight.w700))),
      if (requiredSteps >= 2) Padding(padding: const EdgeInsets.only(top: 7), child: LinearProgressIndicator(value: requiredSteps == 0 ? 0 : completedSteps / requiredSteps, minHeight: 6, borderRadius: BorderRadius.circular(8))),
    ]))));
  }
}

'''
s = s[:start] + new_class + s[end:]
p.write_text(s, encoding='utf-8')
print('v14 final UI applied')