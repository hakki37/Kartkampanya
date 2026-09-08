from pathlib import Path
import re

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

smart = s.find('class SmartCampaignCard extends StatelessWidget {')
mycards = s.find('class MyCardsPage extends StatefulWidget {', smart)
if smart < 0 or mycards < 0:
    raise SystemExit('SmartCampaignCard/MyCardsPage boundaries not found')

segment = s[smart:mycards]

# The generated card can contain either `onTap: () => ...` or
# `onTap: () { ... }` depending on the earlier UI patch. Do not depend on
# indentation or the exact closing braces of the bottom sheet.
start_re = re.compile(
    r'onTap\s*:\s*\(\)\s*(?:=>\s*showModalBottomSheet\s*\(|\{\s*showModalBottomSheet\s*\()',
    re.S,
)
m = start_re.search(segment)
if m:
    child_pos = segment.find('child: Padding(', m.end())
    if child_pos < 0:
        raise SystemExit('Campaign card child Padding boundary not found')
    replacement = '''onTap: () {
          Navigator.of(context).push(
            MaterialPageRoute(
              builder: (_) => CampaignDetailPage(campaign: campaign),
            ),
          );
        },
        '''
    segment = segment[:m.start()] + replacement + segment[child_pos:]
    s = s[:smart] + segment + s[mycards:]
    print('campaign detail navigation patched')
else:
    print('campaign detail viewer already patched; continuing')

marker = 'class MyCardsPage extends StatefulWidget {'
if 'class CampaignDetailPage extends StatelessWidget {' not in s:
    detail = r'''class CampaignDetailPage extends StatelessWidget {
  final Map<String, dynamic> campaign;
  const CampaignDetailPage({super.key, required this.campaign});

  String text(dynamic value) => decodeHtmlEntities('${value ?? ''}').trim();

  @override
  Widget build(BuildContext context) {
    final title = text(campaign['title']);
    final merchant = text(campaign['merchant']);
    final bank = text(campaign['bank_name']);
    final card = text(campaign['card_name']);
    final network = text(campaign['network']);
    final category = text(campaign['category']);
    final reward = campaign['_calculatedReward'] ?? campaign['_reward'] ?? campaign['reward_amount'] ?? campaign['max_reward'];
    final min = campaign['min_spend'];
    final source = text(campaign['source_url'] ?? campaign['detail_url'] ?? campaign['url']);
    final bankDomain = _bankDomain(bank);
    final cardDomain = _brandDomain(card);
    final heading = title.isNotEmpty ? title : (merchant.isNotEmpty ? '$merchant Kampanyası' : 'Kampanya');

    return Scaffold(
      appBar: AppBar(
        title: const Text('Kampanya Detayı', style: TextStyle(fontWeight: FontWeight.w900)),
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 32),
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(18),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                if (merchant.isNotEmpty)
                  Text(merchant, style: TextStyle(color: Theme.of(context).colorScheme.primary, fontWeight: FontWeight.w800)),
                const SizedBox(height: 7),
                Text(heading, style: const TextStyle(fontSize: 23, fontWeight: FontWeight.w900, height: 1.18)),
                const SizedBox(height: 18),
                Row(children: [
                  if (bankDomain.isNotEmpty)
                    Container(
                      width: 78, height: 56, padding: const EdgeInsets.all(6),
                      decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(12)),
                      child: _CatalogLogo(_logoUrl(bankDomain), size: 66),
                    )
                  else if (bank.isNotEmpty)
                    Container(
                      width: 78, height: 56, alignment: Alignment.center,
                      decoration: BoxDecoration(color: const Color(0xFF0B1B31), borderRadius: BorderRadius.circular(12)),
                      child: Text(bank, textAlign: TextAlign.center, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w900)),
                    ),
                  const SizedBox(width: 12),
                  Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                    if (bank.isNotEmpty) Text(bank, style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w900)),
                    if (card.isNotEmpty) Row(children: [
                      if (cardDomain.isNotEmpty)
                        Padding(padding: const EdgeInsets.only(right: 6), child: _CatalogLogo(_logoUrl(cardDomain), size: 30)),
                      Expanded(child: Text(card, style: const TextStyle(fontWeight: FontWeight.w700))),
                    ]),
                    if (network.isNotEmpty) Text(network, style: const TextStyle(fontSize: 12, color: Color(0xFF9CA9C1))),
                  ])),
                ]),
              ]),
            ),
          ),
          const SizedBox(height: 10),
          if (category.isNotEmpty) _detailTile(Icons.category_outlined, 'Kategori', category),
          if (reward is num && reward > 0) _detailTile(Icons.savings_outlined, 'Tahmini avantaj', '${reward.toDouble().toStringAsFixed(0)} TL'),
          if (min != null && '$min' != '0') _detailTile(Icons.shopping_cart_outlined, 'Minimum harcama', '$min TL'),
          const SizedBox(height: 8),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                const Text('Kampanya şartları', style: TextStyle(fontSize: 19, fontWeight: FontWeight.w900)),
                const SizedBox(height: 10),
                SelectableText(campaignConditions(campaign), style: const TextStyle(fontSize: 15, height: 1.5)),
              ]),
            ),
          ),
          if (source.isNotEmpty) ...[
            const SizedBox(height: 14),
            SizedBox(
              width: double.infinity,
              child: FilledButton.icon(
                onPressed: () async {
                  final uri = Uri.tryParse(source);
                  if (uri != null && (uri.scheme == 'http' || uri.scheme == 'https')) {
                    await launchUrl(uri, mode: LaunchMode.externalApplication);
                  }
                },
                icon: const Icon(Icons.open_in_new_rounded),
                label: const Text('Kampanya Kaynağına Git'),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _detailTile(IconData icon, String title, String value) => Card(
    margin: const EdgeInsets.only(bottom: 8),
    child: ListTile(
      leading: Icon(icon),
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.w800)),
      subtitle: Text(value),
    ),
  );
}

'''
    if marker not in s:
        raise SystemExit('MyCardsPage marker not found')
    s = s.replace(marker, detail + marker, 1)

# Keep bank/card matching robust across common naming variants.
old = """      const aliases = <String, List<String>>{\n        'kredi': ['kredi', 'kredi karti', 'credit'],"""
new = """      const aliases = <String, List<String>>{\n        'teb': ['teb', 'cepteteb'],\n        'cepteteb': ['teb', 'cepteteb'],\n        'qnb': ['qnb', 'cardfinans'],\n        'cardfinans': ['qnb', 'cardfinans'],\n        'kredi': ['kredi', 'kredi karti', 'credit'],"""
if old in s:
    s = s.replace(old, new, 1)

p.write_text(s, encoding='utf-8')
print('robust v18 detail and matching fixes applied')
