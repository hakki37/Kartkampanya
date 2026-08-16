
import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'config.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  if (AppConfig.supabasePublishableKey.isNotEmpty) {
    await Supabase.initialize(
      url: AppConfig.supabaseUrl,
      anonKey: AppConfig.supabasePublishableKey,
    );
  }
  runApp(const KartKampanyaApp());
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
  Widget build(BuildContext context) {
    if (AppConfig.supabasePublishableKey.isEmpty) {
      return const Scaffold(body: Center(child: Text('Supabase anahtarı yapılandırılmamış.')));
    }
    return StreamBuilder<AuthState>(
      stream: Supabase.instance.client.auth.onAuthStateChange,
      builder: (_, snapshot) {
        final session = Supabase.instance.client.auth.currentSession;
        return session == null ? const LoginPage() : const MainShell();
      },
    );
  }
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
        final r = await auth.signUp(email: email.text.trim(), password: password.text);
        if (r.session == null && mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Kayıt oluşturuldu. E-posta doğrulaması açıksa e-postanı kontrol et.')),
          );
        }
      } else {
        await auth.signInWithPassword(email: email.text.trim(), password: password.text);
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
          constraints: const BoxConstraints(maxWidth: 420),
          child: Column(
            children: [
              const Icon(Icons.credit_card, size: 64),
              const SizedBox(height: 12),
              Text('Kart Kampanya', style: Theme.of(context).textTheme.headlineMedium),
              const SizedBox(height: 24),
              TextField(controller: email, keyboardType: TextInputType.emailAddress,
                decoration: const InputDecoration(labelText: 'E-posta', border: OutlineInputBorder())),
              const SizedBox(height: 12),
              TextField(controller: password, obscureText: true,
                decoration: const InputDecoration(labelText: 'Şifre', border: OutlineInputBorder())),
              if (error != null) Padding(
                padding: const EdgeInsets.only(top: 12),
                child: Text(error!, style: const TextStyle(color: Colors.red)),
              ),
              const SizedBox(height: 16),
              SizedBox(width: double.infinity, child: FilledButton(
                onPressed: busy ? null : submit,
                child: Text(busy ? 'Bekleyin...' : (register ? 'Kayıt Ol' : 'Giriş Yap')),
              )),
              TextButton(
                onPressed: busy ? null : () => setState(() { register = !register; error = null; }),
                child: Text(register ? 'Zaten hesabım var → Giriş Yap' : 'Hesabım yok → Kayıt Ol'),
              ),
            ],
          ),
        ),
      ),
    ),
  );
}

class UserCard {
  final String id, bank, card, network;
  UserCard({required this.id, required this.bank, required this.card, required this.network});
}

class MainShell extends StatefulWidget {
  const MainShell({super.key});
  @override State<MainShell> createState() => _MainShellState();
}
class _MainShellState extends State<MainShell> {
  int index = 0;
  final cards = <UserCard>[];
  @override void initState() { super.initState(); loadCards(); }

  Future<void> loadCards() async {
    final uid = Supabase.instance.client.auth.currentUser!.id;
    final rows = await Supabase.instance.client.from('user_cards')
      .select().eq('user_id', uid).order('created_at');
    if (!mounted) return;
    setState(() {
      cards.clear();
      cards.addAll(List<Map<String,dynamic>>.from(rows).map((m) => UserCard(
        id: m['id'].toString(), bank: m['bank_name'], card: m['card_name'], network: m['network'])));
    });
  }

  Future<void> addCard(UserCard c) async {
    final uid = Supabase.instance.client.auth.currentUser!.id;
    await Supabase.instance.client.from('user_cards').insert({
      'user_id': uid, 'bank_name': c.bank, 'card_name': c.card, 'network': c.network
    });
    await loadCards();
  }

  Future<void> deleteCard(UserCard c) async {
    await Supabase.instance.client.from('user_cards').delete().eq('id', c.id);
    await loadCards();
  }

