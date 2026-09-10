from pathlib import Path
import re

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

# Start from the repository's already-working Dart and make only targeted visual changes.
# Do not replace pages/state logic wholesale: that was the source of previous parser failures.

# Light catalog theme.
theme = r'''      theme: ThemeData(
        useMaterial3: true,
        brightness: Brightness.light,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF6D3DF5),
          brightness: Brightness.light,
        ),
        scaffoldBackgroundColor: const Color(0xFFF8F7FC),
        appBarTheme: const AppBarTheme(
          elevation: 0,
          scrolledUnderElevation: 0,
          backgroundColor: Color(0xFFF8F7FC),
          foregroundColor: Color(0xFF211D2D),
        ),
        inputDecorationTheme: const InputDecorationTheme(
          filled: true,
          fillColor: Colors.white,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.all(Radius.circular(16)),
            borderSide: BorderSide(color: Color(0xFFE1DCEB)),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.all(Radius.circular(16)),
            borderSide: BorderSide(color: Color(0xFFE1DCEB)),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.all(Radius.circular(16)),
            borderSide: BorderSide(color: Color(0xFF6D3DF5), width: 1.5),
          ),
        ),
        cardTheme: const CardThemeData(
          elevation: 0,
          margin: EdgeInsets.zero,
          surfaceTintColor: Colors.transparent,
        ),
      ),
'''
s2, n = re.subn(r"      theme: ThemeData\(.*?\n      home: const AuthGate\(\),", theme + "      home: const AuthGate(),", s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('Theme block not found')
s = s2

# Existing bottom navigation keeps all application logic. Rename the user-facing label.
s = s.replace("label: 'Kartıma Uygun'", "label: 'Kampanyalar'", 1)

# Replace only the visual campaign card. Constructor matches the existing call sites.
def replace_class(src, name, replacement):
    marker = 'class ' + name
    start = src.find(marker)
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

card = r'''class SmartCampaignCard extends StatelessWidget {
  final Map<String, dynamic> campaign;
  final bool isFavorite, isCompared, showAllCampaigns, expiringSoon;
  final int daysRemaining, requiredSteps, completedSteps;
  final VoidCallback onFavorite, onCompare;
  final Future<void> Function(String url) onOpenUrl;
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

  String _text(dynamic value) => value == null ? '' : '$value'.trim();

  String _first(List<String> keys) {
    for (final key in keys) {
      final value = _text(campaign[key]);
      if (value.isNotEmpty) return value;
    }
    return '';
  }

  String _logo() => _first([
        'logo_url',
        'image_url',
        'merchant_logo',
        'brand_logo',
      ]);

  @override
  Widget build(BuildContext context) {
    final title = _first(['title', 'name']).isEmpty
        ? 'Kampanya'
        : _first(['title', 'name']);
    final merchant = _first(['merchant', 'brand', 'bank_name']);
    final description = _first([
      'description',
      'campaign_text',
      'details',
      'content',
    ]);
    final category = _first(['category']).isEmpty
        ? campaignSection(campaign)
        : _first(['category']);
    final bank = _first(['bank_name', 'bank', 'card_bank']);
    final date = _first(['date_range', 'validity', 'campaign_dates']);
    final logo = _logo();

    return Container(
      margin: const EdgeInsets.only(bottom: 13),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFE1DCEB)),
        boxShadow: const [
          BoxShadow(
            color: Color(0x0C000000),
            blurRadius: 10,
            offset: Offset(0, 3),
          ),
        ],
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(20),
        onTap: () => Navigator.of(context).push(
          MaterialPageRoute(
            builder: (_) => CampaignDetailPage(campaign: campaign),
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.fromLTRB(13, 13, 13, 12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    width: 68,
                    height: 68,
                    decoration: BoxDecoration(
                      color: const Color(0xFFF4F1FA),
                      borderRadius: BorderRadius.circular(15),
                    ),
                    child: logo.isNotEmpty
                        ? ClipRRect(
                            borderRadius: BorderRadius.circular(15),
                            child: Image.network(
                              logo,
                              fit: BoxFit.contain,
                              errorBuilder: (_, __, ___) => const Icon(
                                Icons.local_offer_rounded,
                                color: Color(0xFF6D3DF5),
                                size: 30,
                              ),
                            ),
                          )
                        : const Icon(
                            Icons.local_offer_rounded,
                            color: Color(0xFF6D3DF5),
                            size: 30,
                          ),
                  ),
                  const SizedBox(width: 11),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
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
                                  const SizedBox(height: 2),
                                  Text(
                                    title,
                                    maxLines: 3,
                                    overflow: TextOverflow.ellipsis,
                                    style: const TextStyle(
                                      fontSize: 17,
                                      height: 1.12,
                                      color: Color(0xFF17142A),
                                      fontWeight: FontWeight.w900,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            IconButton(
                              padding: EdgeInsets.zero,
                              constraints: const BoxConstraints(
                                minWidth: 34,
                                minHeight: 34,
                              ),
                              onPressed: onFavorite,
                              icon: Icon(
                                isFavorite
                                    ? Icons.favorite_rounded
                                    : Icons.favorite_border_rounded,
                                color: isFavorite
                                    ? const Color(0xFFE33F77)
                                    : const Color(0xFF666071),
                                size: 27,
                              ),
                            ),
                          ],
                        ),
                        if (expiringSoon) ...[
                          const SizedBox(height: 5),
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 9,
                              vertical: 5,
                            ),
                            decoration: BoxDecoration(
                              color: daysRemaining <= 3
                                  ? const Color(0xFFFFE4E7)
                                  : const Color(0xFFE0F8E8),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Text(
                              '◷  Son $daysRemaining Gün',
                              style: TextStyle(
                                fontSize: 10,
                                fontWeight: FontWeight.w900,
                                color: daysRemaining <= 3
                                    ? const Color(0xFFD33A3A)
                                    : const Color(0xFF19864A),
                              ),
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                ],
              ),
              if (description.isNotEmpty) ...[
                const SizedBox(height: 10),
                Text(
                  description,
                  maxLines: 3,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    fontSize: 13,
                    height: 1.25,
                    color: Color(0xFF5F5968),
                  ),
                ),
              ],
              const SizedBox(height: 10),
              Wrap(
                spacing: 7,
                runSpacing: 7,
                children: [
                  _tag(Icons.local_gas_station_outlined, category),
                  if (bank.isNotEmpty)
                    _tag(Icons.credit_card_outlined, bank),
                  if (date.isNotEmpty)
                    _tag(Icons.calendar_month_outlined, date),
                ],
              ),
              const SizedBox(height: 11),
              SizedBox(
                width: double.infinity,
                height: 43,
                child: FilledButton(
                  onPressed: () => Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (_) => CampaignDetailPage(campaign: campaign),
                    ),
                  ),
                  style: FilledButton.styleFrom(
                    backgroundColor: const Color(0xFF6D3DF5),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14),
                    ),
                  ),
                  child: const Text(
                    'Detaylar  →',
                    style: TextStyle(fontWeight: FontWeight.w900),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _tag(IconData icon, String label) {
    final value = label.isEmpty ? 'Kampanya' : label;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
      decoration: BoxDecoration(
        color: const Color(0xFFF0EDFA),
        borderRadius: BorderRadius.circular(11),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: const Color(0xFF332B50)),
          const SizedBox(width: 5),
          ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 130),
            child: Text(
              value,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(
                fontSize: 10,
                color: Color(0xFF332B50),
                fontWeight: FontWeight.w800,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
'''
s = replace_class(s, 'SmartCampaignCard', card)

# Lighten the remaining known dark surfaces without touching behavior.
s = s.replace('Color(0xFF081120)', 'Color(0xFFF8F7FC)')
s = s.replace('Color(0xFF0B1B31)', 'Colors.white')

p.write_text(s, encoding='utf-8')
print('Clean final catalog UI applied without replacing page/state logic')
