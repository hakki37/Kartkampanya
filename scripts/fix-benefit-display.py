from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

marker = "class SmartCampaignCard extends StatelessWidget {"
helper = r'''String _campaignBenefitText(Map<String, dynamic> campaign, dynamic reward) {
  final title = '${campaign['title'] ?? ''}';
  final description = '${campaign['description'] ?? ''}';
  final text = '$title $description';
  final installment = RegExp(r'(\d+)\s*taksit', caseSensitive: false).firstMatch(text);
  if (installment != null) {
    return '💰 Tahmini avantaj: ${installment.group(1)} taksit';
  }

  if (reward is num) {
    return '💰 Tahmini avantaj: ${reward.toDouble().toStringAsFixed(0)} TL';
  }
  final amount = campaign['reward_amount'] ?? campaign['max_reward'];
  if (amount is num) {
    return '💰 Tahmini avantaj: ${amount.toDouble().toStringAsFixed(0)} TL';
  }
  return '';
}

'''
if 'String _campaignBenefitText(Map<String, dynamic> campaign, dynamic reward)' not in s:
    s = s.replace(marker, helper + marker, 1)

old = "'💰 Tahmini avantaj: \${(reward as num).toDouble().toStringAsFixed(0)} TL',"
new = "_campaignBenefitText(campaign, reward),"
if old in s:
    s = s.replace(old, new, 1)
else:
    raise SystemExit('reward display line not found')

p.write_text(s, encoding='utf-8')
print('benefit display fixed')
