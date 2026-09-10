from pathlib import Path
p=Path('lib/main.dart')
s=p.read_text(encoding='utf-8')
if 'void showFilterSheet()' not in s:
    marker='  @override\n  Widget build(BuildContext context) {'
    state=s.find('class _CampaignsPageState')
    pos=s.find(marker,state)
    if pos<0: raise SystemExit('Campaigns build marker not found')
    method=r'''  void showFilterSheet() {
    showModalBottomSheet(
      context: context,
      showDragHandle: true,
      backgroundColor: const Color(0xFFFCFBFE),
      builder: (ctx) => SafeArea(child: Padding(padding: const EdgeInsets.fromLTRB(18, 8, 18, 24), child: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Text('Filtrele', style: TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: Color(0xFF211D2D))),
        const SizedBox(height: 14),
        Wrap(spacing: 8, runSpacing: 8, children: [
          _v29FilterButton(ctx, 'Tümü', ''),
          _v29FilterButton(ctx, 'Market', 'Market'),
          _v29FilterButton(ctx, 'Akaryakıt', 'Akaryakıt'),
          _v29FilterButton(ctx, 'Restoran', 'Restoran'),
          _v29FilterButton(ctx, 'Seyahat', 'Seyahat'),
          _v29FilterButton(ctx, 'E-ticaret', 'E-ticaret'),
          _v29FilterButton(ctx, 'Elektronik', 'Elektronik'),
          _v29FilterButton(ctx, 'Giyim', 'Giyim'),
        ]),
        const SizedBox(height: 12),
        SizedBox(width: double.infinity, child: FilledButton(onPressed: () => Navigator.pop(ctx), style: FilledButton.styleFrom(backgroundColor: const Color(0xFF6D3FEF)), child: const Text('Uygula'))),
      ]))),
    );
  }
  Widget _v29FilterButton(BuildContext ctx, String label, String value) => OutlinedButton(onPressed: () { setState(() => category = value); Navigator.pop(ctx); }, child: Text(label));
'''
    s=s[:pos]+method+s[pos:]
p.write_text(s,encoding='utf-8')
print('v29 filter method repaired')
