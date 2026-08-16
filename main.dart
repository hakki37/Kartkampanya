import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'config.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  if (AppConfig.supabasePublishableKey.isEmpty) {
    runApp(const SetupApp());
    return;
  }
  await Supabase.initialize(
    url: AppConfig.supabaseUrl,
    anonKey: AppConfig.supabasePublishableKey,
  );
  runApp(const KartKampanyaApp());
}

class SetupApp extends StatelessWidget {
  const SetupApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
    home: Scaffold(
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Text(
            'Supabase anahtarı yapılandırılmamış. '
            'GitHub Actions için SUPABASE_PUBLISHABLE_KEY secret ekleyin.',
            textAlign: TextAlign.center,
          ),
        ),
      ),
    ),
  );
}

class KartKampanyaApp extends StatelessWidget {
  const KartKampanyaApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
    debugShowCheckedModeBanner: false,
    title: 'Kart Kampanya',
    theme: ThemeData(
      colorScheme: ColorScheme.fromSeed(seedColor: Colors.indigo),
      useMaterial3: true,
    ),
    home: const CampaignsPage(),
  );
}

class CampaignsPage extends StatefulWidget {
  const CampaignsPage({super.key});
  @override State<CampaignsPage> createState() => _CampaignsPageState();
}

class _CampaignsPageState extends State<CampaignsPage> {
  late Future<List<Map<String,dynamic>>> future;

  @override
  void initState() {
    super.initState();
    future = fetchCampaigns();
  }

  Future<List<Map<String,dynamic>>> fetchCampaigns() async {
    final rows = await Supabase.instance.client
        .from('active_campaigns')
        .select()
        .order('end_date', ascending: true);
    return List<Map<String,dynamic>>.from(rows);
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Kart Kampanya')),
    body: RefreshIndicator(
      onRefresh: () async => setState(() => future = fetchCampaigns()),
      child: FutureBuilder<List<Map<String,dynamic>>>(
        future: future,
        builder: (context, snap) {
          if (snap.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snap.hasError) {
            return Center(child: Text('Hata: ${snap.error}'));
          }
          final rows = snap.data ?? [];
          if (rows.isEmpty) {
            return const Center(child: Text('Aktif kampanya bulunamadı.'));
          }
          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: rows.length,
            itemBuilder: (_, i) {
              final c = rows[i];
              return Card(
                child: ListTile(
                  leading: const Icon(Icons.local_offer),
                  title: Text('${c['title'] ?? ''}'),
                  subtitle: Text(
                    '${c['merchant'] ?? ''}\n'
                    'Son tarih: ${c['end_date'] ?? '-'}',
                  ),
                ),
              );
            },
          );
        },
      ),
    ),
  );
}
