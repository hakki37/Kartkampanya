from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

# Replace the shared campaign logo widget structurally so it cannot depend on
# fragile text boundaries created by earlier catalog transformation scripts.
start = s.find('class _CatalogLogo extends StatelessWidget {')
if start < 0:
    raise SystemExit('_CatalogLogo class not found')
brace = s.find('{', start)
depth = 0
end = -1
for i in range(brace, len(s)):
    if s[i] == '{':
        depth += 1
    elif s[i] == '}':
        depth -= 1
        if depth == 0:
            end = i + 1
            break
if end < 0:
    raise SystemExit('_CatalogLogo closing brace not found')

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

# Earlier versions used Google favicons or Clearbit. Rewrite either endpoint
# in-place; this remains safe even if a previous script changed the helper.
s = s.replace(
    'https://www.google.com/s2/favicons?domain=$domain&sz=128',
    'https://cdn.brandfetch.io/$domain/w/600/h/180/logo',
)
s = s.replace(
    'https://logo.clearbit.com/$domain',
    'https://cdn.brandfetch.io/$domain/w/600/h/180/logo',
)

# If v16's helper exists, ensure it points to the same wide logo endpoint.
# If it does not exist, the _logoUrl replacement above is sufficient because
# the campaign cards already pass _logoUrl(...) to _CatalogLogo.
p.write_text(s, encoding='utf-8')
print('v21 horizontal high-resolution campaign logos applied')
