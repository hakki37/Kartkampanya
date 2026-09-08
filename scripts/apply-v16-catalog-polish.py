from pathlib import Path
import re

p = Path("lib/main.dart")
s = p.read_text(encoding="utf-8")

marker = "class _CatalogLogo extends StatelessWidget {"
if marker not in s:
    raise SystemExit("v15 catalog UI not found")

helper = r'''
String _catalogBenefitText(Map<String, dynamic> campaign) {
  final title = decodeHtmlEntities('${campaign['title'] ?? ''}');
  final desc = decodeHtmlEntities('${campaign['description'] ?? ''}');
  final rewardType = decodeHtmlEntities('${campaign['reward_type'] ?? ''}');
  final text = '$title $desc $rewardType';

  num? asNum(dynamic v) {
    if (v is num) return v;
    return num.tryParse('${v ?? ''}'.replaceAll(',', '.'));
  }

  final percent = asNum(campaign['reward_percent']) ??
      asNum(campaign['_calculatedPercent']);
  final reward = asNum(campaign['_calculatedReward']) ??
      asNum(campaign['_reward']) ??
      asNum(campaign['reward_amount']) ??
      asNum(campaign['max_reward']);

  final installment = RegExp(
    r'(?<!\d)(\d+)\s*(?:taksite|taksit|taksitli)',
    caseSensitive: false,
  ).firstMatch(text)?.group(1);

  if (installment != null) return '$installment taksit';
  if (percent != null && percent > 0) {
    final p = percent.toDouble();
    return '%${p.toStringAsFixed(p == p.roundToDouble() ? 0 : 1)} indirim';
  }
  if (reward != null && reward > 0) {
    return '${reward.toDouble().toStringAsFixed(0)} TL';
  }
  return '0 TL';
}

String _catalogLogoUrl(String domain) =>
    'https://logo.clearbit.com/$domain';
'''
if "String _catalogBenefitText(" not in s:
    s = s.replace(marker, helper + "\n" + marker, 1)

old = "Padding(padding: const EdgeInsets.only(top: 8), child: Text('💰 Tahmini avantaj: ${hasMoney ? '${(reward as num).toDouble().toStringAsFixed(0)} TL' : installment != null ? '$installment taksit' : '0 TL'}', style: TextStyle(fontWeight: FontWeight.w800, color: hasMoney || installment != null ? Colors.amber : null))),"
new = "Padding(padding: const EdgeInsets.only(top: 8), child: Text('💰 Tahmini avantaj: ${_catalogBenefitText(campaign)}', style: const TextStyle(fontWeight: FontWeight.w800, color: Colors.amber))),"
if old not in s:
    raise SystemExit("benefit widget not found")
s = s.replace(old, new, 1)

s = s.replace("String _logoUrl(String domain) =>\n    'https://www.google.com/s2/favicons?domain=$domain&sz=128';",
              "String _logoUrl(String domain) => _catalogLogoUrl(domain);")

p.write_text(s, encoding="utf-8")
print("v16 catalog polish applied")
