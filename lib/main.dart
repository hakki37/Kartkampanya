import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'config.dart';
import 'pages/login_page.dart';
import 'screens/home_screen.dart';
import 'screens/campaigns_screen.dart';
import 'screens/my_cards_screen.dart';
import 'screens/categories_screen.dart';
import 'widgets/bottom_navigation.dart';
import 'services/auth_service.dart';
import 'services/card_service.dart';
import 'services/campaign_service.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Supabase.initialize(url: AppConfig.supabaseUrl, anonKey: AppConfig.supabasePublishableKey);
  await CampaignService.instance.loadUserState();
  runApp(const KartKampanyaApp());
}

class KartKampanyaApp extends StatelessWidget {
  const KartKampanyaApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'Kart Kampanya', debugShowCheckedModeBanner: false,
    theme: ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF6D3DF5), brightness: Brightness.light),
      scaffoldBackgroundColor: const Color(0xFFF8F7FC), fontFamily: 'Roboto',
      appBarTheme: const AppBarTheme(elevation: 0, backgroundColor: Color(0xFFF8F7FC), foregroundColor: Color(0xFF211D2D)),
      cardTheme: const CardThemeData(elevation: 0, surfaceTintColor: Colors.transparent),
    ),
    home: const AuthGate(),
  );
}

class AuthGate extends StatelessWidget {
  const AuthGate({super.key});
  @override
  Widget build(BuildContext context) => StreamBuilder<AuthState>(
    stream: AuthService.instance.authStateChanges,
    builder: (_, __) => Supabase.instance.client.auth.currentSession == null ? const LoginPage() : const MainScaffold(),
  );
}

class MainScaffold extends StatefulWidget {
  const MainScaffold({super.key});
  @override State<MainScaffold> createState() => _MainScaffoldState();
}

class _MainScaffoldState extends State<MainScaffold> {
  int index = 0;
  List<UserCard> cards = const [];
  bool loadingCards = true;

  @override void initState() { super.initState(); _loadCards(); }
  Future<void> _loadCards() async {
    try { final data = await CardService.instance.fetchMyCards(); if (mounted) setState(() { cards = data; loadingCards = false; }); }
    catch (_) { if (mounted) setState(() => loadingCards = false); }
  }
  Future<void> addCard(UserCard card) async { await CardService.instance.addCard(card); await _loadCards(); }
  Future<void> deleteCard(UserCard card) async { await CardService.instance.deleteCard(card); await _loadCards(); }

  @override
  Widget build(BuildContext context) {
    final pages = <Widget>[
      HomeScreen(cards: cards),
      CampaignsScreen(cards: cards, mode: 'matched'),
      CampaignsScreen(cards: cards, mode: 'all'),
      MyCardsScreen(cards: cards, onAdd: addCard, onDelete: deleteCard, loading: loadingCards),
      const CategoriesScreen(),
    ];
    return Scaffold(
      body: IndexedStack(index: index, children: pages),
      bottomNavigationBar: AppBottomNavigation(currentIndex: index, onTap: (v) => setState(() => index = v)),
    );
  }
}
