from pathlib import Path
p=Path('lib/main.dart')
s=p.read_text(encoding='utf-8')
start=s.find('class SmartCampaignCard extends StatelessWidget {')
if start<0: raise SystemExit('SmartCampaignCard not found')
brace=s.find('{',start); depth=0
for i in range(brace,len(s)):
    if s[i]=='{': depth+=1
    elif s[i]=='}':
        depth-=1
        if depth==0: end=i+1; break
else: raise SystemExit('SmartCampaignCard end not found')
new=r'''class SmartCampaignCard extends StatelessWidget {
  final Map<String, dynamic> campaign;
  final bool isFavorite;
  final bool isCompared;
  final bool showAllCampaigns;
  final bool expiringSoon;
  final int daysRemaining;
  final VoidCallback onFavorite;
  final VoidCallback onCompare;
  final Future<void> Function(String url) onOpenUrl;
  final int requiredSteps;
  final int completedSteps;
  final ValueChanged<int> onProgressChange;
  const SmartCampaignCard({super.key, required this.campaign, required this.isFavorite, required this.isCompared, required this.showAllCampaigns, required this.expiringSoon, required this.daysRemaining, required this.onFavorite, required this.onCompare, required this.onOpenUrl, required this.requiredSteps, required this.completedSteps, required this.onProgressChange});
  @override
  Widget build(BuildContext context) {
    final title = campaign['title']?.toString() ?? 'Kampanya';
    final merchant = campaign['merchant']?.toString() ?? '';
    final category = campaign['category']?.toString() ?? '';
    final detail = campaign['detail_url']?.toString() ?? campaign['url']?.toString() ?? '';
    final lower = merchant.toLowerCase();
    String logo = '';
    if (lower.contains('ispark')) logo = 'https://cdn.brandfetch.io/ispark.istanbul/w/600/h/180/logo';
    if (lower.contains('migros')) logo = 'https://cdn.brandfetch.io/migros.com.tr/w/600/h/180/logo';
    if (lower.contains('trendyol')) logo = 'https://cdn.brandfetch.io/trendyol.com/w/600/h/180/logo';
    if (lower.contains('hepsiburada')) logo = 'https://cdn.brandfetch.io/hepsiburada.com/w/600/h/180/logo';
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(color: const Color(0xFF121A2A), borderRadius: BorderRadius.circular(24), border: Border.all(color: const Color(0xFF34445E), width: 1.2)),
      child: InkWell(
        borderRadius: BorderRadius.circular(20),
        onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => CampaignDetailPage(campaign: campaign))),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            logo.isNotEmpty ? _CatalogLogo(logo, size: 52) : const SizedBox(width: 8),
            const SizedBox(width: 12),
            Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: <Widget>[
              Text(title, maxLines: 3, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 18, height: 1.15, fontWeight: FontWeight.w800, color: Colors.white)),
              const SizedBox(height: 5),
              Text(merchant, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 13, color: Color(0xFFB8C2D8), fontWeight: FontWeight.w600)),
              const SizedBox(height: 10),
              Wrap(spacing: 7, runSpacing: 7, children: <Widget>[
                if (category.isNotEmpty) Container(padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 6), decoration: BoxDecoration(color: const Color(0xFF5D43E7).withOpacity(.25), borderRadius: BorderRadius.circular(18)), child: Text(category, style: const TextStyle(color: Color(0xFFD5CCFF), fontWeight: FontWeight.w700))),
                if (lower.contains('ispark')) const _CatalogLogo('https://cdn.brandfetch.io/ispark.istanbul/w/600/h/180/logo', size: 32),
                if (lower.contains('migros')) const _CatalogLogo('https://cdn.brandfetch.io/migros.com.tr/w/600/h/180/logo', size: 32),
              ]),
            ])),
            IconButton(onPressed: onFavorite, icon: Icon(isFavorite ? Icons.star_rounded : Icons.star_border_rounded, color: Colors.white70)),
            IconButton(onPressed: detail.isEmpty ? null : () => onOpenUrl(detail), icon: const Icon(Icons.arrow_forward_rounded, color: Colors.white70)),
          ],
        ),
      ),
    );
  }
}
'''
s=s[:start]+new+s[end:]
p.write_text(s,encoding='utf-8')
print('v26 applied')
