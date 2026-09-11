import 'package:flutter/material.dart';
import '../services/campaign_service.dart';

class CampaignCard extends StatelessWidget {
  final Campaign campaign;
  final bool isFavorite;
  final VoidCallback? onTap;
  final VoidCallback? onFavoriteTap;
  const CampaignCard({super.key, required this.campaign, this.isFavorite = false, this.onTap, this.onFavoriteTap});

  String _formatAmount(num value) {
    final rounded = value.round();
    final s = rounded.toString();
    final parts = <String>[];
    for (var i = s.length; i > 0; i -= 3) {
      final start = i - 3 < 0 ? 0 : i - 3;
      parts.insert(0, s.substring(start, i));
    }
    return parts.join('.');
  }

  String _cleanCardDescription(String value) {
    var text = value.trim();
    if (text.isEmpty) return '';

    // Some bank pages put the entire site navigation into the scraped description.
    const markers = [
      'Ara Faiz ve Ücretler',
      'KART İŞLEMLERİ',
      'Kartlarımız Kampanyalar',
      'Merak Ettikleriniz Kampüs Modu Menü',
      'Anasayfa ➜ Kampanyalar',
      'AXESS JÜZDAN FREE',
      'Başvuru Maximum Dünyası Geri Maximum Dünyası',
      'Başvuru Maximum Dünyası Maximum',
      'İLGİNİZİ ÇEKEBİLECEK',
      'VakıfBank Web Siteleri',
      'Hızlı Linkler',
      'Sıkça Sorulan Sorular',
      'Çerez Tercihleri',
      'Site Haritası',
    ];
    for (final marker in markers) {
      final i = text.toLowerCase().indexOf(marker.toLowerCase());
      if (i >= 0) text = text.substring(0, i).trim();
    }

    // Remove common breadcrumb/navigation prefixes.
    text = text.replaceFirst(RegExp(r'^(?:Ana Sayfa\s*[>|➜-]\s*)+', caseSensitive: false), '').trim();
    text = text.replaceAll(RegExp(r'\s+'), ' ');

    // If what remains is still clearly navigation, don't show it to the user.
    final low = text.toLowerCase();
    const navWords = [
      'anasayfa', 'kampanyalar', 'kartlarımız', 'menü', 'merak ettikleriniz',
      'faiz ve ücretler', 'kart işlemleri', 'başvuru', 'maximum dünyası',
      'axess ile tanışın', 'jüzdan free', 'ticari kartlar',
    ];
    final hits = navWords.where(low.contains).length;
    if (text.length < 30 || hits >= 3) return '';

    // De-duplicate repeated sentences caused by scraper output.
    final parts = text.split(RegExp(r'(?<=[.!?])\s+')).map((e) => e.trim()).where((e) => e.length >= 15).toList();
    final seen = <String>{};
    final unique = <String>[];
    for (final part in parts) {
      final key = part.toLowerCase().replaceAll(RegExp(r'\s+'), ' ');
      if (seen.add(key)) unique.add(part);
      if (unique.join(' ').length >= 320) break;
    }
    text = unique.isEmpty ? text : unique.join(' ');
    return text.length > 320 ? '${text.substring(0, 320).trim()}…' : text;
  }

  String? get estimatedAdvantage {
    final data = campaign.data;
    final rewardType = '${data['reward_type'] ?? ''}'.trim().toLowerCase();
    final rewardPercent = num.tryParse('${data['reward_percent'] ?? ''}');
    final rewardAmount = num.tryParse('${data['max_reward'] ?? data['reward_amount'] ?? ''}');
    if (rewardPercent != null && rewardPercent > 0) return '%${rewardPercent % 1 == 0 ? rewardPercent.toInt() : rewardPercent} İndirim';
    if (rewardAmount != null && rewardAmount > 0) {
      if (rewardType.contains('taksit')) return '${rewardAmount.toInt()} Taksit';
      if (rewardType.contains('percent')) return '%${rewardAmount.toInt()} İndirim';
      final titleLow = campaign.title.toLowerCase();
      final label = rewardType == 'tl' && titleLow.contains('bonus') ? 'TL Bonus' : rewardType == 'bonus' ? 'TL Bonus' : rewardType.isEmpty ? 'TL Avantaj' : rewardType;
      return '${_formatAmount(rewardAmount)} $label';
    }

    final title = campaign.title;
    final description = campaign.description;
    final titleDiscount = RegExp(r'%\s*(\d{1,3})\s*(?:indirim|indirimli|avantaj|bonus)', caseSensitive: false).firstMatch(title);
    if (titleDiscount != null) return '%${titleDiscount.group(1)} İndirim';
    final titleBonus = RegExp(r'(\d{1,3}(?:[.\s]\d{3})*|\d+)\s*TL\s*(?:bonus|puan|avantaj)', caseSensitive: false).allMatches(title).toList();
    if (titleBonus.isNotEmpty) return '${titleBonus.last.group(1)} TL Bonus';
    final titleInstallment = RegExp(r'(?<!\d)(\d{1,2})\s*(?:taksit|taksitli)', caseSensitive: false).firstMatch(title);
    if (titleInstallment != null) return '${titleInstallment.group(1)} Taksit';
    final text = '$title $description';
    final discount = RegExp(r'%\s*(\d{1,3})\s*(?:indirim|indirimli|avantaj)', caseSensitive: false).firstMatch(text);
    if (discount != null) return '%${discount.group(1)} İndirim';
    final installment = RegExp(r'(?<!\d)(\d{1,2})\s*(?:taksit|taksitli)', caseSensitive: false).firstMatch(title);
    if (installment != null) return '${installment.group(1)} Taksit';
    final amount = RegExp(r'(\d{1,3}(?:[.\s]\d{3})*|\d+)\s*TL\b', caseSensitive: false).firstMatch(text);
    if (amount != null) return '${amount.group(1)} TL Avantaj';
    if (RegExp(r'\b(?:ücretsiz|bedava)\b', caseSensitive: false).hasMatch(text)) return 'Ücretsiz';
    return null;
  }

