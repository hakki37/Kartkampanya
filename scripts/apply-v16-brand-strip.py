from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

# Do not depend on the generated campaign-card class name. v16 has changed
# that class name between package revisions. Instead, replace the stable
# bank/card/network logo row emitted by the catalog UI.
old = "Wrap(spacing:4,runSpacing:2,children:[if(b.isNotEmpty)CatalogLogo(label:b),if(card.isNotEmpty)CatalogLogo(label:card),if(n.isNotEmpty)CatalogLogo(label:n)])"
new = "Wrap(spacing:2,runSpacing:2,children:[if(b.isNotEmpty)CatalogLogo(label:b),if(b.isNotEmpty&&card.isNotEmpty)const Padding(padding:EdgeInsets.symmetric(horizontal:5),child:Text('|',style:TextStyle(color:Color(0xFF8090A8),fontSize:20,fontWeight:FontWeight.w300))),if(card.isNotEmpty)CatalogLogo(label:card),if(card.isNotEmpty&&n.isNotEmpty)const Padding(padding:EdgeInsets.symmetric(horizontal:5),child:Text('|',style:TextStyle(color:Color(0xFF8090A8),fontSize:20,fontWeight:FontWeight.w300))),if(n.isNotEmpty)CatalogLogo(label:n)])"

count = s.count(old)
if count:
    s = s.replace(old, new)
    p.write_text(s, encoding='utf-8')
    print(f'v16 bank | card | network separators applied ({count})')
    raise SystemExit(0)

# Pretty-printed fallback: locate the three consecutive logo calls and add
# separators without assuming a specific widget class.
needle = "if(n.isNotEmpty)CatalogLogo(label:n)"
pos = s.find(needle)
if pos >= 0 and "Color(0xFF8090A8)" not in s:
    s = s[:pos] + "if(card.isNotEmpty&&n.isNotEmpty)const Text('|',style:TextStyle(color:Color(0xFF8090A8),fontSize:20,fontWeight:FontWeight.w300))," + s[pos:]
    p.write_text(s, encoding='utf-8')
    print('v16 network separator fallback applied')
    raise SystemExit(0)

# Never break the APK build just because a package revision changed its
# generated logo-row formatting. The existing v16 row is already functional.
print('v16 logo row pattern not found; keeping existing row')
raise SystemExit(0)