  @override
  Widget build(BuildContext context) {
    final pages = [
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
          NavigationDestination(icon: Icon(Icons.local_offer_outlined), label: 'Kampanyalar'),
          NavigationDestination(icon: Icon(Icons.credit_card_outlined), label: 'Bendeki Kartlar'),
          NavigationDestination(icon: Icon(Icons.category_outlined), label: 'Kategoriler'),
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
  late Future<List<Map<String,dynamic>>> future;
  @override void initState() { super.initState(); future = fetch(); }
  Future<List<Map<String,dynamic>>> fetch() async {
    final r = await Supabase.instance.client.from('active_campaigns').select().order('end_date');
    return List<Map<String,dynamic>>.from(r);
  }
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(
      title: const Text('Aktif Kampanyalar'),
      actions: [IconButton(
        icon: const Icon(Icons.logout),
        onPressed: () => Supabase.instance.client.auth.signOut(),
      )],
    ),
    body: RefreshIndicator(
      onRefresh: () async => setState(() => future = fetch()),
      child: FutureBuilder<List<Map<String,dynamic>>>(
        future: future,
        builder: (_, s) {
          if (s.connectionState == ConnectionState.waiting) return const Center(child: CircularProgressIndicator());
          if (s.hasError) return Center(child: Text('Hata: ${s.error}'));
          final rows = s.data ?? [];
          if (rows.isEmpty) return const Center(child: Text('Aktif kampanya bulunamadı.'));
          return ListView(
            padding: const EdgeInsets.all(16),
            children: rows.map((c) => Card(child: ListTile(
              leading: const Icon(Icons.local_offer),
              title: Text('${c['title'] ?? ''}'),
              subtitle: Text('${c['merchant'] ?? ''}\nSon: ${c['end_date'] ?? '-'}'),
              isThreeLine: true,
            ))).toList(),
          );
        },
      ),
    ),
  );
}

class MyCardsPage extends StatefulWidget {
  final List<UserCard> cards;
  final Future<void> Function(UserCard) onAdd;
  final Future<void> Function(UserCard) onDelete;
  const MyCardsPage({super.key, required this.cards, required this.onAdd, required this.onDelete});
  @override State<MyCardsPage> createState() => _MyCardsPageState();
}
class _MyCardsPageState extends State<MyCardsPage> {
  final banks = const ['Akbank','Garanti BBVA','Yapı Kredi','İş Bankası','Ziraat Bankası','Halkbank','QNB','DenizBank','TEB','VakıfBank'];
  final cardMap = const {
    'Akbank':['Axess'], 'Garanti BBVA':['Bonus'], 'Yapı Kredi':['World'],
    'İş Bankası':['Maximum'], 'Ziraat Bankası':['Bankkart'], 'Halkbank':['Paraf'],
    'QNB':['CardFinans'], 'DenizBank':['Bonus'], 'TEB':['Bonus'], 'VakıfBank':['World'],
  };
  final networks = const ['Visa','Mastercard','Troy'];

  Future<void> addCard() async {
    String bank = banks.first, card = cardMap[banks.first]!.first, network = networks.first;
    final ok = await showDialog<bool>(context: context, builder: (_) => StatefulBuilder(
      builder: (ctx, setDialog) => AlertDialog(
        title: const Text('Kart Ekle'),
        content: Column(mainAxisSize: MainAxisSize.min, children: [
          DropdownButtonFormField<String>(value: bank, decoration: const InputDecoration(labelText: 'Banka'),
            items: banks.map((b)=>DropdownMenuItem(value:b,child:Text(b))).toList(),
            onChanged: (v){ if(v!=null) setDialog((){bank=v; card=cardMap[bank]!.first;}); }),
          DropdownButtonFormField<String>(value: card, decoration: const InputDecoration(labelText: 'Kart'),
            items: (cardMap[bank]??[]).map((c)=>DropdownMenuItem(value:c,child:Text(c))).toList(),
            onChanged: (v){if(v!=null)setDialog(()=>card=v);}),
          DropdownButtonFormField<String>(value: network, decoration: const InputDecoration(labelText: 'Kart ağı'),
            items: networks.map((n)=>DropdownMenuItem(value:n,child:Text(n))).toList(),
            onChanged: (v){if(v!=null)setDialog(()=>network=v);}),
        ]),
        actions: [
          TextButton(onPressed:()=>Navigator.pop(ctx,false),child:const Text('İptal')),
          FilledButton(onPressed:()=>Navigator.pop(ctx,true),child:const Text('Ekle')),
        ],
      ),
    ));
    if (ok == true) {
      try {
        await widget.onAdd(UserCard(id:'',bank:bank,card:card,network:network));
      } catch(e) {
        if(mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content:Text('Kart eklenemedi: $e')));
      }
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Bendeki Kartlar')),
    floatingActionButton: FloatingActionButton.extended(onPressed:addCard,icon:const Icon(Icons.add),label:const Text('Kart Ekle')),
    body: widget.cards.isEmpty
      ? const Center(child:Text('Henüz kart eklemedin.\n+ Kart Ekle ile başlayabilirsin.',textAlign:TextAlign.center))
      : ListView(padding:const EdgeInsets.all(16),children:widget.cards.map((c)=>Card(child:ListTile(
          leading:const Icon(Icons.credit_card), title:Text('${c.bank} • ${c.card}'),
          subtitle:Text('Kart ağı: ${c.network}'),
          trailing:IconButton(icon:const Icon(Icons.delete_outline),onPressed:()=>widget.onDelete(c)),
        ))).toList()),
  );
}

class CategoriesPage extends StatelessWidget {
  const CategoriesPage({super.key});
  @override Widget build(BuildContext context) => ListView(
    padding: const EdgeInsets.all(18),
    children: const [
      Text('Kategoriler',style:TextStyle(fontSize:30,fontWeight:FontWeight.bold)),
      SizedBox(height:16),
      ListTile(leading:Text('⛽',style:TextStyle(fontSize:24)),title:Text('Akaryakıt')),
      ListTile(leading:Text('🛒',style:TextStyle(fontSize:24)),title:Text('Market')),
      ListTile(leading:Text('🍔',style:TextStyle(fontSize:24)),title:Text('Restoran')),
      ListTile(leading:Text('🛍️',style:TextStyle(fontSize:24)),title:Text('Giyim')),
      ListTile(leading:Text('✈️',style:TextStyle(fontSize:24)),title:Text('Seyahat')),
      ListTile(leading:Text('📱',style:TextStyle(fontSize:24)),title:Text('Elektronik')),
    ],
  );
}
