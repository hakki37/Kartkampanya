import 'package:flutter/material.dart';
import '../services/campaign_service.dart';
import '../services/card_service.dart';
import '../pages/campaign_detail_page.dart';
import 'campaign_card.dart';
import 'category_menu.dart';

class CampaignContent extends StatefulWidget {
  final List<UserCard> cards;
  final String mode;
  final String initialCategory;
  const CampaignContent({super.key, required this.cards, this.mode = 'home', this.initialCategory = 'Tümü'});
  @override State<CampaignContent> createState() => _CampaignContentState();
}

class _CampaignContentState extends State<CampaignContent> {
  final service = CampaignService.instance;
  final search = TextEditingController();
  late String category = widget.initialCategory;
  String query = '';
  bool loading = true;
  List<Campaign> campaigns = const [];

  @override void initState() { super.initState(); _load(); }
  @override void dispose() { search.dispose(); super.dispose(); }
  Future<void> _load() async {
    try { final data = await service.fetchCampaigns(); if (mounted) setState(() { campaigns = data; loading = false; }); }
    catch (_) { if (mounted) setState(() => loading = false); }
  }

  List<Campaign> get filtered {
    Iterable<Campaign> result = campaigns;
    if (widget.mode == 'matched') result = result.where((c) => service.matchesAnyCard(c, widget.cards));
    if (category != 'Tümü') result = result.where((c) => c.category == category);
    final q = normalizeCampaignText(query);
    if (q.isNotEmpty) result = result.where((c) => normalizeCampaignText('${c.title} ${c.brand} ${c.bankName} ${c.category} ${c.description}').contains(q));
    final list = result.toList();
    if (widget.mode == 'matched') _sortMatched(list);
    return list;
  }

  void _sortMatched(List<Campaign> list) {
    list.sort((a, b) {
      final endCompare = _urgencyScore(b).compareTo(_urgencyScore(a));
      if (endCompare != 0) return endCompare;
      final benefitCompare = _benefitScore(b).compareTo(_benefitScore(a));
      if (benefitCompare != 0) return benefitCompare;
      final ad = a.endDate, bd = b.endDate;
      if (ad != null && bd != null) return ad.compareTo(bd);
      if (ad != null) return -1;
      if (bd != null) return 1;
      return 0;
    });
  }

  int _urgencyScore(Campaign c) {
    final end = c.endDate;
    if (end == null) return 0;
    final days = end.difference(DateTime.now()).inHours / 24;
    if (days <= 1) return 5000;
    if (days <= 3) return 4000;
    if (days <= 7) return 3000;
    if (days <= 14) return 2000;
    return 1000;
  }

  double _benefitScore(Campaign c) {
    final d = c.data;
    final type = normalizeCampaignText('${d['reward_type'] ?? ''}');
    final percent = num.tryParse('${d['reward_percent'] ?? ''}');
    final amount = num.tryParse('${d['max_reward'] ?? d['reward_amount'] ?? ''}');
    if (percent != null && percent > 0) return 10000 + percent.toDouble();
    if (amount != null && amount > 0) return 5000 + amount.toDouble();
    final text = normalizeCampaignText('${c.title} ${c.description}');
    if (text.contains('ucretsiz') || text.contains('bedava')) return 4500;
    if (text.contains('faizsiz')) return 3500;
    final installment = RegExp(r"(?<!\d)(\d{1,2})\s*(?:['’]?e|['’]?a)?\s*varan\s*taksit").firstMatch(text) ??
        RegExp(r'(?<!\d)(\d{1,2})\s*(?:taksit|taksitli)').firstMatch(text);
    if (installment != null) return 2500 + double.parse(installment.group(1)!);
    if (type.contains('bonus') || type.contains('puan') || type.contains('avantaj')) return 3000;
    if (text.contains('indirim')) return 3000;
    return 0;
  }

  @override
  Widget build(BuildContext context) {
    if (loading) return const Center(child: CircularProgressIndicator());
    final list = filtered;
    return Column(children: [
      Padding(padding: const EdgeInsets.fromLTRB(16, 8, 16, 12), child: Row(children: [
        Expanded(child: TextField(controller: search, onChanged: (v) => setState(() => query = v), decoration: InputDecoration(hintText: 'Kampanya, banka veya kategori ara...', prefixIcon: const Icon(Icons.search, size: 20), isDense: true, contentPadding: const EdgeInsets.symmetric(vertical: 12), filled: true, fillColor: const Color(0xFFF0EEF5), border: OutlineInputBorder(borderRadius: BorderRadius.circular(13), borderSide: BorderSide.none)))),
        const SizedBox(width: 8),
        OutlinedButton.icon(onPressed: _filterSheet, icon: const Icon(Icons.tune, size: 18), label: const Text('Filtrele'), style: OutlinedButton.styleFrom(padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(13)))),
      ])),
      CategoryMenu(categories: service.categories, selected: category, onSelected: (v) => setState(() => category = v)),
      const SizedBox(height: 7),
      Expanded(child: list.isEmpty
        ? Center(child: Padding(padding: const EdgeInsets.all(30), child: Text(widget.mode == 'matched' && widget.cards.isEmpty ? 'Önce Bendeki Kartlar bölümünden kart ekle.' : 'Bu filtreye uygun kampanya bulunamadı.', textAlign: TextAlign.center, style: const TextStyle(color: Color(0xFF777187), fontWeight: FontWeight.w700))))
        : ListView.builder(padding: const EdgeInsets.only(bottom: 18, top: 3), itemCount: list.length, itemBuilder: (_, i) {
            final c = list[i];
            return CampaignCard(campaign: c, isFavorite: service.isFavorite(c.id), onFavoriteTap: () async { await service.toggleFavorite(c.id); if (mounted) setState(() {}); }, onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => CampaignDetailPage(campaign: c))));
          })),
    ]);
  }

  void _filterSheet() {
    showModalBottomSheet(context: context, showDragHandle: true, builder: (_) => SafeArea(child: Padding(padding: const EdgeInsets.fromLTRB(20, 4, 20, 25), child: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start, children: [
      const Text('Filtrele', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900)), const SizedBox(height: 14),
      Wrap(spacing: 8, runSpacing: 8, children: service.categories.map((c) => ChoiceChip(label: Text(c), selected: category == c, showCheckmark: false, onSelected: (_) { setState(() => category = c); Navigator.pop(context); })).toList()),
    ]))));
  }
}
