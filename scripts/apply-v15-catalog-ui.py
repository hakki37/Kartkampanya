from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')
start = s.find('class SmartCampaignCard extends StatelessWidget {')
end = s.find('class MyCardsPage extends StatefulWidget {', start)
if start < 0 or end < 0:
    raise SystemExit('SmartCampaignCard boundaries not found')

new_class = r'''class _CatalogLogo extends StatelessWidget {
  final String url;
  final double size;
  const _CatalogLogo(this.url, {this.size = 38});
  @override
  Widget build(BuildContext context) => ClipRRect(
        borderRadius: BorderRadius.circular(10),
        child: Image.network(
          url,
          width: size,
          height: size,
          fit: BoxFit.contain,
          errorBuilder: (_, __, ___) => const SizedBox.shrink(),
        ),
      );
}

String _logoUrl(String domain) =>
    'https://www.google.com/s2/favicons?domain=$domain&sz=128';

String _merchantDomain(String merchant) {
  final m = merchant.toLowerCase();
  const map = <String, String>{
    'ispark': 'ispark.istanbul', 'i̇spark': 'ispark.istanbul',
    'n11': 'n11.com', 'media markt': 'mediamarkt.com.tr',
    'mediamarkt': 'mediamarkt.com.tr', 'migros': 'migros.com.tr',
    'a101': 'a101.com.tr', 'boyner': 'boyner.com.tr',
    'starbucks': 'starbucks.com.tr', 'nike': 'nike.com',
    'apple': 'apple.com', 'shell': 'shell.com.tr',
    'enuygun': 'enuygun.com', 'muhiku': 'muhiku.com',
  };
  for (final e in map.entries) { if (m.contains(e.key)) return e.value; }
  return '';
}

String _brandDomain(String name) {
  final n = name.toLowerCase();
  if (n.contains('axess')) return 'axess.com.tr';
  if (n.contains('bonus')) return 'bonus.com.tr';
  if (n.contains('world')) return 'worldcard.com.tr';
  if (n.contains('maximum')) return 'maximum.com.tr';
  if (n.contains('paraf')) return 'paraf.com.tr';
  if (n.contains('bankkart')) return 'bankkart.com.tr';
  if (n.contains('sağlam')) return 'kuveytturk.com.tr';
  if (n.contains('happy')) return 'turkiyefinans.com.tr';
  if (n.contains('cardfinans')) return 'qnb.com.tr';
  return '';
}

String _bankDomain(String name) {
  final n = name.toLowerCase();
  if (n.contains('akbank')) return 'akbank.com';
  if (n.contains('garanti')) return 'garantibbva.com.tr';
  if (n.contains('yapı kredi')) return 'yapikredi.com.tr';
  if (n.contains('iş bank')) return 'isbank.com.tr';
  if (n.contains('ziraat')) return 'ziraatbank.com.tr';
  if (n.contains('halkbank')) return 'halkbank.com.tr';
  if (n == 'qnb' || n.contains('qnb')) return 'qnb.com.tr';
  if (n.contains('teb')) return 'teb.com.tr';
  if (n.contains('vakıf')) return 'vakifbank.com.tr';
  if (n.contains('deniz')) return 'denizbank.com';
  if (n.contains('kuveyt')) return 'kuveytturk.com.tr';
  if (n.contains('türkiye finans')) return 'turkiyefinans.com.tr';
  if (n.contains('ing')) return 'ing.com.tr';
  if (n.contains('hsbc')) return 'hsbc.com.tr';
  if (n.contains('odea')) return 'odeabank.com.tr';
  return '';
}

class SmartCampaignCard extends StatelessWidget {
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
    super.key, required this.campaign, required this.isFavorite,
    required this.isCompared, required this.showAllCampaigns,
    required this.expiringSoon, required this.daysRemaining,
    required this.onFavorite, required this.onCompare,
    required this.onOpenUrl, required this.requiredSteps,
    required this.completedSteps, required this.onProgressChange,
  });

  Widget _networkLogo(String network) {
    final n = network.toLowerCase();
    final slug = n.contains('master') ? 'mastercard' : n.contains('troy') ? 'troy' : 'visa';
    return Padding(
      padding: const EdgeInsets.only(right: 14),
      child: Image.network(
        'https://cdn.simpleicons.org/$slug',
        height: 30, width: 66, fit: BoxFit.contain,
        errorBuilder: (_, __, ___) => Text(network, style: const TextStyle(fontWeight: FontWeight.w800)),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final merchant = decodeHtmlEntities('${campaign['merchant'] ?? ''}').trim();
    final title = decodeHtmlEntities('${campaign['title'] ?? ''}').trim();
    final category = decodeHtmlEntities('${campaign['category'] ?? ''}').trim();
    final bank = decodeHtmlEntities('${campaign['bank_name'] ?? ''}').trim();
    final card = decodeHtmlEntities('${campaign['card_name'] ?? ''}').trim();
    final network = decodeHtmlEntities('${campaign['network'] ?? ''}').trim();
    final min = campaign['min_spend'];
    final detailUrl = '${campaign['detail_url'] ?? campaign['url'] ?? campaign['source_url'] ?? ''}'.trim();
    final terms = campaignConditions(campaign);
    final text = '$title ${campaign['description'] ?? ''} ${campaign['reward_type'] ?? ''}'.toLowerCase();
    final installment = RegExp(r'(\d+)\s*taksit').firstMatch(text)?.group(1);
    final reward = campaign['_calculatedReward'] ?? campaign['_reward'] ?? campaign['reward_amount'] ?? campaign['max_reward'];
    final hasMoney = reward is num && reward > 0;
    final merchantDomain = _merchantDomain(merchant);
    final bankDomain = _bankDomain(bank);
    final cardDomain = _brandDomain(card);

    return Card(
      margin: const EdgeInsets.only(bottom: 14),
      clipBehavior: Clip.antiAlias,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(22), side: BorderSide(color: Theme.of(context).colorScheme.outline.withOpacity(.65))),
      child: InkWell(
        onTap: () => showModalBottomSheet(
          context: context, isScrollControlled: true, showDragHandle: true,
          builder: (sheetContext) => SafeArea(child: SingleChildScrollView(
            padding: const EdgeInsets.fromLTRB(20, 8, 20, 28),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(title.isNotEmpty ? title : '$merchant Kampanyası', style: Theme.of(sheetContext).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w800)),
              const SizedBox(height: 14),
              if (bank.isNotEmpty) ListTile(contentPadding: EdgeInsets.zero, title: const Text('Banka'), subtitle: Text(bank)),
              if (card.isNotEmpty) ListTile(contentPadding: EdgeInsets.zero, title: const Text('Kart'), subtitle: Text(card)),
              if (network.isNotEmpty) ListTile(contentPadding: EdgeInsets.zero, title: const Text('Kart ağı'), subtitle: Text(network)),
              if (category.isNotEmpty) ListTile(contentPadding: EdgeInsets.zero, title: const Text('Kategori'), subtitle: Text(category)),
              if (min != null) ListTile(contentPadding: EdgeInsets.zero, title: const Text('Minimum harcama'), subtitle: Text('$min TL')),
              ListTile(contentPadding: EdgeInsets.zero, title: const Text('Avantaj'), subtitle: Text(hasMoney ? '${(reward as num).toDouble().toStringAsFixed(0)} TL' : installment != null ? '$installment taksit' : 'Kampanya avantajı')),
              const SizedBox(height: 8),
              Text(terms.isNotEmpty ? terms : 'Kampanya şartları bulunamadı.', style: const TextStyle(height: 1.45)),
              if (detailUrl.isNotEmpty) ...[
                const SizedBox(height: 14),
                SizedBox(width: double.infinity, child: FilledButton.icon(onPressed: () => onOpenUrl(detailUrl), icon: const Icon(Icons.open_in_new_rounded), label: const Text('Kampanyaya Git')),
              ],
            ]),
          )),
        ),
        child: Padding(
          padding: const EdgeInsets.fromLTRB(14, 14, 14, 16),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
              if (merchantDomain.isNotEmpty) Padding(padding: const EdgeInsets.only(right: 12), child: _CatalogLogo(_logoUrl(merchantDomain), size: 68))
              else const Padding(padding: EdgeInsets.only(right: 12), child: Icon(Icons.local_offer_rounded, size: 52)),
              Expanded(child: Text(title, maxLines: 3, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w800, height: 1.18))),
              IconButton(tooltip: isFavorite ? 'Favoriden çıkar' : 'Favoriye ekle', onPressed: onFavorite, icon: Icon(isFavorite ? Icons.star_rounded : Icons.star_border_rounded)),
              IconButton(tooltip: isCompared ? 'Karşılaştırmadan çıkar' : 'Karşılaştır', onPressed: onCompare, icon: Icon(isCompared ? Icons.check_circle_rounded : Icons.compare_arrows_rounded)),
            ]),
            const SizedBox(height: 8),
            Wrap(crossAxisAlignment: WrapCrossAlignment.center, spacing: 4, children: [
              if (bankDomain.isNotEmpty) _CatalogLogo(_logoUrl(bankDomain), size: 40),
              if (bank.isNotEmpty && bankDomain.isEmpty) Text(bank, style: const TextStyle(fontWeight: FontWeight.w800)),
              if (cardDomain.isNotEmpty) _CatalogLogo(_logoUrl(cardDomain), size: 40),
              if (card.isNotEmpty && cardDomain.isEmpty) Text(card, style: const TextStyle(fontWeight: FontWeight.w800)),
              if (network.isNotEmpty) _networkLogo(network),
            ]),
            if (category.isNotEmpty) Padding(padding: const EdgeInsets.only(top: 8), child: Container(padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7), decoration: BoxDecoration(color: Theme.of(context).colorScheme.primaryContainer.withOpacity(.7), borderRadius: BorderRadius.circular(18)), child: Text(category))),
            if (cards.isEmpty && showAllCampaigns) const Padding(padding: EdgeInsets.only(top: 10), child: Text('ℹ️ Kayıtlı kartlarınla eşleşmiyor')),
            if (cards.isNotEmpty) Padding(padding: const EdgeInsets.only(top: 10), child: Text('🏆 Uygun kart: ${cards.map((c) => '${c.bank} • ${c.card} • ${c.network}').join(', ')}', style: const TextStyle(fontWeight: FontWeight.w700))),
            Padding(padding: const EdgeInsets.only(top: 8), child: Text('💰 Tahmini avantaj: ${hasMoney ? '${(reward as num).toDouble().toStringAsFixed(0)} TL' : installment != null ? '$installment taksit' : '0 TL'}', style: TextStyle(fontWeight: FontWeight.w800, color: hasMoney || installment != null ? Colors.amber : null))),
            if (min != null) Padding(padding: const EdgeInsets.only(top: 5), child: Text('💳 Minimum harcama: $min TL')),
          ]),
        ),
      ),
    );
  }
}

'''
# Preserve the existing cards calculation by adding it as a local getter-like block.
new_class = new_class.replace("    final merchant =", "    final cards = (campaign['_cards'] as List?)?.whereType<UserCard>().toList() ?? <UserCard>[];\n    final merchant =")
s = s[:start] + new_class + s[end:]
p.write_text(s, encoding='utf-8')
print('v15 catalog UI applied')
