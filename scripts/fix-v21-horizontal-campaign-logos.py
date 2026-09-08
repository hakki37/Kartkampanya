from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

# The campaign cards were still using the old Google favicon endpoint through
# _logoUrl(), so the new v20 CatalogLogo did not affect these logos. Replace
# that shared image widget and URL with wide, high-resolution Brandfetch marks.
start = s.find('class _CatalogLogo extends StatelessWidget {')
end = s.find('\n\nString _catalogMerchantDomain', start)
if start < 0 or end < 0:
    raise SystemExit('_CatalogLogo boundaries not found')

logo = r'''class _CatalogLogo extends StatelessWidget {
  final String url;
  final double size;
  const _CatalogLogo(this.url, {this.size = 40});

  @override
  Widget build(BuildContext context) {
    final wide = size >= 60 ? 112.0 : 96.0;
    final height = size >= 60 ? 42.0 : 34.0;
    return SizedBox(
      width: wide,
      height: height,
      child: Image.network(
        url,
        fit: BoxFit.contain,
        filterQuality: FilterQuality.high,
        errorBuilder: (_, __, ___) => const SizedBox.shrink(),
      ),
    );
  }
}'''
s = s[:start] + logo + s[end:]

old = "String _logoUrl(String domain) =>\n    'https://www.google.com/s2/favicons?domain=$domain&sz=128';"
new = "String _logoUrl(String domain) =>\n    'https://cdn.brandfetch.io/$domain/w/600/h/180/logo';"
if old not in s:
    raise SystemExit('_logoUrl endpoint not found')
s = s.replace(old, new, 1)

p.write_text(s, encoding='utf-8')
print('v21 horizontal high-resolution campaign logos applied')
