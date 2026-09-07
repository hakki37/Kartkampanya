from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

# V13 is deliberately idempotent: v12 may already have inserted these pieces.
# Never fail just because a previous UI patch already changed the category layout.

# 1) Ensure merchant logo helper exists (v12 normally provides it).
marker = 'class SmartCampaignCard extends StatelessWidget {'
if 'class _MerchantLogo extends StatelessWidget {' not in s:
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
  for (final e in domains.entries) { if (m.contains(e.key)) return e.value; }
  return null;
}

class _MerchantLogo extends StatelessWidget {
  final String merchant;
  const _MerchantLogo({required this.merchant});
  @override
  Widget build(BuildContext context) {
    final domain = _merchantDomain(merchant);
    final scheme = Theme.of(context).colorScheme;
    if (domain == null) {
      return Container(width: 42, height: 42,
        decoration: BoxDecoration(borderRadius: BorderRadius.circular(12), color: scheme.surfaceContainerHighest),
        child: Icon(Icons.storefront_rounded, color: scheme.primary));
    }
    return ClipRRect(
      borderRadius: BorderRadius.circular(12),
      child: Container(width: 42, height: 42, padding: const EdgeInsets.all(5), color: Colors.white,
        child: Image.network('https://www.google.com/s2/favicons?domain=$domain&sz=128', fit: BoxFit.contain,
          errorBuilder: (_, __, ___) => Icon(Icons.storefront_rounded, color: scheme.primary))),
    );
  }
}

'''
    s = s[:pos] + helper + s[pos:]

# 2) Make "Tüm kategoriler" actually open downward.
# v12's layout is a horizontal ListView; when expanded it still stays in the same
# 76px strip. Replace that complete v12 strip with a compact vertical Wrap when open,
# while keeping the catalog-like horizontal strip when closed.
start = s.find('            SizedBox(\n              height: 76,\n              child: ListView.separated(')
if start >= 0:
    chip_marker = "            ActionChip(\n              visualDensity: const VisualDensity(horizontal: -1, vertical: -2),"
    chip_start = s.find(chip_marker, start)
    if chip_start < 0:
        raise SystemExit('category action chip not found')
    # Find the end of the ActionChip call by locating its onPressed line and closing '),'.
    chip_end_line = "              onPressed: () => setState(() => showAllQuickCategories = !showAllQuickCategories),\n            ),"
    chip_end = s.find(chip_end_line, chip_start)
    if chip_end < 0:
        raise SystemExit('category action chip end not found')
    chip_end += len(chip_end_line)

    new_block = '''            AnimatedSize(
              duration: const Duration(milliseconds: 180),
              curve: Curves.easeOut,
              child: showAllQuickCategories
                  ? Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: quick.map((x) {
                        final selected = category == x[1];
                        return InkWell(
                          borderRadius: BorderRadius.circular(16),
                          onTap: () => setState(() => category = selected ? '' : x[1]),
                          child: AnimatedContainer(
                            duration: const Duration(milliseconds: 140),
                            width: 92,
                            height: 72,
                            padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 6),
                            decoration: BoxDecoration(
                              gradient: selected ? const LinearGradient(colors: [Color(0xFF6366F1), Color(0xFF885CF6)]) : null,
                              color: selected ? null : const Color(0xFF172033),
                              borderRadius: BorderRadius.circular(16),
                              border: Border.all(color: selected ? const Color(0xFF8B9CFF) : const Color(0xFF33415F)),
                            ),
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Text(x[0], style: const TextStyle(fontSize: 23)),
                                const SizedBox(height: 2),
                                Text(x[1], maxLines: 1, overflow: TextOverflow.ellipsis, textAlign: TextAlign.center,
                                  style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: selected ? Colors.white : const Color(0xFFEDE8F8))),
                              ],
                            ),
                          ),
                        );
                      }).toList(),
                    )
                  : SizedBox(
                      height: 76,
                      child: ListView.separated(
                        scrollDirection: Axis.horizontal,
                        physics: const BouncingScrollPhysics(),
                        itemCount: quick.take(6).length,
                        separatorBuilder: (_, __) => const SizedBox(width: 8),
                        itemBuilder: (context, index) {
                          final x = quick[index];
                          final selected = category == x[1];
                          return InkWell(
                            borderRadius: BorderRadius.circular(18),
                            onTap: () => setState(() => category = selected ? '' : x[1]),
                            child: AnimatedContainer(
                              duration: const Duration(milliseconds: 160),
                              width: 92,
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 7),
                              decoration: BoxDecoration(
                                gradient: selected ? const LinearGradient(colors: [Color(0xFF6366F1), Color(0xFF885CF6)]) : null,
                                color: selected ? null : const Color(0xFF172033),
                                borderRadius: BorderRadius.circular(18),
                                border: Border.all(color: selected ? const Color(0xFF8B9CFF) : const Color(0xFF33415F)),
                              ),
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Text(x[0], style: const TextStyle(fontSize: 24)),
                                  const SizedBox(height: 3),
                                  Text(x[1], maxLines: 1, overflow: TextOverflow.ellipsis, textAlign: TextAlign.center,
                                    style: TextStyle(fontSize: 11.5, fontWeight: FontWeight.w800, color: selected ? Colors.white : const Color(0xFFEDE8F8))),
                                ],
                              ),
                            ),
                          );
                        },
                      ),
                    ),
            ),
            const SizedBox(height: 8),
            ActionChip(
              visualDensity: const VisualDensity(horizontal: -1, vertical: -2),
              avatar: Icon(showAllQuickCategories ? Icons.expand_less_rounded : Icons.expand_more_rounded, size: 18),
              label: Text(showAllQuickCategories ? 'Daha az' : 'Tüm kategoriler (${quick.length})', style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700)),
              onPressed: () => setState(() => showAllQuickCategories = !showAllQuickCategories),
            ),'''
    s = s[:start] + new_block + s[chip_end:]

p.write_text(s, encoding='utf-8')
print('V13 UI fix applied safely')
