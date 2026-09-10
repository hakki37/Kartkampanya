from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')
start = s.find('class SmartCampaignCard extends StatelessWidget {')
if start < 0:
    raise SystemExit('SmartCampaignCard not found')
brace = s.find('{', start)
depth = 0
end = None
for i in range(brace, len(s)):
    if s[i] == '{':
        depth += 1
    elif s[i] == '}':
        depth -= 1
        if depth == 0:
            end = i + 1
            break
if end is None:
    raise SystemExit('SmartCampaignCard end not found')

new = r'''class SmartCampaignCard extends StatelessWidget {
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

  String _text(dynamic value) => decodeHtmlEntities('${value ?? ''}').trim();

  String _merchantLogo(String merchant) {
    final m = _norm(merchant);
    const domains = <String, String>{
      'petrol ofisi': 'petrolofisi.com.tr',
      'shell': 'shell.com.tr',
      'opet': 'opet.com.tr',
      'migros': 'migros.com.tr',
      'carrefour': 'carrefoursa.com',
      'trendyol': 'trendyol.com',
      'hepsiburada': 'hepsiburada.com',
      'amazon': 'amazon.com.tr',
      'starbucks': 'starbucks.com.tr',
      'mcdonald': 'mcdonalds.com.tr',
      'burger king': 'burgerking.com.tr',
      'mediamarkt': 'mediamarkt.com.tr',
      'teknosa': 'teknosa.com',
      'boyner': 'boyner.com.tr',
    };
    for (final entry in domains.entries) {
      if (m.contains(entry.key)) {
        return 'https://cdn.brandfetch.io/${entry.value}/w/160/h/160/logo';
      }
    }
    return '';
  }

  String _bankName() {
    final values = [
      campaign['bank_name'],
      campaign['bank'],
      campaign['card_bank'],
      campaign['issuer'],
    ];
    for (final value in values) {
      final v = _text(value);
      if (v.isNotEmpty) return v;
    }
    return '';
  }

  String _cleanTitle(String rawTitle, String merchant, String benefit) {
    final raw = rawTitle.trim();
    final normalized = _norm(raw);
    final generic = raw.isEmpty ||
        normalized == 'kampanya' ||
        normalized.contains(' kampanyalari') ||
        normalized == 'kampanyalar' ||
        normalized == 'kampanyasi';
    if (!generic) return raw;
    if (merchant.isNotEmpty && benefit.isNotEmpty) return "$merchant'de $benefit";
    if (merchant.isNotEmpty) return "$merchant Kampanyası";
    return benefit.isNotEmpty ? benefit : 'Yeni Kampanya';
  }

  String _description(String title, String benefit) {
    final candidates = [
      campaign['description'],
      campaign['campaign_text'],
      campaign['conditions'],
      campaign['terms'],
    ];
    for (final value in candidates) {
      final v = _text(value);
      if (v.isNotEmpty && v.length > 18) {
        return v.replaceAll(RegExp(r'\s+'), ' ');
      }
    }
    if (benefit.isNotEmpty) return 'Kartınızı kullanarak bu kampanyanın avantajından yararlanın.';
    return title;
  }

  String _dateText() {
    final start = _text(campaign['start_date'] ?? campaign['starts_at'] ?? campaign['valid_from']);
    final end = _text(campaign['end_date'] ?? campaign['ends_at'] ?? campaign['valid_until']);
    String shortDate(String value) {
      final match = RegExp(r'(\d{4})-(\d{2})-(\d{2})').firstMatch(value);
      if (match == null) return '';
      return '${match.group(3)}.${match.group(2)}.${match.group(1)}';
    }
    final a = shortDate(start);
    final b = shortDate(end);
    if (a.isNotEmpty && b.isNotEmpty) return '$a - $b';
    if (b.isNotEmpty) return 'Son gün: $b';
    return '';
  }

  Widget _pill(BuildContext context, IconData icon, String label) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 7),
      decoration: BoxDecoration(
        color: const Color(0xFFF0EDFF),
        borderRadius: BorderRadius.circular(18),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 15, color: const Color(0xFF37304F)),
          const SizedBox(width: 5),
          Text(label, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Color(0xFF37304F))),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final merchant = _text(campaign['merchant'] ?? campaign['brand'] ?? campaign['company']);
    final rawTitle = _text(campaign['title']);
    final benefit = _text(_catalogBenefitText(campaign));
    final title = _cleanTitle(rawTitle, merchant, benefit);
    final category = _text(campaign['category']).isNotEmpty ? _text(campaign['category']) : campaignSection(campaign);
    final bank = _bankName();
    final network = _text(campaign['network'] ?? campaign['card_network']);
    final date = _dateText();
    final detail = _text(campaign['detail_url'] ?? campaign['url']);
    final description = _description(title, benefit);
    final logo = _merchantLogo(merchant);
    final expiring = expiringSoon || (daysRemaining > 0 && daysRemaining <= 7);
    final statusText = daysRemaining > 0 ? 'Son $daysRemaining Gün' : (expiring ? 'Yakında Bitiyor' : 'Aktif');

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: const Color(0xFFFAF8FF),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: const Color(0xFFD9D3E4), width: 1.2),
        boxShadow: const [BoxShadow(color: Color(0x12000000), blurRadius: 10, offset: Offset(0, 3))],
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(24),
        onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => CampaignDetailPage(campaign: campaign))),
        child: Padding(
          padding: const EdgeInsets.fromLTRB(16, 15, 14, 14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    width: 72,
                    height: 72,
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(17)),
                    child: logo.isNotEmpty
                        ? _CatalogLogo(logo, size: 56)
                        : const Icon(Icons.local_offer_rounded, size: 42, color: Color(0xFF6B5DD3)),
                  ),
                  const SizedBox(width: 13),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Expanded(
                              child: Text(
                                title,
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                                style: const TextStyle(fontSize: 19, height: 1.12, fontWeight: FontWeight.w800, color: Color(0xFF181624)),
                              ),
                            ),
                            IconButton(
                              visualDensity: VisualDensity.compact,
                              padding: EdgeInsets.zero,
                              constraints: const BoxConstraints(minWidth: 38, minHeight: 38),
                              onPressed: onFavorite,
                              icon: Icon(isFavorite ? Icons.star_rounded : Icons.star_border_rounded, size: 28, color: const Color(0xFF55515E)),
                            ),
                          ],
                        ),
                        if (merchant.isNotEmpty) ...[
                          const SizedBox(height: 3),
                          Text(merchant, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF5E5969))),
                        ],
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 11),
              if (benefit.isNotEmpty)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 9),
                  decoration: BoxDecoration(color: const Color(0xFFECE7FF), borderRadius: BorderRadius.circular(13)),
                  child: Row(
                    children: [
                      const Icon(Icons.card_giftcard_rounded, size: 18, color: Color(0xFF5846C8)),
                      const SizedBox(width: 7),
                      Expanded(child: Text(benefit, maxLines: 2, overflow: TextOverflow.ellipsis, style: const TextStyle(fontWeight: FontWeight.w800, color: Color(0xFF3F347F)))),
                    ],
                  ),
                ),
              const SizedBox(height: 9),
              Text(description, maxLines: 3, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 14, height: 1.3, color: Color(0xFF555061))),
              const SizedBox(height: 11),
              Wrap(
                spacing: 7,
                runSpacing: 7,
                children: [
                  if (category.isNotEmpty) _pill(context, Icons.local_offer_outlined, category),
                  if (bank.isNotEmpty) _pill(context, Icons.credit_card_outlined, bank),
                  if (network.isNotEmpty) _pill(context, Icons.payment_outlined, network),
                  if (date.isNotEmpty) _pill(context, Icons.calendar_month_outlined, date),
                ],
              ),
              const SizedBox(height: 11),
              Row(
                children: [
                  if (expiring)
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
                      decoration: BoxDecoration(color: const Color(0xFFFFE3E3), borderRadius: BorderRadius.circular(16)),
                      child: Row(children: [const Icon(Icons.schedule_rounded, size: 16, color: Color(0xFFB42318)), const SizedBox(width: 5), Text(statusText, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: Color(0xFFB42318)))]),
                    )
                  else
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
                      decoration: BoxDecoration(color: const Color(0xFFDDF8E4), borderRadius: BorderRadius.circular(16)),
                      child: Row(children: [const Icon(Icons.check_circle_outline, size: 16, color: Color(0xFF147A36)), const SizedBox(width: 5), Text(statusText, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: Color(0xFF147A36)))]),
                    ),
                  const Spacer(),
                  IconButton(
                    visualDensity: VisualDensity.compact,
                    onPressed: onCompare,
                    icon: Icon(isCompared ? Icons.compare_arrows_rounded : Icons.compare_arrows_outlined, color: const Color(0xFF55515E)),
                  ),
                  const SizedBox(width: 4),
                  FilledButton(
                    style: FilledButton.styleFrom(backgroundColor: const Color(0xFF6046D8), foregroundColor: Colors.white, padding: const EdgeInsets.symmetric(horizontal: 17, vertical: 11), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18))),
                    onPressed: detail.isEmpty ? () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => CampaignDetailPage(campaign: campaign))) : () => onOpenUrl(detail),
                    child: const Text('Detaylar →', style: TextStyle(fontWeight: FontWeight.w800)),
                  ),
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

s = s[:start] + new + s[end:]
p.write_text(s, encoding='utf-8')
print('v28 catalog reference card applied')
