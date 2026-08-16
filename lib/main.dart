import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'config.dart';

String decodeHtmlEntities(String input) {
  return input.replaceAllMapped(
    RegExp(r'&#x([0-9a-fA-F]+);|&#([0-9]+);|&amp;|&quot;|&apos;|&lt;|&gt;|&nbsp;'),
    (m) {
      final hex = m.group(1);
      final dec = m.group(2);
      if (hex != null) {
        return String.fromCharCode(int.parse(hex, radix: 16));
      }
      if (dec != null) {
        return String.fromCharCode(int.parse(dec));
      }

      switch (m.group(0)) {
        case '&amp;':
          return '&';
        case '&quot;':
          return '"';
        case '&apos;':
          return "'";
        case '&lt;':
          return '<';
        case '&gt;':
          return '>';
        case '&nbsp;':
          return ' ';
        default:
          return m.group(0)!;
      }
    },
  );

}

String bankLogoText(String bank) {
  final b = bank.trim();
  if (b.isEmpty) return 'KB';
  final parts = b.split(RegExp(r'\s+')).where((x) => x.isNotEmpty).toList();
  if (parts.length >= 2) {
    return '${parts[0][0]}${parts[1][0]}'.toUpperCase();
  }
  return b.substring(0, b.length >= 2 ? 2 : 1).toUpperCase();
}

Color bankColor(String bank) {
  final b = bank.toLowerCase();
  if (b.contains('akbank')) return const Color(0xFFE31E24);
  if (b.contains('yapı') || b.contains('yapi')) return const Color(0xFF7A1FA2);
  if (b.contains('iş') || b.contains('is bank')) return const Color(0xFF00AEEF);
  if (b.contains('garanti')) return const Color(0xFF00A651);
  if (b.contains('ziraat')) return const Color(0xFFE30613);
  if (b.contains('qnb')) return const Color(0xFF5B2C83);
  if (b.contains('halk')) return const Color(0xFF005B9A);
  if (b.contains('vakıf') || b.contains('vakif')) return const Color(0xFF0066A1);
  if (b.contains('deniz')) return const Color(0xFF0077B8);
  return const Color(0xFF5B5FEF);
}

String campaignKey(Map<String, dynamic> c) {
  final raw = '${c['id'] ?? c['url'] ?? c['detail_url'] ?? c['merchant'] ?? ''}|${c['bank_name'] ?? ''}|${c['card_name'] ?? ''}';
  return raw.trim().toLowerCase();
}

int? extractUsageTarget(Map<String, dynamic> c) {
  final raw = decodeHtmlEntities(
    '${c['terms'] ?? c['description'] ?? c['conditions'] ?? ''}',
  ).replaceAll('\n', ' ');
  if (raw.isEmpty) return null;
  final patterns = [
    RegExp(r'(\d+)\s*(?:kez|defa|adet)\b', caseSensitive: false),
    RegExp(r'(\d+)\s*(?:alışveriş|islem|işlem|harcama)\b', caseSensitive: false),
    RegExp(r'(\d+)\s*ayrı', caseSensitive: false),
  ];
  for (final p in patterns) {
    final m = p.firstMatch(raw);
    final n = int.tryParse(m?.group(1) ?? '');
    if (n != null && n > 1 && n <= 50) return n;
  }
  return null;
}

int? daysUntil(String raw) {
  if (raw.trim().isEmpty) return null;
  final d = DateTime.tryParse(raw.trim());
  if (d == null) return null;
  final today = DateTime.now();
  final a = DateTime(today.year, today.month, today.day);
  final b = DateTime(d.year, d.month, d.day);
  return b.difference(a).inDays;
}

Future<int> loadCampaignUsage(String key) async {
  final user = Supabase.instance.client.auth.currentUser;
  if (user == null) return 0;
  try {
    final row = await Supabase.instance.client
        .from('campaign_usage')
        .select('used_count')
        .eq('user_id', user.id)
        .eq('campaign_key', key)
        .maybeSingle();
    return int.tryParse('${row?['used_count'] ?? 0}') ?? 0;
  } catch (_) {
    return 0;
  }
}

