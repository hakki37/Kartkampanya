from pathlib import Path
p=Path('lib/main.dart')
s=p.read_text(encoding='utf-8')
patterns=[
("final title = '${campaign['title'] ?? 'Kampanya'}'.trim();", "final title = \"${campaign['title'] ?? 'Kampanya'}\".trim();"),
("final merchant = '${campaign['merchant'] ?? ''}'.trim();", "final merchant = \"${campaign['merchant'] ?? ''}\".trim();"),
("final category = '${campaign['category'] ?? ''}'.trim();", "final category = \"${campaign['category'] ?? ''}\".trim();"),
("final detail = '${campaign['detail_url'] ?? campaign['url'] ?? ''}'.trim();", "final detail = \"${campaign['detail_url'] ?? campaign['url'] ?? ''}\".trim();"),
]
count=0
for old,new in patterns:
    if old in s:
        s=s.replace(old,new,1); count+=1
p.write_text(s,encoding='utf-8')
print(f'v25 fixed {count} nested interpolation lines')
