from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')
ms = s.find('class MyCardsPage extends StatefulWidget')
me = s.find('class CategoriesPage extends StatelessWidget', ms)
if ms < 0 or me <= ms:
    raise SystemExit('MyCardsPage boundaries not found')

my = r'''class MyCardsPage extends StatefulWidget {
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
  State<MyCardsPage> createState() => _MyCardsPageState();
}

class _MyCardsPageState extends State<MyCardsPage> {
  String bank = 'Akbank';
  String program = 'Axess';
  String network = 'Visa';
  String cardType = 'Kredi Kartı';
  String usage = 'Bireysel';
  bool saving = false;

  static const banks = <String>[
    'Akbank', 'Garanti BBVA', 'Yapı Kredi', 'İş Bankası', 'QNB',
    'Ziraat Bankası', 'Halkbank', 'TEB', 'VakıfBank', 'DenizBank',
    'ING', 'HSBC', 'Kuveyt Türk', 'Türkiye Finans', 'Odeabank',
  ];

  static const programs = <String>[
    'Axess', 'Bonus', 'World', 'Maximum', 'Paraf', 'Bankkart',
    'CardFinans', 'Sağlam Kart', 'CEPTETEB',
  ];

  Future<void> save() async {
    setState(() => saving = true);
    try {
      await widget.onAdd(UserCard(
        id: '',
        bank: bank,
        card: program,
        network: network,
        customerType: usage,
        cardType: cardType,
      ));
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Kart eklendi')),
      );
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Kart eklenemedi: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => saving = false);
    }
  }

  Widget dropdownField(
    String label,
    String value,
    List<String> items,
    ValueChanged<String> onChanged,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF29233C))),
        const SizedBox(height: 7),
        DropdownButtonFormField<String>(
          value: value,
          items: items
              .map((x) => DropdownMenuItem<String>(value: x, child: Text(x)))
              .toList(),
          onChanged: (x) {
            if (x != null) onChanged(x);
          },
          decoration: InputDecoration(
            filled: true,
            fillColor: Colors.white,
            contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(14),
              borderSide: const BorderSide(color: Color(0xFFE0DCE9)),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(14),
              borderSide: const BorderSide(color: Color(0xFFE0DCE9)),
            ),
          ),
        ),
      ],
    );
  }

  Widget choiceRow(List<String> values, String selected, ValueChanged<String> onChanged) {
    return Row(
      children: values.map((x) {
        final selectedNow = selected == x;
        return Expanded(
          child: Padding(
            padding: const EdgeInsets.only(right: 7),
            child: GestureDetector(
              onTap: () => onChanged(x),
              child: Container(
                height: 48,
                decoration: BoxDecoration(
                  color: selectedNow ? const Color(0xFFEDE3FF) : Colors.white,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(
                    color: selectedNow ? const Color(0xFF7B45EF) : const Color(0xFFE0DCE9),
                    width: selectedNow ? 1.5 : 1,
                  ),
                ),
                child: Center(
                  child: x == 'Visa' || x == 'Mastercard' || x == 'Troy'
                      ? CatalogLogo(label: x)
                      : Text(x, style: TextStyle(fontWeight: FontWeight.w800, color: selectedNow ? const Color(0xFF5F31C9) : const Color(0xFF393444))),
                ),
              ),
            ),
          ),
        );
      }).toList(),
    );
  }

  Widget cardRow(UserCard x) {
    return Container(
      margin: const EdgeInsets.only(bottom: 9),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE0DCE9)),
      ),
      child: Row(
        children: [
          SizedBox(width: 42, height: 42, child: CatalogLogo(label: x.bank)),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(x.bank, style: const TextStyle(fontWeight: FontWeight.w900, color: Color(0xFF211D2D))),
                Text('${x.card} • ${x.cardType} • ${x.customerType}', style: const TextStyle(color: Color(0xFF777187), fontSize: 11)),
              ],
            ),
          ),
          CatalogLogo(label: x.network),
          IconButton(
            onPressed: () => widget.onDelete(x),
            icon: const Icon(Icons.delete_outline_rounded, color: Color(0xFF777187)),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8F7FC),
      appBar: AppBar(
        title: const Text('Kartlarım', style: TextStyle(fontSize: 22, fontWeight: FontWeight.w900)),
        backgroundColor: const Color(0xFFF8F7FC),
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 4, 16, 100),
        children: [
          if (widget.cards.isNotEmpty) ...[
            ...widget.cards.map(cardRow),
            const SizedBox(height: 10),
          ] else ...[
            Container(
              padding: const EdgeInsets.all(18),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(18),
                border: Border.all(color: const Color(0xFFE0DCE9)),
              ),
              child: const Text('Henüz kart eklemedin. Aşağıdaki alanlardan kartını seçebilirsin.', style: TextStyle(color: Color(0xFF625D6B))),
            ),
            const SizedBox(height: 18),
          ],
          const Text('Kart Ekle', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900, color: Color(0xFF211D2D))),
          const SizedBox(height: 5),
          const Text('Kampanyaları kartlarına göre eşleştirmek için bilgilerini seç.', style: TextStyle(fontSize: 12, color: Color(0xFF777187))),
          const SizedBox(height: 16),
          dropdownField('Banka', bank, banks, (v) => setState(() => bank = v)),
          const SizedBox(height: 14),
          dropdownField('Kart Programı', program, programs, (v) => setState(() => program = v)),
          const SizedBox(height: 16),
          const Text('Kart Ağı', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF29233C))),
          const SizedBox(height: 8),
          choiceRow(['Visa', 'Mastercard', 'Troy'], network, (v) => setState(() => network = v)),
          const SizedBox(height: 16),
          const Text('Kart Türü', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF29233C))),
          const SizedBox(height: 8),
          choiceRow(['Kredi Kartı', 'Banka Kartı'], cardType, (v) => setState(() => cardType = v)),
          const SizedBox(height: 16),
          const Text('Kullanım', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF29233C))),
          const SizedBox(height: 8),
          choiceRow(['Bireysel', 'Ticari'], usage, (v) => setState(() => usage = v)),
          const SizedBox(height: 24),
          SizedBox(
            height: 52,
            width: double.infinity,
            child: FilledButton(
              onPressed: saving ? null : save,
              style: FilledButton.styleFrom(
                backgroundColor: const Color(0xFF6D3DF5),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15)),
              ),
              child: Text(saving ? 'Kaydediliyor...' : 'Kartı Kaydet', style: const TextStyle(fontWeight: FontWeight.w900)),
            ),
          ),
        ],
      ),
    );
  }
}
'''

s = s[:ms] + my + s[me:]
p.write_text(s, encoding='utf-8')
print('MyCardsPage rebuilt without tabs; separate card selectors preserved')
