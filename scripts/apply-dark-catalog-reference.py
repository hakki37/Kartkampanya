from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

# The login screen stays independent; this pass styles the authenticated catalog.
# It is intentionally the LAST visual pass so earlier repair scripts cannot
# switch the catalog back to the old white theme.

theme_start = s.find('      theme: ThemeData(')
theme_end = s.find('      home:', theme_start)
if theme_start < 0 or theme_end < 0:
    raise SystemExit('App theme boundary not found')
theme = s[theme_start:theme_end]
theme = theme.replace('brightness: Brightness.light,', 'brightness: Brightness.dark,', 1)
theme = theme.replace('scaffoldBackgroundColor: const Color(0xFFF7F5FC),', 'scaffoldBackgroundColor: const Color(0xFF081120),', 1)
theme = theme.replace('backgroundColor: const Color(0xFFF7F5FC),', 'backgroundColor: const Color(0xFF081120),', 1)
theme = theme.replace('foregroundColor: Color(0xFF211B2D),', 'foregroundColor: Colors.white,', 1)
s = s[:theme_start] + theme + s[theme_end:]


def class_slice(src, name, next_name):
    start = src.find('class ' + name)
    end = src.find('class ' + next_name, start)
    if start < 0 or end < 0:
        raise SystemExit(f'{name}/{next_name} boundary not found')
    return start, end, src[start:end]

# Dark catalog campaign cards: preserve layout/content, only change surfaces and typography.
start, end, card = class_slice(s, 'SmartCampaignCard', 'MyCardsPage')
card_replacements = {
    'color: Colors.white,': 'color: const Color(0xFF0D1728),',
    'border: Border.all(color: const Color(0xFFDCD7E6))': 'border: Border.all(color: const Color(0xFF20344F))',
    'color: const Color(0xFFF7F5FA)': 'color: const Color(0xFF111F34)',
    'color: const Color(0xFF151225)': 'color: Colors.white',
    'color: const Color(0xFF5F5969)': 'color: const Color(0xFFAAB6C8)',
    'color: const Color(0xFF5E3CCB)': 'color: const Color(0xFFB8A8FF)',
    'color: const Color(0xFFF0EDFA)': 'color: const Color(0xFF14243A)',
    'color: const Color(0xFF29233C)': 'color: const Color(0xFFDCE5F2)',
}
for old, new in card_replacements.items():
    card = card.replace(old, new)
s = s[:start] + card + s[end:]

# The campaign list and category grid live inside CampaignsPage.
start, end, page = class_slice(s, 'CampaignsPage', 'CampaignDetailPage')
page_replacements = {
    'backgroundColor: Colors.white,': 'backgroundColor: const Color(0xFF0B1729),',
    'color: Colors.white,': 'color: const Color(0xFF0D1728),',
    'color: const Color(0xFFF7F5FC)': 'color: const Color(0xFF081120)',
    'color: const Color(0xFFF4F3FB)': 'color: const Color(0xFF081120)',
    'color: const Color(0xFFE3DDF0)': 'color: const Color(0xFF20344F)',
    'color: const Color(0xFFE6E3F5)': 'color: const Color(0xFF20344F)',
    'color: const Color(0xFF1E1B3A)': 'color: Colors.white',
    'color: const Color(0xFF7C7A94)': 'color: const Color(0xFFAAB6C8)',
}
for old, new in page_replacements.items():
    page = page.replace(old, new)

# Exact reference category order from the supplied catalog screenshot.
old_data = """const data = [
                  ['🚗', 'Otomotiv'], ['🛍️', 'E-ticaret'], ['📱', 'Elektronik'], ['🛒', 'Market'],
                  ['⛽', 'Akaryakıt'], ['🧳', 'Seyahat'], ['👕', 'Giyim'], ['▦', 'Tümü'],
                ];"""
new_data = """const data = [
                  ['🍴', 'Restoran'], ['🛒', 'Market'], ['⛽', 'Akaryakıt'], ['🧳', 'Seyahat'],
                  ['👕', 'Giyim'], ['🛋️', 'Ev & Yaşam'], ['▦', 'Tümü'], ['📱', 'Elektronik'],
                ];"""
page = page.replace(old_data, new_data)

# Compact dark category tiles: selected tile stays purple, inactive tiles become navy.
page = page.replace('color: selected ? null : const Color(0xFF0B1B31),', 'color: selected ? null : const Color(0xFF0D1A2D),')
page = page.replace('border: Border.all(color: selected ? const Color(0xFF6D59FF) : const Color(0xFF28415F)),', 'border: Border.all(color: selected ? const Color(0xFF7355FF) : const Color(0xFF213A59)),')
page = page.replace('fontSize: 11.5, fontWeight: FontWeight.w800', 'fontSize: 10.5, fontWeight: FontWeight.w800')
page = page.replace('fontSize: 23', 'fontSize: 20')

s = s[:start] + page + s[end:]

# Bottom navigation is a dark catalog bar; keep the existing destinations/functionality.
nav_start = s.find('bottomNavigationBar:')
if nav_start >= 0:
    nav_end = s.find('\n      ),', nav_start)
    if nav_end >= 0:
        nav = s[nav_start:nav_end]
        nav = nav.replace('color: Colors.white,', 'color: const Color(0xFF081120),')
        nav = nav.replace('backgroundColor: Colors.white,', 'backgroundColor: const Color(0xFF081120),')
        nav = nav.replace('Color(0xFFE9E4F1)', 'Color(0xFF182B43)')
        s = s[:nav_start] + nav + s[nav_end:]

p.write_text(s, encoding='utf-8')
print('Dark catalog reference applied: navy/purple surfaces, compact categories, screenshot category order.')
