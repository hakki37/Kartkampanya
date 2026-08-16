
import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'config.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Supabase.initialize(
    url: AppConfig.supabaseUrl,
    anonKey: AppConfig.supabasePublishableKey,
  );
  runApp(const KartKampanyaApp());
}

class UserCard {
  final String id, bank, card, network;
  UserCard({required this.id, required this.bank, required this.card, required this.network});
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
    home: const AuthGate(),
  );
}

class AuthGate extends StatelessWidget {
  const AuthGate({super.key});
  @override
  Widget build(BuildContext context) => StreamBuilder<AuthState>(
    stream: Supabase.instance.client.auth.onAuthStateChange,
    builder: (_, __) => Supabase.instance.client.auth.currentSession == null
        ? const LoginPage()
        : const MainShell(),
  );
}

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});
  @override State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final email = TextEditingController();
  final password = TextEditingController();
  bool register = false, busy = false;
  String? error;

  Future<void> submit() async {
    setState(() { busy = true; error = null; });
    try {
      final auth = Supabase.instance.client.auth;
      if (register) {
        await auth.signUp(
          email: email.text.trim(),
          password: password.text,
        );
      } else {
        await auth.signInWithPassword(
          email: email.text.trim(),
          password: password.text,
        );
      }
    } catch (e) {
      setState(() => error = e.toString());
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    body: Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 430),
          child: Column(children: [
            const Icon(Icons.credit_card, size: 64),
            const SizedBox(height: 12),
            Text('Kart Kampanya',
              style: Theme.of(context).textTheme.headlineMedium),
            const SizedBox(height: 24),
            TextField(
              controller: email,
              keyboardType: TextInputType.emailAddress,
              decoration: const InputDecoration(
                labelText: 'E-posta',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: password,
              obscureText: true,
              decoration: const InputDecoration(
                labelText: 'Şifre',
                border: OutlineInputBorder(),
              ),
            ),
            if (error != null) Padding(
              padding: const EdgeInsets.only(top: 12),
              child: Text(error!, style: const TextStyle(color: Colors.red)),
            ),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: FilledButton(
                onPressed: busy ? null : submit,
                child: Text(busy ? 'Bekleyin...' : (register ? 'Kayıt Ol' : 'Giriş Yap')),
              ),
            ),
            TextButton(
              onPressed: busy ? null : () => setState(() {
                register = !register;
                error = null;
              }),
              child: Text(register
                ? 'Zaten hesabım var → Giriş Yap'
                : 'Hesabım yok → Kayıt Ol'),
            ),
          ]),
        ),
      ),
    ),
  );
}

class MainShell extends StatefulWidget {
  const MainShell({super.key});
  @override State<MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<MainShell> {
  int index = 0;
  final cards = <UserCard>[];

  @override
  void initState() {
    super.initState();
    loadCards();
  }

  Future<void> loadCards() async {
    final uid = Supabase.instance.client.auth.currentUser!.id;
    final rows = await Supabase.instance.client
        .from('user_cards')
        .select()
        .eq('user_id', uid)
        .order('created_at');
    if (!mounted) return;
    setState(() {
      cards
        ..clear()
        ..addAll(List<Map<String, dynamic>>.from(rows).map((m) => UserCard(
          id: '${m['id']}',
          bank: '${m['bank_name']}',
          card: '${m['card_name']}',
          network: '${m['network']}',
        )));
    });
  }

  Future<void> addCard(UserCard card) async {
    final uid = Supabase.instance.client.auth.currentUser!.id;
    await Supabase.instance.client.from('user_cards').insert({
      'user_id': uid,
      'bank_name': card.bank,
      'card_name': card.card,
      'network': card.network,
    });
    await loadCards();
  }

  Future<void> deleteCard(UserCard card) async {
    await Supabase.instance.client
        .from('user_cards')
        .delete()
        .eq('id', card.id);
    await loadCards();
  }

  @override
  Widget build(BuildContext context) {
    final pages = <Widget>[
      const CampaignsPage(),
      MyCardsPage(cards: cards, onAdd: addCard, onDelete: deleteCard),
      const CategoriesPage(),
    ];
    return Scaffold(
      body: SafeArea(child: pages[index]),
      bottomNavigationBar: NavigationBar(
        selectedIndex: index,
        onDestinationSelected: (v) => setState(() => index = v),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home),
            label: 'Ana Sayfa',
          ),
          NavigationDestination(
            icon: Icon(Icons.credit_card_outlined),
            selectedIcon: Icon(Icons.credit_card),
            label: 'Bendeki Kartlar',
          ),
          NavigationDestination(
            icon: Icon(Icons.category_outlined),
            selectedIcon: Icon(Icons.category),
            label: 'Kategoriler',
          ),
        ],
      ),
    );
  }
}

class CampaignsPage extends StatefulWidget {
  const CampaignsPage({super.key});
  @override State<CampaignsPage> createState() => _CampaignsPageState();
}

