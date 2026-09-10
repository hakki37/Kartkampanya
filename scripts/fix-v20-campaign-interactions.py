from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

# v16 normally adds this helper, but make v20 self-contained so later refactors
# can never leave SmartCampaignCard calling an undefined method.
if 'String _catalogBenefitText(Map<String, dynamic> campaign)' not in s:
    marker = 'class _CatalogLogo extends StatelessWidget {'
    helper = r'''String _catalogBenefitText(Map<String, dynamic> campaign) {
  final title = decodeHtmlEntities('${campaign['title'] ?? ''}');
  final desc = decodeHtmlEntities('${campaign['description'] ?? ''}');
  final campaignText = decodeHtmlEntities('${campaign['campaign_text'] ?? ''}');
  final rewardType = decodeHtmlEntities('${campaign['reward_type'] ?? ''}');
  final text = '$title $desc $campaignText $rewardType';

  num? asNum(dynamic v) {
    if (v is num) return v;
    return num.tryParse('${v ?? ''}'.replaceAll(',', '.'));
  }

  final percent = asNum(campaign['reward_percent']) ?? asNum(campaign['_calculatedPercent']);
  final reward = asNum(campaign['_calculatedReward']) ??
      asNum(campaign['_reward']) ?? asNum(campaign['reward_amount']) ?? asNum(campaign['max_reward']);
  final installment = RegExp(r'(?<!\d)(\d+)\s*(?:taksite|taksit|taksitli)', caseSensitive: false).firstMatch(text)?.group(1);

  if (installment != null) return '$installment taksit';
  if (percent != null && percent > 0) {
    final value = percent.toDouble();
    return '%${value.toStringAsFixed(value == value.roundToDouble() ? 0 : 1)} indirim';
  }
  if (reward != null && reward > 0) return '${reward.toDouble().toStringAsFixed(0)} TL';
  final normalized = _norm(text);
  if (normalized.contains('bonus')) return 'Bonus';
  if (normalized.contains('puan')) return 'Puan';
  if (normalized.contains('indirim')) return 'İndirim';
  if (normalized.contains('taksit')) return 'Taksit';
  return 'Avantaj tutarı belirtilmemiş';
}

'''
    if marker not in s:
        raise SystemExit('Catalog logo marker not found')
    s = s.replace(marker, helper + marker, 1)

# Never display a fabricated zero-value advantage.
s = s.replace("return '0 TL';", "return 'Avantaj tutarı belirtilmemiş';", 1)

# Campaign detail must show the campaign's own text, never generic bank terms.
start = s.find('String campaignConditions(Map<String, dynamic> campaign) {')
if start >= 0:
    end = s.find('\nclass ', start)
    if end > start:
        fn = r'''String campaignConditions(Map<String, dynamic> campaign) {
  final campaignText = cleanCampaignHtml('${campaign['campaign_text'] ?? ''}');
  final description = cleanCampaignHtml('${campaign['description'] ?? ''}');
  if (campaignText.trim().length >= 20) return decodeHtmlEntities(campaignText.trim());
  if (description.trim().length >= 20) return decodeHtmlEntities(description.trim());
  return 'Kampanya açıklaması bu kayıt için mevcut değil.';
}
'''
        s = s[:start] + fn + s[end + 1:]

# Add an optional starting category so category tiles open a filtered campaign list.
ctor = """  final List<UserCard> cards;
  final String mode; // home | matched | all

  const CampaignsPage({
    super.key,
    required this.cards,
    this.mode = 'home',
  });"""
ctor_new = """  final List<UserCard> cards;
  final String mode; // home | matched | all
  final String initialCategory;

  const CampaignsPage({
    super.key,
    required this.cards,
    this.mode = 'home',
    this.initialCategory = '',
  });"""
if ctor in s:
    s = s.replace(ctor, ctor_new, 1)

init = """  void initState() {
    super.initState();
    future = fetchCampaigns();"""
