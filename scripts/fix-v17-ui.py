from pathlib import Path
import re

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

# Home must still show the campaign feed even when a user's saved cards do not
# match a particular campaign. The dedicated "Kartıma Uygun" tab is the strict
# matching view. This prevents a completely empty home screen.
old = '''      if (widget.cards.isNotEmpty &&
          matchingCards.isEmpty &&
          !showAllCampaigns) {
        continue;
      }'''
new = '''      if (widget.mode == 'matched' &&
          (widget.cards.isEmpty || matchingCards.isEmpty)) {
        continue;
      }'''
if old in s:
    s = s.replace(old, new, 1)
else:
    print('campaign filter block not found')

# Give CategoriesPage real navigation. Each category opens the campaign catalog
# already filtered to that category instead of being a static list.
ms = s.find('class CategoriesPage extends StatelessWidget')
if ms >= 0:
    # It is the final class in main.dart, so replace to EOF.
    cat = r'''class CategoriesPage extends StatelessWidget {
  final List<UserCard> cards;

  const CategoriesPage({super.key, required this.cards});

  static const items = <List<String>>[
    ['⛽', 'Akaryakıt'],
    ['🛒', 'Market'],
    ['🍔', 'Restoran'],
    ['🛍️', 'E-ticaret'],
    ['📱', 'Elektronik'],
    ['👕', 'Giyim'],
    ['✈️', 'Seyahat'],
    ['🎬', 'Eğlence'],
    ['🏠', 'Ev & Yaşam'],
    ['🚗', 'Otomotiv'],
    ['💊', 'Sağlık & Kişisel Bakım'],
    ['📚', 'Eğitim'],
    ['👶', 'Bebek & Çocuk'],
    ['🐾', 'Evcil Hayvan'],
    ['💼', 'Finans & Sigorta'],
    ['🧾', 'Fatura & Abonelik'],
    ['🔧', 'Hizmet'],
    ['🏋️', 'Spor'],
    ['📖', 'Kitap & Kırtasiye'],
    ['🎨', 'Hobi'],
  ];

  void openCategory(BuildContext context, String category) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => CampaignsPage(
          cards: cards,
          mode: 'all',
          initialCategory: category,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Kategoriler',
          style: TextStyle(fontSize: 24, fontWeight: FontWeight.w900),
        ),
      ),
      body: ListView.separated(
        padding: const EdgeInsets.fromLTRB(14, 8, 14, 28),
        itemCount: items.length,
        separatorBuilder: (_, __) => const SizedBox(height: 8),
        itemBuilder: (context, index) {
          final item = items[index];
          return Material(
            color: const Color(0xFF0B1B31),
            borderRadius: BorderRadius.circular(16),
            child: InkWell(
              borderRadius: BorderRadius.circular(16),
              onTap: () => openCategory(context, item[1]),
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                child: Row(
                  children: [
                    SizedBox(
                      width: 48,
                      child: Text(item[0], style: const TextStyle(fontSize: 26)),
                    ),
                    Expanded(
                      child: Text(
                        item[1],
                        style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800),
                      ),
                    ),
                    const Icon(Icons.chevron_right_rounded),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}
'''
    s = s[:ms] + cat
else:
    print('CategoriesPage not found')

# CategoriesPage now needs the user's cards so the opened catalog can match them.
s = s.replace('const CategoriesPage(),', 'CategoriesPage(cards: cards),', 1)

# Allow a category to be supplied by the Categories screen.
needle = '''  final List<UserCard> cards;
  final String mode; // home | matched | all

  const CampaignsPage({
    super.key,
    required this.cards,
    this.mode = 'home',
  });'''
replacement = '''  final List<UserCard> cards;
  final String mode; // home | matched | all
  final String initialCategory;

  const CampaignsPage({
    super.key,
    required this.cards,
    this.mode = 'home',
    this.initialCategory = '',
  });'''
if needle in s:
    s = s.replace(needle, replacement, 1)
else:
    print('CampaignsPage constructor block not found')

needle2 = '''  void initState() {
    super.initState();
    showAllCampaigns = widget.mode == 'all';
    future = fetchCampaigns();
    _loadUserState();
  }'''
replacement2 = '''  void initState() {
    super.initState();
    showAllCampaigns = widget.mode == 'all';
    category = widget.initialCategory;
    future = fetchCampaigns();
    _loadUserState();
  }'''
if needle2 in s:
    s = s.replace(needle2, replacement2, 1)
else:
    print('CampaignsPage init block not found')

p.write_text(s, encoding='utf-8')
print('v17 catalog fixes applied')
