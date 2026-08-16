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
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.indigo),
        useMaterial3: true,
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

    final raw = matches.last
        .group(1)!
        .replaceAll('.', '')
        .replaceAll(' ', '');

    return double.tryParse(raw);
  }

  String detectCategory(String text) {
    final q = text.toLowerCase();

    const map = {
      'E-ticaret': [
        'trendyol',
        'hepsiburada',
        'amazon',
        'n11',
        'online',
        'e-ticaret',
        'eticaret',
      ],
      'Akaryakıt': [
        'benzin',
        'motorin',
        'mazot',
        'akaryakıt',
        'petrol',
        'opet',
        'shell',
        'bp',
        'total',
      ],
      'Market': [
        'market',
        'migros',
        'carrefour',
        'a101',
        'bim',
        'şok',
      ],
      'Restoran': [
        'restoran',
        'yemek',
        'burger',
        'pizza',
        'kahve',
        'yemeksepeti',
        'getir yemek',
      ],
      'Elektronik': [
        'telefon',
        'laptop',
        'bilgisayar',
        'elektronik',
        'teknoloji',
      ],
      'Giyim': [
        'giyim',
        'kıyafet',
        'ayakkabı',
        'zara',
        'defacto',
      ],
    };

    for (final entry in map.entries) {
      if (entry.value.any(q.contains)) {
        return entry.key;
      }
    }

    return category;
  }

  bool cardMatches(
    Map<String, dynamic> campaign,
    UserCard userCard,
  ) {
    final bankRule =
        '${campaign['bank_name'] ?? ''}'.trim().toLowerCase();

    final cardRule =
        '${campaign['card_name'] ?? ''}'.trim().toLowerCase();

    final networkRule =
        '${campaign['network'] ?? ''}'.trim().toLowerCase();

    final bankOk = bankRule.isEmpty ||
        bankRule == '*' ||
        bankRule == userCard.bank.toLowerCase();

    final cardOk = cardRule.isEmpty ||
        cardRule == '*' ||
        cardRule == userCard.card.toLowerCase();

    final networkOk = networkRule.isEmpty ||
        networkRule == '*' ||
        networkRule == userCard.network.toLowerCase();

    return bankOk && cardOk && networkOk;
  }

  double rewardFor(Map<String, dynamic> campaign) {
    final reward =
        double.tryParse('${campaign['reward_amount'] ?? 0}') ?? 0;

    final max =
        double.tryParse('${campaign['max_reward'] ?? 0}') ?? 0;

    if (max > 0 && reward > max) {
      return max;
    }

    return reward;
  }

  List<Map<String, dynamic>> rankCampaigns(
    List<Map<String, dynamic>> rows,
  ) {
    final q = search.text.trim().toLowerCase();

    final detectedCategory =
        category.isEmpty ? detectCategory(search.text) : category;

    final result = <Map<String, dynamic>>[];

    for (final campaign in rows) {
      final blob = campaign.values.join(' ').toLowerCase();

      final words = q
          .split(RegExp(r'\s+'))
          .where(
            (x) =>
                x.isNotEmpty &&
                !RegExp(r'^\d').hasMatch(x),
          );

      final textOk =
          q.isEmpty ||
          words.isEmpty ||
          words.any(blob.contains);

      final categoryOk =
          detectedCategory.isEmpty ||
          blob.contains(detectedCategory.toLowerCase());

      if (!textOk || !categoryOk) {
        continue;
      }

      final minSpend =
          double.tryParse('${campaign['min_spend'] ?? 0}') ?? 0;

      if (spend != null &&
          minSpend > 0 &&
          spend! < minSpend) {
        continue;
      }

      final matchingCards = widget.cards
          .where((card) => cardMatches(campaign, card))
          .toList();

      final copy = Map<String, dynamic>.from(campaign);

      copy['_cards'] = matchingCards;
      copy['_reward'] = rewardFor(campaign);

      copy['_score'] = matchingCards.isEmpty
          ? 0
          : rewardFor(campaign) * 1000 + matchingCards.length;

      result.add(copy);
    }

    result.sort(
      (a, b) =>
          (b['_score'] as num).compareTo(a['_score'] as num),
    );

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
    return Scaffold(
      appBar: AppBar(
        title: const Text('Kart Kampanya'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () =>
                Supabase.instance.client.auth.signOut(),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          setState(() {
            future = fetchCampaigns();
          });
        },
        child: ListView(
          padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
          children: [
            const Text(
              'Bugün ne almayı düşünüyorsun?',
              style: TextStyle(
                fontSize: 26,
                fontWeight: FontWeight.bold,
              ),
            ),

            const SizedBox(height: 8),

            const Text(
              'Ne alacağını yaz, hangi kartın daha avantajlı olduğunu bulalım.',
            ),

            const SizedBox(height: 16),

            TextField(
              controller: search,
              textInputAction: TextInputAction.search,
              onSubmitted: (_) => searchNow(),
              decoration: InputDecoration(
                hintText: 'Örn. Trendyol 3000 TL',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: IconButton(
                  icon: const Icon(Icons.arrow_forward),
                  onPressed: searchNow,
                ),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(18),
                ),
              ),
            ),

            if (category.isNotEmpty || spend != null)
              Padding(
                padding: const EdgeInsets.only(top: 10),
                child: Wrap(
                  spacing: 8,
                  children: [
                    if (category.isNotEmpty)
                      Chip(label: Text(category)),

                    if (spend != null)
                      Chip(
                        label: Text(
                          '${spend!.toStringAsFixed(0)} TL',
                        ),
                      ),

                    ActionChip(
                      label: const Text('Temizle'),
                      onPressed: () {
                        setState(() {
                          category = '';
                          spend = null;
                          search.clear();
                        });
                      },
                    ),
                  ],
                ),
              ),

            const SizedBox(height: 18),

            const Text(
              'Hızlı kategoriler',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),

            const SizedBox(height: 10),

            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: quick.map<Widget>((x) {
                return FilterChip(
                  avatar: Text(x[0]),
                  label: Text(x[1]),
                  selected: category == x[1],
                  onSelected: (_) {
                    setState(() {
                      category =
                          category == x[1] ? '' : x[1];
                    });
                  },
                );
              }).toList(),
            ),

            const SizedBox(height: 20),

            FutureBuilder<List<Map<String, dynamic>>>(
              future: future,
              builder: (_, snapshot) {
                if (snapshot.connectionState ==
                    ConnectionState.waiting) {
                  return const Padding(
                    padding: EdgeInsets.all(40),
                    child: Center(
                      child: CircularProgressIndicator(),
                    ),
                  );
                }

                if (snapshot.hasError) {
                  return Padding(
                    padding: const EdgeInsets.all(12),
                    child: Text(
                      'Hata: ${snapshot.error}',
                    ),
                  );
                }

                final rows =
                    rankCampaigns(snapshot.data ?? []);

                if (rows.isEmpty) {
                  return const Padding(
                    padding: EdgeInsets.all(30),
                    child: Center(
                      child: Text(
                        'Uygun kampanya bulunamadı.',
                      ),
                    ),
                  );
                }

                return Column(
                  crossAxisAlignment:
                      CrossAxisAlignment.start,
                  children: [
                    if (search.text.trim().isNotEmpty)
                      Padding(
                        padding:
                            const EdgeInsets.only(bottom: 10),
                        child: Text(
                          widget.cards.isEmpty
                              ? 'Kart ekleyerek sana özel sonuçları görebilirsin.'
                              : 'En avantajlı seçenekler',
                          style: const TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),

                    ...rows.map<Widget>(
                      (campaign) =>
                          SmartCampaignCard(
                        campaign: campaign,
                      ),
                    ),
                  ],
                );
              },
            ),
          ],
        ),
      ),
      ),
    );
  }
}

