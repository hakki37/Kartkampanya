from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

def replace_class(src, name, replacement):
    start = src.find('class ' + name)
    if start < 0:
        raise SystemExit(name + ' not found')
    brace = src.find('{', start)
    depth = 0
    quote = None
    escape = False
    for i in range(brace, len(src)):
        ch = src[i]
        if quote:
            if ch == quote and not escape:
                quote = None
            escape = (ch == '\\' and not escape)
            if ch != '\\':
                escape = False
            continue
        if ch in ("'", '"'):
            quote = ch
        elif ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return src[:start] + replacement + src[i + 1:]
    raise SystemExit(name + ' end not found')

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

  Future<void> submit() async {
    if (email.text.trim().isEmpty || password.text.isEmpty) {
      setState(() => error = 'E-posta ve şifre gerekli.');
      return;
    }
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
      if (mounted) {
        setState(() => error = e.toString());
      }
    } finally {
      if (mounted) {
        setState(() => busy = false);
      }
    }
  }

  @override
  void dispose() {
    email.dispose();
    password.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: Stack(
          children: [
            Positioned.fill(child: CustomPaint(painter: _LoginWavePainter())),
            SingleChildScrollView(
              padding: const EdgeInsets.fromLTRB(26, 44, 26, 28),
              child: Column(
                children: [
                  _logo(),
                  const SizedBox(height: 14),
                  const Text(
                    'Kart Kampanya',
                    style: TextStyle(
                      fontSize: 19,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF1E1B3A),
                    ),
                  ),
                  const SizedBox(height: 3),
                  const Text(
                    'Tek Uygulamada, Tüm Fırsatlar',
                    style: TextStyle(
                      fontSize: 12.5,
                      color: Color(0xFF7C7A94),
                    ),
                  ),
                  const SizedBox(height: 22),
                  _tabs(),
                  const SizedBox(height: 20),
                  _field(email, Icons.mail_outline_rounded, 'E-posta adresi'),
                  const SizedBox(height: 12),
                  _field(
                    password,
                    Icons.lock_outline_rounded,
                    'Şifre',
                    obscure: obscure,
                    suffix: IconButton(
                      onPressed: () => setState(() => obscure = !obscure),
                      icon: Icon(
                        obscure
                            ? Icons.visibility_outlined
                            : Icons.visibility_off_outlined,
                        size: 17,
                        color: const Color(0xFF7C7A94),
                      ),
                    ),
                  ),
                  if (error != null) ...[
                    const SizedBox(height: 8),
                    Align(
                      alignment: Alignment.centerLeft,
                      child: Text(
                        error!,
                        style: const TextStyle(
                          fontSize: 11,
                          color: Color(0xFFEF4444),
                        ),
                      ),
                    ),
                  ],
                  const SizedBox(height: 10),
                  _options(),
                  const SizedBox(height: 6),
                  SizedBox(
                    width: double.infinity,
                    height: 50,
                    child: FilledButton(
                      onPressed: busy ? null : submit,
                      style: FilledButton.styleFrom(
                        backgroundColor: const Color(0xFF6C5CE7),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(16),
                        ),
                      ),
                      child: Text(
                        busy ? 'Bekleyin...' : (register ? 'Kayıt Ol' : 'Giriş Yap'),
                        style: const TextStyle(
                          fontSize: 14.5,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  _divider(),
                  const SizedBox(height: 16),
                  SizedBox(
                    width: double.infinity,
                    height: 50,
                    child: OutlinedButton(
                      onPressed: () {},
                      style: OutlinedButton.styleFrom(
                        side: const BorderSide(color: Color(0xFFE6E3F5)),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(16),
                        ),
                      ),
                      child: const Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            'G',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w900,
                              color: Color(0xFF4285F4),
                            ),
                          ),
                          SizedBox(width: 8),
                          Text(
                            'Google ile Giriş Yap',
                            style: TextStyle(
                              fontSize: 13.5,
                              fontWeight: FontWeight.w700,
                              color: Color(0xFF1E1B3A),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 18),
                  const Text(
                    'Kampanyaları kaçırma, avantajını yaşa! 🤍',
                    style: TextStyle(
                      fontSize: 11.5,
                      color: Color(0xFF7C7A94),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _logo() {
    return Container(
      width: 64,
      height: 64,
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF8C7CFF), Color(0xFF5A47D6)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(18),
      ),
      child: const Icon(
        Icons.credit_card_rounded,
        color: Colors.white,
        size: 31,
      ),
    );
  }

  Widget _tabs() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        color: const Color(0xFFEAE8F7),
        borderRadius: BorderRadius.circular(14),
      ),
      child: Row(
        children: [
          _tab('Giriş Yap', !register, () => setState(() => register = false)),
          _tab('Kayıt Ol', register, () => setState(() => register = true)),
        ],
      ),
    );
  }

  Widget _tab(String text, bool active, VoidCallback onTap) {
    return Expanded(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(11),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 10),
          decoration: BoxDecoration(
            color: active ? Colors.white : Colors.transparent,
            borderRadius: BorderRadius.circular(11),
          ),
          alignment: Alignment.center,
          child: Text(
            text,
            style: TextStyle(
              fontSize: 13.5,
              fontWeight: FontWeight.w700,
              color: active
                  ? const Color(0xFF6C5CE7)
                  : const Color(0xFF7C7A94),
            ),
          ),
        ),
      ),
    );
  }

  Widget _field(
    TextEditingController controller,
    IconData icon,
    String hint, {
    bool obscure = false,
    Widget? suffix,
  }) {
    return Container(
      height: 49,
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border.all(color: const Color(0xFFE6E3F5)),
        borderRadius: BorderRadius.circular(14),
      ),
      child: TextField(
        controller: controller,
        obscureText: obscure,
        keyboardType: hint.startsWith('E-posta')
            ? TextInputType.emailAddress
            : TextInputType.text,
        style: const TextStyle(
          fontSize: 13.5,
          color: Color(0xFF1E1B3A),
        ),
        decoration: InputDecoration(
          prefixIcon: Icon(icon, size: 17, color: const Color(0xFF7C7A94)),
          suffixIcon: suffix,
          hintText: hint,
          hintStyle: const TextStyle(
            fontSize: 13.5,
            color: Color(0xFFAAA7B8),
          ),
          border: InputBorder.none,
          contentPadding: const EdgeInsets.symmetric(
            vertical: 14,
            horizontal: 14,
          ),
        ),
      ),
    );
  }

  Widget _options() {
    return Row(
      children: [
        SizedBox(
          width: 22,
          height: 22,
          child: Checkbox(
            value: remember,
            onChanged: (v) => setState(() => remember = v ?? true),
            activeColor: const Color(0xFF6C5CE7),
            visualDensity: VisualDensity.compact,
          ),
        ),
        const SizedBox(width: 5),
        const Text(
          'Beni hatırla',
          style: TextStyle(fontSize: 12, color: Color(0xFF7C7A94)),
        ),
        const Spacer(),
        TextButton(
          onPressed: () {},
          style: TextButton.styleFrom(
            padding: EdgeInsets.zero,
            minimumSize: Size.zero,
          ),
          child: const Text(
            'Şifremi Unuttum?',
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w700,
              color: Color(0xFF6C5CE7),
            ),
          ),
        ),
      ],
    );
  }

  Widget _divider() {
    return Row(
      children: [
        const Expanded(child: Divider(color: Color(0xFFE6E3F5))),
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 10),
          child: Text(
            'veya',
            style: TextStyle(fontSize: 12, color: Color(0xFF7C7A94)),
          ),
        ),
        const Expanded(child: Divider(color: Color(0xFFE6E3F5))),
      ],
    );
  }
}

class _LoginWavePainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final p1 = Paint()..color = const Color(0xFFEFEBFC);
    final p2 = Paint()..color = const Color(0xFFE3DBFA);
    final h = size.height;
    final path1 = Path()
      ..moveTo(0, h - 105)
      ..cubicTo(size.width * .16, h - 145, size.width * .29, h - 75, size.width * .50, h - 105)
      ..cubicTo(size.width * .71, h - 135, size.width * .84, h - 75, size.width, h - 115)
      ..lineTo(size.width, h)
      ..lineTo(0, h)
      ..close();
    final path2 = Path()
      ..moveTo(0, h - 85)
      ..cubicTo(size.width * .18, h - 115, size.width * .34, h - 55, size.width * .53, h - 85)
      ..cubicTo(size.width * .74, h - 120, size.width * .87, h - 65, size.width, h - 90)
      ..lineTo(size.width, h)
      ..lineTo(0, h)
      ..close();
    canvas.drawPath(path1, p1);
    canvas.drawPath(path2, p2);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
'''

s = replace_class(s, 'LoginPage', login)
p.write_text(s, encoding='utf-8')
print('parser-safe reference login locked')
