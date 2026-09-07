from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

smart_marker = 'class SmartCampaignCard extends StatelessWidget {'
smart_pos = s.find(smart_marker)
if smart_pos < 0:
    raise SystemExit('SmartCampaignCard marker not found')

# Replace only the old brand-badge section. Do NOT consume the merchant-logo helper
# that V12 may already have inserted before SmartCampaignCard.
brand_start = s.find('class _BrandBadge extends StatelessWidget {')
if brand_start < 0:
    raise SystemExit('Brand badge block not found')
merchant_start = s.find('String? _merchantDomain(String merchant) {', brand_start, smart_pos)
brand_end = merchant_start if merchant_start >= 0 else smart_pos

new_badge = r'''String? _brandLogoDomain(String label) {
  final n = _norm(label);
  const domains = <String, String>{
    'axess': 'axess.com.tr',
    'bonus': 'bonus.com.tr',
    'world': 'worldcard.com.tr',
    'maximum': 'maximum.com.tr',
    'paraf': 'paraf.com.tr',
    'bankkart': 'bankkart.com.tr',
    'saglam kart': 'kuveytturk.com.tr',
    'sağlam kart': 'kuveytturk.com.tr',
    'cepteteb': 'cepteteb.com.tr',
    'visa': 'visa.com',
    'mastercard': 'mastercard.com',
    'troy': 'troyodeme.com',
  };
  return domains[n];
}

class _BrandBadge extends StatelessWidget {
  final String label;
  final bool compact;

  const _BrandBadge({required this.label, this.compact = false});

  @override
  Widget build(BuildContext context) {
    final text = label.trim();
    if (text.isEmpty) return const SizedBox.shrink();
    final domain = _brandLogoDomain(text);
    final width = compact ? 58.0 : 72.0;
    final height = compact ? 30.0 : 34.0;

    if (domain == null) {
      return Container(
        height: height,
        padding: EdgeInsets.symmetric(horizontal: compact ? 7 : 9),
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.surfaceContainerHighest,
          borderRadius: BorderRadius.circular(9),
          border: Border.all(color: Theme.of(context).colorScheme.outline),
        ),
        alignment: Alignment.center,
        child: Text(
          text.toUpperCase(),
          style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w900),
        ),
      );
    }

    return Container(
      width: width,
      height: height,
      padding: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(9),
        border: Border.all(color: Theme.of(context).colorScheme.outline.withOpacity(.45)),
      ),
      child: Image.network(
        'https://www.google.com/s2/favicons?domain=$domain&sz=128',
        fit: BoxFit.contain,
        errorBuilder: (_, __, ___) => Center(
          child: Text(
            text.toUpperCase(),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(fontSize: 9, fontWeight: FontWeight.w900, color: Colors.black87),
          ),
        ),
      ),
    );
  }
}

'''

s = s[:brand_start] + new_badge + s[brand_end:]

# Ensure the merchant-logo helper exists after the badge block and before the card.
smart_pos = s.find(smart_marker)
if 'class _MerchantLogo extends StatelessWidget {' not in s:
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
    s = s[:smart_pos] + helper + s[smart_pos:]

p.write_text(s, encoding='utf-8')
print('v13 brand logos applied safely')