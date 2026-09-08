import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:wallpaper_manager_flutter/wallpaper_manager_flutter.dart';

void main() => runApp(const DiniVakitApp());

class DiniVakitApp extends StatelessWidget {
  const DiniVakitApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Dini Vakit',
      theme: ThemeData(useMaterial3: true, colorSchemeSeed: const Color(0xFF176B5B), scaffoldBackgroundColor: const Color(0xFFF5F8F6)),
      home: const HomeShell(),
    );
  }
}

class HomeShell extends StatefulWidget {
  const HomeShell({super.key});
  @override
  State<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends State<HomeShell> {
  int index = 0;
  final favorites = <String>{};

  @override
  void initState() { super.initState(); loadFavorites(); }

  Future<void> loadFavorites() async {
    final p = await SharedPreferences.getInstance();
    if (mounted) setState(() => favorites.addAll(p.getStringList('favorites') ?? []));
  }

  Future<void> toggleFavorite(String url) async {
    final p = await SharedPreferences.getInstance();
    setState(() => favorites.contains(url) ? favorites.remove(url) : favorites.add(url));
    await p.setStringList('favorites', favorites.toList());
  }

  @override
  Widget build(BuildContext context) {
    final pages = [HomePage(favorites: favorites, onFavorite: toggleFavorite), PrayerPage(), FavoritesPage(favorites: favorites, onFavorite: toggleFavorite)];
    return Scaffold(
      body: pages[index],
      bottomNavigationBar: NavigationBar(selectedIndex: index, onDestinationSelected: (v) => setState(() => index = v), destinations: const [
        NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home), label: 'Ana Sayfa'),
        NavigationDestination(icon: Icon(Icons.mosque_outlined), selectedIcon: Icon(Icons.mosque), label: 'Vakitler'),
        NavigationDestination(icon: Icon(Icons.favorite_outline), selectedIcon: Icon(Icons.favorite), label: 'Favoriler'),
      ]),
    );
  }
}

class HomePage extends StatelessWidget {
  final Set<String> favorites;
  final Future<void> Function(String) onFavorite;
  const HomePage({super.key, required this.favorites, required this.onFavorite});

  static const images = [
    'https://images.unsplash.com/photo-1564769625905-50e93615e769?auto=format&fit=crop&w=1200&q=85',
    'https://images.unsplash.com/photo-1519817650390-64a93db51149?auto=format&fit=crop&w=1200&q=85',
    'https://images.unsplash.com/photo-1609599006353-e629aaabfeae?auto=format&fit=crop&w=1200&q=85',
  ];

  @override
  Widget build(BuildContext context) {
    return CustomScrollView(slivers: [
      SliverAppBar.large(title: const Text('Dini Vakit', style: TextStyle(fontWeight: FontWeight.w800)), actions: [IconButton(onPressed: () {}, icon: const Icon(Icons.notifications_none))]),
      SliverToBoxAdapter(child: Padding(padding: const EdgeInsets.fromLTRB(16, 0, 16, 18), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text('Huzura bir adım daha…', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700)),
        const SizedBox(height: 14),
        Container(padding: const EdgeInsets.all(18), decoration: BoxDecoration(borderRadius: BorderRadius.circular(24), gradient: const LinearGradient(begin: Alignment.topLeft, end: Alignment.bottomRight, colors: [Color(0xFF195C50), Color(0xFF2E8772)])), child: const Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Icon(Icons.format_quote, color: Colors.white70, size: 30), SizedBox(height: 6),
          Text('Ameller niyetlere göredir.', style: TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold)),
          SizedBox(height: 8), Text('Buhârî, Bed’ü’l-vahy, 1', style: TextStyle(color: Colors.white70)),
        ])),
        const SizedBox(height: 18),
        const Text('Günün Ayeti', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)), const SizedBox(height: 8),
        Container(padding: const EdgeInsets.all(18), decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(20)), child: const Text('“Kalpler ancak Allah’ı anmakla huzur bulur.”\n\nRa’d Suresi, 28', style: TextStyle(fontSize: 17, height: 1.5, fontWeight: FontWeight.w500))),
        const SizedBox(height: 20),
        const Text('İslami Görseller', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)), const SizedBox(height: 10),
      ])),
      SliverPadding(padding: const EdgeInsets.symmetric(horizontal: 16), sliver: SliverList(delegate: SliverChildBuilderDelegate((context, i) {
        final url = images[i]; final fav = favorites.contains(url);
        return Padding(padding: const EdgeInsets.only(bottom: 16), child: ClipRRect(borderRadius: BorderRadius.circular(24), child: Stack(children: [
          AspectRatio(aspectRatio: 1.65, child: Image.network(url, fit: BoxFit.cover, errorBuilder: (_, __, ___) => Container(color: Colors.grey.shade300))),
          Positioned.fill(child: DecoratedBox(decoration: BoxDecoration(gradient: LinearGradient(begin: Alignment.topCenter, end: Alignment.bottomCenter, colors: [Colors.transparent, Colors.black.withValues(alpha: .72)])))),
          Positioned(left: 16, right: 8, bottom: 10, child: Row(children: [const Expanded(child: Text('Allah’ın zikriyle kalpler huzur bulur.', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16))),
            IconButton(onPressed: () => onFavorite(url), icon: Icon(fav ? Icons.favorite : Icons.favorite_border, color: Colors.white)),
            IconButton(onPressed: () => setWallpaper(context, url), icon: const Icon(Icons.wallpaper, color: Colors.white)),
          ])),
        ])));
      }, childCount: images.length))),
    ]);
  }
}

