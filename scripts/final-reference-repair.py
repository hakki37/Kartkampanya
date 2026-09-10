from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')


def replace_class(src, name, replacement):
    start = src.find('class ' + name)
    if start < 0:
        raise SystemExit(name + ' not found')
    brace = src.find('{', start)
    depth = 0
    quote = None
    esc = False
    for i in range(brace, len(src)):
        ch = src[i]
        if quote:
            if esc:
                esc = False
            elif ch == '\\':
                esc = True
            elif ch == quote:
                quote = None
        elif ch in "'\"":
            quote = ch
        elif ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return src[:start] + replacement + src[i + 1:]
    raise SystemExit(name + ' end not found')


smart = r'''class SmartCampaignCard extends StatelessWidget {
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

  String text(dynamic value) => value == null ? '' : '$value'.trim();

  String logoUrl() {
    for (final key in ['logo_url', 'image_url', 'merchant_logo', 'brand_logo']) {
      final value = text(campaign[key]);
      if (value.isNotEmpty) return value;
    }
    return '';
  }

  @override
  Widget build(BuildContext context) {
    final title = text(campaign['title']).isEmpty
        ? 'Kampanya'
        : text(campaign['title']);
    final merchant = text(campaign['merchant']);
    final category = text(campaign['category']).isEmpty
        ? campaignSection(campaign)
        : text(campaign['category']);
    final logo = logoUrl();

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.fromLTRB(14, 14, 10, 13),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: const Color(0xFFE0DCEB)),
        boxShadow: const [
          BoxShadow(
            color: Color(0x0C000000),
            blurRadius: 8,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 74,
                height: 74,
                decoration: BoxDecoration(
                  color: const Color(0xFFF3F1F8),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: logo.isNotEmpty
                    ? ClipRRect(
                        borderRadius: BorderRadius.circular(14),
                        child: Image.network(
                          logo,
                          fit: BoxFit.contain,
                          errorBuilder: (_, __, ___) => const Icon(
                            Icons.local_offer_rounded,
                            color: Color(0xFF6D3DF5),
                            size: 32,
                          ),
                        ),
                      )
                    : const Icon(
                        Icons.local_offer_rounded,
                        color: Color(0xFF6D3DF5),
                        size: 32,
                      ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (merchant.isNotEmpty)
                      Text(
                        merchant,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          fontSize: 10,
                          color: Color(0xFF777187),
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    const SizedBox(height: 3),
                    Text(
                      title,
                      maxLines: 3,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        fontSize: 17,
                        height: 1.08,
                        color: Color(0xFF17142A),
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                    if (expiringSoon) ...[
                      const SizedBox(height: 7),
                      _badge(
                        Icons.schedule_rounded,
                        'Son $daysRemaining Gün',
                        const Color(0xFFE7F8EA),
                        const Color(0xFF16803C),
                      ),
                    ],
                  ],
                ),
              ),
              IconButton(
                onPressed: onFavorite,
                padding: EdgeInsets.zero,
                constraints: const BoxConstraints(minWidth: 38, minHeight: 38),
                icon: Icon(
                  isFavorite
                      ? Icons.star_rounded
                      : Icons.star_border_rounded,
                  color: isFavorite
                      ? const Color(0xFFFFB300)
                      : const Color(0xFF55505F),
                  size: 30,
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Text(
            text(campaign['description']).isEmpty
                ? text(campaign['campaign_text'])
                : text(campaign['description']),
            maxLines: 3,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(
              fontSize: 14,
              height: 1.28,
              color: Color(0xFF5D5868),
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 11),
          Wrap(
            spacing: 7,
            runSpacing: 7,
            children: [
              _chip(Icons.local_gas_station_outlined, category),
              if (merchant.isNotEmpty)
                _chip(Icons.credit_card_outlined, merchant),
              if (text(campaign['start_date']).isNotEmpty ||
                  text(campaign['end_date']).isNotEmpty)
                _chip(
                  Icons.calendar_month_outlined,
                  '${text(campaign['start_date'])}-${text(campaign['end_date'])}',
                ),
            ],
          ),
          const SizedBox(height: 11),
          Align(
            alignment: Alignment.centerRight,
            child: SizedBox(
              height: 43,
              child: FilledButton.icon(
                onPressed: () => Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (_) => CampaignDetailPage(campaign: campaign),
                  ),
                ),
                style: FilledButton.styleFrom(
                  backgroundColor: const Color(0xFF6D3DF5),
                  padding: const EdgeInsets.symmetric(horizontal: 18),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                  ),
                ),
                icon: const Icon(Icons.arrow_forward_rounded, size: 18),
                label: const Text(
                  'Detaylar',
                  style: TextStyle(fontWeight: FontWeight.w900),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _chip(IconData icon, String label) {
    if (label.isEmpty) return const SizedBox.shrink();
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
      decoration: BoxDecoration(
        color: const Color(0xFFF0ECFA),
        borderRadius: BorderRadius.circular(11),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: const Color(0xFF2F2850)),
          const SizedBox(width: 5),
          Text(
            label,
            style: const TextStyle(
              fontSize: 10,
              color: Color(0xFF383342),
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }

  Widget _badge(IconData icon, String label, Color background, Color foreground) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 6),
      decoration: BoxDecoration(
        color: background,
        borderRadius: BorderRadius.circular(11),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 15, color: foreground),
          const SizedBox(width: 5),
          Text(
            label,
            style: TextStyle(
              fontSize: 10,
              color: foreground,
              fontWeight: FontWeight.w900,
            ),
          ),
        ],
      ),
    );
  }
}
'''
s = replace_class(s, 'SmartCampaignCard', smart)

