from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

# Reference bottom navigation: exact five labels/icons from the approved reference.
s = s.replace("label:'Kartıma Uygun'", "label:'Kampanyalar'")
s = s.replace("label: 'Kartıma Uygun'", "label: 'Kampanyalar'")
s = s.replace("label:'Bendeki Kartlar'", "label:'Kartlarım'")
s = s.replace("label: 'Bendeki Kartlar'", "label: 'Kartlarım'")

# Use the same visual icon family as the reference: home, tag, card, grid, profile.
s = s.replace("Icons.auto_awesome_outlined", "Icons.local_offer_outlined")
s = s.replace("Icons.auto_awesome", "Icons.local_offer_rounded")

# Normalize the other four destinations as well so later UI generators cannot drift.
s = s.replace("Icons.home_outlined", "Icons.home_outlined")
s = s.replace("Icons.home)", "Icons.home_rounded)")
s = s.replace("Icons.credit_card)", "Icons.credit_card_rounded)")
s = s.replace("Icons.grid_view)", "Icons.grid_view_rounded)")
s = s.replace("Icons.person)", "Icons.person_rounded)")

p.write_text(s, encoding='utf-8')
print('v42 reference bottom navigation locked')
