from pathlib import Path
import re

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

# V14 already builds the complete SmartCampaignCard. Patch its benefit calculation
# directly instead of looking for an older reward Text() line.
old = re.compile(
    r"String advantage = '0 TL';\n"
    r"\s*if \(isInstallment\) \{.*?\n"
    r"\s*else if \(campaign\['reward_percent'\] is num.*?\n",
    re.S,
)
new = """String advantage = '0 TL';
    if (isInstallment) {
      advantage = taksit != null ? '$taksit taksit' : 'Taksit';
    } else if (reward is num && reward > 0) {
      advantage = '${reward.toDouble().toStringAsFixed(0)} TL';
    } else if (campaign['reward_percent'] is num && (campaign['reward_percent'] as num) > 0) {
      advantage = '%${(campaign['reward_percent'] as num).toDouble().toStringAsFixed(0)}';
    }
"""

s, count = old.subn(new, s, count=1)
if count == 0:
    # If the desired V14 block is already present, leave it alone.
    if "advantage = taksit != null ? '$taksit taksit' : 'Taksit';" not in s:
        raise SystemExit('V14 advantage block not found')

p.write_text(s, encoding='utf-8')
print('benefit display fixed safely')