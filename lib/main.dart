import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:url_launcher/url_launcher.dart';
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
  final String customerType; // Bireysel / Ticari
  final String cardType; // Kredi / Banka (Bankamatik)

  UserCard({
    required this.id,
    required this.bank,
    required this.card,
    required this.network,
    required this.customerType,
    required this.cardType,
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
          seedColor: const Color(0xFF5B4BDB),
          brightness: Brightness.light,
        ),
        scaffoldBackgroundColor: const Color(0xFFF6F7FB),
        appBarTheme: const AppBarTheme(
          elevation: 0,
          backgroundColor: Colors.transparent,
        ),
        cardTheme: const CardThemeData(
          elevation: 0,
          margin: EdgeInsets.zero,
          surfaceTintColor: Colors.transparent,
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
              customerType: '${m['customer_type'] ?? 'Bireysel'}',
              cardType: '${m['card_type'] ?? 'Kredi'}',
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
      'customer_type': card.customerType,
      'card_type': card.cardType,
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

  final Set<String> favoriteIds = <String>{};
  final Set<String> compareIds = <String>{};
  bool showFavoritesOnly = false;
  bool showAllCampaigns = false;
  bool showAllQuickCategories = false;
  List<Map<String, dynamic>> cachedCampaigns = <Map<String, dynamic>>[];
  final Map<String, int> campaignProgress = <String, int>{};

  late Future<List<Map<String, dynamic>>> future;

  final quick = const [
    ['⛽', 'Akaryakıt'],
    ['🚗', 'Otomotiv'],
    ['🛒', 'Market'],
    ['🍔', 'Restoran'],
    ['🛍️', 'E-ticaret'],
    ['📱', 'Elektronik'],
    ['👕', 'Giyim'],
    ['🏠', 'Ev & Yaşam'],
    ['✈️', 'Seyahat'],
    ['🎬', 'Eğlence'],
    ['💊', 'Sağlık & Kişisel Bakım'],
    ['📚', 'Eğitim'],
    ['👶', 'Bebek & Çocuk'],
    ['🐾', 'Evcil Hayvan'],
    ['💼', 'Finans & Sigorta'],
    ['🧾', 'Fatura & Abonelik'],
    ['🔧', 'Hizmet'],
    ['🏋️', 'Spor'],
    ['📖', 'Kitap & Kırtasiye'],
    ['🎨', 'Hobi'],
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
    .from('campaign')
    .select();

    final list = List<Map<String, dynamic>>.from(rows);
    cachedCampaigns = list;
    return list;
  }

  String _norm(String value) {
    return value
        .toLowerCase()
        .trim()
        .replaceAll('ı', 'i')
        .replaceAll('İ', 'i')
        .replaceAll('ş', 's')
        .replaceAll('Ş', 's')
        .replaceAll('ğ', 'g')
        .replaceAll('Ğ', 'g')
        .replaceAll('ü', 'u')
        .replaceAll('Ü', 'u')
        .replaceAll('ö', 'o')
        .replaceAll('Ö', 'o')
        .replaceAll('ç', 'c')
        .replaceAll('Ç', 'c');
  }

  bool _ruleMatches(String rule, String actual) {
    final r = _norm(rule);
    final a = _norm(actual);

    if (r.isEmpty || r == '*' || r == 'all' || r == 'tum' || r == 'hepsi') return true;
    if (a.isEmpty) return false;

    const aliases = <String, List<String>>{
      'axess': ['axess', 'akbank axess'],
      'bonus': ['bonus', 'garanti bonus', 'teb bonus'],
      'world': ['world', 'yapi kredi world'],
      'maximum': ['maximum', 'is bankasi maximum'],
      'bankkart': ['bankkart', 'ziraat bankkart'],
      'paraf': ['paraf', 'halkbank paraf'],
      'cardfinans': ['cardfinans', 'qnb cardfinans'],
      'wings': ['wings', 'akbank wings'],
      'free': ['free', 'akbank free'],
      'bankamatik': ['banka karti', 'bankamatik', 'debit'],
      'banka karti': ['banka karti', 'bankamatik', 'debit'],
      'kredi': ['kredi', 'kredi karti', 'credit'],
      'kredi karti': ['kredi', 'kredi karti', 'credit'],
      'bireysel': ['bireysel', 'individual'],
      'ticari': ['ticari', 'business', 'commercial'],
    };

    bool matchesOne(String item) {
      final x = _norm(item);
      final xs = <String>{x, ...(aliases[x] ?? const <String>[])};
      final ys = <String>{a, ...(aliases[a] ?? const <String>[])};
      return xs.any((left) => ys.any(
        (right) => left == right || left.contains(right) || right.contains(left),
      ));
    }

    return r.split(RegExp(r'[,;/|]'))
        .map((x) => x.trim())
        .where((x) => x.isNotEmpty)
        .any(matchesOne);
  }

  List<String> fieldMatches(
    Map<String, dynamic> campaign,
    String query,
  ) {
    final q = _norm(query);
    if (q.isEmpty) return <String>[];

    final values = <String>[
      '${campaign['merchant'] ?? ''}',
      '${campaign['category'] ?? ''}',
      '${campaign['bank_name'] ?? ''}',
      '${campaign['card_name'] ?? ''}',
      '${campaign['network'] ?? ''}',
      '${campaign['campaign_text'] ?? ''}',
      '${campaign['terms'] ?? ''}',
    ];

    final haystack = _norm(values.join(' '));

    const aliases = <String, List<String>>{
      'benzin': ['benzin', 'akaryakit', 'motorin', 'mazot'],
      'mazot': ['mazot', 'motorin', 'dizel', 'akaryakit'],
      'dizel': ['dizel', 'motorin', 'mazot', 'akaryakit'],
      'lpg': ['lpg', 'otogaz', 'akaryakit'],
      'akaryakit': ['akaryakit', 'benzin', 'motorin', 'mazot', 'dizel', 'lpg', 'otogaz'],
      'lastik': ['lastik', 'oto lastik', 'arac lastigi', 'lastikci'],
      'hamburger': ['hamburger', 'burger', 'yemek', 'restoran', 'restaurant'],
      'yemek': ['yemek', 'restoran', 'restaurant', 'lokanta', 'hamburger'],
      'market': ['market', 'supermarket', 'gida'],
      'gida': ['gida', 'market', 'supermarket'],
    };

    final terms = <String>{q, ...(aliases[q] ?? const <String>[])};
    return terms.where(haystack.contains).toList();
  }

  String campaignId(Map<String, dynamic> campaign) =>
      '${campaign['id'] ?? campaign['detail_url'] ?? campaign['merchant'] ?? ''}';

  DateTime? parseCampaignDate(String value) {
    final v = value.trim();
    if (v.isEmpty) return null;

    final iso = DateTime.tryParse(v);
    if (iso != null) return iso;

    final m = RegExp(r'^(\d{1,2})[./-](\d{1,2})[./-](\d{4})').firstMatch(v);
    if (m == null) return null;

    return DateTime(
      int.parse(m.group(3)!),
      int.parse(m.group(2)!),
      int.parse(m.group(1)!),
    );
  }

  int daysLeft(Map<String, dynamic> campaign) {
    final end = parseCampaignDate('${campaign['end_date'] ?? ''}');
    if (end == null) return -1;

    final now = DateTime.now();
    final a = DateTime(now.year, now.month, now.day);
    final b = DateTime(end.year, end.month, end.day);
    return b.difference(a).inDays;
  }

  bool isExpiringSoon(Map<String, dynamic> campaign) {
    final days = daysLeft(campaign);
    return days >= 0 && days <= 3;
  }

  int requiredSteps(Map<String, dynamic> campaign) {
    // Öncelik gerçek kampanya metninde. `terms` çoğu bankada
    // genel kart/ürün şartlarını içerdiği için ilerleme şartını
    // yanlışlıkla buradan okumuyoruz.
    final campaignText = _norm('${campaign['campaign_text'] ?? ''}');
    final conditions = _norm('${campaign['conditions'] ?? ''}');
    final terms = _norm('${campaign['terms'] ?? ''}');

    final text = campaignText.isNotEmpty
        ? campaignText
        : (conditions.isNotEmpty ? conditions : terms);

    final patterns = <RegExp>[
      RegExp(r'\b(\d{1,2})\s*(?:kez|adet)\s*(?:alisveris|islem)\b'),
      RegExp(r'\b(\d{1,2})\s*(?:alisveris|islem|adim)\b'),
      RegExp(r'\b(\d{1,2})\.\s*(?:alisveris|islem|adim)\b'),
      RegExp(r'(?:en az|toplam)\s*(\d{1,2})\s*(?:alisveris|islem)\b'),
    ];

    for (final pattern in patterns) {
      final match = pattern.firstMatch(text);
      if (match == null) continue;
      final value = int.tryParse(match.group(1)!);
      if (value != null && value >= 2 && value <= 30) return value;
    }
    return 0;
  }

  int currentProgress(Map<String, dynamic> campaign) {
    final id = campaignId(campaign);
    return campaignProgress[id] ?? 0;
  }

  void changeProgress(Map<String, dynamic> campaign, int delta) {
    final id = campaignId(campaign);
    final required = requiredSteps(campaign);
    if (id.isEmpty || required < 2) return;

    final current = currentProgress(campaign);
    final next = (current + delta).clamp(0, required);

    setState(() {
      campaignProgress[id] = next;
    });
  }

  void toggleFavorite(Map<String, dynamic> campaign) {
    final id = campaignId(campaign);
    if (id.isEmpty) return;

    setState(() {
      if (!favoriteIds.add(id)) {
        favoriteIds.remove(id);
      }
    });
  }

  void toggleCompare(Map<String, dynamic> campaign) {
    final id = campaignId(campaign);
    if (id.isEmpty) return;

    setState(() {
      if (compareIds.contains(id)) {
        compareIds.remove(id);
      } else if (compareIds.length < 3) {
        compareIds.add(id);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Karşılaştırmaya en fazla 3 kampanya ekleyebilirsin.'),
          ),
        );
      }
    });
  }

  Future<void> openCampaignUrl(String rawUrl) async {
    final uri = Uri.tryParse(rawUrl.trim());
    if (uri == null || (uri.scheme != 'http' && uri.scheme != 'https')) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Kampanya bağlantısı bulunamadı.')),
        );
      }
      return;
    }

    final ok = await launchUrl(uri, mode: LaunchMode.externalApplication);
    if (!ok && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Kampanya bağlantısı açılamadı.')),
      );
    }
  }

  void showComparison() {
    final selected = cachedCampaigns
        .where((c) => compareIds.contains(campaignId(c)))
        .toList();

    if (selected.isEmpty) return;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      builder: (sheetContext) {
        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
            child: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Kampanya karşılaştırma',
                    style: TextStyle(fontSize: 23, fontWeight: FontWeight.w800),
                  ),
                  const SizedBox(height: 6),
                  const Text('Ödül, minimum harcama ve bitiş tarihini karşılaştır.'),
                  const SizedBox(height: 16),
                  ...selected.map((c) {
                    final merchant = decodeHtmlEntities('${c['merchant'] ?? ''}');
                    final reward = rewardFor(c);
                    final min = double.tryParse('${c['min_spend'] ?? 0}') ?? 0;
                    final left = daysLeft(c);

                    return Card(
                      margin: const EdgeInsets.only(bottom: 10),
                      child: Padding(
                        padding: const EdgeInsets.all(14),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              merchant.isEmpty ? 'Kampanya' : merchant,
                              style: const TextStyle(fontSize: 17, fontWeight: FontWeight.bold),
                            ),
                            const SizedBox(height: 8),
                            Text('💰 Avantaj: ${reward.toStringAsFixed(0)} TL'),
                            Text('🛒 Minimum: ${min > 0 ? '${min.toStringAsFixed(0)} TL' : 'Yok'}'),
                            Text(
                              left >= 0
                                  ? '📅 ${left == 0 ? 'Bugün bitiyor' : '$left gün kaldı'}'
                                  : '📅 Son tarih belirtilmemiş',
                            ),
                          ],
                        ),
                      ),
                    );
                  }),
                  OutlinedButton.icon(
                    onPressed: () => Navigator.pop(sheetContext),
                    icon: const Icon(Icons.close),
                    label: const Text('Kapat'),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
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
    final q = text.toLowerCase().trim();

    const keywords = <String, List<String>>{
      'Akaryakıt': ['benzin','motorin','mazot','lpg','otogaz','yakıt','yakit','akaryakıt','akaryakit','benzinlik','petrol','shell','opet','bp','total','petrol ofisi'],
      'Otomotiv': ['lastik','lastikler','lastikçi','lastikci','oto lastik','oto lastikçi','oto lastikci','lastik bayii','lastik bayi','lastik değişimi','lastik degisimi','lastik montaj','lastik tamiri','kış lastiği','kis lastigi','yaz lastiği','yaz lastigi','4 mevsim','jant','rot balans','rotbalans','motor yağı','motor yagi','yağ değişimi','yag degisimi','antifriz','akü','aku','fren balatası','fren balatasi','fren diski','amortisör','amortisor','oto servis','araç bakım','arac bakim','oto bakım','oto bakim','yedek parça','yedek parca','oto aksesuar','oto yıkama','oto yikama','otomobil','araba'],
      'Market': ['market','alışveriş','alisveris','erzak','gıda','gida','migros','carrefour','carrefoursa','bim','a101','şok','sok','file market','macrocenter'],
      'Restoran': ['yemek','hamburger','burger','pizza','döner','doner','kebap','lahmacun','pide','restoran','restaurant','lokanta','cafe','kafe','kahve','coffee','fast food','tatlı','tatli','pastane','fırın','firin','yemeksepeti','getir yemek'],
      'E-ticaret': ['trendyol','hepsiburada','amazon','n11','çiçeksepeti','ciceksepeti','online','e-ticaret','eticaret','internet alışverişi','internet alisverisi','online alışveriş','online alisveris'],
      'Elektronik': ['telefon','cep telefonu','iphone','samsung','xiaomi','tablet','laptop','bilgisayar','pc','macbook','televizyon','tv','monitör','monitor','kulaklık','kulaklik','playstation','xbox','nintendo','elektronik','teknoloji','mediamarkt','teknosa','vatan'],
      'Giyim': ['giyim','kıyafet','kiyafet','elbise','pantolon','tişört','tisort','gömlek','gomlek','mont','ceket','ayakkabı','ayakkabi','spor ayakkabı','çanta','canta','zara','h&m','lc waikiki','defacto','mavi','boyner'],
      'Ev & Yaşam': ['mobilya','koltuk','masa','sandalye','yatak','ev','dekorasyon','mutfak','banyo','halı','hali','perde','aydınlatma','beyaz eşya','beyaz esya','ikea','koçtaş','koctas','english home','madame coco'],
      'Seyahat': ['uçak','ucak','uçuş','ucus','bilet','otel','konaklama','tatil','seyahat','tur','rent a car','araç kiralama','arac kiralama','otobüs','otobus','tren','thy','pegasus','booking','airbnb'],
      'Eğlence': ['sinema','film','tiyatro','konser','etkinlik','biletix','oyun','bowling','lunapark','müze','muze','eğlence','eglence','netflix','spotify','steam'],
      'Sağlık & Kişisel Bakım': ['eczane','ilaç','ilac','vitamin','kozmetik','parfüm','parfum','makyaj','cilt bakımı','cilt bakimi','şampuan','sampuan','diş','dis','diş macunu','dis macunu','kuaför','kuafor','berber','güzellik','guzellik','fitness'],
      'Eğitim': ['eğitim','egitim','kurs','ders','kitap','kırtasiye','kirtasiye','okul','üniversite','universite','online eğitim','online egitim','udemy','dil kursu'],
      'Bebek & Çocuk': ['bebek','çocuk','cocuk','bez','mama','bebek arabası','bebek arabasi','oyuncak','lego','çocuk giyim','cocuk giyim'],
      'Evcil Hayvan': ['evcil hayvan','kedi','köpek','kopek','mama','pet shop','veteriner','kedi maması','kopek mamasi','petshop'],
      'Finans & Sigorta': ['sigorta','kasko','trafik sigortası','trafik sigortasi','bireysel emeklilik','bes','yatırım','yatirim','finans','kredi'],
      'Fatura & Abonelik': ['fatura','elektrik','su faturası','su faturasi','doğalgaz','dogalgaz','internet faturası','internet faturasi','telefon faturası','telefon faturasi','abonelik'],
      'Hizmet': ['hizmet','tamir','tesisat','temizlik','nakliye','kargo','kurye','teknik servis','ev temizliği','ev temizligi'],
      'Spor': ['spor','fitness','gym','spor salonu','forma','spor malzemesi','bisiklet','koşu','kosu','kamp','outdoor'],
      'Kitap & Kırtasiye': ['kitap','kırtasiye','kirtasiye','kalem','defter','roman','dergi','d&r'],
      'Hobi': ['hobi','fotoğraf','fotograf','kamera','müzik aleti','muzik aleti','model','koleksiyon','el işi','el isi'],
    };

    for (final entry in keywords.entries) {
      if (entry.value.any(q.contains)) return entry.key;
    }
    return category;
  }

  bool categoryMatches(String detectedCategory, String text) {
    final q = text.toLowerCase();
    const aliases = <String, List<String>>{
      'Akaryakıt': ['akaryakıt','akaryakit','benzin','motorin','mazot','lpg','otogaz','yakıt','yakit','petrol','benzinlik','shell','opet','bp','total','petrol ofisi'],
      'Otomotiv': ['otomotiv','lastik','lastikler','lastikçi','lastikci','oto lastik','lastik bayii','lastik bayi','lastik değişimi','lastik degisimi','lastik montaj','lastik tamiri','jant','rot balans','rotbalans','motor yağı','motor yagi','akü','aku','fren','fren balatası','fren balatasi','servis','yedek parça','yedek parca','oto bakım','oto bakim','oto aksesuar','oto yıkama','oto yikama','araba','otomobil'],
      'Market': ['market','migros','carrefour','bim','a101','şok','sok','gıda','gida'],
      'Restoran': ['restoran','restaurant','yemek','hamburger','burger','pizza','döner','doner','kebap','lahmacun','pide','cafe','kafe','kahve','coffee','fast food'],
      'E-ticaret': ['e-ticaret','eticaret','online','trendyol','hepsiburada','amazon','n11','çiçeksepeti','ciceksepeti'],
      'Elektronik': ['elektronik','telefon','tablet','laptop','bilgisayar','televizyon','tv','playstation','xbox','teknosa','mediamarkt','vatan'],
      'Giyim': ['giyim','kıyafet','kiyafet','ayakkabı','ayakkabi','zara','mavi','boyner','defacto','lc waikiki'],
      'Ev & Yaşam': ['mobilya','koltuk','mutfak','banyo','dekorasyon','beyaz eşya','beyaz esya','ikea','koçtaş','koctas'],
      'Seyahat': ['seyahat','uçak','ucak','uçuş','ucus','otel','tatil','tur','bilet','thy','pegasus','booking','airbnb','araç kiralama','arac kiralama'],
      'Eğlence': ['eğlence','eglence','sinema','tiyatro','konser','biletix','bowling','netflix','spotify','steam'],
      'Sağlık & Kişisel Bakım': ['sağlık','saglik','eczane','ilaç','ilac','kozmetik','parfüm','parfum','kuaför','kuafor','berber','güzellik','guzellik'],
      'Eğitim': ['eğitim','egitim','kurs','ders','kitap','kırtasiye','kirtasiye','okul'],
      'Bebek & Çocuk': ['bebek','çocuk','cocuk','bez','mama','oyuncak','lego'],
      'Evcil Hayvan': ['evcil hayvan','kedi','köpek','kopek','pet shop','veteriner'],
      'Finans & Sigorta': ['sigorta','kasko','yatırım','yatirim','kredi','bes'],
      'Fatura & Abonelik': ['fatura','elektrik','su faturası','su faturasi','doğalgaz','dogalgaz','abonelik'],
      'Hizmet': ['hizmet','tamir','tesisat','temizlik','nakliye','kargo','kurye'],
      'Spor': ['spor','fitness','gym','bisiklet','koşu','kosu','outdoor'],
      'Kitap & Kırtasiye': ['kitap','kırtasiye','kirtasiye','kalem','defter','dergi'],
      'Hobi': ['hobi','fotoğraf','fotograf','kamera','müzik aleti','muzik aleti','koleksiyon'],
    };
    return aliases[detectedCategory]?.any(q.contains) ??
        q.contains(detectedCategory.toLowerCase());
  }

  bool cardMatches(
    Map<String, dynamic> campaign,
    UserCard userCard,
  ) {
    final campaignCustomerType = '${campaign['customer_type'] ?? ''}';
    final campaignCardType = '${campaign['card_type'] ?? ''}';
    final campaignBank = '${campaign['bank_name'] ?? ''}';
    final campaignCard = '${campaign['card_name'] ?? ''}';
    final campaignNetwork = '${campaign['network'] ?? ''}';

    // Kampanya alanı boşsa o özellik için kısıtlama yoktur.
    final customerOk = _ruleMatches(
      campaignCustomerType,
      userCard.customerType,
    );
    final cardTypeOk = _ruleMatches(
      campaignCardType,
      userCard.cardType,
    );
    final bankOk = _ruleMatches(campaignBank, userCard.bank);
    final cardOk = _ruleMatches(campaignCard, userCard.card);
    final networkOk = _ruleMatches(campaignNetwork, userCard.network);

    return customerOk && cardTypeOk && bankOk && cardOk && networkOk;
  }


  double _moneyValue(dynamic value) {
    final n = double.tryParse('$value') ?? 0;
    // Bazı kampanya kaynakları TL tutarlarını kuruş olarak döndürebilir.
    // Çok büyük ödülleri kullanıcıya 180000 TL gibi göstermemek için
    // bu yaygın formatı normalize ediyoruz.
    if (n >= 10000) return n / 100;
    return n;
  }

  double? _extractPercent(Map<String, dynamic> campaign) {
    // Yüzdeyi de önce gerçek kampanya metninden oku.
    // Genel `terms` metnindeki alakasız yüzdeler ödül hesabını bozmasın.
    final campaignText = _norm('${campaign['campaign_text'] ?? ''}');
    final conditions = _norm('${campaign['conditions'] ?? ''}');
    final terms = _norm('${campaign['terms'] ?? ''}');

    final text = campaignText.isNotEmpty
        ? campaignText
        : (conditions.isNotEmpty ? conditions : terms);

    final m = RegExp(r'%\\s*(\\d+(?:[\\.,]\\d+)?)').firstMatch(text);
    if (m == null) return null;

    return double.tryParse(m.group(1)!.replaceAll(',', '.'));
  }

  double rewardFor(Map<String, dynamic> campaign) {
    final reward = _moneyValue(campaign['reward_amount'] ?? 0);
    final max = _moneyValue(campaign['max_reward'] ?? 0);

    if (max > 0 && reward > max) return max;
    return reward;
  }

  double calculatedReward(
    Map<String, dynamic> campaign, {
    double? amount,
  }) {
    final spendAmount = amount ?? spend;
    final fixedReward = rewardFor(campaign);
    final percent = _extractPercent(campaign);

    double result = fixedReward;

    if (spendAmount != null && spendAmount > 0 && percent != null) {
      result = spendAmount * percent / 100;
    }

    final max = _moneyValue(campaign['max_reward'] ?? 0);
    if (max > 0 && result > max) result = max;

    return result;
  }

  double calculatedPercent(
    Map<String, dynamic> campaign, {
    double? amount,
  }) {
    final spendAmount = amount ?? spend;
    if (spendAmount == null || spendAmount <= 0) return 0;

    final reward = calculatedReward(campaign, amount: spendAmount);
    return reward / spendAmount * 100;
  }

  List<Map<String, dynamic>> rankCampaigns(
    List<Map<String, dynamic>> rows,
  ) {
    final q = search.text.trim().toLowerCase();

    final detectedCategory =
        category.isEmpty ? detectCategory(search.text) : category;

    final result = <Map<String, dynamic>>[];

    for (final campaign in rows) {
      if (showFavoritesOnly &&
          !favoriteIds.contains(campaignId(campaign))) {
        continue;
      }

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

      // Kullanıcı "lastik", "jant", "lastikçi" gibi bir kelime
      // yazdığında kampanyanın category alanı sadece "Otomotiv"
      // olsa bile kampanya gösterilsin.
      final categoryOk =
          detectedCategory.isEmpty ||
          categoryMatches(detectedCategory, blob);

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

      if (widget.cards.isNotEmpty &&
          matchingCards.isEmpty &&
          !showAllCampaigns) {
        continue;
      }

      final copy = Map<String, dynamic>.from(campaign);

      copy['_cards'] = matchingCards;
      copy['_reward'] = rewardFor(campaign);
      copy['_calculatedReward'] = calculatedReward(campaign);
      copy['_calculatedPercent'] = calculatedPercent(campaign);

      copy['_score'] = matchingCards.isEmpty
          ? 0
          : calculatedReward(campaign) * 1000 + matchingCards.length;

      result.add(copy);
    }

    result.sort((a, b) {
      if (showFavoritesOnly) {
        final da = daysLeft(a);
        final db = daysLeft(b);
        final va = da >= 0 ? da : 99999;
        final vb = db >= 0 ? db : 99999;
        if (va != vb) return va.compareTo(vb);
      }

      return (b['_score'] as num).compareTo(a['_score'] as num);
    });

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
        title: const Text(
          'Kart Kampanya',
          style: TextStyle(fontWeight: FontWeight.w800),
        ),
        actions: [
          IconButton(
            tooltip: 'Yenile',
            icon: const Icon(Icons.refresh_rounded),
            onPressed: () => setState(() {
              future = fetchCampaigns();
            }),
          ),
          IconButton(
            tooltip: 'Çıkış',
            icon: const Icon(Icons.logout_rounded),
            onPressed: () => Supabase.instance.client.auth.signOut(),
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
            Container(
              padding: const EdgeInsets.fromLTRB(20, 20, 20, 22),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFF5B4BDB), Color(0xFF7A63E8)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(26),
              ),
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Bugün ne almayı düşünüyorsun?',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 25,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  SizedBox(height: 7),
                  Text(
                    'Harcamanı yaz, sana en avantajlı kartı bulalım.',
                    style: TextStyle(color: Colors.white70, fontSize: 14),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 14),

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
                filled: true,
                fillColor: Colors.white,
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 18,
                  vertical: 16,
                ),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(18),
                  borderSide: BorderSide.none,
                ),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(18),
                  borderSide: BorderSide.none,
                ),
              ),
            ),

            if (search.text.trim().isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(top: 10),
                child: Card(
                  child: ListTile(
                    leading: const CircleAvatar(
                      child: Icon(Icons.calculate_rounded),
                    ),
                    title: const Text(
                      'Harcama planın hazır',
                      style: TextStyle(fontWeight: FontWeight.w800),
                    ),
                    subtitle: Text(
                      spend != null
                          ? '${spend!.toStringAsFixed(0)} TL için minimum harcama ve avantajları kontrol ediyorum.'
                          : 'Tutar eklersen minimum harcama şartlarını da kontrol ederim.',
                    ),
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
              spacing: 6,
              runSpacing: 6,
              children: [
                ...(showAllQuickCategories ? quick : quick.take(6)).map<Widget>(
                  (x) => FilterChip(
                    visualDensity: const VisualDensity(horizontal: -2, vertical: -2),
                    padding: const EdgeInsets.symmetric(horizontal: 4),
                    avatar: Text(x[0], style: const TextStyle(fontSize: 15)),
                    label: Text(x[1], style: const TextStyle(fontSize: 13)),
                    selected: category == x[1],
                    onSelected: (_) {
                      setState(() {
                        category = category == x[1] ? '' : x[1];
                      });
                    },
                  ),
                ),
                ActionChip(
                  visualDensity: const VisualDensity(horizontal: -2, vertical: -2),
                  avatar: Icon(
                    showAllQuickCategories
                        ? Icons.expand_less_rounded
                        : Icons.expand_more_rounded,
                    size: 18,
                  ),
                  label: Text(
                    showAllQuickCategories
                        ? 'Daha az'
                        : 'Tüm kategoriler (${quick.length})',
                    style: const TextStyle(fontSize: 13),
                  ),
                  onPressed: () {
                    setState(() {
                      showAllQuickCategories = !showAllQuickCategories;
                    });
                  },
                ),
              ],
            ),

            const SizedBox(height: 14),

            Wrap(
              spacing: 8,
              children: [
                FilterChip(
                  avatar: const Icon(Icons.star_rounded, size: 18),
                  label: Text(
                    favoriteIds.isEmpty
                        ? 'Favoriler'
                        : 'Favoriler (${favoriteIds.length})',
                  ),
                  selected: showFavoritesOnly,
                  onSelected: (_) {
                    setState(() {
                      showFavoritesOnly = !showFavoritesOnly;
                    });
                  },
                ),
                if (compareIds.isNotEmpty)
                  ActionChip(
                    avatar: const Icon(
                      Icons.compare_arrows_rounded,
                      size: 18,
                    ),
                    label: Text('Karşılaştır (${compareIds.length})'),
                    onPressed: showComparison,
                  ),
              ],
            ),

            const SizedBox(height: 10),

            Wrap(
              spacing: 8,
              children: [
                FilterChip(
                  avatar: Icon(
                    showAllCampaigns
                        ? Icons.public_rounded
                        : Icons.credit_card_rounded,
                    size: 18,
                  ),
                  label: Text(
                    showAllCampaigns
                        ? 'Tüm kampanyalar'
                        : 'Kartlarıma uygun',
                  ),
                  selected: showAllCampaigns,
                  onSelected: (_) {
                    setState(() {
                      showAllCampaigns = !showAllCampaigns;
                    });
                  },
                ),
              ],
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

                cachedCampaigns =
                    snapshot.data ?? const <Map<String, dynamic>>[];
                final rows = rankCampaigns(cachedCampaigns);

                final bestPlan = rows.isNotEmpty && spend != null
                    ? rows.first
                    : null;

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

                    if (bestPlan != null)
                      Padding(
                        padding: const EdgeInsets.only(bottom: 12),
                        child: _PlanSummaryCard(
                          campaign: bestPlan,
                          amount: spend!,
                          calculatedReward: (bestPlan['_calculatedReward'] as num?)?.toDouble()
                              ?? calculatedReward(bestPlan, amount: spend),
                          calculatedPercent: (bestPlan['_calculatedPercent'] as num?)?.toDouble()
                              ?? calculatedPercent(bestPlan, amount: spend),
                        ),
                      ),

                    if (compareIds.isNotEmpty)
                      Padding(
                        padding: const EdgeInsets.only(bottom: 10),
                        child: FilledButton.icon(
                          onPressed: showComparison,
                          icon: const Icon(Icons.compare_arrows_rounded),
                          label: Text(
                            'Seçilenleri karşılaştır (${compareIds.length}/3)',
                          ),
                        ),
                      ),

                    ...rows.map<Widget>(
                      (campaign) => SmartCampaignCard(
                        campaign: campaign,
                        isFavorite: favoriteIds.contains(
                          campaignId(campaign),
                        ),
                        isCompared: compareIds.contains(
                          campaignId(campaign),
                        ),
                        showAllCampaigns: showAllCampaigns,
                        expiringSoon: isExpiringSoon(campaign),
                        daysRemaining: daysLeft(campaign),
                        onFavorite: () => toggleFavorite(campaign),
                        onCompare: () => toggleCompare(campaign),
                        onOpenUrl: openCampaignUrl,
                        requiredSteps: requiredSteps(campaign),
                        completedSteps: currentProgress(campaign),
                        onProgressChange: (delta) => changeProgress(campaign, delta),
                      ),
                    ),
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


class _PlanSummaryCard extends StatelessWidget {
  final Map<String, dynamic> campaign;
  final double amount;
  final double calculatedReward;
  final double calculatedPercent;

  const _PlanSummaryCard({
    required this.campaign,
    required this.amount,
    required this.calculatedReward,
    required this.calculatedPercent,
  });

  @override
  Widget build(BuildContext context) {
    final merchant = decodeHtmlEntities('${campaign['merchant'] ?? ''}').trim();
    final bank = decodeHtmlEntities('${campaign['bank_name'] ?? ''}').trim();
    final card = decodeHtmlEntities('${campaign['card_name'] ?? ''}').trim();
    final min = double.tryParse('${campaign['min_spend'] ?? 0}') ?? 0;
    final end = '${campaign['end_date'] ?? ''}'.trim();

    return Card(
      elevation: 0,
      color: Theme.of(context).colorScheme.primaryContainer,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Text('🏆', style: TextStyle(fontSize: 24)),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'SANA EN ÇOK KAZANDIRAN KART',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w900,
                      color: Theme.of(context).colorScheme.onPrimaryContainer,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Text(
              '$bank • $card',
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800),
            ),
            if (merchant.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(top: 3),
                child: Text('$merchant kampanyası'),
              ),
            const SizedBox(height: 10),
            Text('💳 Harcama: ${amount.toStringAsFixed(0)} TL'),
            Text('🎁 Tahmini kazanç: ${calculatedReward.toStringAsFixed(0)} TL'),
            if (calculatedPercent > 0)
              Text('📈 Net avantaj: %${calculatedPercent.toStringAsFixed(1)}'),
            if (min > 0)
              Text('🛒 Minimum harcama: ${min.toStringAsFixed(0)} TL'),
            if (end.isNotEmpty)
              Text('📅 Son tarih: $end'),
          ],
        ),
      ),
    );
  }
}

