from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

# The catalog card navigates to this page. Keep title, description and conditions
# semantically separate so campaign copy never gets mixed together.
if 'class CampaignDetailPage extends StatelessWidget {' not in s:
    marker = 'class MyCardsPage extends StatefulWidget {'
    if marker not in s:
        raise SystemExit('MyCardsPage marker not found')
    detail = r'''class CampaignDetailPage extends StatelessWidget {
  final Map<String, dynamic> campaign;
  const CampaignDetailPage({super.key, required this.campaign});

  String _text(dynamic value) {
    if (value == null) return '';
    return '$value'
        .replaceAll(RegExp(r'<[^>]*>'), ' ')
        .replaceAll('&nbsp;', ' ')
        .replaceAll('&amp;', '&')
        .replaceAll('&quot;', '"')
        .replaceAll('&#39;', "'")
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

  Widget _info(String title, String value, IconData icon) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Icon(icon),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.w900)),
        subtitle: Text(value),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final title = _first(['title', 'name']);
    final merchant = _first(['merchant', 'brand']);
    final description = _first([
      'description',
      'campaign_text',
      'summary',
      'details',
      'content',
    ]);
    final conditions = _first([
      'conditions',
      'terms',
      'usage_conditions',
      'terms_text',
    ]);
    final bank = _first(['bank_name', 'bank', 'card_bank']);
    final card = _first(['card_name', 'card', 'card_type']);
    final network = _first(['network', 'card_network']);
    final category = _first(['category']);
    final minimum = _first(['min_spend', 'minimum_spend', 'minimum_spending']);
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
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (merchant.isNotEmpty)
                    Text(
                      merchant,
                      style: TextStyle(
                        color: Theme.of(context).colorScheme.primary,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                  const SizedBox(height: 7),
                  Text(
                    heading,
                    style: const TextStyle(fontSize: 23, fontWeight: FontWeight.w900, height: 1.18),
                  ),
                  if (bank.isNotEmpty || card.isNotEmpty || network.isNotEmpty) ...[
                    const SizedBox(height: 14),
                    Wrap(
                      spacing: 7,
                      runSpacing: 7,
                      children: [
                        if (bank.isNotEmpty) Chip(label: Text(bank)),
                        if (card.isNotEmpty) Chip(label: Text(card)),
                        if (network.isNotEmpty) Chip(label: Text(network)),
                      ],
                    ),
                  ],
                ],
              ),
            ),
          ),
          if (category.isNotEmpty) _info('Kategori', category, Icons.category_outlined),
          if (minimum.isNotEmpty) _info('Minimum harcama', minimum, Icons.shopping_cart_outlined),
          if (description.isNotEmpty) ...[
            const SizedBox(height: 8),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Açıklama', style: TextStyle(fontSize: 19, fontWeight: FontWeight.w900)),
                    const SizedBox(height: 10),
                    SelectableText(description, style: const TextStyle(fontSize: 15, height: 1.5)),
                  ],
                ),
              ),
            ),
          ],
          if (conditions.isNotEmpty) ...[
            const SizedBox(height: 8),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Kampanya şartları', style: TextStyle(fontSize: 19, fontWeight: FontWeight.w900)),
                    const SizedBox(height: 10),
                    SelectableText(conditions, style: const TextStyle(fontSize: 15, height: 1.5)),
                  ],
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}

'''
    s = s.replace(marker, detail + marker, 1)

p.write_text(s, encoding='utf-8')

# The generated Flutter test still references the old starter class. It should
# compile against the actual app root without changing production behavior.
test = Path('test/widget_test.dart')
if test.exists():
    ts = test.read_text(encoding='utf-8')
    ts = ts.replace('MyApp()', 'KartKampanyaApp()')
    test.write_text(ts, encoding='utf-8')

print('Campaign detail restored and widget test aligned with KartKampanyaApp')