Future<void> saveCampaignUsage(String key, int count) async {
  final user = Supabase.instance.client.auth.currentUser;
  if (user == null) return;
  await Supabase.instance.client.from('campaign_usage').upsert({
    'user_id': user.id,
    'campaign_key': key,
    'used_count': count < 0 ? 0 : count,
    'updated_at': DateTime.now().toIso8601String(),
  });
}

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await Supabase.initialize(
    url: AppConfig.supabaseUrl,
    anonKey: AppConfig.supabasePublishableKey,
  );

  runApp(const KartKampanyaApp());
}

class UserCard {
  final String id;
  final String bank;
  final String card;
  final String network;

  UserCard({
    required this.id,
    required this.bank,
    required this.card,
    required this.network,
  });
}

class KartKampanyaApp extends StatelessWidget {
  const KartKampanyaApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Kart Kampanya',
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF5B5FEF),
          brightness: Brightness.light,
        ),
        scaffoldBackgroundColor: const Color(0xFFF7F7FB),
        cardTheme: CardTheme(
          elevation: 0,
          margin: EdgeInsets.zero,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
            side: BorderSide(color: Colors.black.withOpacity(.05)),
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: Colors.white,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(18),
            borderSide: BorderSide.none,
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(18),
            borderSide: BorderSide(color: Colors.black.withOpacity(.06)),
          ),
        ),
        chipTheme: ChipThemeData(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(14),
          ),
        ),
      ),
      home: const AuthGate(),
    );
  }
}

