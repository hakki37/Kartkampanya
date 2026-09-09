from pathlib import Path
p=Path('lib/main.dart')
s=p.read_text(encoding='utf-8')
repls={
"final title = '${campaign['title'] ?? 'Kampanya'}'.trim();":"final title = \"${campaign['title'] ?? 'Kampanya'}\".trim();",
"final merchant = '${campaign['merchant'] ?? ''}'.trim();":"final merchant = \"${campaign['merchant'] ?? ''}\".trim();",
"final category = '${campaign['category'] ?? ''}'.trim();":"final category = \"${campaign['category'] ?? ''}\".trim();",
"final detail = '${campaign['detail_url'] ?? campaign['url'] ?? ''}'.trim();":"final detail = \"${campaign['detail_url'] ?? campaign['url'] ?? ''}\".trim();",
}
for old,new in repls.items(): s=s.replace(old,new)
p.write_text(s,encoding='utf-8')
print('v25 Dart interpolation syntax fixed')