class SmartCampaignCard extends StatelessWidget {
  final Map<String, dynamic> campaign;

  const SmartCampaignCard({
    super.key,
    required this.campaign,
  });

  @override
  Widget build(BuildContext context) {
    final cards = List<UserCard>.from(
      campaign['_cards'] ?? const <UserCard>[],
    );

    final reward = campaign['_reward'];

    final merchant = decodeHtmlEntities(
        '${campaign['merchant'] ?? ''}').trim();

    final category = decodeHtmlEntities(
        '${campaign['category'] ?? ''}').trim();

    final min =
        campaign['min_spend'];

    final bankName = decodeHtmlEntities(
      '${campaign['bank_name'] ?? ''}',
    ).trim();

    final cardName = decodeHtmlEntities(
      '${campaign['card_name'] ?? ''}',
    ).trim();

    final network = decodeHtmlEntities(
      '${campaign['network'] ?? ''}',
    ).trim();

    final terms = decodeHtmlEntities(
      '${campaign['terms'] ?? campaign['description'] ?? campaign['conditions'] ?? ''}',
    ).trim();

    final detailUrl = '${campaign['detail_url'] ?? campaign['url'] ?? ''}'.trim();

    final startDate = '${campaign['start_date'] ?? ''}'.trim();
    final endDate = '${campaign['end_date'] ?? ''}'.trim();

    final displayReward = reward ?? campaign['reward_amount'] ?? campaign['max_reward'];
    final displayMin = min ?? campaign['min_spend'];

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () {
          showModalBottomSheet(
            context: context,
            isScrollControlled: true,
            showDragHandle: true,
            builder: (sheetContext) {
              return SafeArea(
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(20, 8, 20, 24),
                  child: SingleChildScrollView(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '$merchant Kampanyası',
                          style: Theme.of(sheetContext).textTheme.headlineSmall
                              ?.copyWith(fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 16),
                        if (bankName.isNotEmpty)
                          ListTile(
                            contentPadding: EdgeInsets.zero,
                            leading: const Icon(Icons.account_balance),
                            title: const Text('Banka'),
                            subtitle: Text(bankName),
                          ),
                        if (cardName.isNotEmpty)
                          ListTile(
                            contentPadding: EdgeInsets.zero,
                            leading: const Icon(Icons.credit_card),
                            title: const Text('Kart'),
                            subtitle: Text(cardName),
                          ),
                        if (network.isNotEmpty)
                          ListTile(
                            contentPadding: EdgeInsets.zero,
                            leading: const Icon(Icons.payment),
                            title: const Text('Kart ağı'),
                            subtitle: Text(network),
                          ),
                        if (category.isNotEmpty)
                          ListTile(
                            contentPadding: EdgeInsets.zero,
                            leading: const Icon(Icons.category_outlined),
                            title: const Text('Kategori'),
                            subtitle: Text(category),
                          ),
                        if (displayMin != null)
                          ListTile(
                            contentPadding: EdgeInsets.zero,
                            leading: const Icon(Icons.shopping_cart_outlined),
                            title: const Text('Minimum harcama'),
                            subtitle: Text('$displayMin TL'),
                          ),
                        if (displayReward != null)
                          ListTile(
                            contentPadding: EdgeInsets.zero,
                            leading: const Icon(Icons.savings_outlined),
                            title: const Text('Tahmini avantaj'),
                            subtitle: Text('$displayReward TL'),
                          ),
                        if (startDate.isNotEmpty)
                          ListTile(
                            contentPadding: EdgeInsets.zero,
                            leading: const Icon(Icons.event_outlined),
                            title: const Text('Başlangıç'),
                            subtitle: Text(startDate),
                          ),
                        if (endDate.isNotEmpty)
                          ListTile(
                            contentPadding: EdgeInsets.zero,
                            leading: const Icon(Icons.event_available_outlined),
                            title: const Text('Son gün'),
                            subtitle: Text(endDate),
                          ),
                        const SizedBox(height: 8),
                        Text(
                          'Kampanya şartları',
                          style: Theme.of(sheetContext).textTheme.titleMedium
                              ?.copyWith(fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          terms.isNotEmpty
                              ? terms
                              : 'Kampanya şartları bulunamadı.',
                          style: const TextStyle(height: 1.45),
                        ),
                        if (detailUrl.isNotEmpty) ...[
                          const SizedBox(height: 12),
                          SelectableText(
                            'Kaynak: $detailUrl',
                            style: TextStyle(
                              fontSize: 12,
                              color: Theme.of(sheetContext)
                                  .colorScheme
                                  .primary,
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                ),
              );
            },
          );
        },
        child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment:
              CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  cards.isNotEmpty
                      ? Icons.emoji_events
                      : Icons.local_offer,
                ),

                const SizedBox(width: 8),

                Expanded(
                  child: Text(
                    '$merchant Kampanyası',
                    style: const TextStyle(
                      fontSize: 17,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),

            if (category.isNotEmpty)
              Padding(
                padding:
                    const EdgeInsets.only(top: 6),
                child: Text(category),
              ),

            if (cards.isNotEmpty)
              Padding(
                padding:
                    const EdgeInsets.only(top: 10),
                child: Text(
                  '🏆 Uygun kart:\n'
                  '${cards.map(
                    (c) =>
                        '${c.bank} • ${c.card} • ${c.network}',
                  ).join('\n')}',
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),

            if (reward != null)
              Padding(
                padding:
                    const EdgeInsets.only(top: 8),
                child: Text(
                  '💰 Tahmini avantaj: $reward TL',
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),

            if (min != null)
              Padding(
                padding:
                    const EdgeInsets.only(top: 5),
                child: Text(
                  'Minimum harcama: $min TL',
                ),
              ),
          ],
        ),
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
