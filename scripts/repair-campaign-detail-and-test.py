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

# Keep the detail page independent from other generated catalog classes. Later
# repair scripts are allowed to replace SmartCampaignCard without breaking the
# detail route's logo helpers.
helpers = r'''String _detailBankDomain(String bank) {
  final b = bank.toLowerCase().replaceAll(' ', '');
  if (b.contains('garanti')) return 'garantibbva.com.tr';
  if (b.contains('akbank')) return 'akbank.com';
  if (b.contains('işbank') || b.contains('isbank') || b.contains('işbankası') || b.contains('isbankasi')) return 'isbank.com.tr';
  if (b.contains('yapı') || b.contains('yapi') || b.contains('world')) return 'yapikredi.com.tr';
  if (b.contains('qnb') || b.contains('cardfinans')) return 'qnb.com.tr';
  if (b.contains('teb') || b.contains('cepteteb')) return 'teb.com.tr';
  if (b.contains('ing')) return 'ing.com.tr';
  if (b.contains('enpara')) return 'enpara.com';
  if (b.contains('vakıf') || b.contains('vakif')) return 'vakifbank.com.tr';
  if (b.contains('halk')) return 'halkbank.com.tr';
  if (b.contains('ziraat')) return 'ziraatbank.com.tr';
  if (b.contains('deniz')) return 'denizbank.com';
  if (b.contains('fibabanka')) return 'fibabanka.com.tr';
  return '';
}

String _detailBrandDomain(String card) {
  final c = card.toLowerCase();
  if (c.contains('world')) return 'worldcard.com.tr';
  if (c.contains('maximum')) return 'maximum.com.tr';
  if (c.contains('bonus')) return 'bonus.com.tr';
  if (c.contains('axess')) return 'axess.com.tr';
  if (c.contains('cardfinans') || c.contains('card finans')) return 'qnb.com.tr';
  if (c.contains('paraf')) return 'paraf.com.tr';
  return '';
}

String _detailLogoUrl(String domain) => 'https://www.google.com/s2/favicons?domain=$domain&sz=128';

class _DetailLogo extends StatelessWidget {
  final String url;
  final double size;
  const _DetailLogo(this.url, {this.size = 40});

  @override
  Widget build(BuildContext context) => ClipRRect(
    borderRadius: BorderRadius.circular(10),
    child: Image.network(
      url,
      width: size,
      height: size,
      fit: BoxFit.contain,
      errorBuilder: (_, __, ___) => const Icon(Icons.credit_card_rounded, size: 28, color: Color(0xFF6C5CE7)),
    ),
  );
}
'''

if 'String _detailBankDomain(String bank)' not in s:
    marker = 'class CampaignDetailPage extends StatelessWidget {'
    if marker not in s:
        raise SystemExit('CampaignDetailPage marker not found for helper insertion')
    s = s.replace(marker, helpers + '\n' + marker, 1)

