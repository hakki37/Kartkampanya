from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

# The v30 reference pass generated an invalid SmartCampaignCard body.
# Replace that entire presentation-only class with a compact, parser-safe card.
start = s.find('class SmartCampaignCard extends StatelessWidget {')
end = s.find('class MyCardsPage extends StatefulWidget {', start)
if start < 0 or end < 0:
    raise SystemExit('SmartCampaignCard boundaries not found')

card = r'''class SmartCampaignCard extends StatelessWidget {
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

  @override
  Widget build(BuildContext context) {
    final cards = (campaign['_cards'] as List?)?.whereType<UserCard>().toList() ?? <UserCard>[];
    final title = decodeHtmlEntities('${campaign['title'] ?? ''}').trim();
    final merchant = decodeHtmlEntities('${campaign['merchant'] ?? ''}').trim();
    final bank = decodeHtmlEntities('${campaign['bank_name'] ?? ''}').trim();
    final card = decodeHtmlEntities('${campaign['card_name'] ?? ''}').trim();
    final network = decodeHtmlEntities('${campaign['network'] ?? ''}').trim();
    final category = decodeHtmlEntities('${campaign['category'] ?? ''}').trim();
    final reward = campaign['_calculatedReward'] ?? campaign['_reward'];
    final min = campaign['min_spend'];
    final url = '${campaign['detail_url'] ?? campaign['source_url'] ?? campaign['url'] ?? ''}'.trim();

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      color: Colors.white,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
      child: InkWell(
        borderRadius: BorderRadius.circular(18),
        onTap: () => showModalBottomSheet<void>(
          context: context,
          isScrollControlled: true,
          showDragHandle: true,
          builder: (ctx) => SafeArea(
            child: SingleChildScrollView(
              padding: const EdgeInsets.fromLTRB(20, 8, 20, 24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title.isEmpty ? '$merchant Kampanyası' : title, style: const TextStyle(fontSize: 21, fontWeight: FontWeight.w900)),
                  const SizedBox(height: 12),
                  if (bank.isNotEmpty) Text('Banka: $bank'),
                  if (card.isNotEmpty) Text('Kart: $card'),
                  if (network.isNotEmpty) Text('Kart ağı: $network'),
                  if (category.isNotEmpty) Text('Kategori: $category'),
                  if (min != null) Text('Minimum harcama: $min TL'),
                  if (reward != null) Text('Tahmini avantaj: ${(reward as num).toDouble().toStringAsFixed(0)} TL'),
                  const SizedBox(height: 12),
                  Text(campaignConditions(campaign), style: const TextStyle(height: 1.45)),
                  if (url.isNotEmpty) ...[
                    const SizedBox(height: 14),
                    SizedBox(
                      width: double.infinity,
                      child: FilledButton.icon(
                        onPressed: () => onOpenUrl(url),
                        icon: const Icon(Icons.open_in_new_rounded),
                        label: const Text('Kampanyaya Git'),
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    width: 48,
                    height: 48,
                    decoration: BoxDecoration(
                      color: const Color(0xFFEDE7FF),
                      borderRadius: BorderRadius.circular(14),
                    ),
                    alignment: Alignment.center,
                    child: const Icon(Icons.local_offer_rounded, color: Color(0xFF6D3DF5)),
                  ),
                  const SizedBox(width: 11),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        if (merchant.isNotEmpty) Text(merchant, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 11, color: Color(0xFF777187), fontWeight: FontWeight.w800)),
                        const SizedBox(height: 2),
                        Text(title.isEmpty ? 'Kampanya' : title, maxLines: 3, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 15, height: 1.15, color: Color(0xFF211D2D), fontWeight: FontWeight.w900)),
                      ],
                    ),
                  ),
                  IconButton(onPressed: onFavorite, icon: Icon(isFavorite ? Icons.favorite_rounded : Icons.favorite_border_rounded, color: isFavorite ? const Color(0xFFE33F77) : const Color(0xFF777187))),
                ],
              ),
              if (category.isNotEmpty) ...[
                const SizedBox(height: 9),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(color: const Color(0xFFEDE7FF), borderRadius: BorderRadius.circular(9)),
                  child: Text(category, style: const TextStyle(fontSize: 9, color: Color(0xFF5B21B6), fontWeight: FontWeight.w900)),
                ),
              ],
              if (cards.isNotEmpty) ...[
                const SizedBox(height: 9),
                Text('💳 ${cards.map((c) => '${c.bank} • ${c.card} • ${c.network}').join(' | ')}', maxLines: 2, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700)),
              ],
              if (reward != null) ...[
                const SizedBox(height: 7),
                Text('🎁 ${(reward as num).toDouble().toStringAsFixed(0)} TL avantaj', style: const TextStyle(fontWeight: FontWeight.w900, color: Color(0xFF5B21B6))),
              ],
              if (expiringSoon) ...[
                const SizedBox(height: 7),
                Text(daysRemaining == 0 ? 'Son gün bugün' : 'Son $daysRemaining gün', style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFFD33A3A))),
              ],
              if (requiredSteps >= 2) ...[
                const SizedBox(height: 9),
                Row(
                  children: [
                    Expanded(child: Text('İlerleme: $completedSteps / $requiredSteps', style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800))),
                    IconButton(onPressed: completedSteps > 0 ? () => onProgressChange(-1) : null, icon: const Icon(Icons.remove_circle_outline, size: 20)),
                    IconButton(onPressed: completedSteps < requiredSteps ? () => onProgressChange(1) : null, icon: const Icon(Icons.add_circle_outline, size: 20)),
                  ],
                ),
              ],
              if (showAllCampaigns && cards.isEmpty) ...[
                const SizedBox(height: 7),
                const Text('Bu kampanya kayıtlı kartlarınla eşleşmiyor.', style: TextStyle(fontSize: 10, color: Color(0xFF777187))),
              ],
              const SizedBox(height: 5),
              Row(
                children: [
                  const Spacer(),
                  TextButton.icon(onPressed: onCompare, icon: Icon(isCompared ? Icons.check_circle_rounded : Icons.compare_arrows_rounded, size: 18), label: Text(isCompared ? 'Seçildi' : 'Karşılaştır')),
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
s = s[:start] + card + s[end:]

# v30 also left one extra closing parenthesis in the compact Profile build.
s = s.replace("))),),const SizedBox(height:22)", "))),const SizedBox(height:22)")

p.write_text(s, encoding='utf-8')
print('v31 clean syntax fix applied')
