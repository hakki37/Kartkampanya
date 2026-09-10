from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

start = s.find('class SmartCampaignCard extends StatelessWidget {')
if start < 0:
    raise SystemExit('SmartCampaignCard not found')
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
    raise SystemExit('SmartCampaignCard end not found')

card = r'''class SmartCampaignCard extends StatelessWidget {
  final Map<String, dynamic> campaign;
  final bool isFavorite;
  final bool isCompared;
  final bool showAllCampaigns;
  final bool expiringSoon;
  final int daysRemaining;
  final int requiredSteps;
  final int completedSteps;
  final VoidCallback onFavorite;
  final VoidCallback onCompare;
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

  String _text(dynamic value) {
    if (value == null) return '';
    return '$value'
        .replaceAll(RegExp(r'<[^>]*>'), ' ')
        .replaceAll('&nbsp;', ' ')
        .replaceAll('&amp;', '&')
        .replaceAll(RegExp(r'\s+'), ' ')
        .trim();
  }

  String _first(List<String> keys) {
    for (final key in keys) {
      final value = _text(campaign[key]);
      if (value.isNotEmpty) return value;
    }
    return '';
  }

  String _benefit() {
    final explicit = _first(['benefit_label', 'advantage_label']);
    if (explicit.isNotEmpty) return explicit;
    final type = _first(['reward_type', 'benefit_type', 'advantage_type']).toLowerCase();
    final installment = _first(['installment', 'installments', 'taksit']);
    final reward = _first(['reward', 'reward_amount', 'cashback', 'discount']);
    if (type.contains('taksit') || type.contains('install')) {
      if (installment.isNotEmpty) {
        return installment.toLowerCase().contains('taksit') ? installment : '$installment taksit';
      }
    }
    if (type.contains('indirim') || type.contains('discount')) {
      if (reward.isNotEmpty) return reward.contains('%') ? reward : '%$reward indirim';
    }
    if (reward.isNotEmpty) return reward;
    if (installment.isNotEmpty) {
      return installment.toLowerCase().contains('taksit') ? installment : '$installment taksit';
    }
    return '';
  }

  @override
  Widget build(BuildContext context) {
    final title = _first(['title', 'name']);
    final merchant = _first(['merchant', 'brand', 'bank_name']);
    final description = _first(['description', 'campaign_text', 'summary', 'details', 'content']);
    final category = _first(['category']);
    final bank = _first(['bank_name', 'bank', 'card_bank']);
    final minimum = _first(['min_spend', 'minimum_spend', 'minimum_spending']);
    final benefit = _benefit();

    return Card(
      margin: const EdgeInsets.only(bottom: 13),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      child: InkWell(
        borderRadius: BorderRadius.circular(20),
        onTap: () {
          Navigator.of(context).push(
            MaterialPageRoute(builder: (_) => CampaignDetailPage(campaign: campaign)),
          );
        },
        child: Padding(
          padding: const EdgeInsets.all(15),
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
                            style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800),
                          ),
                        const SizedBox(height: 3),
                        Text(
                          title.isEmpty ? 'Kampanya' : title,
                          maxLines: 3,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w900),
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    onPressed: onFavorite,
                    icon: Icon(
                      isFavorite ? Icons.favorite_rounded : Icons.favorite_border_rounded,
                    ),
                  ),
                ],
              ),
              if (expiringSoon) ...[
                const SizedBox(height: 6),
                Text('Son $daysRemaining Gün', style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800)),
              ],
              if (description.isNotEmpty) ...[
                const SizedBox(height: 10),
                Text(
                  description,
                  maxLines: 3,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(fontSize: 13, height: 1.3),
                ),
              ],
              if (benefit.isNotEmpty || minimum.isNotEmpty) ...[
                const SizedBox(height: 10),
                Row(
                  children: [
                    if (benefit.isNotEmpty)
                      Expanded(
                        child: Text(
                          'Tahmini avantaj: $benefit',
                          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w900),
                        ),
                      ),
                    if (minimum.isNotEmpty)
                      Expanded(
                        child: Text(
                          'Minimum harcama: $minimum',
                          textAlign: TextAlign.right,
                          style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700),
                        ),
                      ),
                  ],
                ),
              ],
              if (category.isNotEmpty || bank.isNotEmpty) ...[
                const SizedBox(height: 10),
                Wrap(
                  spacing: 7,
                  runSpacing: 7,
                  children: [
                    if (category.isNotEmpty) Chip(label: Text(category)),
                    if (bank.isNotEmpty) Chip(label: Text(bank)),
                  ],
                ),
              ],
              const SizedBox(height: 10),
              SizedBox(
                width: double.infinity,
                child: FilledButton(
                  onPressed: () {
                    Navigator.of(context).push(
                      MaterialPageRoute(builder: (_) => CampaignDetailPage(campaign: campaign)),
                    );
                  },
                  child: const Text('Detaylar →'),
                ),
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
p.write_text(s, encoding='utf-8')
print('SmartCampaignCard replaced with syntax-safe catalog card')