class _CampaignsPageState extends State<CampaignsPage> {
  final search = TextEditingController();
  String category = '';
  late Future<List<Map<String, dynamic>>> future;

  final quick = const [
    ['⛽', 'Akaryakıt'],
    ['🛒', 'Market'],
    ['🍔', 'Restoran'],
    ['🛍️', 'E-ticaret'],
    ['📱', 'Elektronik'],
    ['👕', 'Giyim'],
  ];

  @override
  void initState() {
    super.initState();
    future = fetchCampaigns();
  }

  Future<List<Map<String, dynamic>>> fetchCampaigns() async {
    final rows = await Supabase.instance.client
        .from('active_campaigns')
        .select()
        .order('end_date');
    return List<Map<String, dynamic>>.from(rows);
  }

  bool matches(Map<String, dynamic> c) {
    final blob = c.values.join(' ').toLowerCase();
    final q = search.text.trim().toLowerCase();
    return (q.isEmpty || blob.contains(q)) &&
        (category.isEmpty || blob.contains(category.toLowerCase()));
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(
      title: const Text('Kart Kampanya'),
      actions: [
        IconButton(
          icon: const Icon(Icons.logout),
          onPressed: () => Supabase.instance.client.auth.signOut(),
        ),
      ],
    ),
    body: RefreshIndicator(
      onRefresh: () async => setState(() => future = fetchCampaigns()),
      child: ListView(
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
        children: [
          const Text(
            'Bugün ne almayı düşünüyorsun?',
            style: TextStyle(fontSize: 26, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          const Text('Ne alacağını yaz, uygun kampanyaları bulalım.'),
          const SizedBox(height: 16),
          TextField(
            controller: search,
            textInputAction: TextInputAction.search,
            onSubmitted: (_) => setState(() {}),
            decoration: InputDecoration(
              hintText: 'Örn. Trendyol, akaryakıt, 3000 TL...',
              prefixIcon: const Icon(Icons.search),
              suffixIcon: IconButton(
                icon: const Icon(Icons.arrow_forward),
                onPressed: () => setState(() {}),
              ),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(18),
              ),
            ),
          ),
          const SizedBox(height: 18),
          const Text('Hızlı kategoriler',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 10),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: quick.map<Widget>((x) => FilterChip(
              avatar: Text(x[0]),
              label: Text(x[1]),
              selected: category == x[1],
              onSelected: (_) => setState(() {
                category = category == x[1] ? '' : x[1];
              }),
            )).toList(),
          ),
          const SizedBox(height: 20),
          const Text('Aktif kampanyalar',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          const SizedBox(height: 10),
          FutureBuilder<List<Map<String, dynamic>>>(
            future: future,
            builder: (_, s) {
              if (s.connectionState == ConnectionState.waiting) {
                return const Padding(
                  padding: EdgeInsets.all(40),
                  child: Center(child: CircularProgressIndicator()),
                );
              }
              if (s.hasError) {
                return Padding(
                  padding: const EdgeInsets.all(12),
                  child: Text('Hata: ${s.error}'),
                );
              }
              final rows = (s.data ?? []).where(matches).toList();
              if (rows.isEmpty) {
                return const Padding(
                  padding: EdgeInsets.all(30),
                  child: Center(
                    child: Text('Uygun aktif kampanya bulunamadı.'),
                  ),
                );
              }
              return Column(
                children: rows.map<Widget>(
                  (c) => CampaignCard(campaign: c),
                ).toList(),
              );
            },
          ),
        ],
      ),
    ),
  );
}

class CampaignCard extends StatelessWidget {
  final Map<String, dynamic> campaign;
  const CampaignCard({super.key, required this.campaign});

  @override
  Widget build(BuildContext context) {
    final title = '${campaign['title'] ?? 'Kampanya'}';
    final merchant = '${campaign['merchant'] ?? ''}';
    final reward = campaign['reward_amount'];
    final end = '${campaign['end_date'] ?? '-'}';
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: ListTile(
        leading: const Icon(Icons.local_offer),
        title: Text(title),
        subtitle: Text(
          '${merchant.isEmpty ? '' : '$merchant\n'}'
          '${reward == null ? '' : 'Avantaj: $reward\n'}'
          'Son gün: $end',
        ),
        isThreeLine: true,
      ),
    );
  }
}

class MyCardsPage extends StatefulWidget {
  final List<UserCard> cards;
  final Future<void> Function(UserCard) onAdd;
  final Future<void> Function(UserCard) onDelete;
  const MyCardsPage({
    super.key,
    required this.cards,
    required this.onAdd,
    required this.onDelete,
  });
  @override State<MyCardsPage> createState() => _MyCardsPageState();
}

