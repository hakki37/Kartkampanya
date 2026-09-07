from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

# 1) Merchant logo helper: always check for the actual class declaration.
if 'class _MerchantLogo extends StatelessWidget' not in s:
    marker = 'class SmartCampaignCard extends StatelessWidget {'
    pos = s.find(marker)
    if pos < 0:
        raise SystemExit('SmartCampaignCard marker not found')
    helper = r'''String? _merchantDomain(String merchant) {
  final m = _norm(merchant);
  const domains = <String, String>{
    'migros':'migros.com.tr', 'shell':'shell.com.tr', 'opet':'opet.com.tr',
    'petrol ofisi':'petrolofisi.com.tr', 'boyner':'boyner.com.tr',
    'trendyol':'trendyol.com', 'hepsiburada':'hepsiburada.com',
    'amazon':'amazon.com.tr', 'n11':'n11.com', 'a101':'a101.com.tr',
    'bim':'bim.com.tr', 'carrefour':'carrefoursa.com', 'starbucks':'starbucks.com.tr',
    'nike':'nike.com', 'apple':'apple.com', 'teknosa':'teknosa.com',
    'vatan':'vatanbilgisayar.com', 'mediamarkt':'mediamarkt.com.tr',
    'lc waikiki':'lcwaikiki.com', 'mavi':'mavi.com', 'zara':'zara.com',
    'ikea':'ikea.com.tr', 'pegasus':'flypgs.com', 'thy':'turkishairlines.com',
    'booking':'booking.com', 'spotify':'spotify.com', 'netflix':'netflix.com',
    'steam':'steampowered.com', 'gastroclub':'gastroclub.com.tr',
    'muhiku':'muhiku.com', 'enuygun':'enuygun.com',
  };
  if (domains.containsKey(m)) return domains[m];
  for (final e in domains.entries) {
    if (m.contains(e.key)) return e.value;
  }
  return null;
}

class _MerchantLogo extends StatelessWidget {
  final String merchant;
  const _MerchantLogo({required this.merchant});
  @override
  Widget build(BuildContext context) {
    final domain = _merchantDomain(merchant);
    final fallback = Container(
      width: 42,
      height: 42,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
        color: Theme.of(context).colorScheme.surfaceContainerHighest,
      ),
      child: Icon(Icons.storefront_rounded, color: Theme.of(context).colorScheme.primary),
    );
    if (domain == null) return fallback;
    return ClipRRect(
      borderRadius: BorderRadius.circular(12),
      child: Container(
        width: 42,
        height: 42,
        padding: const EdgeInsets.all(5),
        color: Colors.white,
        child: Image.network(
          'https://www.google.com/s2/favicons?domain=$domain&sz=128',
          fit: BoxFit.contain,
          errorBuilder: (_, __, ___) => Icon(Icons.storefront_rounded, color: Theme.of(context).colorScheme.primary),
        ),
      ),
    );
  }
}

'''
    s = s[:pos] + helper + s[pos:]

# 2) Ensure the campaign card actually uses the merchant logo.
if '_MerchantLogo(merchant: merchant)' not in s:
    needle = "            Row(\n              children: [\n                Icon(\n                  cards.isNotEmpty\n                      ? Icons.emoji_events\n                      : Icons.local_offer,\n                ),"
    replacement = "            Row(\n              crossAxisAlignment: CrossAxisAlignment.start,\n              children: [\n                if (merchant.isNotEmpty) ...[\n                  _MerchantLogo(merchant: merchant),\n                  const SizedBox(width: 9),\n                ] else ...[\n                  Icon(cards.isNotEmpty ? Icons.emoji_events : Icons.local_offer, size: 25),\n                  const SizedBox(width: 8),\n                ],"
    if needle in s:
        s = s.replace(needle, replacement, 1)

# 3) Compact catalog-style quick categories. Replace only the Wrap after its heading.
anchor = "            const Text(\n              'Hızlı kategoriler',"
pos = s.find(anchor)
if pos < 0:
    raise SystemExit('Hızlı kategoriler heading not found')
start = s.find('            Wrap(\n', pos)
end_marker = '            const SizedBox(height: 14),\n\n            Wrap('
end = s.find(end_marker, start)
if start < 0 or end < 0:
    raise SystemExit('quick category block not found')
new_block = '''            SizedBox(\n              height: 76,\n              child: ListView.separated(\n                scrollDirection: Axis.horizontal,\n                physics: const BouncingScrollPhysics(),\n                itemCount: (showAllQuickCategories ? quick : quick.take(6)).length,\n                separatorBuilder: (_, __) => const SizedBox(width: 8),\n                itemBuilder: (context, index) {\n                  final items = (showAllQuickCategories ? quick : quick.take(6)).toList();\n                  final x = items[index];\n                  final selected = category == x[1];\n                  return InkWell(\n                    borderRadius: BorderRadius.circular(18),\n                    onTap: () => setState(() { category = selected ? '' : x[1]; }),\n                    child: AnimatedContainer(\n                      duration: const Duration(milliseconds: 160),\n                      width: 92,\n                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 7),\n                      decoration: BoxDecoration(\n                        gradient: selected ? const LinearGradient(colors: [Color(0xFF6366F1), Color(0xFF885CF6)]) : null,\n                        color: selected ? null : const Color(0xFF172033),\n                        borderRadius: BorderRadius.circular(18),\n                        border: Border.all(color: selected ? const Color(0xFF8B9CFF) : const Color(0xFF33415F)),\n                      ),\n                      child: Column(\n                        mainAxisAlignment: MainAxisAlignment.center,\n                        children: [\n                          Text(x[0], style: const TextStyle(fontSize: 24)),\n                          const SizedBox(height: 3),\n                          Text(x[1], maxLines: 1, overflow: TextOverflow.ellipsis, textAlign: TextAlign.center,\n                            style: TextStyle(fontSize: 11.5, fontWeight: FontWeight.w800, color: selected ? Colors.white : const Color(0xFFEDE8F8))),\n                        ],\n                      ),\n                    ),\n                  );\n                },\n              ),\n            ),\n            const SizedBox(height: 8),\n            ActionChip(\n              visualDensity: const VisualDensity(horizontal: -1, vertical: -2),\n              avatar: Icon(showAllQuickCategories ? Icons.expand_less_rounded : Icons.expand_more_rounded, size: 18),\n              label: Text(showAllQuickCategories ? 'Daha az' : 'Tüm kategoriler (${quick.length})', style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700)),\n              onPressed: () => setState(() { showAllQuickCategories = !showAllQuickCategories; }),\n            ),\n'''
s = s[:start] + new_block + s[end:]
p.write_text(s, encoding='utf-8')
print('V13 UI fix applied')
