from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

# V12: Mor-Mavi + compact cards + merchant logos.
repls = {
    '0xFF8B5CF6': '0xFF6366F1', '0xFF9B7CFF': '0xFF6366F1',
    '0xFF35245F': '0xFF27306B', '0xFFC4B5FD': '0xFF885CF6',
    '0xFF15121E': '0xFF111827', '0xFF211C2D': '0xFF1E293B',
    '0xFF51466A': '0xFF3B4565', '0xFF0D0B14': '0xFF0F172A',
    '0xFF171421': '0xFF111827', '0xFF292238': '0xFF293554',
    '0xFF302842': '0xFF33415F', '0xFF191622': '0xFF172033',
    '0xFF5B3FA8': '0xFF3949A3', '0xFF342B48': '0xFF33415F',
    '0xFF110E18': '0xFF0B1220', '0xFF49317A': '0xFF4B3CC4',
    '0xFF8062E8': '0xFF6366F1',
}
for a, b in repls.items():
    s = s.replace(a, b)

s = s.replace('margin: const EdgeInsets.only(bottom: 14),', 'margin: const EdgeInsets.only(bottom: 8),', 1)
s = s.replace('padding: const EdgeInsets.all(14),\n        child: Column(', 'padding: const EdgeInsets.fromLTRB(10, 9, 10, 10),\n        child: Column(', 1)

# Always make the merchant-logo widget available before SmartCampaignCard.
# This guard deliberately checks the class declaration itself, not a reference/call.
marker = 'class SmartCampaignCard extends StatelessWidget {'
helper = r'''String? _merchantDomain(String merchant) {
  final m = _norm(merchant);
  const domains = <String, String>{
    'migros': 'migros.com.tr', 'shell': 'shell.com.tr', 'opet': 'opet.com.tr',
    'petrol ofisi': 'petrolofisi.com.tr', 'boyner': 'boyner.com.tr',
    'trendyol': 'trendyol.com', 'hepsiburada': 'hepsiburada.com',
    'amazon': 'amazon.com.tr', 'n11': 'n11.com', 'a101': 'a101.com.tr',
    'bim': 'bim.com.tr', 'carrefour': 'carrefoursa.com', 'starbucks': 'starbucks.com.tr',
    'nike': 'nike.com', 'apple': 'apple.com', 'teknosa': 'teknosa.com',
    'vatan': 'vatanbilgisayar.com', 'mediamarkt': 'mediamarkt.com.tr',
    'lc waikiki': 'lcwaikiki.com', 'mavi': 'mavi.com', 'zara': 'zara.com',
    'ikea': 'ikea.com.tr', 'pegasus': 'flypgs.com', 'thy': 'turkishairlines.com',
    'booking': 'booking.com', 'spotify': 'spotify.com', 'netflix': 'netflix.com',
    'steam': 'steampowered.com', 'gastroclub': 'gastroclub.com.tr',
    'muhiku': 'muhiku.com', 'enuygun': 'enuygun.com',
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
    final scheme = Theme.of(context).colorScheme;
    final fallback = Container(
      width: 42, height: 42,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
        color: scheme.surfaceContainerHighest,
      ),
      child: Icon(Icons.storefront_rounded, color: scheme.primary),
    );
    if (domain == null) return fallback;
    return ClipRRect(
      borderRadius: BorderRadius.circular(12),
      child: Container(
        width: 42, height: 42, padding: const EdgeInsets.all(5), color: Colors.white,
        child: Image.network(
          'https://www.google.com/s2/favicons?domain=$domain&sz=128',
          fit: BoxFit.contain,
          errorBuilder: (_, __, ___) => Icon(Icons.storefront_rounded, color: scheme.primary),
        ),
      ),
    );
  }
}

'''
# Remove any duplicate helper block produced by earlier attempts, then insert exactly one.
start = s.find('String? _merchantDomain(String merchant) {')
if start != -1:
    end = s.find(marker, start)
    if end != -1:
        s = s[:start] + s[end:]
if 'class _MerchantLogo extends StatelessWidget {' not in s:
    s = s.replace(marker, helper + marker, 1)