init_new = """  void initState() {
    super.initState();
    category = widget.initialCategory;
    showAllCampaigns = widget.mode == 'all';
    future = fetchCampaigns();"""
if init in s:
    s = s.replace(init, init_new, 1)

# Make the quick 'Bana Uygun' action actually navigate to the matched view.
old_pill = "_pill('✧','Bana Uygun',widget.mode=='matched',()=>setState(()=>category=''))"
new_pill = "_pill('✧','Bana Uygun',widget.mode=='matched',(){ if(widget.mode=='matched'){ setState(()=>future=fetchCampaigns()); } else { Navigator.of(context).push(MaterialPageRoute(builder:(_)=>CampaignsPage(cards:widget.cards,mode:'matched'))); } })"
if old_pill in s:
    s = s.replace(old_pill, new_pill, 1)

# Replace CategoriesPage with a genuinely tappable catalog.
def replace_class(src, name, replacement):
    start = src.find('class ' + name)
    if start < 0:
        raise SystemExit(f'{name} not found')
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
    raise SystemExit(f'{name} end not found')

categories = r'''class CategoriesPage extends StatelessWidget {
  final List<UserCard> cards;
  const CategoriesPage({super.key, required this.cards});
  static const data = [
    ['▦', 'Tümü', 0xFFEDE7FF], ['⛽', 'Akaryakıt', 0xFFFFE4E8], ['🛒', 'Market', 0xFFE1F8EF],
    ['🍴', 'Restoran', 0xFFFFEAD8], ['🛍', 'E-ticaret', 0xFFE8E1FF], ['👕', 'Giyim', 0xFFFFE2F1],
    ['📱', 'Elektronik', 0xFFE1EEFF], ['✈', 'Seyahat', 0xFFFFE8D8], ['🚗', 'Otomotiv', 0xFFE2F2EE],
    ['⌂', 'Ev & Yaşam', 0xFFE3F4E9], ['💄', 'Sağlık & Güzellik', 0xFFFFE1F0], ['🎮', 'Eğlence', 0xFFFFE5E5],
    ['🎓', 'Eğitim', 0xFFFFE5F2], ['🏦', 'Finans', 0xFFE2E9FF], ['✦', 'Diğer', 0xFFE9EBF4],
  ];
  void openCategory(BuildContext context, String value) {
    Navigator.of(context).push(MaterialPageRoute(
      builder: (_) => CampaignsPage(cards: cards, mode: 'all', initialCategory: value == 'Tümü' ? '' : value),
    ));
  }
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8F7FC),
      appBar: AppBar(title: const Text('Kategoriler', style: TextStyle(fontWeight: FontWeight.w900))),
      body: GridView.builder(
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 30),
        itemCount: data.length,
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 3, crossAxisSpacing: 10, mainAxisSpacing: 10, childAspectRatio: 1.02),
        itemBuilder: (_, i) {
          final x = data[i];
          return Material(
            color: Color(x[2] as int),
            borderRadius: BorderRadius.circular(18),
            child: InkWell(
              borderRadius: BorderRadius.circular(18),
              onTap: () => openCategory(context, x[1] as String),
              child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
                Text(x[0] as String, style: const TextStyle(fontSize: 25)),
                const SizedBox(height: 7),
                Padding(padding: const EdgeInsets.symmetric(horizontal: 4), child: Text(x[1] as String, maxLines: 2, textAlign: TextAlign.center, style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: Color(0xFF353146)))),
              ]),
            ),
          );
        },
      ),
    );
  }
}
'''
if 'class CategoriesPage extends StatelessWidget {' in s:
    s = replace_class(s, 'CategoriesPage', categories)

s = s.replace('const CategoriesPage(),', 'CategoriesPage(cards: cards),', 1)
p.write_text(s, encoding='utf-8')
print('v20 campaign interactions, category navigation and advantage display fixed')
