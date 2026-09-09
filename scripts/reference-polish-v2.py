from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')


def class_end(src, start):
    brace = src.find('{', start)
    if brace < 0:
        raise SystemExit('class opening brace not found')
    depth = 0
    quote = None
    esc = False
    line_comment = False
    block_comment = False
    i = brace
    while i < len(src):
        ch = src[i]
        nxt = src[i + 1] if i + 1 < len(src) else ''
        if line_comment:
            if ch == '\n': line_comment = False
        elif block_comment:
            if ch == '*' and nxt == '/': block_comment = False; i += 1
        elif quote:
            if esc: esc = False
            elif ch == '\\': esc = True
            elif ch == quote: quote = None
        else:
            if ch == '/' and nxt == '/': line_comment = True; i += 1
            elif ch == '/' and nxt == '*': block_comment = True; i += 1
            elif ch in "'\"": quote = ch
            elif ch == '{': depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0: return i + 1
        i += 1
    raise SystemExit('class closing brace not found')


def replace_class(src, name, replacement):
    start = src.find('class ' + name)
    if start < 0: raise SystemExit(name + ' not found')
    return src[:start] + replacement + src[class_end(src, start):]


login = r'''class LoginPage extends StatefulWidget {
  const LoginPage({super.key});
  @override State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final email = TextEditingController();
  final password = TextEditingController();
  bool register = false;
  bool busy = false;
  String? error;

  Future<void> submit() async {
    setState(() { busy = true; error = null; });
    try {
      final auth = Supabase.instance.client.auth;
      if (register) {
        await auth.signUp(email: email.text.trim(), password: password.text);
      } else {
        await auth.signInWithPassword(email: email.text.trim(), password: password.text);
      }
    } catch (e) {
      if (mounted) setState(() => error = e.toString());
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8F7FC),
      body: SafeArea(
        child: Stack(
          children: [
            Positioned(left: -80, bottom: -80, child: Container(width: 330, height: 220, decoration: BoxDecoration(color: const Color(0xFFE9DFFF), borderRadius: BorderRadius.circular(180)))),
            Positioned(right: -80, bottom: -110, child: Container(width: 330, height: 230, decoration: BoxDecoration(color: const Color(0xFFF0E7FF), borderRadius: BorderRadius.circular(180)))),
            SingleChildScrollView(
              padding: const EdgeInsets.fromLTRB(24, 30, 24, 28),
              child: Column(
                children: [
                  const SizedBox(height: 4),
                  Container(width: 82, height: 82, decoration: BoxDecoration(gradient: const LinearGradient(colors: [Color(0xFF7C3AED), Color(0xFF4C1D95)]), borderRadius: BorderRadius.circular(23), boxShadow: const [BoxShadow(color: Color(0x337C3AED), blurRadius: 18, offset: Offset(0, 8))]), child: const Icon(Icons.credit_card_rounded, color: Colors.white, size: 45)),
                  const SizedBox(height: 15),
                  const Text('Kart Kampanya', style: TextStyle(fontSize: 28, fontWeight: FontWeight.w900, color: Color(0xFF17142A))),
                  const SizedBox(height: 5),
                  const Text('Tek Uygulamada, Tüm Fırsatlar', style: TextStyle(fontSize: 13, color: Color(0xFF777187), fontWeight: FontWeight.w600)),
                  const SizedBox(height: 27),
                  Container(padding: const EdgeInsets.all(4), decoration: BoxDecoration(color: const Color(0xFFEDEAF7), borderRadius: BorderRadius.circular(15)), child: Row(children: [
                    Expanded(child: _tab('Giriş Yap', !register, () => setState(() { register = false; error = null; }))),
                    Expanded(child: _tab('Kayıt Ol', register, () => setState(() { register = true; error = null; }))),
                  ])),
                  const SizedBox(height: 18),
                  TextField(controller: email, keyboardType: TextInputType.emailAddress, decoration: const InputDecoration(prefixIcon: Icon(Icons.mail_outline_rounded), hintText: 'E-posta adresi')),
                  const SizedBox(height: 12),
                  TextField(controller: password, obscureText: true, decoration: const InputDecoration(prefixIcon: Icon(Icons.lock_outline_rounded), hintText: 'Şifre', suffixIcon: Icon(Icons.visibility_outlined))),
                  if (!register) Align(alignment: Alignment.centerRight, child: TextButton(onPressed: () {}, child: const Text('Şifremi Unuttum?', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800)))),
                  if (error != null) Padding(padding: const EdgeInsets.only(bottom: 8), child: Text(error!, textAlign: TextAlign.center, style: const TextStyle(color: Color(0xFFD32F2F), fontSize: 11))),
                  SizedBox(width: double.infinity, height: 52, child: FilledButton(onPressed: busy ? null : submit, style: FilledButton.styleFrom(backgroundColor: const Color(0xFF6D3DF5), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16))), child: Text(busy ? 'Bekleyin...' : (register ? 'Kayıt Ol' : 'Giriş Yap'), style: const TextStyle(fontWeight: FontWeight.w900)))),
                  const SizedBox(height: 14),
                  const Row(children: [Expanded(child: Divider(color: Color(0xFFE1DDEA))), Padding(padding: EdgeInsets.symmetric(horizontal: 12), child: Text('veya', style: TextStyle(color: Color(0xFF8A8495), fontSize: 11))), Expanded(child: Divider(color: Color(0xFFE1DDEA)))]),
                  const SizedBox(height: 12),
                  SizedBox(width: double.infinity, height: 50, child: OutlinedButton(onPressed: () {}, style: OutlinedButton.styleFrom(backgroundColor: Colors.white, side: const BorderSide(color: Color(0xFFE1DDEA)), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15))), child: const Row(mainAxisAlignment: MainAxisAlignment.center, children: [Text('G', style: TextStyle(fontSize: 19, fontWeight: FontWeight.w900)), SizedBox(width: 8), Text('Google ile Giriş Yap', style: TextStyle(fontWeight: FontWeight.w800, color: Color(0xFF3F394B)))]))),
                  const SizedBox(height: 18),
                  TextButton(onPressed: busy ? null : () => setState(() => register = !register), child: Text(register ? 'Zaten hesabım var → Giriş Yap' : 'Hesabım yok → Kayıt Ol', style: const TextStyle(fontWeight: FontWeight.w800))),
                  const SizedBox(height: 22),
                  const Text('Kampanyaları kaçırma, avantajını yaşa!  ♡', style: TextStyle(color: Color(0xFF777187), fontSize: 11, fontWeight: FontWeight.w700)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _tab(String text, bool selected, VoidCallback onTap) => InkWell(onTap: onTap, borderRadius: BorderRadius.circular(12), child: Container(padding: const EdgeInsets.symmetric(vertical: 11), alignment: Alignment.center, decoration: BoxDecoration(color: selected ? Colors.white : Colors.transparent, borderRadius: BorderRadius.circular(12)), child: Text(text, style: TextStyle(color: selected ? const Color(0xFF5B21B6) : const Color(0xFF777187), fontWeight: FontWeight.w900))));
}
'''