# Compact campaign title row.
old_title = '''            Row(
              children: [
                Icon(
                  cards.isNotEmpty
                      ? Icons.emoji_events
                      : Icons.local_offer,
                ),

                const SizedBox(width: 8),

                Expanded(
  child: Text(
    decodeHtmlEntities(
      campaign['title']?.toString().trim() ?? '',
    ),
    style: const TextStyle(
      fontSize: 17,
      fontWeight: FontWeight.bold,
    ),
  ),
),'''
new_title = '''            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (merchant.isNotEmpty) ...[
                  _MerchantLogo(merchant: merchant),
                  const SizedBox(width: 9),
                ] else ...[
                  Icon(cards.isNotEmpty ? Icons.emoji_events : Icons.local_offer, size: 25),
                  const SizedBox(width: 8),
                ],
                Expanded(
                  child: Text(
                    campaignTitle.isNotEmpty ? campaignTitle : '$merchant Kampanyası',
                    maxLines: 3,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(fontSize: 15.5, height: 1.2, fontWeight: FontWeight.w800),
                  ),
                ),'''
if old_title in s:
    s = s.replace(old_title, new_title, 1)

s = s.replace('onPressed: onFavorite,\n                  icon: Icon(', 'onPressed: onFavorite,\n                  constraints: const BoxConstraints(minWidth: 36, minHeight: 36),\n                  padding: EdgeInsets.zero,\n                  icon: Icon(', 1)
s = s.replace('onPressed: onCompare,\n                  icon: Icon(', 'onPressed: onCompare,\n                  constraints: const BoxConstraints(minWidth: 36, minHeight: 36),\n                  padding: EdgeInsets.zero,\n                  icon: Icon(', 1)
s = s.replace('padding: const EdgeInsets.only(top: 2),\n                child: Wrap(\n                  spacing: 6,\n                  runSpacing: 6,', 'padding: const EdgeInsets.only(top: 5),\n                child: Wrap(\n                  spacing: 5,\n                  runSpacing: 4,', 1)
s = s.replace('ℹ️ Bu kampanya kayıtlı kartlarınla eşleşmiyor.', 'ℹ️ Kayıtlı kartlarınla eşleşmiyor', 1)

# Katalog-6 style quick category strip.
anchor = "            const Text(\n              'Hızlı kategoriler',"
anchor_pos = s.find(anchor)
if anchor_pos == -1:
    raise SystemExit('quick category heading not found')
wrap_start = s.find('            Wrap(\n', anchor_pos)
if wrap_start == -1:
    raise SystemExit('quick category Wrap start not found')
end_marker = '            const SizedBox(height: 14),\n\n            Wrap('
wrap_end = s.find(end_marker, wrap_start)
if wrap_end == -1:
    raise SystemExit('quick category Wrap end marker not found')
replacement = '''            SizedBox(
              height: 76,
              child: ListView.separated(
                scrollDirection: Axis.horizontal,
                physics: const BouncingScrollPhysics(),
                itemCount: (showAllQuickCategories ? quick : quick.take(6)).length,
                separatorBuilder: (_, __) => const SizedBox(width: 8),
                itemBuilder: (context, index) {
                  final items = (showAllQuickCategories ? quick : quick.take(6)).toList();
                  final x = items[index];
                  final selected = category == x[1];
                  return InkWell(
                    borderRadius: BorderRadius.circular(18),
                    onTap: () => setState(() => category = selected ? '' : x[1]),
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 160), width: 92,
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
            const SizedBox(height: 8),
            ActionChip(
              visualDensity: const VisualDensity(horizontal: -1, vertical: -2),
              avatar: Icon(showAllQuickCategories ? Icons.expand_less_rounded : Icons.expand_more_rounded, size: 18),
              label: Text(showAllQuickCategories ? 'Daha az' : 'Tüm kategoriler (${quick.length})', style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700)),
              onPressed: () => setState(() => showAllQuickCategories = !showAllQuickCategories),
            ),
'''
s = s[:wrap_start] + replacement + s[wrap_end:]
p.write_text(s, encoding='utf-8')
print('v12 UI applied successfully')
