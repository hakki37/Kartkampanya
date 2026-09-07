from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

start = s.find('class _BrandBadge extends StatelessWidget {')
smart = s.find('class SmartCampaignCard extends StatelessWidget {')
if start < 0 or smart < 0:
    raise SystemExit('Brand/card markers not found')
merchant = s.find('String? _merchantDomain(String merchant) {', start, smart)
end = merchant if merchant >= 0 else smart

badge = r'''String? _logoUrl(String label) {
  final n = _norm(label);
  const slugs = <String, String>{
    'visa': 'visa',
    'mastercard': 'mastercard',
    'troy': 'troy',
    'axess': 'axess',
    'bonus': 'bonus',
    'world': 'world',
    'maximum': 'maximum',
    'paraf': 'paraf',
    'bankkart': 'bankkart',
    'saglam kart': 'kuveytturk',
    'sağlam kart': 'kuveytturk',
    'cepteteb': 'cepteteb',
  };
  final slug = slugs[n];
  return slug == null ? null : 'https://cdn.simpleicons.org/$slug';
}

class _BrandBadge extends StatelessWidget {
  final String label;
  final bool compact;
  const _BrandBadge({required this.label, this.compact = false});

  @override
  Widget build(BuildContext context) {
    final text = label.trim();
    if (text.isEmpty) return const SizedBox.shrink();
    final url = _logoUrl(text);
    if (url == null) {
      return Text(text.toUpperCase(), style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w900));
    }
    return SizedBox(
      width: compact ? 58 : 72,
      height: compact ? 28 : 32,
      child: Padding(
        padding: const EdgeInsets.all(3),
        child: Image.network(
          url,
          fit: BoxFit.contain,
          errorBuilder: (_, __, ___) => Text(text.toUpperCase(), maxLines: 1, overflow: TextOverflow.ellipsis,
            style: const TextStyle(fontSize: 9, fontWeight: FontWeight.w900)),
        ),
      ),
    );
  }
}

'''
s = s[:start] + badge + s[end:]

# Remove white background from merchant logo too; let the actual logo sit directly on the card.
s = s.replace('width: 42, height: 42, padding: const EdgeInsets.all(5), color: Colors.white,', 'width: 42, height: 42, padding: const EdgeInsets.all(5), color: Colors.transparent,')

p.write_text(s, encoding='utf-8')
print('V14 logo polish applied')
