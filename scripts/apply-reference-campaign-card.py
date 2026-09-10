from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')


def replace_class(src, name, replacement):
    start = src.find('class ' + name)
    if start < 0:
        raise SystemExit(f'{name} not found')
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
    raise SystemExit(f'{name} end not found')

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

  String clean(dynamic value) {
    if (value == null) return '';
    return decodeHtmlEntities('$value')
        .replaceAll(RegExp(r'<[^>]*>'), ' ')
        .replaceAll(RegExp(r'\\s+'), ' ')
        .trim();
  }

  String first(List<String> keys) {
    for (final key in keys) {
      final value = clean(campaign[key]);
      if (value.isNotEmpty) return value;
    }
    return '';
  }

  String dateRange() {
    final direct = first(['date_range', 'validity', 'campaign_dates']);
    if (direct.isNotEmpty) return direct;
    final start = first(['start_date', 'starts_at']);
    final end = first(['end_date', 'ends_at']);
    if (start.isEmpty && end.isEmpty) return '';
    String shortDate(String value) {
      final parsed = parseCampaignDate(value);
      if (parsed == null) return value;
      const months = ['', 'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'];
      return '${parsed.day} ${months[parsed.month]} ${parsed.year}';
    }
    if (start.isNotEmpty && end.isNotEmpty) return '${shortDate(start)} - ${shortDate(end)}';
    return shortDate(start.isNotEmpty ? start : end);
  }

  String logoUrl() {
    final direct = first(['logo_url', 'image_url', 'merchant_logo', 'brand_logo']);
    if (direct.isNotEmpty) return direct;
    final source = first(['source_url', 'detail_url', 'url']);
    final uri = Uri.tryParse(source);
    final host = uri?.host.replaceFirst('www.', '') ?? '';
    if (host.isNotEmpty) return 'https://www.google.com/s2/favicons?domain=$host&sz=128';
    return '';
  }

  String benefitText() {
    final explicit = first(['benefit_label', 'advantage_label']);
    if (explicit.isNotEmpty) return explicit;
    final type = _norm(first(['reward_type', 'benefit_type', 'advantage_type']));
    final installment = first(['installment', 'installments', 'taksit']);
    final reward = first(['reward', 'reward_amount', 'cashback', 'discount']);
    if (type.contains('taksit') || type.contains('install')) {
      if (installment.isNotEmpty) return installment.toLowerCase().contains('taksit') ? installment : '$installment taksit';
    }
    if (type.contains('indirim') || type.contains('discount')) {
      if (reward.isNotEmpty) return reward.contains('%') ? reward : '%$reward indirim';
    }
    if (reward.isNotEmpty) return reward;
    if (installment.isNotEmpty) return installment.toLowerCase().contains('taksit') ? installment : '$installment taksit';
    return '';
  }

  @override
  Widget build(BuildContext context) {
    final title = first(['title', 'name']);
    final merchant = first(['merchant', 'brand']);
    final category = first(['category']).isNotEmpty ? first(['category']) : campaignSection(campaign);
    final bank = first(['bank_name', 'bank', 'card_bank']);
    final description = first(['campaign_text', 'description', 'summary', 'details', 'content']);
    final date = dateRange();
    final logo = logoUrl();
    final benefit = benefitText();

    final statusText = expiringSoon
        ? 'Son ${daysRemaining < 1 ? 1 : daysRemaining} Gün'
        : (showAllCampaigns ? 'Popüler' : 'Size Özel');
    final statusColor = expiringSoon
        ? (daysRemaining <= 3 ? const Color(0xFFFFDDE2) : const Color(0xFFDDF8E7))
        : (showAllCampaigns ? const Color(0xFFDDEEFF) : const Color(0xFFEDE4FF));
    final statusTextColor = expiringSoon
        ? (daysRemaining <= 3 ? const Color(0xFFD52E39) : const Color(0xFF187A3B))
        : (showAllCampaigns ? const Color(0xFF1472B8) : const Color(0xFF6530D8));

    return Container(
      margin: const EdgeInsets.only(bottom: 13),
      padding: const EdgeInsets.fromLTRB(13, 13, 13, 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFDCD7E6)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Container(
              width: 102,
              height: 102,
              decoration: BoxDecoration(color: const Color(0xFFF7F5FA), borderRadius: BorderRadius.circular(15)),
              clipBehavior: Clip.antiAlias,
              child: logo.isNotEmpty
                  ? Image.network(logo, fit: BoxFit.contain, errorBuilder: (_, __, ___) => const Icon(Icons.local_offer_rounded, size: 40, color: Color(0xFF6D3DF5)))
                  : const Icon(Icons.local_offer_rounded, size: 40, color: Color(0xFF6D3DF5)),
            ),
            const SizedBox(width: 13),
            Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Expanded(child: Text(title.isEmpty ? 'Kampanya' : title, maxLines: 3, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 18, height: 1.12, fontWeight: FontWeight.w900, color: Color(0xFF151225)))),
                const SizedBox(width: 4),
                IconButton(
                  padding: EdgeInsets.zero,
                  constraints: const BoxConstraints(minWidth: 34, minHeight: 34),
                  onPressed: onFavorite,
                  icon: Icon(isFavorite ? Icons.star_rounded : Icons.star_border_rounded, size: 29, color: const Color(0xFF4E4A58)),
                ),
              ]),
              const SizedBox(height: 5),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 6),
                decoration: BoxDecoration(color: statusColor, borderRadius: BorderRadius.circular(13)),
                child: Text(statusText, style: TextStyle(fontSize: 10.5, fontWeight: FontWeight.w900, color: statusTextColor)),
              ),
            ])),
          ]),
          const SizedBox(height: 10),
          Wrap(spacing: 5, runSpacing: 5, children: [
            if (category.isNotEmpty) _meta(Icons.category_outlined, category),
            if (bank.isNotEmpty) _meta(Icons.credit_card_outlined, bank),
            if (date.isNotEmpty) _meta(Icons.calendar_month_outlined, date),
          ]),
          if (description.isNotEmpty) ...[
            const SizedBox(height: 9),
            Text(description, maxLines: 3, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 13, height: 1.28, color: Color(0xFF5F5969))),
          ],
          if (benefit.isNotEmpty) ...[
            const SizedBox(height: 6),
            Text(benefit, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w900, color: Color(0xFF5E3CCB))),
          ],
          const SizedBox(height: 10),
          Align(
            alignment: Alignment.centerRight,
            child: SizedBox(
              height: 42,
              width: 132,
              child: FilledButton(
                onPressed: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => CampaignDetailPage(campaign: campaign))),
                style: FilledButton.styleFrom(backgroundColor: const Color(0xFF6D3DF5), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14))),
                child: const Text('Detaylar  →', style: TextStyle(fontWeight: FontWeight.w900)),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _meta(IconData icon, String text) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 7),
    decoration: BoxDecoration(color: const Color(0xFFF0EDFA), borderRadius: BorderRadius.circular(11)),
    child: Row(mainAxisSize: MainAxisSize.min, children: [
      Icon(icon, size: 14, color: const Color(0xFF29233C)),
      const SizedBox(width: 5),
      ConstrainedBox(constraints: const BoxConstraints(maxWidth: 150), child: Text(text, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 10.5, color: Color(0xFF29233C), fontWeight: FontWeight.w800))),
    ]),
  );
}
'''

s = replace_class(s, 'SmartCampaignCard', card)
p.write_text(s, encoding='utf-8')
print('Exact reference campaign card layout applied')
