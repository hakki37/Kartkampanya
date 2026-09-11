import 'package:flutter/material.dart';
import '../services/card_service.dart';
import '../widgets/app_header.dart';
import 'campaigns_screen.dart';

class _CategoryItem { final String label; final IconData icon; final Color color; const _CategoryItem(this.label, this.icon, this.color); }
class CategoriesScreen extends StatelessWidget {
  const CategoriesScreen({super.key});
  static const items = [
    _CategoryItem('Tümü', Icons.grid_view, Color(0xFF6D3DF5)),
    _CategoryItem('Akaryakıt', Icons.local_gas_station_outlined, Color(0xFFD32F2F)),
    _CategoryItem('Otomotiv', Icons.directions_car_outlined, Color(0xFF1565C0)),
    _CategoryItem('Market', Icons.shopping_cart_outlined, Color(0xFF2E7D32)),
    _CategoryItem('Restoran', Icons.restaurant_outlined, Color(0xFFF57C00)),
    _CategoryItem('Giyim', Icons.checkroom_outlined, Color(0xFFAD1457)),
    _CategoryItem('E-ticaret', Icons.shopping_bag_outlined, Color(0xFF00897B)),
    _CategoryItem('Elektronik', Icons.devices_outlined, Color(0xFF37474F)),
    _CategoryItem('Bebek & Çocuk', Icons.child_care_outlined, Color(0xFFE91E63)),
    _CategoryItem('Ev & Yaşam', Icons.chair_outlined, Color(0xFFC62828)),
    _CategoryItem('Hobi', Icons.palette_outlined, Color(0xFF7B1FA2)),
    _CategoryItem('Seyahat', Icons.flight_outlined, Color(0xFF1565C0)),
    _CategoryItem('Eğlence', Icons.movie_outlined, Color(0xFF6A1B9A)),
    _CategoryItem('Sağlık & Kişisel Bakım', Icons.spa_outlined, Color(0xFF43A047)),
    _CategoryItem('Spor', Icons.fitness_center_outlined, Color(0xFF00838F)),
    _CategoryItem('Eğitim', Icons.school_outlined, Color(0xFF3949AB)),
    _CategoryItem('Fatura & Abonelik', Icons.receipt_long_outlined, Color(0xFF00897B)),
    _CategoryItem('Kitap & Kırtasiye', Icons.menu_book_outlined, Color(0xFF5E35B1)),
    _CategoryItem('Hizmet', Icons.handyman_outlined, Color(0xFF546E7A)),
    _CategoryItem('Otomotiv', Icons.directions_car_outlined, Color(0xFF1565C0)),
    _CategoryItem('Finans & Sigorta', Icons.account_balance_outlined, Color(0xFF2E7D32)),
    _CategoryItem('Evcil Hayvan', Icons.pets_outlined, Color(0xFF8D6E63)),
    _CategoryItem('Diğer', Icons.more_horiz, Color(0xFF616161)),
  ];
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: const AppHeader(title: 'Kategoriler'),
    body: GridView.builder(
      padding: const EdgeInsets.all(16),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 3, mainAxisSpacing: 12, crossAxisSpacing: 12, childAspectRatio: .86),
      itemCount: items.length,
      itemBuilder: (_, i) {
        final item = items[i];
        return Material(color: Colors.transparent, child: InkWell(borderRadius: BorderRadius.circular(16), onTap: () {
          Navigator.push(context, MaterialPageRoute(builder: (_) => Scaffold(
            appBar: AppHeader(title: item.label, showBackButton: true),
            body: CampaignsScreen(cards: const <UserCard>[], initialCategory: item.label, showHeader: false),
          )));
        }, child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
          Container(width: 56, height: 56, decoration: BoxDecoration(color: item.color.withOpacity(.12), borderRadius: BorderRadius.circular(16)), child: Icon(item.icon, color: item.color)),
          const SizedBox(height: 8), Text(item.label, textAlign: TextAlign.center, maxLines: 2, style: const TextStyle(fontSize: 11.5, fontWeight: FontWeight.w700)),
        ])));
      },
    ),
  );
}