String cleanCampaignHtml(String value) {
  return decodeHtmlEntities(
    value
      .replaceAll(RegExp(r'<br\s*/?>', caseSensitive: false), '\n')
      .replaceAll(RegExp(r'</p>', caseSensitive: false), '\n')
      .replaceAll(RegExp(r'<[^>]+>'), ' ')
      .replaceAll(RegExp(r'\s+'), ' ')
      .trim(),
  );
}

String campaignConditions(Map<String, dynamic> campaign) {
  // `campaign_text` gerçek kampanyanın açıklamasıdır.
  // `terms` ise çoğu kayıtta bankanın genel kart şartlarını içeriyor.
  // Bu yüzden ekranda kampanya koşulu olarak önce campaign_text gösterilir.
  final campaignText =
      cleanCampaignHtml('${campaign['campaign_text'] ?? ''}');
  final conditions =
      cleanCampaignHtml('${campaign['conditions'] ?? ''}');
  final terms = cleanCampaignHtml('${campaign['terms'] ?? ''}');
  final description =
      cleanCampaignHtml('${campaign['description'] ?? ''}');

  if (campaignText.isNotEmpty) return campaignText;
  if (conditions.isNotEmpty) return conditions;
  if (description.isNotEmpty) return description;
  if (terms.isNotEmpty) return terms;

  return 'Kampanya koşulları bulunamadı.';
}

