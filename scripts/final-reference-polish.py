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

# The reference uses the Turkish label "Kampanyalar" in the bottom navigation.
s = s.replace("label:'Kartıma Uygun'", "label:'Kampanyalar'", 1)

# Final catalog-style campaign card: large logo, title, status, description,
# category/bank/date chips and a prominent Details button.
smart = r'''class SmartCampaignCard extends StatelessWidget {
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

  String text(dynamic value) => value == null ? '' : '$value'.trim();

  String firstValue(List<String> keys) {
    for (final key in keys) {
      final value = text(campaign[key]);
      if (value.isNotEmpty) return value;
    }
    return '';
  }

  String logoUrl() => firstValue([
        'logo_url',
        'image_url',
        'merchant_logo',
        'brand_logo',
      ]);

  @override
  Widget build(BuildContext context) {
    final title = firstValue(['title', 'name']).isEmpty
        ? 'Kampanya'
        : firstValue(['title', 'name']);
    final merchant = firstValue(['merchant', 'brand', 'bank_name']);
    final description = firstValue([
      'description',
      'campaign_text',
      'details',
      'content',
    ]);
    final category = firstValue(['category']).isEmpty
        ? campaignSection(campaign)
        : firstValue(['category']);
    final bank = firstValue(['bank_name', 'bank', 'card_bank']);
    final date = firstValue(['date_range', 'validity', 'campaign_dates']);
    final logo = logoUrl();
    final detailTitle = title.length > 64 ? '${title.substring(0, 61)}...' : title;

    return Container(
      margin: const EdgeInsets.only(bottom: 13),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(21),
        border: Border.all(color: const Color(0xFFE1DCEB)),
        boxShadow: const [
          BoxShadow(
            color: Color(0x0D000000),
            blurRadius: 12,
            offset: Offset(0, 4),
          ),
        ],
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(21),
        onTap: () => Navigator.of(context).push(
          MaterialPageRoute(
            builder: (_) => CampaignDetailPage(campaign: campaign),
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.fromLTRB(13, 13, 13, 12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    width: 72,
                    height: 72,
                    decoration: BoxDecoration(
                      color: const Color(0xFFF4F1FA),
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: logo.isNotEmpty
                        ? ClipRRect(
                            borderRadius: BorderRadius.circular(16),
                            child: Image.network(
                              logo,
                              fit: BoxFit.contain,
                              errorBuilder: (_, __, ___) => const Icon(
                                Icons.local_offer_rounded,
                                color: Color(0xFF6D3DF5),
                                size: 31,
                              ),
                            ),
                          )
                        : const Icon(
                            Icons.local_offer_rounded,
                            color: Color(0xFF6D3DF5),
                            size: 31,
                          ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  if (merchant.isNotEmpty)
                                    Text(
                                      merchant,
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                      style: const TextStyle(
                                        fontSize: 10,
                                        color: Color(0xFF777187),
                                        fontWeight: FontWeight.w800,
                                      ),
                                    ),
                                  const SizedBox(height: 2),
                                  Text(
                                    detailTitle,
                                    maxLines: 3,
                                    overflow: TextOverflow.ellipsis,
                                    style: const TextStyle(
                                      fontSize: 17,
                                      height: 1.12,
                                      color: Color(0xFF17142A),
                                      fontWeight: FontWeight.w900,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            IconButton(
                              padding: EdgeInsets.zero,
                              constraints: const BoxConstraints(
                                minWidth: 34,
                                minHeight: 34,
                              ),
                              onPressed: onFavorite,
                              icon: Icon(
                                isFavorite
                                    ? Icons.favorite_rounded
                                    : Icons.favorite_border_rounded,
                                color: isFavorite
                                    ? const Color(0xFFE33F77)
                                    : const Color(0xFF666071),
                                size: 27,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 7),
                        if (expiringSoon)
                          Align(
                            alignment: Alignment.centerLeft,
                            child: Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 9,
                                vertical: 5,
                              ),
                              decoration: BoxDecoration(
                                color: daysRemaining <= 3
                                    ? const Color(0xFFFFE4E7)
                                    : const Color(0xFFE0F8E8),
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: Text(
                                daysRemaining >= 0
                                    ? '◷  Son $daysRemaining Gün'
                                    : '◷  Süresi Yaklaşıyor',
                                style: TextStyle(
                                  fontSize: 10,
                                  fontWeight: FontWeight.w900,
                                  color: daysRemaining <= 3
                                      ? const Color(0xFFD33A3A)
                                      : const Color(0xFF19864A),
                                ),
                              ),
                            ),
                          ),
                      ],
                    ),
                  ),
                ],
              ),
              if (description.isNotEmpty) ...[
                const SizedBox(height: 10),
                Text(
                  description,
                  maxLines: 3,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    fontSize: 13,
                    height: 1.25,
                    color: Color(0xFF5F5968),
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
              const SizedBox(height: 11),
              Wrap(
                spacing: 7,
                runSpacing: 7,
                children: [
                  _tag(Icons.local_gas_station_outlined, category),
                  if (bank.isNotEmpty) _tag(Icons.credit_card_outlined, bank),
                  if (date.isNotEmpty) _tag(Icons.calendar_month_outlined, date),
                ],
              ),
              const SizedBox(height: 11),
              Row(
                children: [
                  Expanded(
                    child: SizedBox(
                      height: 43,
                      child: FilledButton(
                        onPressed: () => Navigator.of(context).push(
                          MaterialPageRoute(
                            builder: (_) => CampaignDetailPage(campaign: campaign),
                          ),
                        ),
                        style: FilledButton.styleFrom(
                          backgroundColor: const Color(0xFF6D3DF5),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(14),
                          ),
                        ),
                        child: const Text(
                          'Detaylar  →',
                          style: TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w900,
                          ),
                        ),
                      ),
                    ),
                  ),
                  if (isCompared) ...[
                    const SizedBox(width: 8),
                    IconButton(
                      onPressed: onCompare,
                      tooltip: 'Karşılaştırmadan çıkar',
                      icon: const Icon(
                        Icons.compare_arrows_rounded,
                        color: Color(0xFF6D3DF5),
                      ),
                    ),
                  ],
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _tag(IconData icon, String label) {
    final value = label.isEmpty ? 'Kampanya' : label;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
      decoration: BoxDecoration(
        color: const Color(0xFFF0EDFA),
        borderRadius: BorderRadius.circular(11),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: const Color(0xFF332B50)),
          const SizedBox(width: 5),
          ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 125),
            child: Text(
              value,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(
                fontSize: 10,
                color: Color(0xFF332B50),
                fontWeight: FontWeight.w800,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
'''

s = replace_class(s, 'SmartCampaignCard', smart)
p.write_text(s, encoding='utf-8')
print('Final catalog reference polish applied')
