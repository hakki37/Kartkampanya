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

# Read bank/card/network directly from the campaign. The strip intentionally
# stays text/logo based so it works offline and keeps the catalog compact.
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

  @override
  Widget build(BuildContext context) {
    final values = <String>[
      if (bank.isNotEmpty) bank,
      if (card.isNotEmpty) card,
      if (network.isNotEmpty) network,
    ];
    if (values.isEmpty) return const SizedBox.shrink();

    return Padding(
      padding: const EdgeInsets.only(top: 8, bottom: 4),
      child: Row(
        children: [
          for (int i = 0; i < values.length; i++) ...[
            Expanded(child: Center(child: CatalogLogo(label: values[i]))),
            if (i < values.length - 1)
              const Padding(
                padding: EdgeInsets.symmetric(horizontal: 8),
                child: Text('|', style: TextStyle(color: Color(0xFF8090A8), fontSize: 22, fontWeight: FontWeight.w300)),
              ),
          ],
        ],
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
print('bank | card | network brand strip applied')
