from pathlib import Path
import re

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
  int tab = 0;
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
      setState(() => tab = 0);
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
        Text(label, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800)),
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
            fillColor: const Color(0xFF0B1B31),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Color(0xFF294263)),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Color(0xFF294263)),
            ),
          ),
        ),
      ],
    );
  }

  Widget choiceRow(List<String> values, String selected, ValueChanged<String> onChanged) {
    return Row(
      children: values.map((x) {
        return Expanded(
          child: Padding(
            padding: const EdgeInsets.only(right: 7),
            child: GestureDetector(
              onTap: () => onChanged(x),
              child: Container(
                height: 50,
                decoration: BoxDecoration(
                  color: selected == x ? const Color(0xFF5B3DF5) : const Color(0xFF0B1B31),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: selected == x ? const Color(0xFF7653FF) : const Color(0xFF294263),
                  ),
                ),
                child: Center(
                  child: x == 'Visa' || x == 'Mastercard' || x == 'Troy'
                      ? CatalogLogo(label: x)
                      : Text(x, style: const TextStyle(fontWeight: FontWeight.w800)),
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
        color: const Color(0xFF0B1B31),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFF294263)),
      ),
      child: Row(
        children: [
          SizedBox(width: 48, child: CatalogLogo(label: x.bank)),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(x.bank, style: const TextStyle(fontWeight: FontWeight.w900)),
                Text(x.card, style: const TextStyle(color: Color(0xFFB7C1D5), fontSize: 12)),
              ],
            ),
          ),
          CatalogLogo(label: x.network),
          IconButton(
            onPressed: () => widget.onDelete(x),
            icon: const Icon(Icons.delete_outline_rounded),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Bendeki Kartlar', style: TextStyle(fontSize: 22, fontWeight: FontWeight.w900)),
        actions: [
          IconButton(
            onPressed: () => setState(() => tab = 1),
            icon: const Icon(Icons.add_circle_outline, size: 25),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(14, 2, 14, 100),
        children: [
          Container(
            decoration: BoxDecoration(
              color: const Color(0xFF0B1B31),
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: const Color(0xFF294263)),
            ),
            child: Row(
              children: [
                Expanded(
                  child: GestureDetector(
                    onTap: () => setState(() => tab = 0),
                    child: Container(
                      padding: const EdgeInsets.symmetric(vertical: 13),
                      decoration: BoxDecoration(
                        color: tab == 0 ? const Color(0xFF5B3DF5) : Colors.transparent,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Center(child: Text('Kartlarım', style: TextStyle(fontWeight: FontWeight.w900))),
                    ),
                  ),
                ),
                Expanded(
                  child: GestureDetector(
                    onTap: () => setState(() => tab = 1),
                    child: Container(
                      padding: const EdgeInsets.symmetric(vertical: 13),
                      decoration: BoxDecoration(
                        color: tab == 1 ? const Color(0xFF5B3DF5) : Colors.transparent,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Center(child: Text('Kart Ekle', style: TextStyle(fontWeight: FontWeight.w900))),
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),
          if (tab == 0 && widget.cards.isEmpty)
            const Padding(
              padding: EdgeInsets.all(35),
              child: Center(child: Text('Henüz kart eklemedin.')),
            ),
          if (tab == 0) ...widget.cards.map(cardRow),
          if (tab == 1) ...[
            dropdownField('Banka', bank, banks, (v) => setState(() => bank = v)),
            const SizedBox(height: 14),
            dropdownField('Kart Programı', program, programs, (v) => setState(() => program = v)),
            const SizedBox(height: 16),
            const Text('Kart Ağı', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800)),
            const SizedBox(height: 8),
            choiceRow(['Visa', 'Mastercard', 'Troy'], network, (v) => setState(() => network = v)),
            const SizedBox(height: 16),
            const Text('Kart Türü', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800)),
            const SizedBox(height: 8),
            choiceRow(['Kredi Kartı', 'Banka Kartı'], cardType, (v) => setState(() => cardType = v)),
            const SizedBox(height: 16),
            const Text('Kullanım', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800)),
            const SizedBox(height: 8),
            choiceRow(['Bireysel', 'Ticari'], usage, (v) => setState(() => usage = v)),
            const SizedBox(height: 24),
            SizedBox(
              height: 52,
              width: double.infinity,
              child: FilledButton(
                onPressed: saving ? null : save,
                child: Text(saving ? 'Kaydediliyor...' : 'Kartı Kaydet'),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
'''
s = s[:ms] + my + s[me:]
p.write_text(s, encoding='utf-8')
print('reference MyCardsPage rebuilt with balanced Dart')
