from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

start = s.find('class MyCardsPage extends StatefulWidget {')
end = s.find('class CatalogLogo extends StatelessWidget {', start)
if start < 0 or end <= start:
    raise SystemExit('MyCardsPage/CatalogLogo boundaries not found')

replacement = r'''class MyCardsPage extends StatefulWidget {
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
  static const banks = <String>[
    'Akbank', 'Garanti BBVA', 'Yapı Kredi', 'İş Bankası', 'Ziraat Bankası',
    'Halkbank', 'QNB', 'DenizBank', 'TEB', 'VakıfBank', 'Kuveyt Türk',
    'Türkiye Finans', 'Albaraka Türk', 'ING', 'Fibabanka', 'HSBC',
    'Anadolubank', 'Odeabank', 'Enpara', 'CEPTETEB', 'Alternatif Bank',
  ];

  static const cardMap = <String, List<String>>{
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

  String bank = banks.first;
  String card = cardMap[banks.first]!.first;
  String network = 'Visa';
  String customerType = 'Bireysel';
  String cardType = 'Kredi';
  bool saving = false;

  Future<void> openAddCard() async {
    var b = bank;
    var c = cardMap[b]!.first;
    var n = network;
    var u = customerType;
    var t = cardType;

    final result = await Navigator.of(context).push<Map<String, String>>(
      MaterialPageRoute(
        builder: (_) => _CardAddPage(
          bank: b,
          card: c,
          network: n,
          customerType: u,
          cardType: t,
        ),
      ),
    );
    if (result == null || !mounted) return;

    b = result['bank']!;
    c = result['card']!;
    n = result['network']!;
    u = result['customerType']!;
    t = result['cardType']!;
    setState(() {
      bank = b;
      card = c;
      network = n;
      customerType = u;
      cardType = t;
      saving = true;
    });
    try {
      await widget.onAdd(UserCard(
        id: '',
        bank: b,
        card: c,
        network: n,
        customerType: u,
        cardType: t,
      ));
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Kart eklendi')),
        );
      }
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

  Widget cardRow(UserCard c) => Container(
        margin: const EdgeInsets.only(bottom: 10),
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(18),
          boxShadow: const [
            BoxShadow(
              color: Color(0x12000000),
              blurRadius: 10,
              offset: Offset(0, 3),
            ),
          ],
        ),
        child: Row(
          children: [
            Container(
              width: 58,
              height: 42,
              decoration: BoxDecoration(
                color: const Color(0xFFF1EDFA),
                borderRadius: BorderRadius.circular(10),
              ),
              alignment: Alignment.center,
              child: CatalogLogo(label: c.bank, big: true),
            ),
            const SizedBox(width: 11),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '${c.bank} • ${c.card}',
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w900,
                      color: Color(0xFF211D2D),
                    ),
                  ),
                  const SizedBox(height: 3),
                  Text(
                    '${c.customerType} • ${c.cardType}',
                    style: const TextStyle(fontSize: 11, color: Color(0xFF777187)),
                  ),
                  Text(
                    c.network,
                    style: const TextStyle(fontSize: 11, color: Color(0xFF777187)),
                  ),
                ],
              ),
            ),
            IconButton(
              onPressed: () => widget.onDelete(c),
              icon: const Icon(Icons.delete_outline_rounded, color: Color(0xFF3D3747)),
            ),
          ],
        ),
      );

  @override
  Widget build(BuildContext context) => Scaffold(
        backgroundColor: const Color(0xFFF8F7FC),
        body: ListView(
          padding: const EdgeInsets.fromLTRB(18, 18, 18, 110),
          children: [
            Row(
              children: [
                const Expanded(
                  child: Text(
                    'Bendeki Kartlar',
                    style: TextStyle(
                      fontSize: 28,
                      fontWeight: FontWeight.w900,
                      color: Color(0xFF211D2D),
                    ),
                  ),
                ),
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: const Color(0xFFE9DEFF),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: IconButton(
                    onPressed: saving ? null : openAddCard,
                    icon: const Icon(Icons.add_rounded, color: Color(0xFF6D3DF5), size: 28),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 15),
            if (widget.cards.isEmpty)
              const Padding(
                padding: EdgeInsets.all(45),
                child: Center(
                  child: Text(
                    'Henüz kart eklemedin.\nKart Ekle ile başlayabilirsin.',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Color(0xFF777187), fontWeight: FontWeight.w700),
                  ),
                ),
              ),
            ...widget.cards.map(cardRow),
            const SizedBox(height: 8),
            SizedBox(
              height: 52,
              child: FilledButton.icon(
                onPressed: saving ? null : openAddCard,
                icon: const Icon(Icons.add_rounded),
                label: Text(
                  saving ? 'Kaydediliyor...' : 'Kart Ekle',
                  style: const TextStyle(fontWeight: FontWeight.w900),
                ),
                style: FilledButton.styleFrom(
                  backgroundColor: const Color(0xFF6D3DF5),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(17)),
                ),
              ),
            ),
          ],
        ),
      );
}

class _CardAddPage extends StatefulWidget {
  final String bank;
  final String card;
  final String network;
  final String customerType;
  final String cardType;

  const _CardAddPage({
    required this.bank,
    required this.card,
    required this.network,
    required this.customerType,
    required this.cardType,
  });

  @override
  State<_CardAddPage> createState() => _CardAddPageState();
}

class _CardAddPageState extends State<_CardAddPage> {
  late String bank = widget.bank;
  late String card = widget.card;
  late String network = widget.network;
  late String customerType = widget.customerType;
  late String cardType = widget.cardType;

  List<String> get cardOptions => _MyCardsPageState.cardMap[bank] ?? const ['Kart'];

  @override
  void initState() {
    super.initState();
    if (!cardOptions.contains(card)) card = cardOptions.first;
  }

  Widget selectField(
    String label,
    String value,
    List<String> items,
    ValueChanged<String> onChanged,
  ) => Padding(
        padding: const EdgeInsets.only(bottom: 13),
        child: DropdownButtonFormField<String>(
          value: value,
          isExpanded: true,
          items: items
              .map((x) => DropdownMenuItem<String>(
                    value: x,
                    child: Text(x, style: const TextStyle(fontWeight: FontWeight.w700)),
                  ))
              .toList(),
          onChanged: (v) {
            if (v != null) onChanged(v);
          },
          decoration: InputDecoration(
            labelText: label,
            filled: true,
            fillColor: Colors.white,
            contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(16),
              borderSide: BorderSide.none,
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(16),
              borderSide: const BorderSide(color: Color(0xFFE4DFEA)),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(16),
              borderSide: const BorderSide(color: Color(0xFF6D3DF5), width: 1.5),
            ),
          ),
        ),
      );

  @override
  Widget build(BuildContext context) => Scaffold(
        backgroundColor: const Color(0xFFF8F7FC),
        appBar: AppBar(
          backgroundColor: const Color(0xFFF8F7FC),
          elevation: 0,
          title: const Text('Kart Ekle', style: TextStyle(fontWeight: FontWeight.w900, color: Color(0xFF211D2D))),
        ),
        body: ListView(
          padding: const EdgeInsets.fromLTRB(18, 8, 18, 30),
          children: [
            const Text(
              'Kart bilgilerini seç',
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: Color(0xFF211D2D)),
            ),
            const SizedBox(height: 6),
            const Text(
              'Her alanı ayrı seç. Banka seçince kart seçenekleri otomatik güncellenir.',
              style: TextStyle(fontSize: 12, color: Color(0xFF777187)),
            ),
            const SizedBox(height: 20),
            selectField('Banka', bank, _MyCardsPageState.banks, (v) {
              setState(() {
                bank = v;
                final options = cardOptions;
                card = options.first;
              });
            }),
            selectField('Kart', card, cardOptions, (v) => setState(() => card = v)),
            selectField('Kart ağı', network, const ['Visa', 'Mastercard', 'Troy'], (v) => setState(() => network = v)),
            selectField('Müşteri tipi', customerType, const ['Bireysel', 'Ticari'], (v) => setState(() => customerType = v)),
            selectField('Kart tipi', cardType, const ['Kredi', 'Banka'], (v) => setState(() => cardType = v)),
            const SizedBox(height: 8),
            SizedBox(
              height: 54,
              child: FilledButton.icon(
                onPressed: () => Navigator.pop(context, {
                  'bank': bank,
                  'card': card,
                  'network': network,
                  'customerType': customerType,
                  'cardType': cardType,
                }),
                icon: const Icon(Icons.check_rounded),
                label: const Text('Kartı Kaydet', style: TextStyle(fontWeight: FontWeight.w900)),
                style: FilledButton.styleFrom(
                  backgroundColor: const Color(0xFF6D3DF5),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(17)),
                ),
              ),
            ),
          ],
        ),
      );
}

'''

s = s[:start] + replacement + s[end:]
p.write_text(s, encoding='utf-8')
print('v19 card selection screen applied')
