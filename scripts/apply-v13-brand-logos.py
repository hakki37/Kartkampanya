from pathlib import Path
import re

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

start = s.find('class _BrandBadge extends StatelessWidget {')
end = s.find('class SmartCampaignCard extends StatelessWidget {', start)
if start < 0 or end < 0:
    raise SystemExit('Brand badge block not found')

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

s = s[:start] + new_badge + s[end:]
p.write_text(s, encoding='utf-8')
print('v13 brand logos applied')
