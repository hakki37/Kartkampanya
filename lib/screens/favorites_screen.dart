import 'package:flutter/material.dart';
import '../services/campaign_service.dart';
import '../widgets/campaign_card.dart';

class FavoritesScreen extends StatefulWidget {
  const FavoritesScreen({super.key});
  @override
  State<FavoritesScreen> createState() => _FavoritesScreenState();
}

class _FavoritesScreenState extends State<FavoritesScreen> {
  final service = CampaignService.instance;
  bool loading = true;
  List<Campaign> campaigns = const [];

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    try {
      final all = await service.fetchCampaigns();
      if (mounted) setState(() { campaigns = all.where((c) => service.isFavorite(c.id)).toList(); loading = false; });
    } catch (_) {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<void> _toggle(String id) async {
    await service.toggleFavorite(id);
    await _load();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Favorilerim', style: TextStyle(fontWeight: FontWeight.w900))),
    body: loading
      ? const Center(child: CircularProgressIndicator())
      : campaigns.isEmpty
        ? const Center(child: Padding(padding: EdgeInsets.all(28), child: Text('Henüz favori kampanyan yok.\nKampanyalardaki ❤️ simgesine dokunarak ekleyebilirsin.', textAlign: TextAlign.center, style: TextStyle(color: Color(0xFF77717F), fontWeight: FontWeight.w700))))
        : ListView.builder(
            padding: const EdgeInsets.only(top: 6, bottom: 20),
            itemCount: campaigns.length,
            itemBuilder: (_, i) => CampaignCard(
              campaign: campaigns[i],
              isFavorite: true,
              onFavoriteTap: () => _toggle(campaigns[i].id),
              onTap: () => Navigator.pushNamed(context, '/campaign-detail', arguments: campaigns[i]),
            ),
          ),
  );
}
