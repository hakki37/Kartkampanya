from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

def replace_class(src, name, replacement):
    marker = f'class {name}'
    start = src.find(marker)
    if start < 0:
        raise SystemExit(f'{name} not found')
    brace = src.find('{', start)
    if brace < 0:
        raise SystemExit(f'{name} opening brace not found')
    depth = 0
    in_single = in_double = False
    escape = False
    for i in range(brace, len(src)):
        ch = src[i]
        if escape:
            escape = False
            continue
        if ch == '\\' and (in_single or in_double):
            escape = True
            continue
        if ch == "'" and not in_double:
            in_single = not in_single
            continue
        if ch == '"' and not in_single:
            in_double = not in_double
            continue
        if in_single or in_double:
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return src[:start] + replacement + src[i + 1:]
    raise SystemExit(f'{name} end not found')

login = r'''class LoginPage extends StatefulWidget {
  const LoginPage({super.key});
  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final email = TextEditingController();
  final password = TextEditingController();
  bool register = false;
  bool busy = false;
  bool remember = true;
  bool obscure = true;
  String? error;

  @override
  void dispose() {
    email.dispose();
    password.dispose();
    super.dispose();
  }

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

  Widget field({required Widget icon, required String hint, TextEditingController? controller, bool password = false}) {
    return Container(
      height: 50,
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border.all(color: const Color(0xFFE6E3F5)),
        borderRadius: BorderRadius.circular(14),
      ),
      child: Row(children: [
        const SizedBox(width: 13),
        IconTheme(data: const IconThemeData(color: Color(0xFF7C7A94), size: 18), child: icon),
        const SizedBox(width: 10),
        Expanded(child: TextField(
          controller: controller,
          obscureText: password ? obscure : false,
          keyboardType: password ? TextInputType.text : TextInputType.emailAddress,
          decoration: InputDecoration(hintText: hint, border: InputBorder.none, isDense: true, hintStyle: const TextStyle(fontSize: 13.5, color: Color(0xFF7C7A94))),
        )),
        if (password) IconButton(onPressed: () => setState(() => obscure = !obscure), icon: Icon(obscure ? Icons.visibility_outlined : Icons.visibility_off_outlined, color: const Color(0xFF7C7A94), size: 18)),
        if (password) const SizedBox(width: 3),
      ]),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: Stack(children: [
          Positioned(left: 0, right: 0, bottom: 0, height: 145, child: IgnorePointer(child: CustomPaint(painter: _LoginWavePainter()))),
          SingleChildScrollView(
            padding: const EdgeInsets.fromLTRB(26, 38, 26, 28),
            child: Column(children: [
              Container(width: 64, height: 64, decoration: BoxDecoration(gradient: const LinearGradient(colors: [Color(0xFF8C7CFF), Color(0xFF5A47D6)], begin: Alignment.topLeft, end: Alignment.bottomRight), borderRadius: BorderRadius.circular(18), boxShadow: const [BoxShadow(color: Color(0x385A47D6), blurRadius: 22, offset: Offset(0, 10))]), child: const Icon(Icons.credit_card_rounded, color: Colors.white, size: 30)),
              const SizedBox(height: 13),
              const Text('Kart Kampanya', style: TextStyle(fontSize: 19, fontWeight: FontWeight.w800, color: Color(0xFF1E1B3A))),
              const SizedBox(height: 3),
              const Text('Tek Uygulamada, Tüm Fırsatlar', style: TextStyle(fontSize: 12.5, color: Color(0xFF7C7A94))),
              const SizedBox(height: 22),
              Container(padding: const EdgeInsets.all(4), decoration: BoxDecoration(color: const Color(0xFFEAE8F7), borderRadius: BorderRadius.circular(14)), child: Row(children: [
                Expanded(child: _tab('Giriş Yap', !register, () => setState(() { register = false; error = null; }))),
                Expanded(child: _tab('Kayıt Ol', register, () => setState(() { register = true; error = null; }))),
              ])),
              const SizedBox(height: 20),
              field(icon: const Icon(Icons.mail_outline_rounded), hint: 'E-posta adresi', controller: email),
              const SizedBox(height: 12),
              field(icon: const Icon(Icons.lock_outline_rounded), hint: 'Şifre', controller: password, password: true),
              if (error != null) Padding(padding: const EdgeInsets.only(top: 8), child: Text(error!, textAlign: TextAlign.center, style: const TextStyle(fontSize: 11, color: Color(0xFFEF4444)))),
              const SizedBox(height: 5),
              Row(children: [
                SizedBox(width: 24, height: 24, child: Checkbox(value: remember, onChanged: (v) => setState(() => remember = v ?? true), activeColor: const Color(0xFF6C5CE7), materialTapTargetSize: MaterialTapTargetSize.shrinkWrap)),
                const SizedBox(width: 4),
                const Text('Beni hatırla', style: TextStyle(fontSize: 12, color: Color(0xFF7C7A94))),
                const Spacer(),
                TextButton(onPressed: () {}, style: TextButton.styleFrom(padding: EdgeInsets.zero, minimumSize: Size.zero, tapTargetSize: MaterialTapTargetSize.shrinkWrap), child: const Text('Şifremi Unuttum?', style: TextStyle(fontSize: 12, color: Color(0xFF6C5CE7), fontWeight: FontWeight.w700))),
              ]),
              const SizedBox(height: 12),
              SizedBox(width: double.infinity, height: 50, child: FilledButton(onPressed: busy ? null : submit, style: FilledButton.styleFrom(backgroundColor: const Color(0xFF6C5CE7), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)), elevation: 0), child: Text(busy ? 'Bekleyin...' : (register ? 'Kayıt Ol' : 'Giriş Yap'), style: const TextStyle(fontSize: 14.5, fontWeight: FontWeight.w700)))),
              const SizedBox(height: 16),
              Row(children: [const Expanded(child: Divider(color: Color(0xFFE6E3F5))), const Padding(padding: EdgeInsets.symmetric(horizontal: 10), child: Text('veya', style: TextStyle(fontSize: 12, color: Color(0xFF7C7A94)))), const Expanded(child: Divider(color: Color(0xFFE6E3F5)))]),
              const SizedBox(height: 16),
              SizedBox(width: double.infinity, height: 48, child: OutlinedButton(onPressed: () {}, style: OutlinedButton.styleFrom(side: const BorderSide(color: Color(0xFFE6E3F5)), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16))), child: Row(mainAxisAlignment: MainAxisAlignment.center, children: [Container(width: 19, height: 19, decoration: const BoxDecoration(shape: BoxShape.circle, color: Color(0xFF4285F4)), alignment: Alignment.center, child: const Text('G', style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.w800))), const SizedBox(width: 8), const Text('Google ile Giriş Yap', style: TextStyle(fontSize: 13.5, color: Color(0xFF1E1B3A), fontWeight: FontWeight.w600))])),
              const SizedBox(height: 18),
              const Text('Kampanyaları kaçırma, avantajını yaşa! 🤍', style: TextStyle(fontSize: 11.5, color: Color(0xFF7C7A94))),
              const SizedBox(height: 75),
            ]),
          ),
        ]),
      ),
    );
  }

  Widget _tab(String text, bool selected, VoidCallback onTap) => InkWell(onTap: onTap, borderRadius: BorderRadius.circular(11), child: Container(padding: const EdgeInsets.symmetric(vertical: 10), decoration: BoxDecoration(color: selected ? Colors.white : Colors.transparent, borderRadius: BorderRadius.circular(11), boxShadow: selected ? const [BoxShadow(color: Color(0x14000000), blurRadius: 8, offset: Offset(0, 3))] : null), alignment: Alignment.center, child: Text(text, style: TextStyle(fontSize: 13.5, fontWeight: FontWeight.w600, color: selected ? const Color(0xFF6C5CE7) : const Color(0xFF7C7A94))));
}

class _LoginWavePainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final p1 = Paint()..color = const Color(0xFFEFEBFC);
    final p2 = Paint()..color = const Color(0xFFE3DBFA);
    final a = Path()..moveTo(0, size.height * .5)..cubicTo(size.width * .16, size.height * .22, size.width * .30, size.height * .72, size.width * .5, size.height * .5)..cubicTo(size.width * .70, size.height * .30, size.width * .84, size.height * .72, size.width, size.height * .44)..lineTo(size.width, size.height)..lineTo(0, size.height)..close();
    final b = Path()..moveTo(0, size.height * .63)..cubicTo(size.width * .18, size.height * .42, size.width * .34, size.height * .82, size.width * .53, size.height * .63)..cubicTo(size.width * .74, size.height * .40, size.width * .86, size.height * .78, size.width, size.height * .60)..lineTo(size.width, size.height)..lineTo(0, size.height)..close();
    canvas.drawPath(a, p1);
    canvas.drawPath(b, p2);
  }
  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
'''
s = replace_class(s, 'LoginPage', login)
p.write_text(s, encoding='utf-8')
print('HTML reference login locked')