mycards = r'''class MyCardsPage extends StatefulWidget {
  final List<UserCard> cards;
  final Future<void> Function(UserCard) onAdd;
  final Future<void> Function(UserCard) onDelete;
  const MyCardsPage({super.key, required this.cards, required this.onAdd, required this.onDelete});
  @override State<MyCardsPage> createState() => _MyCardsPageState();
}

class _MyCardsPageState extends State<MyCardsPage> {
  static const banks = ['Akbank','Garanti BBVA','Yapı Kredi','İş Bankası','QNB','Ziraat Bankası','Halkbank','TEB','VakıfBank','DenizBank','ING','HSBC','Kuveyt Türk','Türkiye Finans','Odeabank'];
  static const programs = ['Axess','Bonus','World','Maximum','Paraf','Bankkart','CardFinans','Sağlam Kart','CEPTETEB'];
  String bank = 'Akbank';
  String program = 'Axess';
  String network = 'Visa';
  String usage = 'Bireysel';
  String cardType = 'Kredi Kartı';
  bool saving = false;

  Future<void> openAddCard() async {
    var b = bank, p = program, n = network, u = usage, t = cardType;
    final result = await showDialog<Map<String,String>>(
      context: context,
      builder: (dialogContext) => StatefulBuilder(
        builder: (dialogContext, setDialogState) => AlertDialog(
          backgroundColor: const Color(0xFFF8F5FC),
          surfaceTintColor: Colors.transparent,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(28)),
          title: const Text('Kart Ekle', style: TextStyle(fontSize: 25, fontWeight: FontWeight.w900, color: Color(0xFF211D2D))),
          content: SingleChildScrollView(child: Column(mainAxisSize: MainAxisSize.min, children: [
            _select('Banka', b, banks, (v) => setDialogState(() => b = v)),
            const SizedBox(height: 10),
            _select('Kart', p, programs, (v) => setDialogState(() => p = v)),
            const SizedBox(height: 10),
            _select('Müşteri tipi', u, const ['Bireysel','Ticari'], (v) => setDialogState(() => u = v)),
            const SizedBox(height: 10),
            _select('Kart tipi', t, const ['Kredi Kartı','Banka Kartı'], (v) => setDialogState(() => t = v)),
            const SizedBox(height: 10),
            _select('Kart ağı', n, const ['Visa','Mastercard','Troy'], (v) => setDialogState(() => n = v)),
          ])),
          actionsPadding: const EdgeInsets.fromLTRB(18, 0, 18, 16),
          actions: [
            TextButton(onPressed: () => Navigator.pop(dialogContext), child: const Text('İptal', style: TextStyle(fontWeight: FontWeight.w900, color: Color(0xFF5B4A78)))),
            FilledButton(onPressed: () => Navigator.pop(dialogContext, {'bank':b,'program':p,'network':n,'usage':u,'type':t}), style: FilledButton.styleFrom(backgroundColor: const Color(0xFF6D3DF5), padding: const EdgeInsets.symmetric(horizontal: 23, vertical: 14), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18))), child: const Text('Ekle', style: TextStyle(fontWeight: FontWeight.w900))),
          ],
        ),
      ),
    );
    if (result == null || !mounted) return;
    bank = result['bank']!; program = result['program']!; network = result['network']!; usage = result['usage']!; cardType = result['type']!;
    setState(() => saving = true);
    try {
      await widget.onAdd(UserCard(id:'', bank:bank, card:program, network:network, customerType:usage, cardType:cardType));
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Kart eklendi')));
    } finally { if (mounted) setState(() => saving = false); }
  }

  Widget _select(String label, String value, List<String> items, ValueChanged<String> onChanged) => DropdownButtonFormField<String>(
    value: value,
    isExpanded: true,
    items: items.map((x) => DropdownMenuItem<String>(value:x, child: Text(x, style: const TextStyle(fontWeight: FontWeight.w700)))).toList(),
    onChanged: (v) { if (v != null) onChanged(v); },
    decoration: InputDecoration(labelText: label, filled:true, fillColor:Colors.white, contentPadding:const EdgeInsets.symmetric(horizontal:16, vertical:14), border:OutlineInputBorder(borderRadius:BorderRadius.circular(16),borderSide:BorderSide.none), enabledBorder:OutlineInputBorder(borderRadius:BorderRadius.circular(16),borderSide:BorderSide(color:Color(0xFFE4DFEA))), focusedBorder:OutlineInputBorder(borderRadius:BorderRadius.circular(16),borderSide:BorderSide(color:Color(0xFF6D3DF5),width:1.5))),
  );

  Widget cardRow(UserCard c) => Container(margin:const EdgeInsets.only(bottom:10),padding:const EdgeInsets.all(13),decoration:BoxDecoration(color:Colors.white,borderRadius:BorderRadius.circular(18),boxShadow:const[BoxShadow(color:Color(0x12000000),blurRadius:10,offset:Offset(0,3))]),child:Row(children:[Container(width:58,height:40,decoration:BoxDecoration(color:const Color(0xFF172033),borderRadius:BorderRadius.circular(9)),alignment:Alignment.center,child:Text(c.bank, maxLines:1,overflow:TextOverflow.ellipsis,style:const TextStyle(color:Colors.white,fontSize:8,fontWeight:FontWeight.w900)),),const SizedBox(width:11),Expanded(child:Column(crossAxisAlignment:CrossAxisAlignment.start,children:[Text('${c.bank} • ${c.card}',style:const TextStyle(fontSize:14,fontWeight:FontWeight.w900,color:Color(0xFF211D2D))),const SizedBox(height:3),Text('${c.customerType} • ${c.cardType}',style:const TextStyle(fontSize:11,color:Color(0xFF777187))),Text('Kart ağı: ${c.network}',style:const TextStyle(fontSize:11,color:Color(0xFF777187)))])),IconButton(onPressed:()=>widget.onDelete(c),icon:const Icon(Icons.delete_outline_rounded,size:27,color:Color(0xFF3D3747))) ]));

  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: const Color(0xFFF8F7FC),
    body: ListView(padding:const EdgeInsets.fromLTRB(18,18,18,110),children:[
      Row(children:[const Expanded(child:Text('Bendeki Kartlar',style:TextStyle(fontSize:28,fontWeight:FontWeight.w900,color:Color(0xFF211D2D)))),Container(width:48,height:48,decoration:BoxDecoration(color:const Color(0xFFE9DEFF),borderRadius:BorderRadius.circular(16)),child:IconButton(onPressed:openAddCard,icon:const Icon(Icons.add_rounded,color:Color(0xFF6D3DF5),size:28)))]),
      const SizedBox(height:15),
      Row(children:[_filter('Tümü (${widget.cards.length})',true),_filter('Kredi Kartı (${widget.cards.where((c)=>c.cardType=="Kredi Kartı").length})',false),_filter('Banka Kartı (${widget.cards.where((c)=>c.cardType=="Banka Kartı").length})',false)]),
      const SizedBox(height:15),
      if (widget.cards.isEmpty) const Padding(padding:EdgeInsets.all(45),child:Center(child:Text('Henüz kart eklemedin.',style:TextStyle(color:Color(0xFF777187),fontWeight:FontWeight.w700)))),
      ...widget.cards.map(cardRow),
      const SizedBox(height:8),
      SizedBox(height:52,child:FilledButton.icon(onPressed:saving?null:openAddCard,icon:const Icon(Icons.add_rounded),label:Text(saving?'Kaydediliyor...':'Kart Ekle',style:const TextStyle(fontWeight:FontWeight.w900)),style:FilledButton.styleFrom(backgroundColor:const Color(0xFFE9DEFF),foregroundColor:const Color(0xFF5B21B6),shape:RoundedRectangleBorder(borderRadius:BorderRadius.circular(17))))),
    ]),
  );

  Widget _filter(String text,bool selected)=>Expanded(child:Container(margin:const EdgeInsets.only(right:6),padding:const EdgeInsets.symmetric(vertical:11),decoration:BoxDecoration(color:selected?const Color(0xFF6D3DF5):const Color(0xFFEDEAF7),borderRadius:BorderRadius.circular(14)),alignment:Alignment.center,child:Text(text,style:TextStyle(fontSize:10,fontWeight:FontWeight.w900,color:selected?Colors.white:const Color(0xFF5B5363)))));
}
'''

s = replace_class(s, 'LoginPage', login)
s = replace_class(s, 'MyCardsPage', mycards)
p.write_text(s, encoding='utf-8')
print('Reference polish v2 applied: login + selectable card dialog + light catalog styling')