class _MyCardsPageState extends State<MyCardsPage> {
  final banks = const [
    'Akbank','Garanti BBVA','Yapı Kredi','İş Bankası','Ziraat Bankası',
    'Halkbank','QNB','DenizBank','TEB','VakıfBank'
  ];
  final cardMap = const {
    'Akbank': ['Axess'],
    'Garanti BBVA': ['Bonus'],
    'Yapı Kredi': ['World'],
    'İş Bankası': ['Maximum'],
    'Ziraat Bankası': ['Bankkart'],
    'Halkbank': ['Paraf'],
    'QNB': ['CardFinans'],
    'DenizBank': ['Bonus'],
    'TEB': ['Bonus'],
    'VakıfBank': ['World'],
  };
  final networks = const ['Visa', 'Mastercard', 'Troy'];

  Future<void> addCard() async {
    String bank = banks.first;
    String card = cardMap[bank]!.first;
    String network = networks.first;

    final ok = await showDialog<bool>(
      context: context,
      builder: (_) => StatefulBuilder(
        builder: (ctx, setDialog) => AlertDialog(
          title: const Text('Kart Ekle'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              DropdownButtonFormField<String>(
                value: bank,
                decoration: const InputDecoration(labelText: 'Banka'),
                items: banks.map((b) =>
                  DropdownMenuItem(value: b, child: Text(b))).toList(),
                onChanged: (v) {
                  if (v != null) {
                    setDialog(() {
                      bank = v;
                      card = cardMap[bank]!.first;
                    });
                  }
                },
              ),
              DropdownButtonFormField<String>(
                value: card,
                decoration: const InputDecoration(labelText: 'Kart'),
                items: (cardMap[bank] ?? []).map((c) =>
                  DropdownMenuItem(value: c, child: Text(c))).toList(),
                onChanged: (v) {
                  if (v != null) setDialog(() => card = v);
                },
              ),
              DropdownButtonFormField<String>(
                value: network,
                decoration: const InputDecoration(labelText: 'Kart ağı'),
                items: networks.map((n) =>
                  DropdownMenuItem(value: n, child: Text(n))).toList(),
                onChanged: (v) {
                  if (v != null) setDialog(() => network = v);
                },
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx, false),
              child: const Text('İptal'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(ctx, true),
              child: const Text('Ekle'),
            ),
          ],
        ),
      ),
    );

    if (ok == true) {
      try {
        await widget.onAdd(UserCard(
          id: '',
          bank: bank,
          card: card,
          network: network,
        ));
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Kart eklenemedi: $e')),
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Bendeki Kartlar')),
    floatingActionButton: FloatingActionButton.extended(
      onPressed: addCard,
      icon: const Icon(Icons.add),
      label: const Text('Kart Ekle'),
    ),
    body: widget.cards.isEmpty
      ? const Center(
          child: Text(
            'Henüz kart eklemedin.\n+ Kart Ekle ile başlayabilirsin.',
            textAlign: TextAlign.center,
          ),
        )
      : ListView(
          padding: const EdgeInsets.all(16),
          children: widget.cards.map<Widget>((c) => Card(
            child: ListTile(
              leading: const Icon(Icons.credit_card),
              title: Text('${c.bank} • ${c.card}'),
              subtitle: Text('Kart ağı: ${c.network}'),
              trailing: IconButton(
                icon: const Icon(Icons.delete_outline),
                onPressed: () async {
                  await widget.onDelete(c);
                  if (mounted) setState(() {});
                },
              ),
            ),
          )).toList(),
        ),
  );
}

class CategoriesPage extends StatelessWidget {
  const CategoriesPage({super.key});
  @override
  Widget build(BuildContext context) => ListView(
    padding: const EdgeInsets.all(18),
    children: const [
      Text('Kategoriler',
        style: TextStyle(fontSize: 30, fontWeight: FontWeight.bold)),
      SizedBox(height: 16),
      ListTile(leading: Text('⛽', style: TextStyle(fontSize: 24)), title: Text('Akaryakıt')),
      ListTile(leading: Text('🛒', style: TextStyle(fontSize: 24)), title: Text('Market')),
      ListTile(leading: Text('🍔', style: TextStyle(fontSize: 24)), title: Text('Restoran')),
      ListTile(leading: Text('🛍️', style: TextStyle(fontSize: 24)), title: Text('E-ticaret')),
      ListTile(leading: Text('📱', style: TextStyle(fontSize: 24)), title: Text('Elektronik')),
      ListTile(leading: Text('👕', style: TextStyle(fontSize: 24)), title: Text('Giyim')),
      ListTile(leading: Text('✈️', style: TextStyle(fontSize: 24)), title: Text('Seyahat')),
      ListTile(leading: Text('🎬', style: TextStyle(fontSize: 24)), title: Text('Eğlence')),
      ListTile(leading: Text('🏠', style: TextStyle(fontSize: 24)), title: Text('Ev & Yaşam')),
      ListTile(leading: Text('💊', style: TextStyle(fontSize: 24)), title: Text('Sağlık')),
    ],
  );
}
