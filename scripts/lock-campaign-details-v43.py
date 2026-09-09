from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

# Add a compact reference-style detail block inside every campaign card.
marker = "              if (cards.isNotEmpty) ...[\n"
if marker not in s:
    raise SystemExit('campaign detail insertion marker not found')

block = r'''              if (bank.isNotEmpty || card.isNotEmpty || network.isNotEmpty) ...[
                const SizedBox(height: 10),
                Wrap(
                  spacing: 7,
                  runSpacing: 7,
                  children: [
                    if (bank.isNotEmpty) _CampaignLogo(label: bank, kind: 'bank'),
                    if (card.isNotEmpty) _CampaignLogo(label: card, kind: 'card'),
                    if (network.isNotEmpty) _CampaignLogo(label: network, kind: 'network'),
                  ],
                ),
                const SizedBox(height: 10),
                if (bank.isNotEmpty)
                  _CampaignInfoRow(Icons.account_balance_rounded, 'Banka', bank),
                if (card.isNotEmpty)
                  _CampaignInfoRow(Icons.credit_card_rounded, 'Kart', card),
                if (network.isNotEmpty)
                  _CampaignInfoRow(Icons.contactless_rounded, 'Kart ağı', network),
                if (reward != null)
                  _CampaignInfoRow(Icons.emoji_events_rounded, 'Tahmini avantaj', '${(reward as num).toDouble().toStringAsFixed(0)} TL'),
                if (min != null && '$min'.trim().isNotEmpty)
                  _CampaignInfoRow(Icons.payments_rounded, 'Minimum harcama', '$min TL'),
              ],
'''
s = s.replace(marker, block + marker, 1)

# Insert small reusable widgets before MyCardsPage.
helper_marker = 'class MyCardsPage extends StatefulWidget {'
if helper_marker not in s:
    raise SystemExit('MyCardsPage marker not found')

helpers = r'''class _CampaignLogo extends StatelessWidget {
  final String label;
  final String kind;
  const _CampaignLogo({required this.label, required this.kind});

  @override
  Widget build(BuildContext context) {
    final normalized = label.toLowerCase();
    String text = label;
    if (normalized.contains('visa')) text = 'VISA';
    if (normalized.contains('master')) text = 'mastercard';
    if (normalized.contains('troy')) text = 'troy';
    if (normalized.contains('akbank')) text = 'AKBANK';
    if (normalized.contains('axess')) text = 'axess';
    return Container(
      constraints: const BoxConstraints(minWidth: 70),
      height: 34,
      padding: const EdgeInsets.symmetric(horizontal: 11),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(9),
        border: Border.all(color: const Color(0xFFE4E0EF)),
        boxShadow: const [BoxShadow(color: Color(0x08000000), blurRadius: 5, offset: Offset(0, 2))],
      ),
      alignment: Alignment.center,
      child: Text(
        text,
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
        style: TextStyle(
          fontSize: kind == 'network' ? 12 : 11,
          fontWeight: FontWeight.w900,
          letterSpacing: normalized.contains('master') ? -0.3 : 0,
          color: const Color(0xFF242032),
        ),
      ),
    );
  }
}

class _CampaignInfoRow extends StatelessWidget {
  final IconData icon;
  final String title;
  final String value;
  const _CampaignInfoRow(this.icon, this.title, this.value);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 7),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Icon(icon, size: 21, color: const Color(0xFF6D3DF5)),
          const SizedBox(width: 10),
          Expanded(
            child: RichText(
              text: TextSpan(
                style: const TextStyle(fontSize: 12, color: Color(0xFF4D4859)),
                children: [
                  TextSpan(text: '$title: ', style: const TextStyle(fontWeight: FontWeight.w800, color: Color(0xFF211D2D))),
                  TextSpan(text: value, style: const TextStyle(fontWeight: FontWeight.w600)),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

'''
s = s.replace(helper_marker, helpers + helper_marker, 1)
p.write_text(s, encoding='utf-8')
print('v43 campaign details locked')
