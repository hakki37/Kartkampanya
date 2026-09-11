import 'package:flutter/material.dart';
import '../services/card_service.dart';
import '../widgets/campaign_content.dart';

class HomeScreen extends StatelessWidget {
  final List<UserCard> cards;
  const HomeScreen({super.key, required this.cards});

  @override
  Widget build(BuildContext context) => SafeArea(
        child: Column(
          children: [
            const Padding(
              padding: EdgeInsets.fromLTRB(18, 18, 18, 4),
              child: Align(
                alignment: Alignment.centerLeft,
                child: Text(
                  'Kampanyaları Keşfet',
                  style: TextStyle(fontSize: 27, fontWeight: FontWeight.w900, color: Color(0xFF211D2D)),
                ),
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
