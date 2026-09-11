import 'package:flutter/material.dart';

class QuickActions extends StatelessWidget {
  final VoidCallback onFavorites;
  final VoidCallback onProfile;
  const QuickActions({super.key, required this.onFavorites, required this.onProfile});

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.fromLTRB(16, 8, 16, 4),
    child: Row(children: [
      Expanded(child: OutlinedButton.icon(onPressed: onFavorites, icon: const Icon(Icons.favorite_outline, size: 18), label: const Text('Favorilerim'))),
      const SizedBox(width: 10),
      Expanded(child: OutlinedButton.icon(onPressed: onProfile, icon: const Icon(Icons.person_outline, size: 18), label: const Text('Profilim'))),
    ]),
  );
}
