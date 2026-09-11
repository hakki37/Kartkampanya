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
      if (parts.join(' ').length >= 850) break;
    }

    clean = parts.join(' ').trim();
    if (clean.length > 850) {
      final cut = clean.substring(0, 850);
      final end = cut.lastIndexOf(RegExp(r'[.!?]'));
      clean = (end > 220 ? cut.substring(0, end + 1) : '$cut…').trim();
    }
    return clean;
  }

  String _summary(String text) {
    final clean = text.trim();
    if (clean.length <= 280) return clean;
    final cut = clean.substring(0, 280);
    final end = cut.lastIndexOf(RegExp(r'[.!?]'));
    return (end > 100 ? cut.substring(0, end + 1) : '$cut…').trim();
  }

  @override
  Widget build(BuildContext context) {
    final c = widget.campaign;
    final detail = _compactDetail(_cleanDetail(c.description));
    final summary = _summary(detail);
    final brandColor = c.brandColor;

    return Scaffold(
      backgroundColor: const Color(0xFFF8F7FC),
      body: SafeArea(
        child: ListView(
          padding: EdgeInsets.zero,
          children: [
            Container(
              decoration: BoxDecoration(
                color: brandColor,
                borderRadius: const BorderRadius.vertical(
                  bottom: Radius.circular(28),
                ),
              ),
              padding: const EdgeInsets.fromLTRB(12, 6, 12, 26),
              child: Column(
                children: [
                  Row(
                    children: [
                      IconButton(
                        onPressed: () => Navigator.pop(context),
                        icon: const Icon(Icons.arrow_back_rounded),
                        color: Colors.white,
                      ),
                      const Expanded(
                        child: Center(
                          child: Text(
                            'Kampanya Detayı',
                            style: TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.w900,
                              fontSize: 16,
                            ),
                          ),
                        ),
                      ),
                      IconButton(
                        onPressed: toggle,
                        icon: Icon(
                          favorite
                              ? Icons.favorite_rounded
                              : Icons.favorite_border_rounded,
                          color: Colors.white,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Container(
                    constraints: const BoxConstraints(minHeight: 82),
                    padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 18),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(.14),
                      borderRadius: BorderRadius.circular(22),
                      border: Border.all(color: Colors.white.withOpacity(.22)),
                    ),
                    alignment: Alignment.center,
                    child: Text(
                      c.brand,
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 27,
                        fontWeight: FontWeight.w900,
                        letterSpacing: -.3,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 22, 20, 0),
              child: Text(
                c.title,
                style: const TextStyle(
                  fontSize: 23,
                  height: 1.18,
                  fontWeight: FontWeight.w900,
                  color: Color(0xFF211D2D),
                ),
              ),
            ),
            if (summary.isNotEmpty)
              Padding(
                padding: const EdgeInsets.fromLTRB(20, 10, 20, 0),
                child: Text(
                  summary,
                  style: const TextStyle(
                    color: Color(0xFF5F5969),
                    fontSize: 15,
                    height: 1.48,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
            const Padding(
              padding: EdgeInsets.fromLTRB(20, 18, 20, 8),
              child: Divider(height: 1),
            ),
            _InfoRow(Icons.local_offer_outlined, 'Kategori', c.category),
            _InfoRow(
              Icons.account_balance_outlined,
              'Banka',
              c.bankName.isEmpty ? 'Belirtilmemiş' : c.bankName,
            ),
            if (c.cardName.isNotEmpty)
              _InfoRow(Icons.credit_card_outlined, 'Kart', c.cardName),
            if (c.network.isNotEmpty)
              _InfoRow(Icons.payment_outlined, 'Kart ağı', c.network),
            _InfoRow(
              Icons.calendar_today_outlined,
              'Kampanya Tarihleri',
              c.dateRangeLabel,
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 16, 20, 0),
              child: Container(
                padding: const EdgeInsets.fromLTRB(18, 18, 18, 20),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFE3DFEA)),
                  boxShadow: const [
                    BoxShadow(
                      blurRadius: 18,
                      offset: Offset(0, 5),
                      color: Color(0x10000000),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          width: 34,
                          height: 34,
                          decoration: BoxDecoration(
                            color: brandColor.withOpacity(.10),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Icon(
                            Icons.description_outlined,
                            size: 19,
                            color: brandColor,
                          ),
                        ),
                        const SizedBox(width: 10),
                        const Text(
                          'Kampanya Detayları',
                          style: TextStyle(
                            fontWeight: FontWeight.w900,
                            fontSize: 17,
                            color: Color(0xFF211D2D),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Text(
                      detail.isEmpty ? 'Detay bulunmuyor.' : detail,
                      style: const TextStyle(
                        color: Color(0xFF5F5969),
                        fontSize: 14.5,
                        height: 1.55,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 16, 20, 0),
              child: SizedBox(
                height: 54,
                child: FilledButton.icon(
                  onPressed: c.sourceUrl.isEmpty ? null : open,
                  icon: const Icon(Icons.open_in_new_rounded),
                  label: const Text(
                    'Kampanyaya Git',
                    style: TextStyle(fontWeight: FontWeight.w900),
                  ),
                  style: FilledButton.styleFrom(
                    backgroundColor: brandColor,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(17),
                    ),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 30),
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
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 38,
              height: 38,
              decoration: BoxDecoration(
                color: const Color(0xFFF0EDF5),
                borderRadius: BorderRadius.circular(11),
              ),
              child: Icon(icon, size: 20, color: const Color(0xFF777187)),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    label,
                    style: const TextStyle(
                      color: Color(0xFF777187),
                      fontSize: 11.5,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 3),
                  Text(
                    value,
                    style: const TextStyle(
                      fontWeight: FontWeight.w800,
                      fontSize: 15,
                      color: Color(0xFF211D2D),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      );
}
