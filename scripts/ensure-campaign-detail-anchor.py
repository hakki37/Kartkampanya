from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

# apply-final-clean-ui intentionally replaces the presentation classes and may
# remove CampaignDetailPage. The existing detail repair script expects that
# class as an anchor, so restore a harmless placeholder before it runs.
if 'class CampaignDetailPage extends StatelessWidget {' not in s:
    anchor = 'class MyCardsPage extends StatefulWidget {'
    if anchor not in s:
        raise SystemExit('MyCardsPage anchor not found for CampaignDetailPage restoration')
    placeholder = 'class CampaignDetailPage extends StatelessWidget {}\n\n'
    s = s.replace(anchor, placeholder + anchor, 1)
    p.write_text(s, encoding='utf-8')
    print('CampaignDetailPage anchor restored')
else:
    print('CampaignDetailPage already present')
