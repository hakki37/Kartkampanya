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

  const SmartCampaignCard({
    super.key,
    required this.campaign,
    required this.isFavorite,
    required this.isCompared,
    required this.showAllCampaigns,
    required this.expiringSoon,
    required this.daysRemaining,
    required this.onFavorite,
    required this.onCompare,
    required this.onOpenUrl,
    required this.requiredSteps,
    required this.completedSteps,
    required this.onProgressChange,
  });

  @override
  Widget build(BuildContext context) {
    final title = '${campaign['title'] ?? 'Kampanya'}'.trim();
    final merchant = '${campaign['merchant'] ?? ''}'.trim();
    final category = '${campaign['category'] ?? ''}'.trim();
    final detail = '${campaign['detail_url'] ?? campaign['url'] ?? ''}'.trim();
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF121A2A),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: const Color(0xFF34445E), width: 1.2),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Row(
            children: <Widget>[
              Expanded(
                child: Text(
                  title,
                  maxLines: 3,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Colors.white),
                ),
              ),
              IconButton(onPressed: onFavorite, icon: Icon(isFavorite ? Icons.star_rounded : Icons.star_border_rounded, color: Colors.white70)),
              IconButton(onPressed: onCompare, icon: const Icon(Icons.compare_arrows_rounded, color: Colors.white70)),
            ],
          ),
          if (merchant.isNotEmpty) Text(merchant, style: const TextStyle(color: Color(0xFFB8C2D8), fontWeight: FontWeight.w600)),
          const SizedBox(height: 12),
          Row(
            children: <Widget>[
              if (merchant.isNotEmpty) Expanded(child: Text(merchant, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(color: Color(0xFF172033), fontWeight: FontWeight.w900))) else const SizedBox.shrink(),
              if (detail.isNotEmpty) IconButton(onPressed: () => onOpenUrl(detail), icon: const Icon(Icons.arrow_forward_rounded, color: Colors.white70)),
            ],
          ),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: <Widget>[
              if (category.isNotEmpty) Container(padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7), decoration: BoxDecoration(color: const Color(0xFF5D43E7).withOpacity(.25), borderRadius: BorderRadius.circular(18)), child: Text(category, style: const TextStyle(color: Color(0xFFD5CCFF), fontWeight: FontWeight.w700))),
              if (merchant.toLowerCase().contains('ispark')) const _CatalogLogo('https://cdn.brandfetch.io/ispark.istanbul/w/600/h/180/logo', size: 34),
              if (merchant.toLowerCase().contains('migros')) const _CatalogLogo('https://cdn.brandfetch.io/migros.com.tr/w/600/h/180/logo', size: 34),
            ],
          ),
        ],
      ),
    );
  }
}
'''
s=s[:start]+new+s[end:]
p.write_text(s,encoding='utf-8')
print('v24 applied')
