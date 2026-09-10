from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

def replace_class(src, name, replacement):
    marker = 'class ' + name
    start = src.find(marker)
    if start < 0:
        return None
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

detail = r'''class CampaignDetailPage extends StatelessWidget {
  final Map<String, dynamic> campaign;
  const CampaignDetailPage({super.key, required this.campaign});

  String _text(dynamic value) => value == null ? '' : '$value'
      .replaceAll(RegExp(r'<[^>]*>'), ' ')
      .replaceAll('&nbsp;', ' ')
      .replaceAll('&amp;', '&')
      .replaceAll('&quot;', '"')
      .replaceAll('&#39;', "'")
      .replaceAll(RegExp(r'\s+'), ' ')
      .trim();

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
      if (installment.isNotEmpty) return installment.toLowerCase().contains('taksit') ? installment : '$installment taksit';
    }
    if (type.contains('indirim') || type.contains('discount')) {
      if (reward.isNotEmpty) return reward.contains('%') ? reward : '%$reward indirim';
    }
    if (reward.isNotEmpty) return reward;
    if (installment.isNotEmpty) return installment.toLowerCase().contains('taksit') ? installment : '$installment taksit';
    return '';
  }

  Widget _info(String title, String value, IconData icon) => Card(
    margin: const EdgeInsets.only(bottom: 8),
    child: ListTile(
      leading: Icon(icon),
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.w900)),
      subtitle: Text(value),
    ),
  );

  @override
  Widget build(BuildContext context) {
    final title = _first(['title', 'name']);
    final merchant = _first(['merchant', 'brand']);
    final description = _first(['description', 'campaign_text', 'summary', 'details', 'content']);
    final conditions = _first(['conditions', 'terms', 'usage_conditions', 'terms_text']);
    final bank = _first(['bank_name', 'bank', 'card_bank']);
    final card = _first(['card_name', 'card', 'card_type']);
    final network = _first(['network', 'card_network']);
    final category = _first(['category']);
    final minimum = _first(['min_spend', 'minimum_spend', 'minimum_spending']);
    final benefit = _benefit();
    final heading = title.isNotEmpty ? title : (merchant.isNotEmpty ? '$merchant Kampanyası' : 'Kampanya');

    return Scaffold(
      appBar: AppBar(title: const Text('Kampanya Detayı', style: TextStyle(fontWeight: FontWeight.w900))),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 32),
        children: [
          Card(child: Padding(padding: const EdgeInsets.all(18), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            if (merchant.isNotEmpty) Text(merchant, style: TextStyle(color: Theme.of(context).colorScheme.primary, fontWeight: FontWeight.w900)),
            const SizedBox(height: 7),
            Text(heading, style: const TextStyle(fontSize: 23, fontWeight: FontWeight.w900, height: 1.18)),
            if (bank.isNotEmpty || card.isNotEmpty || network.isNotEmpty) ...[
              const SizedBox(height: 14),
              Wrap(spacing: 7, runSpacing: 7, children: [if (bank.isNotEmpty) Chip(label: Text(bank)), if (card.isNotEmpty) Chip(label: Text(card)), if (network.isNotEmpty) Chip(label: Text(network))]),
            ],
          ]))),
          if (benefit.isNotEmpty) _info('Tahmini avantaj', benefit, Icons.local_offer_outlined),
          if (minimum.isNotEmpty) _info('Minimum harcama', minimum, Icons.shopping_cart_outlined),
          if (category.isNotEmpty) _info('Kategori', category, Icons.category_outlined),
          if (description.isNotEmpty) ...[
            const SizedBox(height: 8),
            Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              const Text('Açıklama', style: TextStyle(fontSize: 19, fontWeight: FontWeight.w900)),
              const SizedBox(height: 10),
              SelectableText(description, style: const TextStyle(fontSize: 15, height: 1.5)),
            ]))),
          ],
          if (conditions.isNotEmpty) ...[
            const SizedBox(height: 8),
            Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              const Text('Kampanya şartları', style: TextStyle(fontSize: 19, fontWeight: FontWeight.w900)),
              const SizedBox(height: 10),
              SelectableText(conditions, style: const TextStyle(fontSize: 15, height: 1.5)),
            ]))),
          ],
        ],
      ),
    );
  }
}
'''

existing = replace_class(s, 'CampaignDetailPage', detail)
if existing is not None:
    s = existing
else:
    marker = 'class MyCardsPage extends StatefulWidget {'
    if marker not in s:
        raise SystemExit('MyCardsPage marker not found')
    s = s.replace(marker, detail + '\n' + marker, 1)

p.write_text(s, encoding='utf-8')

test = Path('test/widget_test.dart')
if test.exists():
    ts = test.read_text(encoding='utf-8')
    ts = ts.replace('MyApp()', 'KartKampanyaApp()')
    test.write_text(ts, encoding='utf-8')

print('Campaign detail restored with separated description/conditions and semantic benefit')