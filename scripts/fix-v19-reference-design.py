from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

# The reference screen uses real bank marks in Bendeki Kartlar.
# Replace the legacy text-only leading widget with the same network logo
# helper used by the campaign catalog.
old = '''                    leading: Container(
                      width: 46,
                      height: 46,
                      decoration: BoxDecoration(
                        color: const Color(0xFF162844),
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(color: const Color(0xFF294263)),
                      ),
                      alignment: Alignment.center,
                      child: Text(
                        c.bank.length > 7 ? c.bank.substring(0, 7) : c.bank,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(fontSize: 9, fontWeight: FontWeight.w900),
                      ),
                    ),'''
new = '''                    leading: Container(
                      width: 52,
                      height: 52,
                      padding: const EdgeInsets.all(5),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(color: const Color(0xFF294263)),
                      ),
                      alignment: Alignment.center,
                      child: _CatalogLogo(
                        _logoUrl(_bankDomain(c.bank)),
                        size: 42,
                      ),
                    ),'''
if old in s:
    s = s.replace(old, new, 1)

# Keep bank matching tolerant of TEB/CEPTETEB naming differences and the
# common QNB/CardFinans naming difference.
needle = "        'kredi': ['kredi', 'kredi karti', 'credit'],"
insert = "        'teb': ['teb', 'cepteteb'],\n        'cepteteb': ['teb', 'cepteteb'],\n        'qnb': ['qnb', 'cardfinans'],\n        'cardfinans': ['qnb', 'cardfinans'],\n"
if needle in s and "'teb': ['teb', 'cepteteb']" not in s:
    s = s.replace(needle, insert + needle, 1)

# The detail screen is a full route, never a bottom sheet. Keep this guard
# so an older generated class cannot accidentally reintroduce the sheet.
if 'class CampaignDetailPage extends StatelessWidget {' not in s:
    raise SystemExit('CampaignDetailPage missing; v18 must run before v19')

p.write_text(s, encoding='utf-8')
print('v19 reference design fixes applied')