class AuthGate extends StatelessWidget {
  const AuthGate({super.key});

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<AuthState>(
      stream: Supabase.instance.client.auth.onAuthStateChange,
      builder: (_, __) {
        return Supabase.instance.client.auth.currentSession == null
            ? const LoginPage()
            : const MainShell();
      },
    );
  }
}

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final email = TextEditingController();
  final password = TextEditingController();

  bool register = false;
  bool busy = false;
  String? error;

  Future<void> submit() async {
    setState(() {
      busy = true;
      error = null;
    });

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
      if (mounted) {
        setState(() => busy = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 430),
            child: Column(
              children: [
                const Icon(Icons.credit_card, size: 64),
                const SizedBox(height: 12),
                Text(
                  'Kart Kampanya',
                  style: Theme.of(context).textTheme.headlineMedium,
                ),
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

                if (error != null)
                  Padding(
                    padding: const EdgeInsets.only(top: 12),
                    child: Text(
                      error!,
                      style: const TextStyle(color: Colors.red),
                    ),
                  ),

                const SizedBox(height: 16),

                SizedBox(
                  width: double.infinity,
                  child: FilledButton(
                    onPressed: busy ? null : submit,
                    child: Text(
                      busy
                          ? 'Bekleyin...'
                          : (register ? 'Kayıt Ol' : 'Giriş Yap'),
                    ),
                  ),
                ),

                TextButton(
                  onPressed: busy
                      ? null
                      : () {
                          setState(() {
                            register = !register;
                            error = null;
                          });
                        },
                  child: Text(
                    register
                        ? 'Zaten hesabım var → Giriş Yap'
                        : 'Hesabım yok → Kayıt Ol',
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class MainShell extends StatefulWidget {
  const MainShell({super.key});

  @override
  State<MainShell> createState() => _MainShellState();
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
        ..addAll(
          List<Map<String, dynamic>>.from(rows).map(
            (m) => UserCard(
              id: '${m['id']}',
              bank: '${m['bank_name']}',
              card: '${m['card_name']}',
              network: '${m['network']}',
            ),
          ),
        );
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
      CampaignsPage(cards: cards),
      MyCardsPage(
        cards: cards,
        onAdd: addCard,
        onDelete: deleteCard,
      ),
      const CategoriesPage(),
    ];

    return Scaffold(
      body: SafeArea(child: pages[index]),
      bottomNavigationBar: NavigationBar(
        selectedIndex: index,
        onDestinationSelected: (v) {
          setState(() => index = v);
        },
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
  final List<UserCard> cards;

  const CampaignsPage({
    super.key,
    required this.cards,
  });

  @override
  State<CampaignsPage> createState() => _CampaignsPageState();
}

class _CampaignsPageState extends State<CampaignsPage> {
  final search = TextEditingController();
  String category = '';
  double? spend;
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

  @override
  void dispose() {
    search.dispose();
    super.dispose();
  }

  Future<List<Map<String, dynamic>>> fetchCampaigns() async {
    final rows = await Supabase.instance.client
        .from('campaign_rules')
        .select()
        .order('created_at', ascending: false);
    return List<Map<String, dynamic>>.from(rows);
  }

  double? parseAmount(String text) {
    final matches = RegExp(
      r'(\d[\d\.\s]*)(?:\s*)(?:TL|₺)',
      caseSensitive: false,
    ).allMatches(text);
    if (matches.isEmpty) return null;
    final raw = matches.last.group(1)!.replaceAll('.', '').replaceAll(' ', '');
    return double.tryParse(raw);
  }

  String detectCategory(String text) {
    final q = text.toLowerCase();
    const map = {
      'E-ticaret': ['trendyol', 'hepsiburada', 'amazon', 'n11', 'online', 'e-ticaret', 'eticaret'],
      'Akaryakıt': ['benzin', 'motorin', 'mazot', 'akaryakıt', 'petrol', 'opet', 'shell', 'bp', 'total'],
      'Market': ['market', 'migros', 'carrefour', 'a101', 'bim', 'şok'],
      'Restoran': ['restoran', 'yemek', 'burger', 'pizza', 'kahve', 'yemeksepeti', 'getir yemek'],
      'Elektronik': ['telefon', 'laptop', 'bilgisayar', 'elektronik', 'teknoloji'],
      'Giyim': ['giyim', 'kıyafet', 'ayakkabı', 'zara', 'defacto'],
    };
    for (final entry in map.entries) {
      if (entry.value.any(q.contains)) return entry.key;
    }
    return category;
  }

  bool cardMatches(Map<String, dynamic> campaign, UserCard userCard) {
    final bankRule = '${campaign['bank_name'] ?? ''}'.trim().toLowerCase();
    final cardRule = '${campaign['card_name'] ?? ''}'.trim().toLowerCase();
    final networkRule = '${campaign['network'] ?? ''}'.trim().toLowerCase();

    bool ok(String rule, String value) {
      if (rule.isEmpty || rule == '*') return true;
      final v = value.toLowerCase().trim();
      return rule == v || rule.contains(v) || v.contains(rule);
    }

    return ok(bankRule, userCard.bank) &&
        ok(cardRule, userCard.card) &&
        ok(networkRule, userCard.network);
  }

  double rewardFor(Map<String, dynamic> campaign) {
    final reward = double.tryParse('${campaign['reward_amount'] ?? 0}') ?? 0;
    final max = double.tryParse('${campaign['max_reward'] ?? 0}') ?? 0;
    if (max > 0 && reward > max) return max;
    return reward;
  }

  List<Map<String, dynamic>> rankCampaigns(List<Map<String, dynamic>> rows) {
    final q = search.text.trim().toLowerCase();
    final detectedCategory = category.isEmpty ? detectCategory(search.text) : category;
    final result = <Map<String, dynamic>>[];

    for (final campaign in rows) {
      final blob = decodeHtmlEntities(campaign.values.join(' ')).toLowerCase();
      final words = q.split(RegExp(r'\s+')).where((x) => x.isNotEmpty && !RegExp(r'^\d').hasMatch(x));
      final textOk = q.isEmpty || words.isEmpty || words.any(blob.contains);
      final categoryOk = detectedCategory.isEmpty || blob.contains(detectedCategory.toLowerCase());
      if (!textOk || !categoryOk) continue;

      final minSpend = double.tryParse('${campaign['min_spend'] ?? 0}') ?? 0;
      if (spend != null && minSpend > 0 && spend! < minSpend) continue;

      final matchingCards = widget.cards.where((card) => cardMatches(campaign, card)).toList();
      final copy = Map<String, dynamic>.from(campaign);
      copy['_cards'] = matchingCards;
      copy['_reward'] = rewardFor(campaign);
      copy['_score'] = (matchingCards.isEmpty ? 0 : 100000000) +
          rewardFor(campaign) * 1000 +
          matchingCards.length;
      result.add(copy);
    }

    result.sort((a, b) => (b['_score'] as num).compareTo(a['_score'] as num));
    return result;
  }

  void searchNow() {
    setState(() {
      category = detectCategory(search.text);
      spend = parseAmount(search.text);
    });
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Scaffold(
      appBar: AppBar(
        title: const Text('Kart Kampanya', style: TextStyle(fontWeight: FontWeight.w800)),
        actions: [
          IconButton(
            tooltip: 'Yenile',
            icon: const Icon(Icons.refresh_rounded),
            onPressed: () => setState(() => future = fetchCampaigns()),
          ),
          IconButton(
            tooltip: 'Çıkış',
            icon: const Icon(Icons.logout_rounded),
            onPressed: () => Supabase.instance.client.auth.signOut(),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async => setState(() => future = fetchCampaigns()),
        child: ListView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.fromLTRB(16, 8, 16, 28),
          children: [
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [cs.primary, cs.primaryContainer],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(26),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('AKILLI KAMPANYA', style: TextStyle(
                    color: Colors.white70, fontSize: 12, fontWeight: FontWeight.w800, letterSpacing: 1.2,
                  )),
                  const SizedBox(height: 6),
                  const Text('Bugün ne almayı düşünüyorsun?', style: TextStyle(
                    color: Colors.white, fontSize: 25, fontWeight: FontWeight.w900,
                  )),
                  const SizedBox(height: 6),
                  Text(
                    widget.cards.isEmpty
                        ? 'Alışverişini yaz, kampanyaları karşılaştıralım.'
                        : '${widget.cards.length} kartınla en avantajlı seçeneği bulalım.',
                    style: const TextStyle(color: Colors.white70),
                  ),
                  const SizedBox(height: 16),
                  TextField(
                    controller: search,
                    textInputAction: TextInputAction.search,
                    onSubmitted: (_) => searchNow(),
                    decoration: InputDecoration(
                      hintText: 'Trendyol 3000 TL, benzin 2000 TL...',
                      prefixIcon: const Icon(Icons.search),
                      suffixIcon: IconButton(
                        icon: const Icon(Icons.arrow_forward_rounded),
                        onPressed: searchNow,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            if (category.isNotEmpty || spend != null)
              Padding(
                padding: const EdgeInsets.only(top: 12),
                child: Wrap(
                  spacing: 8,
                  children: [
                    if (category.isNotEmpty) Chip(avatar: const Icon(Icons.auto_awesome, size: 16), label: Text(category)),
                    if (spend != null) Chip(label: Text('${spend!.toStringAsFixed(0)} TL')),
                    ActionChip(
                      label: const Text('Temizle'),
                      onPressed: () => setState(() {
                        category = '';
                        spend = null;
                        search.clear();
                      }),
                    ),
                  ],
                ),
              ),
            const SizedBox(height: 18),
            Row(
              children: [
                const Expanded(child: Text('Hızlı kategoriler', style: TextStyle(fontSize: 19, fontWeight: FontWeight.w800))),
                if (widget.cards.isNotEmpty)
                  Text('${widget.cards.length} kart', style: TextStyle(color: cs.primary, fontWeight: FontWeight.w700)),
              ],
            ),
            const SizedBox(height: 10),
            SizedBox(
              height: 92,
              child: ListView.separated(
                scrollDirection: Axis.horizontal,
                itemCount: quick.length,
                separatorBuilder: (_, __) => const SizedBox(width: 10),
                itemBuilder: (_, i) {
                  final x = quick[i];
                  final selected = category == x[1];
                  return InkWell(
                    borderRadius: BorderRadius.circular(18),
                    onTap: () => setState(() => category = selected ? '' : x[1]),
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 180),
                      width: 105,
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: selected ? cs.primaryContainer : Colors.white,
                        borderRadius: BorderRadius.circular(18),
                        border: Border.all(color: selected ? cs.primary : Colors.black.withOpacity(.06)),
                      ),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(x[0], style: const TextStyle(fontSize: 25)),
                          const SizedBox(height: 5),
                          Text(x[1], textAlign: TextAlign.center, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700)),
                        ],
                      ),
                    ),
                  );
                },
              ),
            ),
            const SizedBox(height: 20),
            FutureBuilder<List<Map<String, dynamic>>>(
              future: future,
              builder: (_, snapshot) {
                if (snapshot.connectionState == ConnectionState.waiting) {
                  return const Padding(
                    padding: EdgeInsets.all(50),
                    child: Center(child: CircularProgressIndicator()),
                  );
                }
                if (snapshot.hasError) {
                  return Card(
                    child: Padding(
                      padding: const EdgeInsets.all(18),
                      child: Row(children: [
                        const Icon(Icons.error_outline, color: Colors.red),
                        const SizedBox(width: 10),
                        Expanded(child: Text('Kampanyalar yüklenemedi: ${snapshot.error}')),
                      ]),
                    ),
                  );
                }
                final rows = rankCampaigns(snapshot.data ?? []);
                if (rows.isEmpty) {
                  return const Card(
                    child: Padding(
                      padding: EdgeInsets.all(28),
                      child: Center(child: Text('Bu aramaya uygun kampanya bulunamadı.')),
                    ),
                  );
                }
                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Expanded(child: Text('Kampanyalar', style: TextStyle(fontSize: 21, fontWeight: FontWeight.w900))),
                        Text('${rows.length} sonuç', style: TextStyle(color: cs.primary, fontWeight: FontWeight.w700)),
                      ],
                    ),
                    const SizedBox(height: 10),
                    ...rows.map((campaign) => SmartCampaignCard(campaign: campaign)),
                  ],
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}

class SmartCampaignCard extends StatefulWidget {
  final Map<String, dynamic> campaign;
  const SmartCampaignCard({super.key, required this.campaign});

  @override
  State<SmartCampaignCard> createState() => _SmartCampaignCardState();
}

class _SmartCampaignCardState extends State<SmartCampaignCard> {
  int used = 0;
  bool loadingUsage = true;
  bool saving = false;

  Map<String, dynamic> get c => widget.campaign;

  String get merchant => decodeHtmlEntities('${c['merchant'] ?? ''}').trim().isEmpty
      ? 'Kampanya'
      : decodeHtmlEntities('${c['merchant'] ?? ''}').trim();

  String get category => decodeHtmlEntities('${c['category'] ?? ''}').trim();
  String get bank => decodeHtmlEntities('${c['bank_name'] ?? ''}').trim();
  String get card => decodeHtmlEntities('${c['card_name'] ?? ''}').trim();
  String get network => decodeHtmlEntities('${c['network'] ?? ''}').trim();
  String get terms => decodeHtmlEntities('${c['terms'] ?? c['description'] ?? c['conditions'] ?? ''}').trim();
  String get detailUrl => '${c['detail_url'] ?? c['url'] ?? ''}'.trim();
  String get endDate => '${c['end_date'] ?? ''}'.trim();
  int? get target => extractUsageTarget(c);
  int? get daysLeft => daysUntil(endDate);
  int get remaining => target == null ? 0 : (target! - used).clamp(0, target!).toInt();

  List<UserCard> get cards => List<UserCard>.from(c['_cards'] ?? const <UserCard>[]);

  @override
  void initState() {
    super.initState();
    _loadUsage();
  }

  Future<void> _loadUsage() async {
    final value = await loadCampaignUsage(campaignKey(c));
    if (!mounted) return;
    setState(() {
      used = value;
      loadingUsage = false;
    });
  }

  Future<void> _changeUsage(int delta) async {
    if (saving) return;
    final next = (used + delta).clamp(0, target ?? 999).toInt();
    if (next == used) return;
    setState(() {
      used = next;
      saving = true;
    });
    try {
      await saveCampaignUsage(campaignKey(c), next);
    } catch (e) {
      if (mounted) setState(() => used -= delta);
    } finally {
      if (mounted) setState(() => saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final reward = double.tryParse('${c['_reward'] ?? 0}') ?? 0;
    final min = double.tryParse('${c['min_spend'] ?? 0}') ?? 0;
    final bankName = bank.isEmpty ? (cards.isNotEmpty ? cards.first.bank : '') : bank;
    final urgent = daysLeft != null && daysLeft! <= 3 && daysLeft! >= 0;
    final expired = daysLeft != null && daysLeft! < 0;
    final progress = target == null || target == 0 ? null : (used / target!).clamp(0.0, 1.0).toDouble();

    return Card(
      clipBehavior: Clip.antiAlias,
      margin: const EdgeInsets.only(bottom: 14),
      child: InkWell(
        onTap: () => _showDetails(context),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  CircleAvatar(
                    radius: 23,
                    backgroundColor: bankColor(bankName).withOpacity(.12),
                    child: Text(bankLogoText(bankName), style: TextStyle(
                      color: bankColor(bankName), fontWeight: FontWeight.w900, fontSize: 13,
                    )),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(merchant, style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w900)),
                        if (bankName.isNotEmpty) Text(bankName, style: TextStyle(color: Colors.grey.shade700, fontWeight: FontWeight.w600)),
                      ],
                    ),
                  ),
                  if (urgent)
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 6),
                      decoration: BoxDecoration(color: Colors.red.withOpacity(.10), borderRadius: BorderRadius.circular(12)),
                      child: Text(
                        daysLeft == 0 ? 'SON GÜN' : '$daysLeft gün',
                        style: const TextStyle(color: Colors.red, fontSize: 11, fontWeight: FontWeight.w900),
                      ),
                    ),
                ],
              ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 7,
                runSpacing: 7,
                children: [
                  if (category.isNotEmpty) _pill(Icons.category_outlined, category, cs.primaryContainer, cs.primary),
                  if (network.isNotEmpty) _pill(Icons.credit_card, network, Colors.grey.shade100, Colors.black87),
                  if (cards.isNotEmpty) _pill(Icons.check_circle_outline, '${cards.length} uygun kart', Colors.green.withOpacity(.10), Colors.green.shade800),
                  if (reward > 0) _pill(Icons.savings_outlined, '+${reward.toStringAsFixed(0)} TL', Colors.amber.withOpacity(.16), Colors.orange.shade900),
                ],
              ),
              if (target != null) ...[
                const SizedBox(height: 14),
                Row(
                  children: [
                    const Icon(Icons.track_changes_rounded, size: 19),
                    const SizedBox(width: 7),
                    Expanded(child: Text('$used / $target kullanım', style: const TextStyle(fontWeight: FontWeight.w800))),
                    Text('$remaining kaldı', style: TextStyle(color: cs.primary, fontWeight: FontWeight.w800)),
                  ],
                ),
                const SizedBox(height: 7),
                ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: LinearProgressIndicator(value: progress, minHeight: 8),
                ),
              ],
              const SizedBox(height: 12),
              Row(
                children: [
                  if (min > 0)
                    Text('Min. ${min.toStringAsFixed(0)} TL', style: const TextStyle(fontWeight: FontWeight.w700)),
                  const Spacer(),
                  Text('Detaylar ›', style: TextStyle(color: cs.primary, fontWeight: FontWeight.w800)),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _pill(IconData icon, String label, Color bg, Color fg) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
      decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(12)),
      child: Row(mainAxisSize: MainAxisSize.min, children: [
        Icon(icon, size: 15, color: fg),
        const SizedBox(width: 5),
        Text(label, style: TextStyle(color: fg, fontSize: 12, fontWeight: FontWeight.w800)),
      ]),
    );
  }

  Future<void> _showDetails(BuildContext context) async {
    final cs = Theme.of(context).colorScheme;
    await showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      builder: (sheetContext) {
        return StatefulBuilder(
          builder: (context, setSheetState) {
            final urgent = daysLeft != null && daysLeft! <= 3 && daysLeft! >= 0;
            return SafeArea(
              child: FractionallySizedBox(
                heightFactor: .90,
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(20, 8, 20, 20),
                  child: SingleChildScrollView(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(children: [
                          CircleAvatar(
                            radius: 25,
                            backgroundColor: bankColor(bank).withOpacity(.12),
                            child: Text(bankLogoText(bank), style: TextStyle(color: bankColor(bank), fontWeight: FontWeight.w900)),
                          ),
                          const SizedBox(width: 12),
                          Expanded(child: Text(merchant, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w900))),
                        ]),
                        const SizedBox(height: 16),
                        if (urgent)
                          Container(
                            width: double.infinity,
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: Colors.red.withOpacity(.08),
                              borderRadius: BorderRadius.circular(14),
                            ),
                            child: Text(
                              daysLeft == 0 ? '⚠️ Bu kampanyanın son günü!' : '⚠️ Kampanyanın bitmesine $daysLeft gün kaldı.',
                              style: const TextStyle(color: Colors.red, fontWeight: FontWeight.w800),
                            ),
                          ),
                        if (target != null) ...[
                          const SizedBox(height: 14),
                          Card(
                            color: cs.primaryContainer.withOpacity(.55),
                            child: Padding(
                              padding: const EdgeInsets.all(14),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(children: [
                                    const Icon(Icons.track_changes_rounded),
                                    const SizedBox(width: 8),
                                    Expanded(child: Text('$used / $target kullanım tamamlandı', style: const TextStyle(fontWeight: FontWeight.w900))),
                                    Text('$remaining kaldı', style: TextStyle(color: cs.primary, fontWeight: FontWeight.w900)),
                                  ]),
                                  const SizedBox(height: 9),
                                  LinearProgressIndicator(value: (used / target!).clamp(0.0, 1.0).toDouble(), minHeight: 9),
                                  const SizedBox(height: 12),
                                  Row(children: [
                                    Expanded(
                                      child: OutlinedButton.icon(
                                        onPressed: used > 0 ? () async {
                                          await _changeUsage(-1);
                                          setSheetState(() {});
                                        } : null,
                                        icon: const Icon(Icons.undo),
                                        label: const Text('Geri al'),
                                      ),
                                    ),
                                    const SizedBox(width: 10),
                                    Expanded(
                                      child: FilledButton.icon(
                                        onPressed: used < target! ? () async {
                                          await _changeUsage(1);
                                          setSheetState(() {});
                                        } : null,
                                        icon: const Icon(Icons.check),
                                        label: const Text('1 kez yaptım'),
                                      ),
                                    ),
                                  ]),
                                ],
                              ),
                            ),
                          ),
                        ],
                        const SizedBox(height: 8),
                        _detailRow(Icons.account_balance, 'Banka', bank),
                        _detailRow(Icons.credit_card, 'Kart', card),
                        _detailRow(Icons.payment, 'Kart ağı', network),
                        _detailRow(Icons.category_outlined, 'Kategori', category),
                        if (min > 0) _detailRow(Icons.shopping_cart_outlined, 'Minimum harcama', '${min.toStringAsFixed(0)} TL'),
                        if (reward > 0) _detailRow(Icons.savings_outlined, 'Tahmini avantaj', '${reward.toStringAsFixed(0)} TL'),
                        if (endDate.isNotEmpty) _detailRow(Icons.event_available_outlined, 'Son gün', endDate),
                        const SizedBox(height: 12),
                        const Text('Kampanya şartları', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900)),
                        const SizedBox(height: 8),
                        SelectableText(
                          terms.isEmpty ? 'Kampanya şartları bulunamadı.' : terms,
                          style: const TextStyle(height: 1.5),
                        ),
                        if (detailUrl.isNotEmpty) ...[
                          const SizedBox(height: 16),
                          SelectableText('Kaynak: $detailUrl', style: TextStyle(fontSize: 12, color: cs.primary)),
                        ],
                      ],
                    ),
                  ),
                ),
              ),
            );
          },
        );
      },
    );
  }

  Widget _detailRow(IconData icon, String title, String value) {
    if (value.trim().isEmpty) return const SizedBox.shrink();
    return ListTile(
      contentPadding: EdgeInsets.zero,
      leading: Icon(icon),
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.w700)),
      subtitle: Text(value),
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

  @override
  State<MyCardsPage> createState() =>
      _MyCardsPageState();
}

