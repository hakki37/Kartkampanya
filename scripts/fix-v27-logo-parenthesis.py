from pathlib import Path
p=Path('lib/main.dart')
s=p.read_text(encoding='utf-8')
start=s.find('class _CatalogLogo extends StatelessWidget {')
if start<0: raise SystemExit('_CatalogLogo not found')
brace=s.find('{',start); depth=0
for i in range(brace,len(s)):
    if s[i]=='{': depth+=1
    elif s[i]=='}':
        depth-=1
        if depth==0: end=i+1; break
else: raise SystemExit('_CatalogLogo end not found')
new=r'''class _CatalogLogo extends StatelessWidget {
  final String url;
  final double size;
  const _CatalogLogo(this.url, {this.size = 42});

  String get fallback {
    final u = url.toLowerCase();
    const map = <String, String>{
      'axess': 'axess', 'akbank': 'AKBANK', 'garanti': 'Garanti BBVA',
      'vakif': 'VakıfBank', 'qnb': 'QNB', 'teb': 'TEB', 'hsbc': 'HSBC',
      'ispark': 'İSPARK', 'migros': 'MİGROS', 'mastercard': 'mastercard',
      'visa': 'VISA', 'troy': 'troy',
    };
    for (final entry in map.entries) {
      if (u.contains(entry.key)) return entry.value;
    }
    return '';
  }

  @override
  Widget build(BuildContext context) {
    final label = fallback;
    return Container(
      width: size * 2.45,
      height: size,
      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 5),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: const Color(0xFFE1E5EC)),
      ),
      alignment: Alignment.center,
      child: Image.network(
        url,
        fit: BoxFit.contain,
        filterQuality: FilterQuality.high,
        errorBuilder: (_, __, ___) {
          if (label.isEmpty) {
            return const Icon(Icons.credit_card_rounded, color: Color(0xFF667085), size: 22);
          }
          return FittedBox(
            fit: BoxFit.scaleDown,
            child: Text(label, maxLines: 1, style: const TextStyle(color: Color(0xFF172033), fontWeight: FontWeight.w900, fontSize: 17)),
          );
        },
      ),
    );
  }
}
'''
s=s[:start]+new+s[end:]
p.write_text(s,encoding='utf-8')
print('v27 structural logo widget applied')
