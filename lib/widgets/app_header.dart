import 'package:flutter/material.dart';
import '../screens/favorites_screen.dart';
import '../screens/profile_screen.dart';

class AppHeader extends StatelessWidget implements PreferredSizeWidget {
  final String title;
  final IconData? actionIcon;
  final VoidCallback? onActionTap;
  final bool showBackButton;
  final bool showAccountActions;

  const AppHeader({
    super.key,
    required this.title,
    this.actionIcon,
    this.onActionTap,
    this.showBackButton = false,
    this.showAccountActions = true,
  });

  @override
  Widget build(BuildContext context) => AppBar(
        elevation: 0,
        scrolledUnderElevation: 0,
        backgroundColor: Theme.of(context).scaffoldBackgroundColor,
        automaticallyImplyLeading: showBackButton,
        titleSpacing: showBackButton ? 0 : 20,
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 20)),
        actions: [
          if (actionIcon != null) IconButton(icon: Icon(actionIcon), onPressed: onActionTap),
          if (showAccountActions && !showBackButton) ...[
            IconButton(
              tooltip: 'Favorilerim',
              icon: const Icon(Icons.favorite_border, color: Color(0xFF6D3DF5)),
              onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const FavoritesScreen())),
            ),
            IconButton(
              tooltip: 'Profilim',
              icon: const Icon(Icons.person_outline, color: Color(0xFF6D3DF5)),
              onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const ProfileScreen())),
            ),
          ],
          const SizedBox(width: 6),
        ],
      );

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);
}