class _MyCardsPageState extends State<MyCardsPage> {
  final banks = const [
    'Akbank',
    'Garanti BBVA',
    'Yapı Kredi',
    'İş Bankası',
    'Ziraat Bankası',
    'Halkbank',
    'QNB',
    'DenizBank',
    'TEB',
    'VakıfBank',
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

  final networks = const [
    'Visa',
    'Mastercard',
    'Troy',
  ];

  Future<void> addCard() async {
    String bank = banks.first;
    String card = cardMap[bank]!.first;
    String network = networks.first;

    final ok = await showDialog<bool>(
      context: context,
      builder: (_) => StatefulBuilder(
        builder: (ctx, setDialog) {
          return AlertDialog(
            title: const Text('Kart Ekle'),

            content: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                DropdownButtonFormField<String>(
                  value: bank,
                  decoration:
                      const InputDecoration(
                    labelText: 'Banka',
                  ),
                  items: banks.map((b) {
                    return DropdownMenuItem(
                      value: b,
                      child: Text(b),
                    );
                  }).toList(),
                  onChanged: (v) {
                    if (v != null) {
                      setDialog(() {
                        bank = v;
                        card =
                            cardMap[bank]!.first;
                      });
                    }
                  },
                ),

                DropdownButtonFormField<String>(
                  value: card,
                  decoration:
                      const InputDecoration(
                    labelText: 'Kart',
                  ),
                  items:
                      (cardMap[bank] ?? [])
                          .map((c) {
                    return DropdownMenuItem(
                      value: c,
                      child: Text(c),
                    );
                  }).toList(),
                  onChanged: (v) {
                    if (v != null) {
                      setDialog(() => card = v);
                    }
                  },
                ),

                DropdownButtonFormField<String>(
                  value: network,
                  decoration:
                      const InputDecoration(
                    labelText: 'Kart ağı',
                  ),
                  items: networks.map((n) {
                    return DropdownMenuItem(
                      value: n,
                      child: Text(n),
                    );
                  }).toList(),
                  onChanged: (v) {
                    if (v != null) {
                      setDialog(() => network = v);
                    }
                  },
                ),
              ],
            ),

            actions: [
              TextButton(
                onPressed: () =>
                    Navigator.pop(ctx, false),
                child: const Text('İptal'),
              ),

              FilledButton(
                onPressed: () =>
                    Navigator.pop(ctx, true),
                child: const Text('Ekle'),
              ),
            ],
          );
        },
      ),
    );

