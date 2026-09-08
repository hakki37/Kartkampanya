from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

smart = s.find('class SmartCampaignCard extends StatelessWidget {')
if smart < 0:
    raise SystemExit('SmartCampaignCard not found')
end = s.find('class CampaignDetailPage', smart)
if end < 0:
    end = len(s)
block = s[smart:end]

if 'final displayNetwork = decodeHtmlEntities' not in block:
    marker = "final card = decodeHtmlEntities('${campaign['card_name'] ?? ''}').trim();"
    pos = block.find(marker)
    if pos < 0:
        raise SystemExit('SmartCampaignCard card variable not found')
    pos += len(marker)
    block = block[:pos] + "\n    final displayNetwork = decodeHtmlEntities('${campaign['network'] ?? ''}').trim();" + block[pos:]

if 'class _CatalogBrandStrip' not in s:
    helper = '''class _CatalogBrandStrip extends StatelessWidget {
  final String bank;
  final String card;
  final String network;
  const _CatalogBrandStrip({required this.bank, required this.card, required this.network});

  Widget _logo(String domain) => domain.isEmpty
      ? const SizedBox.shrink()
      : _CatalogLogo(_logoUrl(domain), size: 44);

  @override
  Widget build(BuildContext context) {
    final bankDomain = _bankDomain(bank);
    final cardDomain = _brandDomain(card);
    final hasNetwork = network.isNotEmpty;
    if (bankDomain.isEmpty && cardDomain.isEmpty && !hasNetwork) return const SizedBox.shrink();

    final parts = <Widget>[];
    if (bankDomain.isNotEmpty) parts.add(_logo(bankDomain));
    if (cardDomain.isNotEmpty) {
      if (parts.isNotEmpty) parts.add(const _BrandDivider());
      parts.add(_logo(cardDomain));
    }
    if (hasNetwork) {
      if (parts.isNotEmpty) parts.add(const _BrandDivider());
      parts.add(_NetworkBrandLogo(network));
    }

    return Padding(
      padding: const EdgeInsets.only(top: 8, bottom: 5),
      child: Row(children: parts),
    );
  }
}

class _BrandDivider extends StatelessWidget {
  const _BrandDivider();
  @override
  Widget build(BuildContext context) => const Padding(
    padding: EdgeInsets.symmetric(horizontal: 14),
    child: SizedBox(height: 34, child: VerticalDivider(width: 1, thickness: 1, color: Color(0xFF7E8AA0))),
  );
}

class _NetworkBrandLogo extends StatelessWidget {
  final String network;
  const _NetworkBrandLogo(this.network);
  @override
  Widget build(BuildContext context) {
    final n = network.toLowerCase();
    final slug = n.contains('master') ? 'mastercard' : n.contains('troy') ? 'troy' : 'visa';
    return Padding(
      padding: const EdgeInsets.only(left: 2),
      child: Image.network(
        'https://cdn.simpleicons.org/$slug',
        height: 34,
        width: 90,
        fit: BoxFit.contain,
        errorBuilder: (_, __, ___) => Text(network, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900)),
      ),
    );
  }
}

'''
    s = s[:smart] + helper + s[smart:]
    smart += len(helper)
    end = s.find('class CampaignDetailPage', smart)
    if end < 0:
        end = len(s)
    block = s[smart:end]

if '_CatalogBrandStrip(bank: bank, card: card, network: displayNetwork)' not in block:
    marker = 'if (category.isNotEmpty || spend != null)'
    pos = block.find(marker)
    if pos < 0:
        raise SystemExit('SmartCampaignCard category marker not found')
    strip = '_CatalogBrandStrip(bank: bank, card: card, network: displayNetwork),\n\n            '
    block = block[:pos] + strip + block[pos:]

s = s[:smart] + block + s[end:]
p.write_text(s, encoding='utf-8')
print('bank | card | network logos applied')
