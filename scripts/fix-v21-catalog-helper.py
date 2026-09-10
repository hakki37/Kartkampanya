from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

signature = 'String _catalogBenefitText(Map<String, dynamic> campaign) {'
if signature not in s:
    marker = 'class _CatalogLogo extends StatelessWidget {'
    helper = r'''String _catalogBenefitText(Map<String, dynamic> campaign) {
  final title = decodeHtmlEntities('${campaign['title'] ?? ''}');
  final desc = decodeHtmlEntities('${campaign['description'] ?? ''}');
  final campaignText = decodeHtmlEntities('${campaign['campaign_text'] ?? ''}');
  final rewardType = decodeHtmlEntities('${campaign['reward_type'] ?? ''}');
  final text = '$title $desc $campaignText $rewardType';

  num? asNum(dynamic value) {
    if (value is num) return value;
    return num.tryParse('${value ?? ''}'.replaceAll(',', '.'));
  }

  final percent = asNum(campaign['reward_percent']) ?? asNum(campaign['_calculatedPercent']);
  final reward = asNum(campaign['_calculatedReward']) ?? asNum(campaign['_reward']) ?? asNum(campaign['reward_amount']) ?? asNum(campaign['max_reward']);
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

p.write_text(s, encoding='utf-8')
print('v21 catalog benefit helper guaranteed')