    if (ok == true) {
      try {
        await widget.onAdd(
          UserCard(
            id: '',
            bank: bank,
            card: card,
            network: network,
          ),
        );
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context)
              .showSnackBar(
            SnackBar(
              content:
                  Text('Kart eklenemedi: $e'),
            ),
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Bendeki Kartlar'),
      ),

      floatingActionButton:
          FloatingActionButton.extended(
        onPressed: addCard,
        icon: const Icon(Icons.add),
        label: const Text('Kart Ekle'),
      ),

      body: widget.cards.isEmpty
          ? const Center(
              child: Text(
                'Henüz kart eklemedin.\n'
                '+ Kart Ekle ile başlayabilirsin.',
                textAlign: TextAlign.center,
              ),
            )
          : ListView(
              padding:
                  const EdgeInsets.all(16),
              children:
                  widget.cards.map<Widget>((c) {
                return Card(
                  child: ListTile(
                    leading:
                        const Icon(Icons.credit_card),
                    title: Text(
                      '${c.bank} • ${c.card}',
                    ),
                    subtitle:
                        Text('Kart ağı: ${c.network}'),
                    trailing: IconButton(
                      icon: const Icon(
                        Icons.delete_outline,
                      ),
                      onPressed: () async {
                        await widget.onDelete(c);
                      },
                    ),
                  ),
                );
              }).toList(),
            ),
    );
  }
}

