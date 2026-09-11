import 'package:flutter/material.dart';
import '../services/card_service.dart';
import '../widgets/campaign_content.dart';
import '../screens/favorites_screen.dart';
import '../screens/profile_screen.dart';

class HomeScreen extends StatelessWidget {
  final List<UserCard> cards;
  const HomeScreen({super.key, required this.cards});

  @override
  Widget build(BuildContext context) => SafeArea(
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(18, 18, 18, 4),
              child: Row(
                children: [
                  const Expanded(
                    child: Text(
                      'Kampanyaları Keşfet',
                      style: TextStyle(fontSize: 27, fontWeight: FontWeight.w900, color: Color(0xFF211D2D)),
                    ),
                  ),
                  IconButton(
                    tooltip: 'Favorilerim',
                    onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const FavoritesScreen())),
                    icon: const Icon(Icons.favorite_border, color: Color(0xFF6D3DF5)),
                  ),
                  IconButton(
                    tooltip: 'Profilim',
                    onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const ProfileScreen())),
                    icon: const Icon(Icons.person_outline, color: Color(0xFF6D3DF5)),
                  ),
                ],
              ),
            ),
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 18),
              child: Align(
                alignment: Alignment.centerLeft,
                child: Text(
                  'Kartlarına uygun fırsatları kolayca bul.',
                  style: TextStyle(color: Color(0xFF777187), fontSize: 12),
                ),
              ),
            ),
            const SizedBox(height: 5),
            Expanded(child: CampaignContent(cards: cards, mode: 'matched')),
          ],
        ),
      );
}
