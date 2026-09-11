import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../services/campaign_service.dart';

class CampaignDetailPage extends StatefulWidget {
  final Campaign campaign;
  const CampaignDetailPage({super.key, required this.campaign});
  @override
  State<CampaignDetailPage> createState() => _CampaignDetailPageState();
}

class _CampaignDetailPageState extends State<CampaignDetailPage> {
  bool favorite = false;

  @override
  void initState() {
    super.initState();
    favorite = CampaignService.instance.isFavorite(widget.campaign.id);
  }

  Future<void> toggle() async {
    await CampaignService.instance.toggleFavorite(widget.campaign.id);
    if (mounted) setState(() => favorite = !favorite);
  }

  Future<void> open() async {
    final uri = Uri.tryParse(widget.campaign.sourceUrl);
    if (uri != null && uri.hasScheme) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }

  String _cleanDetail(String value) {
    var text = value.trim();
    const cutMarkers = [
      'İLGİNİZİ ÇEKEBİLECEK',
      'İlginizi Çekebilecek',
      'YENİLENEN BONUSFLAŞ',
      'BONUS\'U TANIYIN',
      'Cüzdan | Kampanyalar | Ödemeler | Kartlar',
      'VakıfBank Web Siteleri',
      'Hızlı Linkler',
      'Sıkça Sorulan Sorular',
      'Çerez Tercihleri',
      'Site Haritası',
      'Footer',
    ];
    for (final marker in cutMarkers) {
      final i = text.toLowerCase().indexOf(marker.toLowerCase());
      if (i > 0) text = text.substring(0, i).trim();
    }

    final bodyStart = text.toLowerCase().indexOf('katılmak için');
    if (bodyStart > 0 && bodyStart < 1200) {
      final prefix = text.substring(0, bodyStart);
      if (prefix.length > 100 && prefix.contains('|')) {
        text = text.substring(bodyStart).trim();
      }
    }
    return text;
  }

  String _compactDetail(String text) {
    var clean = text.trim();
    if (clean.isEmpty) return '';

    // Scraped pages can contain the same condition paragraph dozens of times.
    // Keep only unique, useful sentences and stop before the content becomes a wall of text.
    final rawParts = clean
        .split(RegExp(r'(?<=[.!?])\s+'))
        .map((e) => e.trim())
        .where((e) => e.length >= 18)
        .toList();

    final seen = <String>{};
    final parts = <String>[];
    for (final part in rawParts) {
      final key = part
          .toLowerCase()
          .replaceAll(RegExp(r'[^a-z0-9çğıöşüİÇĞIÖŞÜ]+'), ' ')
          .replaceAll(RegExp(r'\s+'), ' ')
          .trim();
      if (key.isEmpty || seen.contains(key)) continue;
      seen.add(key);
      parts.add(part);
      if (parts.join(' ').length >= 700) break;
    }

    clean = parts.join(' ').trim();
    if (clean.length > 700) {
      final cut = clean.substring(0, 700);
      final end = cut.lastIndexOf(RegExp(r'[.!?]'));
      clean = (end > 220 ? cut.substring(0, end + 1) : '$cut…').trim();
    }
    return clean;
  }

  String _summary(String text) {
    final clean = text.trim();
    if (clean.length <= 260) return clean;
    final cut = clean.substring(0, 260);
    final end = cut.lastIndexOf(RegExp(r'[.!?]'));
    return (end > 100 ? cut.substring(0, end + 1) : '$cut…').trim();
  }

  @override
  Widget build(BuildContext context) {
    final c = widget.campaign;
    final detail = _compactDetail(_cleanDetail(c.description));
    final summary = _summary(detail);

    return Scaffold(
      backgroundColor: const Color(0xFFF8F7FC),
      body: SafeArea(
        child: ListView(
          padding: EdgeInsets.zero,
          children: [
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              child: Row(children: [
                IconButton(icon: const Icon(Icons.arrow_back_rounded), onPressed: () => Navigator.pop(context)),
                const Expanded(child: Center(child: Text('Kampanya Detayı', style: TextStyle(fontWeight: FontWeight.w900, fontSize: 16)))),
                IconButton(icon: Icon(favorite ? Icons.favorite : Icons.favorite_border, color: favorite ? Colors.redAccent : null), onPressed: toggle),
              ]),
            ),
            Container(
              margin: const EdgeInsets.fromLTRB(16, 4, 16, 0),
              height: 160,
              decoration: BoxDecoration(color: c.brandColor, borderRadius: BorderRadius.circular(20)),
              alignment: Alignment.center,
              child: Text(c.brand, textAlign: TextAlign.center, style: const TextStyle(color: Colors.white, fontSize: 25, fontWeight: FontWeight.w900)),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 18, 20, 0),
              child: Text(c.title, style: const TextStyle(fontSize: 21, fontWeight: FontWeight.w900, color: Color(0xFF211D2D))),
            ),
            if (summary.isNotEmpty)
              Padding(
                padding: const EdgeInsets.fromLTRB(20, 10, 20, 0),
                child: Text(summary, style: const TextStyle(color: Color(0xFF5F5969), height: 1.45)),
              ),
            const Padding(padding: EdgeInsets.fromLTRB(20, 18, 20, 0), child: Divider()),
            _InfoRow(Icons.local_offer_outlined, 'Kategori', c.category),
            _InfoRow(Icons.account_balance_outlined, 'Banka', c.bankName.isEmpty ? 'Belirtilmemiş' : c.bankName),
            if (c.cardName.isNotEmpty) _InfoRow(Icons.credit_card_outlined, 'Kart', c.cardName),
            if (c.network.isNotEmpty) _InfoRow(Icons.payment_outlined, 'Kart ağı', c.network),
            _InfoRow(Icons.calendar_today_outlined, 'Kampanya Tarihleri', c.dateRangeLabel),
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 12, 20, 0),
              child: Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16), border: Border.all(color: const Color(0xFFE7E1EE))),
                child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  const Text('Kampanya Detayları', style: TextStyle(fontWeight: FontWeight.w900, fontSize: 16)),
                  const SizedBox(height: 8),
                  Text(detail.isEmpty ? 'Detay bulunmuyor.' : detail, style: const TextStyle(color: Color(0xFF5F5969), height: 1.45)),
                ]),
              ),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 14, 20, 0),
              child: SizedBox(
                height: 52,
                child: FilledButton.icon(
                  onPressed: c.sourceUrl.isEmpty ? null : open,
                  icon: const Icon(Icons.open_in_new_rounded),
                  label: const Text('Kampanyaya Git', style: TextStyle(fontWeight: FontWeight.w900)),
                  style: FilledButton.styleFrom(backgroundColor: const Color(0xFF6D3DF5), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16))),
                ),
              ),
            ),
            const SizedBox(height: 28),
          ],
        ),
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  const _InfoRow(this.icon, this.label, this.value);
  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
        child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Icon(icon, size: 20, color: const Color(0xFF777187)),
          const SizedBox(width: 12),
          Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(label, style: const TextStyle(color: Color(0xFF777187), fontSize: 11)),
            const SizedBox(height: 2),
            Text(value, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14, color: Color(0xFF211D2D))),
          ])),
        ]),
      );
}
