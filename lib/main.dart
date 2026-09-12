import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'config.dart';
import 'design_system.dart';
import 'pages/login_page.dart';
import 'screens/home_screen.dart';
import 'screens/campaigns_screen.dart';
import 'screens/my_cards_screen.dart';
import 'screens/categories_screen.dart';
import 'widgets/bottom_navigation.dart';
import 'services/auth_service.dart';
import 'services/card_service.dart';
import 'services/campaign_service.dart';
import 'services/guest_session.dart';
import 'services/notification_service.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Supabase.initialize(
    url: AppConfig.supabaseUrl,
    anonKey: AppConfig.supabasePublishableKey,
  );
  await CampaignService.instance.loadUserState();
  await NotificationService.instance.initialize();
  runApp(const KartKampanyaApp());
}

class KartKampanyaApp extends StatelessWidget {
  const KartKampanyaApp({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'Kart Kampanya',
        debugShowCheckedModeBanner: false,
        theme: KKDesign.theme(),
        home: const AuthGate(),
      );
}

class AuthGate extends StatelessWidget {
  const AuthGate({super.key});

  @override
  Widget build(BuildContext context) => ValueListenableBuilder<bool>(
        valueListenable: GuestSession.active,
        builder: (_, isGuest, __) => StreamBuilder<AuthState>(
          stream: AuthService.instance.authStateChanges,
          builder: (_, __) => isGuest || Supabase.instance.client.auth.currentSession != null
              ? const MainScaffold()
              : const LoginPage(),
        ),
      );
}

class MainScaffold extends StatefulWidget {
  const MainScaffold({super.key});

  @override
  State<MainScaffold> createState() => _MainScaffoldState();
}

class _MainScaffoldState extends State<MainScaffold> {
  int index = 0;
  List<UserCard> cards = const [];
  bool loadingCards = true;

  @override
  void initState() {
    super.initState();
    _loadCards();
  }

  Future<void> _loadCards() async {
    if (GuestSession.isGuest) {
      if (mounted) setState(() => loadingCards = false);
      return;
    }
    try {
      final data = await CardService.instance.fetchMyCards();
      if (mounted) {
        setState(() {
          cards = data;
          loadingCards = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() => loadingCards = false);
    }
  }

  Future<void> addCard(UserCard card) async {
    if (GuestSession.isGuest) return;
    await CardService.instance.addCard(card);
    await _loadCards();
  }

  Future<void> deleteCard(UserCard card) async {
    if (GuestSession.isGuest) return;
    await CardService.instance.deleteCard(card);
    await _loadCards();
  }

  @override
  Widget build(BuildContext context) {
    final isGuest = GuestSession.isGuest;
    final pages = <Widget>[
      HomeScreen(cards: cards),
      CampaignsScreen(cards: cards, mode: 'matched'),
      CampaignsScreen(cards: cards, mode: 'all'),
      MyCardsScreen(
        cards: cards,
        onAdd: addCard,
        onDelete: deleteCard,
        loading: loadingCards,
        guest: isGuest,
      ),
      const CategoriesScreen(),
    ];

    return Scaffold(
      body: IndexedStack(index: index, children: pages),
      bottomNavigationBar: AppBottomNavigation(
        currentIndex: index,
        onTap: (value) => setState(() => index = value),
      ),
    );
  }
}