class CategoriesPage extends StatelessWidget {
  const CategoriesPage({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(18),
      children: const [
        Text(
          'Kategoriler',
          style: TextStyle(
            fontSize: 30,
            fontWeight: FontWeight.bold,
          ),
        ),

        SizedBox(height: 16),

        ListTile(
          leading: Text('⛽',
              style: TextStyle(fontSize: 24)),
          title: Text('Akaryakıt'),
        ),

        ListTile(
          leading: Text('🛒',
              style: TextStyle(fontSize: 24)),
          title: Text('Market'),
        ),

        ListTile(
          leading: Text('🍔',
              style: TextStyle(fontSize: 24)),
          title: Text('Restoran'),
        ),

        ListTile(
          leading: Text('🛍️',
              style: TextStyle(fontSize: 24)),
          title: Text('E-ticaret'),
        ),

        ListTile(
          leading: Text('📱',
              style: TextStyle(fontSize: 24)),
          title: Text('Elektronik'),
        ),

        ListTile(
          leading: Text('👕',
              style: TextStyle(fontSize: 24)),
          title: Text('Giyim'),
        ),

        ListTile(
          leading: Text('✈️',
              style: TextStyle(fontSize: 24)),
          title: Text('Seyahat'),
        ),

        ListTile(
          leading: Text('🎬',
              style: TextStyle(fontSize: 24)),
          title: Text('Eğlence'),
        ),

        ListTile(
          leading: Text('🏠',
              style: TextStyle(fontSize: 24)),
          title: Text('Ev & Yaşam'),
        ),
      ],
    );
  }
}