profile = r'''class ProfilePage extends StatelessWidget {
  const ProfilePage({super.key});

  @override
  Widget build(BuildContext context) {
    final user = Supabase.instance.client.auth.currentUser;
    final email = user?.email ?? '';

    return Scaffold(
      backgroundColor: const Color(0xFFF8F7FC),
      appBar: AppBar(
        title: const Text(
          'Profil',
          style: TextStyle(fontSize: 23, fontWeight: FontWeight.w900),
        ),
        actions: [
          IconButton(
            onPressed: () {},
            icon: const Icon(Icons.settings_outlined),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(18, 12, 18, 30),
        children: [
          Center(
            child: Container(
              width: 78,
              height: 78,
              decoration: const BoxDecoration(
                color: Color(0xFFE7DEFF),
                shape: BoxShape.circle,
              ),
              alignment: Alignment.center,
              child: const Text(
                'H',
                style: TextStyle(
                  fontSize: 32,
                  color: Color(0xFF6D3DF5),
                  fontWeight: FontWeight.w900,
                ),
              ),
            ),
          ),
          const SizedBox(height: 10),
          const Center(
            child: Text(
              'Kart Kampanya',
              style: TextStyle(
                fontSize: 19,
                color: Color(0xFF211D2D),
                fontWeight: FontWeight.w900,
              ),
            ),
          ),
          if (email.isNotEmpty)
            Center(
              child: Text(
                email,
                style: const TextStyle(
                  fontSize: 11,
                  color: Color(0xFF777187),
                ),
              ),
            ),
          const SizedBox(height: 22),
          ...[
            'Bendeki Kartlar',
            'Favori Kampanyalar',
            'Bildirimler',
            'Ayarlar',
            'Yardım & Destek',
          ].map(
            (label) => Container(
              margin: const EdgeInsets.only(bottom: 9),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(15),
                border: Border.all(color: const Color(0xFFE5E1EF)),
              ),
              child: ListTile(
                title: Text(
                  label,
                  style: const TextStyle(fontWeight: FontWeight.w700),
                ),
                trailing: const Icon(Icons.chevron_right_rounded),
              ),
            ),
          ),
          Container(
            decoration: BoxDecoration(
              color: const Color(0xFFFFEEEE),
              borderRadius: BorderRadius.circular(15),
            ),
            child: ListTile(
              onTap: () => Supabase.instance.client.auth.signOut(),
              leading: const Icon(
                Icons.logout_rounded,
                color: Color(0xFFD33A3A),
              ),
              title: const Text(
                'Çıkış Yap',
                style: TextStyle(
                  color: Color(0xFFD33A3A),
                  fontWeight: FontWeight.w800,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
'''
s = replace_class(s, 'ProfilePage', profile)

p.write_text(s, encoding='utf-8')
print('Final reference repair applied')