  @override
  Widget build(BuildContext context) {
    final advantage = estimatedAdvantage;
    final description = _cleanCardDescription(campaign.description);
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18), side: const BorderSide(color: Color(0xFFE5DFEB))),
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
              _Logo(campaign.brand, campaign.brandColor),
              const SizedBox(width: 12),
              Expanded(child: Text(campaign.title, style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15, height: 1.25))),
              const SizedBox(width: 8),
              Column(crossAxisAlignment: CrossAxisAlignment.end, children: [
                _Badge(campaign.badgeType, campaign.badgeLabel),
                const SizedBox(height: 6),
                GestureDetector(onTap: onFavoriteTap, child: Icon(isFavorite ? Icons.favorite : Icons.favorite_border, size: 20, color: isFavorite ? Colors.redAccent : const Color(0xFF77717F))),
              ]),
            ]),
            const SizedBox(height: 8),
            Text(description.isEmpty ? 'Kampanya detaylarını görmek için dokun.' : description, maxLines: 3, overflow: TextOverflow.ellipsis, style: const TextStyle(color: Color(0xFF6F687A), fontSize: 12.5, height: 1.35)),
            const SizedBox(height: 10),
            Wrap(spacing: 7, runSpacing: 6, children: [
              _Tag(Icons.local_offer_outlined, campaign.category),
              if (campaign.bankName.isNotEmpty) _Tag(Icons.account_balance_outlined, campaign.bankName),
              if (campaign.cardName.isNotEmpty) _Tag(Icons.credit_card_outlined, campaign.cardName),
            ]),
            const SizedBox(height: 11),
            Row(children: [
              if (advantage != null) Expanded(child: _Advantage(advantage)) else const Spacer(),
              const SizedBox(width: 10),
              ElevatedButton.icon(
                onPressed: onTap,
                style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF6D3DF5), foregroundColor: Colors.white, elevation: 0, padding: const EdgeInsets.symmetric(horizontal: 15, vertical: 9), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(11))),
                icon: const Text('Detaylar', style: TextStyle(fontSize: 12.5, fontWeight: FontWeight.w800)),
                label: const Icon(Icons.arrow_forward, size: 16),
              ),
            ]),
          ]),
        ),
      ),
    );
  }
}

class _Advantage extends StatelessWidget {
  final String value;
  const _Advantage(this.value);
  @override
  Widget build(BuildContext context) => Container(
        constraints: const BoxConstraints(minHeight: 58),
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
        decoration: BoxDecoration(color: const Color(0xFFFFF4CC), border: Border.all(color: const Color(0xFFFFD76A)), borderRadius: BorderRadius.circular(12)),
        child: Row(children: [
          const Icon(Icons.local_offer, color: Color(0xFFE7A400), size: 22),
          const SizedBox(width: 8),
          Flexible(child: Column(crossAxisAlignment: CrossAxisAlignment.start, mainAxisAlignment: MainAxisAlignment.center, children: [
            const Text('Tahmini Avantaj', style: TextStyle(color: Color(0xFFB87500), fontSize: 10.5, fontWeight: FontWeight.w600)),
            Text(value, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(color: Color(0xFFB56B00), fontSize: 14, fontWeight: FontWeight.w900)),
          ])),
        ]),
      );
}

class _Logo extends StatelessWidget {
  final String text;
  final Color color;
  const _Logo(this.text, this.color);
  @override
  Widget build(BuildContext context) => Container(width: 48, height: 48, decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(12)), alignment: Alignment.center, child: Text(text.isEmpty ? '?' : text.substring(0, 1).toUpperCase(), style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w900, fontSize: 18)));
}

class _Badge extends StatelessWidget {
  final BadgeType type;
  final String label;
  const _Badge(this.type, this.label);
  @override
  Widget build(BuildContext context) {
    final urgent = type == BadgeType.urgent;
    return Container(padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4), decoration: BoxDecoration(color: urgent ? const Color(0xFFFDEAEA) : const Color(0xFFE9F6EC), borderRadius: BorderRadius.circular(20)), child: Row(mainAxisSize: MainAxisSize.min, children: [Icon(Icons.access_time, size: 11, color: urgent ? const Color(0xFFD32F2F) : const Color(0xFF2E7D32)), const SizedBox(width: 3), Text(label, style: TextStyle(color: urgent ? const Color(0xFFD32F2F) : const Color(0xFF2E7D32), fontSize: 10.5, fontWeight: FontWeight.w800))]));
  }
}

class _Tag extends StatelessWidget {
  final IconData icon;
  final String label;
  const _Tag(this.icon, this.label);
  @override
  Widget build(BuildContext context) => Container(padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 5), decoration: BoxDecoration(color: const Color(0xFFF1EFF5), borderRadius: BorderRadius.circular(8)), child: Row(mainAxisSize: MainAxisSize.min, children: [Icon(icon, size: 12, color: const Color(0xFF77717F)), const SizedBox(width: 4), Text(label, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 10.5, color: Color(0xFF77717F)))]));
}