class FavoritesPage extends StatelessWidget {
  final Set<String> favorites; final Future<void> Function(String) onFavorite;
  const FavoritesPage({super.key, required this.favorites, required this.onFavorite});
  @override
  Widget build(BuildContext context) => Scaffold(appBar: AppBar(title: const Text('Favoriler', style: TextStyle(fontWeight: FontWeight.bold))), body: favorites.isEmpty ? const Center(child: Text('Henüz favori görsel yok.')) : ListView(padding: const EdgeInsets.all(16), children: favorites.map((url) => Padding(padding: const EdgeInsets.only(bottom: 16), child: ClipRRect(borderRadius: BorderRadius.circular(22), child: Stack(children: [AspectRatio(aspectRatio: 1.65, child: Image.network(url, fit: BoxFit.cover)), Positioned(right: 6, bottom: 6, child: Row(children: [IconButton(onPressed: () => onFavorite(url), icon: const Icon(Icons.favorite, color: Colors.white)), IconButton(onPressed: () => setWallpaper(context, url), icon: const Icon(Icons.wallpaper, color: Colors.white))]))]))).toList()));
}

Future<void> setWallpaper(BuildContext context, String url) async {
  try {
    final result = await WallpaperManagerFlutter().setWallpaperFromNetwork(url, WallpaperManagerFlutter.HOME_SCREEN);
    if (context.mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(result ? 'Arka plan ayarlandı.' : 'Arka plan ayarlanamadı.')));
  } catch (e) { if (context.mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Arka plan için izin/uyumluluk sorunu oluştu.'))); }
}

class PrayerPage extends StatefulWidget { const PrayerPage({super.key}); @override State<PrayerPage> createState() => _PrayerPageState(); }
class _PrayerPageState extends State<PrayerPage> {
  String city = 'Istanbul';
  Map<String, dynamic>? timings; bool loading = true;
  @override void initState() { super.initState(); fetch(); }
  Future<void> fetch() async {
    setState(() => loading = true);
    try { final d = DateTime.now(); final u = Uri.parse('https://api.aladhan.com/v1/timingsByCity/${d.day}-${d.month}-${d.year}?city=${Uri.encodeComponent(city)}&country=Turkey&method=13'); final r = await http.get(u); final j = jsonDecode(r.body); if (j['code'] == 200) timings = Map<String,dynamic>.from(j['data']['timings']); }
    catch (_) {} finally { if (mounted) setState(() => loading = false); }
  }
  @override Widget build(BuildContext context) {
    final names = {'Fajr':'İmsak','Sunrise':'Güneş','Dhuhr':'Öğle','Asr':'İkindi','Maghrib':'Akşam','Isha':'Yatsı'};
    return Scaffold(appBar: AppBar(title: const Text('Namaz Vakitleri', style: TextStyle(fontWeight: FontWeight.bold)), actions: [IconButton(onPressed: fetch, icon: const Icon(Icons.refresh))]), body: ListView(padding: const EdgeInsets.all(16), children: [
      Container(padding: const EdgeInsets.all(18), decoration: BoxDecoration(borderRadius: BorderRadius.circular(24), color: const Color(0xFF195C50)), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [const Text('Bugünün Vakitleri', style: TextStyle(color: Colors.white70)), const SizedBox(height: 5), Text(city, style: const TextStyle(color: Colors.white, fontSize: 25, fontWeight: FontWeight.bold)), const SizedBox(height: 12), OutlinedButton.icon(onPressed: () async { final c = await showDialog<String>(context: context, builder: (_) => CityDialog(initial: city)); if (c != null) { setState(() => city = c); fetch(); } }, icon: const Icon(Icons.location_on_outlined, color: Colors.white), label: const Text('Şehri değiştir', style: TextStyle(color: Colors.white))) ])),
      const SizedBox(height: 16),
      if (loading) const Center(child: Padding(padding: EdgeInsets.all(30), child: CircularProgressIndicator())) else ...names.entries.map((e) => Card(child: ListTile(leading: CircleAvatar(child: Icon(e.key == 'Maghrib' ? Icons.nights_stay : Icons.access_time)), title: Text(e.value, style: const TextStyle(fontWeight: FontWeight.w700)), trailing: Text('${timings?[e.key] ?? '--:--'}', style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold))))),
      const SizedBox(height: 12),
      const Card(child: Padding(padding: EdgeInsets.all(16), child: Row(children: [Icon(Icons.volume_up_outlined), SizedBox(width: 12), Expanded(child: Text('Vakit geldiğinde ezan bildirimi ve ezan sesi özelliği için bildirim izni gereklidir.'))])))
    ]));
  }
}

class CityDialog extends StatefulWidget { final String initial; const CityDialog({super.key, required this.initial}); @override State<CityDialog> createState() => _CityDialogState(); }
class _CityDialogState extends State<CityDialog> { late String value; final cities = ['Istanbul','Ankara','Izmir','Bursa','Antalya','Adana','Konya','Samsun','Amasya','Trabzon','Gaziantep','Diyarbakir']; @override void initState(){super.initState();value=widget.initial;} @override Widget build(BuildContext context)=>AlertDialog(title:const Text('Şehir seç'),content:SizedBox(width:300,child:DropdownButtonFormField<String>(initialValue:cities.contains(value)?value:cities.first,items:cities.map((c)=>DropdownMenuItem(value:c,child:Text(c))).toList(),onChanged:(v)=>setState(()=>value=v!))),actions:[TextButton(onPressed:()=>Navigator.pop(context),child:const Text('İptal')),FilledButton(onPressed:()=>Navigator.pop(context,value),child:const Text('Seç'))]); }
