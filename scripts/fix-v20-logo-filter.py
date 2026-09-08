from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

# v20: replace the square/text-heavy CatalogLogo with a wide, high-resolution
# logo renderer. Brandfetch serves the original horizontal brand mark instead
# of a tiny favicon, so TEB/VakıfBank/etc. do not look pixelated when enlarged.
start = s.find('class CatalogLogo extends StatelessWidget')
end = s.find('\n\nclass CampaignDetailPage', start)
if start < 0 or end < 0:
    raise SystemExit('CatalogLogo boundaries not found')

logo = r'''class CatalogLogo extends StatelessWidget {
  final String label;
  final bool big;
  const CatalogLogo({super.key, required this.label, this.big = false});

  static String _domain(String raw) {
    final n = raw.toLowerCase().trim();
    const map = <String, String>{
      'garanti bbva': 'garantibbva.com.tr', 'garanti': 'garantibbva.com.tr',
      'akbank': 'akbank.com', 'axess': 'akbank.com',
      'yapı kredi': 'yapikredi.com.tr', 'yapi kredi': 'yapikredi.com.tr', 'world': 'worldcard.com.tr',
      'iş bankası': 'isbank.com.tr', 'is bankasi': 'isbank.com.tr', 'maximum': 'maximum.com.tr',
      'ziraat bankası': 'ziraatbank.com.tr', 'ziraat bankasi': 'ziraatbank.com.tr', 'bankkart': 'bankkart.com.tr',
      'halkbank': 'halkbank.com.tr', 'paraf': 'paraf.com.tr',
      'qnb': 'qnb.com.tr', 'cardfinans': 'qnb.com.tr',
      'teb': 'teb.com.tr', 'cepteteb': 'teb.com.tr',
      'vakıfbank': 'vakifbank.com.tr', 'vakifbank': 'vakifbank.com.tr',
      'denizbank': 'denizbank.com', 'denizbank': 'denizbank.com',
      'ing': 'ing.com.tr', 'hsbc': 'hsbc.com.tr', 'odeabank': 'odeabank.com.tr',
      'fibabanka': 'fibabanka.com.tr', 'şekerbank': 'sekerbank.com.tr', 'sekerbank': 'sekerbank.com.tr',
      'anadolubank': 'anadolubank.com.tr', 'albaraka': 'albaraka.com.tr',
      'kuveyt türk': 'kuveytturk.com.tr', 'kuveytturk': 'kuveytturk.com.tr',
      'emlak katılım': 'emlakkatilim.com.tr', 'emlakkatilim': 'emlakkatilim.com.tr',
      'türkiye finans': 'turkiyefinans.com.tr', 'turkiye finans': 'turkiyefinans.com.tr',
      'vakıf katılım': 'vakifkatilim.com.tr', 'vakif katilim': 'vakifkatilim.com.tr',
      'ziraat katılım': 'ziraatkatilim.com.tr', 'ziraat katilim': 'ziraatkatilim.com.tr',
      'visa': 'visa.com', 'mastercard': 'mastercard.com', 'troy': 'troyodeme.com',
      'bonus': 'bonus.com.tr', 'sağlam kart': 'kuveytturk.com.tr', 'saglam kart': 'kuveytturk.com.tr',
      'happy': 'turkiyefinans.com.tr',
    };
    return map[n] ?? '';
  }

  @override
  Widget build(BuildContext context) {
    final domain = _domain(label);
    final w = big ? 150.0 : 112.0;
    final h = big ? 50.0 : 36.0;
    if (domain.isEmpty) {
      return SizedBox(
        width: w, height: h,
        child: Center(child: Text(label, maxLines: 1, overflow: TextOverflow.ellipsis,
          textAlign: TextAlign.center,
          style: TextStyle(fontSize: big ? 18 : 13, fontWeight: FontWeight.w900, color: Colors.white))),
      );
    }
    final url = 'https://cdn.brandfetch.io/$domain/w/600/h/180/logo';
    return SizedBox(
      width: w,
      height: h,
      child: Image.network(
        url,
        fit: BoxFit.contain,
        filterQuality: FilterQuality.high,
        errorBuilder: (_, __, ___) => Text(label, maxLines: 1, overflow: TextOverflow.ellipsis,
          textAlign: TextAlign.center,
          style: TextStyle(fontSize: big ? 18 : 13, fontWeight: FontWeight.w900, color: Colors.white)),
      ),
    );
  }
}'''
s = s[:start] + logo + s[end:]

# v20: Home + "Kartıma Uygun" must contain only campaigns matching at least
# one saved card. "Tüm Kampanyalar" remains the unrestricted catalog.
needle = "    cachedCampaigns = unique;\n    return unique;"
replacement = r'''    bool valueOf(Map<String, dynamic> row, List<String> keys, String Function(String) norm) {
      return keys.any((key) => '${row[key] ?? ''}'.trim().isNotEmpty);
    }

    String field(Map<String, dynamic> row, List<String> keys) {
      for (final key in keys) {
        final value = '${row[key] ?? ''}'.trim();
        if (value.isNotEmpty) return value;
      }
      return '';
    }

    bool matchesCard(Map<String, dynamic> campaign, UserCard card) {
      bool same(String ruleValue, String actual) {
        final r = _norm(ruleValue);
        final a = _norm(actual);
        if (r.isEmpty) return true;
        return _ruleMatches(r, a);
      }

      final rules = (campaign['_rules'] as List?)
          ?.whereType<Map>()
          .map((x) => Map<String, dynamic>.from(x))
          .toList() ?? <Map<String, dynamic>>[];

      bool rowMatches(Map<String, dynamic> row) {
        final bank = field(row, ['bank_name', 'bank']);
        final cardName = field(row, ['card_name', 'card', 'card_program', 'card_brand']);
        final network = field(row, ['network', 'card_network']);
        final cardType = field(row, ['card_type']);
        final customerType = field(row, ['customer_type', 'customer_segment']);
        return same(bank, card.bank) &&
            same(cardName, card.card) &&
            same(network, card.network) &&
            same(cardType, card.cardType) &&
            same(customerType, card.customerType);
      }

      if (rules.isNotEmpty && rules.any(rowMatches)) return true;
      if (rules.isNotEmpty) return false;

      // Some imported campaigns carry the targeting fields directly instead
      // of in campaign_rules. Those fields are still matched strictly.
      return rowMatches(campaign);
    }

    final visible = widget.mode == 'all'
        ? unique
        : unique.where((campaign) {
            if (widget.cards.isEmpty) return false;
            final matchingCards = widget.cards.where((card) => matchesCard(campaign, card)).toList();
            campaign['_cards'] = matchingCards;
            return matchingCards.isNotEmpty;
          }).toList();

    if (widget.mode == 'all') {
      for (final campaign in visible) {
        campaign['_cards'] = widget.cards.where((card) => matchesCard(campaign, card)).toList();
      }
    }

    cachedCampaigns = visible;
    return visible;'''
if needle not in s:
    raise SystemExit('campaign result boundary not found')
s = s.replace(needle, replacement, 1)

p.write_text(s, encoding='utf-8')
print('v20 horizontal logos and strict card matching applied')
