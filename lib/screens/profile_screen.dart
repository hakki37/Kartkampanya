import 'package:flutter/material.dart';
import '../services/auth_service.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final user = AuthService.instance.currentUser;
    return Scaffold(
      appBar: AppBar(title: const Text('Profilim', style: TextStyle(fontWeight: FontWeight.w900))),
      body: ListView(
        padding: const EdgeInsets.all(18),
        children: [
          Card(
            child: ListTile(
              leading: const CircleAvatar(child: Icon(Icons.person_outline)),
              title: Text(user?.email ?? 'Kullanıcı', style: const TextStyle(fontWeight: FontWeight.w800)),
              subtitle: const Text('Kart Kampanya hesabın'),
            ),
          ),
          const SizedBox(height: 12),
          Card(
            child: ListTile(
              leading: const Icon(Icons.favorite_outline),
              title: const Text('Favorilerim', style: TextStyle(fontWeight: FontWeight.w800)),
              subtitle: const Text('Kaydettiğin kampanyaları görüntüle'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => Navigator.pushNamed(context, '/favorites'),
            ),
          ),
          const SizedBox(height: 24),
          OutlinedButton.icon(
            onPressed: () async => AuthService.instance.signOut(),
            icon: const Icon(Icons.logout),
            label: const Text('Çıkış Yap'),
          ),
        ],
      ),
    );
  }
}
