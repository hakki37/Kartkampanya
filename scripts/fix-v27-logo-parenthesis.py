from pathlib import Path
p=Path('lib/main.dart')
s=p.read_text(encoding='utf-8')
needle="      child: Image.network(url, fit: BoxFit.contain, filterQuality: FilterQuality.high,\n        errorBuilder: (_, __, ___) => label.isEmpty\n          ? const Icon(Icons.credit_card_rounded, color: Color(0xFF667085), size: 22)\n          : FittedBox(child: Text(label, maxLines: 1, style: const TextStyle(color: Color(0xFF172033), fontWeight: FontWeight.w900, fontSize: 17))),\n    );\n  }\n}\n\nString _logoUrl"
repl="      child: Image.network(url, fit: BoxFit.contain, filterQuality: FilterQuality.high,\n        errorBuilder: (_, __, ___) => label.isEmpty\n          ? const Icon(Icons.credit_card_rounded, color: Color(0xFF667085), size: 22)\n          : FittedBox(child: Text(label, maxLines: 1, style: const TextStyle(color: Color(0xFF172033), fontWeight: FontWeight.w900, fontSize: 17))),\n      ),\n    );\n  }\n}\n\nString _logoUrl"
if needle not in s: raise SystemExit('logo block not found')
s=s.replace(needle,repl,1)
p.write_text(s,encoding='utf-8')
print('v27 logo parenthesis fixed')