detail = r'''class CampaignDetailPage extends StatelessWidget {
  final Map<String, dynamic> campaign;
  const CampaignDetailPage({super.key, required this.campaign});

  String _text(dynamic value) => value == null ? '' : decodeHtmlEntities('$value')
      .replaceAll(RegExp(r'<[^>]*>'), ' ')
      .replaceAll(RegExp(r'\\s+'), ' ')
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
    final title = _first(['title', 'name']);
    final description = _first(['campaign_text', 'description', 'summary', 'details', 'content']);
    final text = '$title $description'.toLowerCase();
    final percent = RegExp(r'%\\s*(\\d+(?:[.,]\\d+)?)').firstMatch(text)?.group(1);
    if (percent != null) return '%${percent.replaceAll(',', '.')} indirim';
    final tl = RegExp(r'(\\d[\\d.]*)\\s*tl').firstMatch(text)?.group(1);
    if (tl != null) return '${tl.replaceAll('.', '')} TL avantaj';
    final count = RegExp(r'(\\d+)\\s*taksit').firstMatch(text)?.group(1);
    if (count != null) return '$count taksit';
    return '';
  }

  Widget _chip(String text, IconData icon) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 8),
    decoration: BoxDecoration(
      color: const Color(0xFFF0ECFF),
      borderRadius: BorderRadius.circular(12),
    ),
    child: Row(mainAxisSize: MainAxisSize.min, children: [
      Icon(icon, size: 15, color: const Color(0xFF6246D9)),
      const SizedBox(width: 6),
      Text(text, style: const TextStyle(fontSize: 11.5, fontWeight: FontWeight.w800, color: Color(0xFF30265D))),
    ]),
  );

  Widget _section(String title, String text) => Container(
    margin: const EdgeInsets.only(top: 12),
    padding: const EdgeInsets.all(16),
    decoration: BoxDecoration(
      color: Colors.white,
      border: Border.all(color: const Color(0xFFE8E3F5)),
      borderRadius: BorderRadius.circular(18),
    ),
    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text(title, style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w900, color: Color(0xFF1E1B3A))),
      const SizedBox(height: 9),
      SelectableText(text, style: const TextStyle(fontSize: 14, height: 1.55, color: Color(0xFF5E5A70))),
    ]),
  );

  @override
  Widget build(BuildContext context) {
    final title = _first(['title', 'name']);
    final merchant = _first(['merchant', 'brand']);
    final description = _first(['campaign_text', 'description', 'summary', 'details', 'content']);
    final conditions = _first(['conditions', 'usage_conditions', 'terms_text']);
    final bank = _first(['bank_name', 'bank', 'card_bank']);
    final card = _first(['card_name', 'card']);
    final network = _first(['network', 'card_network']);
    final category = _first(['category']);
    final minimum = _first(['min_spend', 'minimum_spend', 'minimum_spending']);
    final benefit = _benefit();
    final source = _first(['source_url', 'detail_url', 'url']);
    final bankDomain = _detailBankDomain(bank);
    final cardDomain = _detailBrandDomain(card);
    final heading = title.isNotEmpty ? title : (merchant.isNotEmpty ? '$merchant Kampanyası' : 'Kampanya');

    return Scaffold(
      backgroundColor: const Color(0xFFF8F7FC),
      appBar: AppBar(
        backgroundColor: const Color(0xFFF8F7FC),
        foregroundColor: const Color(0xFF1E1B3A),
        elevation: 0,
        title: const Text('Kampanya Detayı', style: TextStyle(fontSize: 17, fontWeight: FontWeight.w900)),
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 4, 16, 34),
        children: [
          Container(
            padding: const EdgeInsets.fromLTRB(18, 20, 18, 18),
            decoration: BoxDecoration(
              gradient: const LinearGradient(colors: [Color(0xFFF0EBFF), Color(0xFFFFFFFF)], begin: Alignment.topLeft, end: Alignment.bottomRight),
              border: Border.all(color: const Color(0xFFE0D9F5)),
              borderRadius: BorderRadius.circular(24),
            ),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Row(children: [
                if (bankDomain.isNotEmpty)
                  Container(
                    width: 62,
                    height: 62,
                    padding: const EdgeInsets.all(7),
                    decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16)),
                    child: _DetailLogo(_detailLogoUrl(bankDomain), size: 48),
                  )
                else
                  Container(
                    width: 62,
                    height: 62,
                    alignment: Alignment.center,
                    decoration: BoxDecoration(color: const Color(0xFF6C5CE7), borderRadius: BorderRadius.circular(16)),
                    child: Text(bank.isNotEmpty ? bank.substring(0, 1).toUpperCase() : 'K', style: const TextStyle(color: Colors.white, fontSize: 25, fontWeight: FontWeight.w900)),
                  ),
                const SizedBox(width: 13),
                Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  if (merchant.isNotEmpty) Text(merchant, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: Color(0xFF6C5CE7))),
                  if (bank.isNotEmpty) Text(bank, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w900, color: Color(0xFF1E1B3A))),
                ])),
              ]),
              const SizedBox(height: 16),
              Text(heading, style: const TextStyle(fontSize: 23, height: 1.16, fontWeight: FontWeight.w900, color: Color(0xFF17152A))),
              if (category.isNotEmpty || card.isNotEmpty || network.isNotEmpty) ...[
                const SizedBox(height: 14),
                Wrap(spacing: 7, runSpacing: 7, children: [
                  if (category.isNotEmpty) _chip(category, Icons.category_outlined),
                  if (card.isNotEmpty) _chip(card, Icons.credit_card_outlined),
                  if (network.isNotEmpty) _chip(network, Icons.account_tree_outlined),
                ]),
              ],
            ]),
          ),
          if (benefit.isNotEmpty || minimum.isNotEmpty) ...[
            const SizedBox(height: 12),
            Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
              if (benefit.isNotEmpty)
                Expanded(child: Container(
                  padding: const EdgeInsets.all(15),
                  decoration: BoxDecoration(color: const Color(0xFFEDE7FF), borderRadius: BorderRadius.circular(18)),
                  child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                    const Icon(Icons.auto_awesome_rounded, color: Color(0xFF6246D9), size: 21),
                    const SizedBox(height: 7),
                    const Text('Avantaj', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: Color(0xFF6F6790))),
                    const SizedBox(height: 2),
                    Text(benefit, maxLines: 2, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w900, color: Color(0xFF3A2A87))),
                  ]),
                )),
              if (benefit.isNotEmpty && minimum.isNotEmpty) const SizedBox(width: 10),
              if (minimum.isNotEmpty)
                Expanded(child: Container(
                  padding: const EdgeInsets.all(15),
                  decoration: BoxDecoration(color: Colors.white, border: Border.all(color: const Color(0xFFE5E1EF)), borderRadius: BorderRadius.circular(18)),
                  child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                    const Icon(Icons.shopping_bag_outlined, color: Color(0xFF6C5CE7), size: 21),
                    const SizedBox(height: 7),
                    const Text('Minimum harcama', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: Color(0xFF6F6790))),
                    const SizedBox(height: 2),
                    Text(minimum, maxLines: 2, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w900, color: Color(0xFF30265D))),
                  ]),
                )),
            ]),
          ],
          if (description.isNotEmpty) _section('Kampanya açıklaması', description),
          if (conditions.isNotEmpty) _section('Kampanya şartları', conditions),
          if (cardDomain.isNotEmpty) ...[
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(color: Colors.white, border: Border.all(color: const Color(0xFFE8E3F5)), borderRadius: BorderRadius.circular(18)),
              child: Row(children: [
                _DetailLogo(_detailLogoUrl(cardDomain), size: 36),
                const SizedBox(width: 10),
                Expanded(child: Text(card, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: Color(0xFF30265D)))),
              ]),
            ),
          ],
          if (source.isNotEmpty) ...[
            const SizedBox(height: 16),
            SizedBox(
              height: 52,
              width: double.infinity,
              child: FilledButton.icon(
                onPressed: () async {
                  final uri = Uri.tryParse(source);
                  if (uri != null && (uri.scheme == 'http' || uri.scheme == 'https')) {
                    await launchUrl(uri, mode: LaunchMode.externalApplication);
                  }
                },
                style: FilledButton.styleFrom(backgroundColor: const Color(0xFF6C5CE7), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(17))),
                icon: const Icon(Icons.open_in_new_rounded),
                label: const Text('Kampanyaya Git', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w900)),
              ),
            ),
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

print('Campaign detail upgraded to reference white/purple card layout with self-contained logos')
