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


def replace_method(src, state, method, replacement):
    st = src.find('class ' + state)
    start = src.find('  @override\n  Widget ' + method, st)
    if start < 0:
        raise SystemExit(state + ' ' + method + ' not found')
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
    raise SystemExit(method + ' end not found')

# Keep the Claude visual direction, but use deliberately simple Dart so the generated
# campaign card cannot break the parser with deeply nested one-line widgets.
smart = r'''class SmartCampaignCard extends StatelessWidget {
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

  @override
  Widget build(BuildContext context) {
    final title = _claudeCleanTitle(campaign);
    final merchant = decodeHtmlEntities('${campaign['merchant'] ?? ''}').trim();
    final description = decodeHtmlEntities(
      '${campaign['description'] ?? campaign['campaign_text'] ?? ''}',
    ).replaceAll(RegExp(r'\s+'), ' ').trim();
    final category = decodeHtmlEntities('${campaign['category'] ?? ''}').trim();
    final date = _claudeDate(campaign);
    final logo = _claudeMerchantUrl(merchant);
    final rawReward = campaign['_calculatedReward'] ?? campaign['_reward'];

    String initials(String value) {
      final clean = value.trim();
      if (clean.isEmpty) return 'K';
      final parts = clean.split(RegExp(r'\s+'));
      if (parts.length > 1) {
        return '${parts.first[0]}${parts.last[0]}'.toUpperCase();
      }
      return parts.first.substring(0, 1).toUpperCase();
    }

    Widget logoWidget() {
      if (logo.isEmpty) {
        return Center(
          child: Text(
            initials(merchant),
            style: const TextStyle(
              fontSize: 25,
              fontWeight: FontWeight.w900,
              color: Color(0xFF6C5CE7),
            ),
          ),
        );
      }
      return Image.network(
        logo,
        fit: BoxFit.contain,
        errorBuilder: (_, __, ___) => Center(
          child: Text(
            initials(merchant),
            style: const TextStyle(
              fontSize: 25,
              fontWeight: FontWeight.w900,
              color: Color(0xFF6C5CE7),
            ),
          ),
        ),
      );
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 13),
      padding: const EdgeInsets.fromLTRB(14, 14, 14, 13),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: const Color(0xFFECEAF3)),
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(18),
        onTap: () {
          Navigator.of(context).push(
            MaterialPageRoute(
              builder: (_) => CampaignDetailPage(campaign: campaign),
            ),
          );
        },
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 96,
                  height: 96,
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF8F7FB),
                    borderRadius: BorderRadius.circular(15),
                  ),
                  child: logoWidget(),
                ),
                const SizedBox(width: 13),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Expanded(
                            child: Text(
                              title,
                              maxLines: 3,
                              overflow: TextOverflow.ellipsis,
                              style: const TextStyle(
                                fontSize: 16.5,
                                height: 1.12,
                                fontWeight: FontWeight.w900,
                                color: Color(0xFF1E1B2E),
                              ),
                            ),
                          ),
                          IconButton(
                            onPressed: onFavorite,
                            padding: EdgeInsets.zero,
                            constraints: const BoxConstraints(
                              minWidth: 34,
                              minHeight: 34,
                            ),
                            icon: Icon(
                              isFavorite
                                  ? Icons.star_rounded
                                  : Icons.star_border_rounded,
                              size: 29,
                              color: const Color(0xFF575361),
                            ),
                          ),
                        ],
                      ),
                      if (expiringSoon)
                        Align(
                          alignment: Alignment.centerRight,
                          child: Container(
                            margin: const EdgeInsets.only(top: 2),
                            padding: const EdgeInsets.symmetric(
                              horizontal: 10,
                              vertical: 6,
                            ),
                            decoration: BoxDecoration(
                              color: daysRemaining <= 3
                                  ? const Color(0xFFFDE7E9)
                                  : const Color(0xFFE3F9EB),
                              borderRadius: BorderRadius.circular(18),
                            ),
                            child: Text(
                              daysRemaining <= 0
                                  ? 'Son gün'
                                  : 'Son $daysRemaining Gün',
                              style: TextStyle(
                                fontSize: 10,
                                fontWeight: FontWeight.w800,
                                color: daysRemaining <= 3
                                    ? const Color(0xFFE0435C)
                                    : const Color(0xFF1EA35A),
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
                  fontSize: 12.5,
                  height: 1.28,
                  color: Color(0xFF676373),
                ),
              ),
            ],
            const SizedBox(height: 11),
            Wrap(
              spacing: 7,
              runSpacing: 7,
              children: [
                if (category.isNotEmpty)
                  _infoChip(Icons.local_offer_outlined, category),
                if (merchant.isNotEmpty)
                  _infoChip(Icons.credit_card_outlined, merchant),
                if (date.isNotEmpty)
                  _infoChip(Icons.calendar_today_outlined, date),
                if (rawReward is num)
                  _infoChip(
                    Icons.card_giftcard_outlined,
                    '${rawReward.toStringAsFixed(0)} TL',
                  ),
              ],
            ),
            const SizedBox(height: 11),
            Row(
              children: [
                const Spacer(),
                IconButton(
                  onPressed: onCompare,
                  icon: Icon(
                    isCompared
                        ? Icons.compare_arrows_rounded
                        : Icons.compare_arrows_outlined,
                    size: 22,
                    color: const Color(0xFF5A5662),
                  ),
                ),
                const SizedBox(width: 2),
                Container(
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFF7B45EF), Color(0xFF6840D9)],
                    ),
                    borderRadius: BorderRadius.circular(13),
                  ),
                  child: TextButton(
                    onPressed: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (_) => CampaignDetailPage(campaign: campaign),
                        ),
                      );
                    },
                    style: TextButton.styleFrom(
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(
                        horizontal: 18,
                        vertical: 11,
                      ),
                    ),
                    child: const Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          'Detaylar',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                        SizedBox(width: 4),
                        Icon(Icons.arrow_forward_rounded, size: 16),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _infoChip(IconData icon, String text) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
      decoration: BoxDecoration(
        color: const Color(0xFFF1EFFA),
        borderRadius: BorderRadius.circular(15),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 13, color: const Color(0xFF4A4762)),
          const SizedBox(width: 5),
          ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 145),
            child: Text(
              text,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(
                fontSize: 10.5,
                fontWeight: FontWeight.w600,
                color: Color(0xFF4A4762),
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
print('Claude UI syntax repaired')