class SmartCampaignCard extends StatelessWidget {
  final Map<String, dynamic> campaign;
  final bool isFavorite;
  final bool isCompared;
  final bool showAllCampaigns;
  final bool expiringSoon;
  final int daysRemaining;
  final VoidCallback onFavorite;
  final VoidCallback onCompare;
  final Future<void> Function(String url) onOpenUrl;
  final int requiredSteps;
  final int completedSteps;
  final ValueChanged<int> onProgressChange;

  const SmartCampaignCard({
    super.key,
    required this.campaign,
    required this.isFavorite,
    required this.isCompared,
    required this.showAllCampaigns,
    required this.expiringSoon,
    required this.daysRemaining,
    required this.onFavorite,
    required this.onCompare,
    required this.onOpenUrl,
    required this.requiredSteps,
    required this.completedSteps,
    required this.onProgressChange,
  });

  @override
  Widget build(BuildContext context) {
    final cards = (campaign['_cards'] as List?)
        ?.whereType<UserCard>()
        .toList() ??
    <UserCard>[];

    final reward = campaign['_calculatedReward'] ?? campaign['_reward'];

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

    final terms = campaignConditions(campaign);

    final detailUrl = '${campaign['detail_url'] ?? campaign['url'] ?? ''}'.trim();

    final startDate = '${campaign['start_date'] ?? ''}'.trim();
    final endDate = '${campaign['end_date'] ?? ''}'.trim();

    final displayReward = reward ?? campaign['reward_amount'] ?? campaign['max_reward'];
    final displayMin = min ?? campaign['min_spend'];
    final calculated = campaign['_calculatedReward'];
    final calculatedPct = campaign['_calculatedPercent'];

    final bankColor = switch (bankName) {
      'Akbank' => const Color(0xFFE30613),
      'Garanti BBVA' => const Color(0xFF00834A),
      'Yapı Kredi' => const Color(0xFF004B93),
      'İş Bankası' => const Color(0xFF005BAC),
      'Ziraat Bankası' => const Color(0xFFE30613),
      'Halkbank' => const Color(0xFF005BAA),
      'QNB' => const Color(0xFF007E7E),
      'TEB' => const Color(0xFF00A0DF),
      'VakıfBank' => const Color(0xFFFFB400),
      _ => const Color(0xFF5B4BDB),
    };

    return Card(
      margin: const EdgeInsets.only(bottom: 14),
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        borderRadius: BorderRadius.circular(20),
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
                        const SizedBox(height: 10),
                        Wrap(
                          spacing: 8,
                          children: [
                            if (isFavorite)
                              const Chip(
                                avatar: Icon(
                                  Icons.star_rounded,
                                  size: 17,
                                ),
                                label: Text('Favorilerde'),
                              ),
                            if (expiringSoon)
                              Chip(
                                avatar: const Icon(
                                  Icons.schedule_rounded,
                                  size: 17,
                                ),
                                label: Text(
                                  daysRemaining == 0
                                      ? 'Bugün bitiyor'
                                      : '$daysRemaining gün kaldı',
                                ),
                              ),
                          ],
                        ),
                        const SizedBox(height: 8),
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
                        if (calculated != null)
                          ListTile(
                            contentPadding: EdgeInsets.zero,
                            leading: const Icon(Icons.savings_outlined),
                            title: const Text('Tahmini kazanç'),
                            subtitle: Text(
                              '${(calculated as num).toDouble().toStringAsFixed(0)} TL'
                              '${calculatedPct is num && calculatedPct > 0 ? ' • %${calculatedPct.toDouble().toStringAsFixed(1)} net avantaj' : ''}',
                            ),
                          )
                        else if (displayReward != null)
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
                          const SizedBox(height: 14),
                          SizedBox(
                            width: double.infinity,
                            child: FilledButton.icon(
                              onPressed: () => onOpenUrl(detailUrl),
                              icon: const Icon(Icons.open_in_new_rounded),
                              label: const Text('Kampanyaya Git'),
                            ),
                          ),
                          const SizedBox(height: 10),
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
                IconButton(
                  tooltip: isFavorite
                      ? 'Favoriden çıkar'
                      : 'Favoriye ekle',
                  onPressed: onFavorite,
                  icon: Icon(
                    isFavorite
                        ? Icons.star_rounded
                        : Icons.star_border_rounded,
                  ),
                ),
                IconButton(
                  tooltip: isCompared
                      ? 'Karşılaştırmadan çıkar'
                      : 'Karşılaştır',
                  onPressed: onCompare,
                  icon: Icon(
                    isCompared
                        ? Icons.check_circle_rounded
                        : Icons.compare_arrows_rounded,
                  ),
                ),
              ],
            ),

