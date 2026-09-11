from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')


def replace_function(src, signature, replacement):
    start = src.find(signature)
    if start < 0:
        raise SystemExit(f'{signature} not found')
    brace = src.find('{', start)
    if brace < 0:
        raise SystemExit(f'{signature} opening brace not found')
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
    raise SystemExit(f'{signature} end not found')


def clean_body(value, title):
    return decodeHtmlEntities('${value}')

# Add a source-cleaning helper before CampaignsPage.
marker = 'class CampaignsPage extends StatefulWidget {'
if 'String _cleanCampaignBody(' not in s:
    helper = r'''String _cleanCampaignBody(String raw, String title) {
  var text = decodeHtmlEntities(raw)
      .replaceAll(RegExp(r'<[^>]+>'), ' ')
      .replaceAll(RegExp(r'\s+'), ' ')
      .trim();
  if (text.startsWith('-->')) text = text.substring(3).trim();

  final cleanTitle = decodeHtmlEntities(title).trim();
  if (cleanTitle.isNotEmpty) {
    final first = text.indexOf(cleanTitle);
    final last = text.lastIndexOf(cleanTitle);
    if (last >= 0 && last + cleanTitle.length < text.length) {
      text = text.substring(last + cleanTitle.length).trim();
    } else if (first >= 0 && first + cleanTitle.length < text.length) {
      text = text.substring(first + cleanTitle.length).trim();
    }
  }

  const tails = [
    'İlginizi Çekebilecek Kampanyalar',
    'Ilginizi Çekebilecek Kampanyalar',
    'VakıfBank Web Siteleri',
    'Ziraat Bankası A.Ş.',
    '© 2026',
    'Çerez Tercihleri',
  ];
  for (final tail in tails) {
    final i = text.indexOf(tail);
    if (i > 0) text = text.substring(0, i).trim();
  }
  return text.replaceAll(RegExp(r'\s+'), ' ').trim();
}

String _campaignShortDescription(String body) {
  if (body.isEmpty) return '';
  final parts = body.split(RegExp(r'(?<=[.!?])\s+'));
  return parts.take(2).join(' ').trim();
}

'''
    if marker not in s:
        raise SystemExit('CampaignsPage marker not found')
    s = s.replace(marker, helper + marker, 1)

# Remove obvious scraper/error pages from the campaign feed.
blocked = r'''  bool _isBlockedCampaign(Map<String, dynamic> campaign) {
    final title = _norm('${campaign['title'] ?? ''}');
    final merchant = _norm('${campaign['merchant'] ?? ''}');
    final description = _norm('${campaign['description'] ?? ''}');
    final text = '$title $merchant $description';

    const blocked = <String>[
      'kvkk', 'aydinlatma metni', 'cerez politikasi', 'gizlilik politikasi',
      'kullanim kosullari', 'sifre belirleme', 'sifre degistirme',
      'internet alisveris yetkisi', 'dijital platform odeme talimatlari',
      'visa tek tikla ode', 'test kampany', 'kampanya test',
      'tarayiciniz desteklenmiyor', 'sunucuda gecici bir hata olustu',
      'kampanyalar | kampanyalar', 'kampanyalar | axess', 'kampanyalar |',
      'bu kategoride su an icin bir kampanyamiz bulunmamaktadir',
    ];
    return blocked.any(text.contains);
  }'''
s = replace_function(s, '  bool _isBlockedCampaign(Map<String, dynamic> campaign) {', blocked)

# Correct the campaign fields immediately after raw source mapping.
needle = "      campaign['campaign_text'] = '${campaign['campaign_text'] ?? campaign['description'] ?? ''}';\n      campaign['conditions'] = '${campaign['conditions'] ?? ''}';\n      campaign['terms'] = '${campaign['terms'] ?? ''}';"
replacement = "      final rawDescription = '${campaign['description'] ?? ''}';\n      final cleanedBody = _cleanCampaignBody(rawDescription, '${campaign['title'] ?? ''}');\n      campaign['description'] = _campaignShortDescription(cleanedBody);\n      campaign['campaign_text'] = campaign['description'];\n      campaign['conditions'] = cleanedBody;\n      campaign['terms'] = '${campaign['terms'] ?? ''}';"
if needle not in s:
    raise SystemExit('campaign field mapping block not found')
s = s.replace(needle, replacement, 1)

# Replace card matching with bank + explicit network/card restrictions and rule support.
matching = r'''  bool cardMatches(
    Map<String, dynamic> campaign,
    UserCard userCard,
  ) {
    final rules = campaign['_rules'];
    if (rules is List && rules.isNotEmpty) {
      return rules.any((raw) {
        final rule = raw is Map<String, dynamic>
            ? raw
            : Map<String, dynamic>.from(raw as Map);
        return _matchesSingleRule(rule, userCard);
      });
    }

    final campaignBank = '${campaign['bank_name'] ?? ''}'.trim();
    if (campaignBank.isNotEmpty && !_ruleMatches(campaignBank, userCard.bank)) {
      return false;
    }

    final text = _norm([
      campaign['title'],
      campaign['description'],
      campaign['conditions'],
      campaign['terms'],
    ].where((x) => x != null).join(' '));
    final network = _norm(userCard.network);

    // A network named explicitly by the campaign is a hard restriction.
    for (final n in const ['visa', 'mastercard', 'troy']) {
      if (text.contains(n) && network.isNotEmpty && network != n) return false;
    }

    // Generic labels such as "VakıfBank Kartları" do not mean one specific card.
    final campaignCard = _norm('${campaign['card_name'] ?? ''}');
    final genericCard = campaignCard.isEmpty ||
        campaignCard.contains('kartlari') ||
        campaignCard.contains('kartlari') ||
        campaignCard == 'tum kartlar' ||
        campaignCard == 'tum kartlarim';
    if (genericCard) return true;

    if (!_ruleMatches(campaignCard, userCard.card)) return false;
    return true;
  }'''
s = replace_function(s, '  bool cardMatches(\n    Map<String, dynamic> campaign,', matching)

p.write_text(s, encoding='utf-8')
print('Card matching and campaign data separation repaired')