            if (expiringSoon)
              Container(
                margin: const EdgeInsets.only(top: 10),
                padding: const EdgeInsets.symmetric(
                  horizontal: 10,
                  vertical: 8,
                ),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(12),
                  color: Colors.orange.withOpacity(.12),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.schedule_rounded, size: 18),
                    const SizedBox(width: 7),
                    Expanded(
                      child: Text(
                        daysRemaining == 0
                            ? '⚠️ Bu kampanya bugün bitiyor!'
                            : '⚠️ Kampanyanın bitmesine $daysRemaining gün kaldı.',
                        style: const TextStyle(
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                  ],
                ),
              ),

            if (requiredSteps >= 2)
              Container(
                margin: const EdgeInsets.only(top: 10, bottom: 8),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(14),
                  color: Theme.of(context).colorScheme.primaryContainer.withOpacity(.55),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.track_changes_rounded, size: 19),
                        const SizedBox(width: 7),
                        Expanded(
                          child: Text(
                            'Kampanya ilerlemesi',
                            style: const TextStyle(fontWeight: FontWeight.w700),
                          ),
                        ),
                        Text(
                          '$completedSteps / $requiredSteps alışveriş',
                          style: const TextStyle(fontWeight: FontWeight.w800),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    LinearProgressIndicator(
                      value: requiredSteps == 0
                          ? 0
                          : completedSteps / requiredSteps,
                      minHeight: 7,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        OutlinedButton(
                          onPressed: completedSteps > 0
                              ? () => onProgressChange(-1)
                              : null,
                          child: const Text('− 1'),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            completedSteps >= requiredSteps
                                ? '🎉 Şart tamamlandı'
                                : 'Her alışveriş yaptığında +1 ekle',
                            textAlign: TextAlign.center,
                            style: const TextStyle(fontSize: 12),
                          ),
                        ),
                        FilledButton(
                          onPressed: completedSteps < requiredSteps
                              ? () => onProgressChange(1)
                              : null,
                          child: const Text('+ 1'),
                        ),
                      ],
                    ),
                  ],
                ),
              ),

            if (category.isNotEmpty)
              Padding(
                padding:
                    const EdgeInsets.only(top: 6),
                child: Text(category),
              ),

            if (cards.isEmpty && showAllCampaigns)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text(
                  'ℹ️ Bu kampanya kayıtlı kartlarınla eşleşmiyor.',
                  style: TextStyle(
                    fontSize: 12,
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
                ),
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
                  '💰 Tahmini avantaj: ${(reward as num).toDouble().toStringAsFixed(0)} TL',
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),

            if (campaign['_calculatedPercent'] != null &&
                (campaign['_calculatedPercent'] as num) > 0)
              Padding(
                padding: const EdgeInsets.only(top: 5),
                child: Text(
                  '📈 Net avantaj: ${(campaign['_calculatedPercent'] as num).toDouble().toStringAsFixed(1)}%',
                  style: const TextStyle(fontWeight: FontWeight.w700),
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
    'Kuveyt Türk',
    'Türkiye Finans',
    'Albaraka Türk',
    'ING',
    'Fibabanka',
    'HSBC',
    'Anadolubank',
    'Odeabank',
    'Enpara',
    'CEPTETEB',
    'Alternatif Bank',
  ];

  final cardMap = const {
    'Akbank': ['Axess', 'Wings', 'Free', 'Akbank Kart'],
    'Garanti BBVA': ['Bonus', 'Bonus Gold', 'Bonus Platinum', 'Bonus Genç', 'Paracard'],
    'Yapı Kredi': ['World', 'World Gold', 'World Platinum', 'World Elite', 'Play', 'Adios', 'Yapı Kredi Banka Kartı'],
    'İş Bankası': ['Maximum', 'Maximum Gold', 'Maximum Platinum', 'Maximum Black', 'Maximum Genç', 'İş Bankası Bankamatik Kartı'],
    'Ziraat Bankası': ['Bankkart', 'Bankkart Gold', 'Bankkart Platinum', 'Bankkart Genç', 'Ziraat Bankkart'],
    'Halkbank': ['Paraf', 'Paraf Gold', 'Paraf Platinum', 'Parafly', 'Halkbank Banka Kartı'],
    'QNB': ['CardFinans', 'CardFinans Gold', 'CardFinans Platinum', 'CardFinans Xtra', 'QNB Banka Kartı'],
    'DenizBank': ['Bonus', 'Bonus Gold', 'Bonus Platinum', 'DenizBank Banka Kartı'],
    'TEB': ['Bonus', 'Bonus Platinum', 'TEB Platinum', 'TEB Banka Kartı'],
    'VakıfBank': ['World', 'World Gold', 'World Platinum', 'VakıfBank Banka Kartı'],
    'Kuveyt Türk': ['Sağlam Kart', 'Sağlam Kart Platinum', 'Kuveyt Türk Banka Kartı'],
    'Türkiye Finans': ['Happy Card', 'Happy Card Platinum', 'Türkiye Finans Banka Kartı'],
    'Albaraka Türk': ['Bonus Card', 'Albaraka Banka Kartı'],
    'ING': ['ING Bonus', 'ING Banka Kartı'],
    'Fibabanka': ['Bonus Card', 'Fibabanka Banka Kartı'],
    'HSBC': ['HSBC Premier', 'HSBC Advantage', 'HSBC Banka Kartı'],
    'Anadolubank': ['Anadolubank Kart', 'Anadolubank Banka Kartı'],
    'Odeabank': ['Odeabank Kart', 'Odeabank Banka Kartı'],
    'Enpara': ['Enpara Kredi Kartı', 'Enpara Banka Kartı'],
    'CEPTETEB': ['CEPTETEB Bonus', 'CEPTETEB Banka Kartı'],
    'Alternatif Bank': ['Bonus', 'Alternatif Banka Kartı'],
  };

  final networks = const [
    'Visa',
    'Mastercard',
    'Troy',
  ];

  final customerTypes = const [
    'Bireysel',
    'Ticari',
  ];

  final cardTypes = const [
    'Kredi',
    'Banka (Bankamatik)',
  ];

  Future<void> addCard() async {
    String bank = banks.first;
    String card = cardMap[bank]!.first;
    String network = networks.first;
    String customerType = customerTypes.first;
    String cardType = cardTypes.first;

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
                  value: customerType,
                  decoration: const InputDecoration(
                    labelText: 'Müşteri tipi',
                  ),
                  items: customerTypes.map((t) {
                    return DropdownMenuItem(
                      value: t,
                      child: Text(t),
                    );
                  }).toList(),
                  onChanged: (v) {
                    if (v != null) setDialog(() => customerType = v);
                  },
                ),

                DropdownButtonFormField<String>(
                  value: cardType,
                  decoration: const InputDecoration(
                    labelText: 'Kart tipi',
                  ),
                  items: cardTypes.map((t) {
                    return DropdownMenuItem(
                      value: t,
                      child: Text(t),
                    );
                  }).toList(),
                  onChanged: (v) {
                    if (v != null) setDialog(() => cardType = v);
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
            customerType: customerType,
            cardType: cardType,
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
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 6,
                    ),
                    leading: Container(
                      width: 46,
                      height: 46,
                      decoration: BoxDecoration(
                        color: const Color(0xFFECE9FF),
                        borderRadius: BorderRadius.circular(14),
                      ),
                      child: const Icon(
                        Icons.credit_card_rounded,
                        color: Color(0xFF5B4BDB),
                      ),
                    ),
                    title: Text(
                      '${c.bank} • ${c.card}',
                      style: const TextStyle(fontWeight: FontWeight.w800),
                    ),
                    subtitle: Text(
                      '${c.customerType} • ${c.cardType}\nKart ağı: ${c.network}',
                    ),
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
