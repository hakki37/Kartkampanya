from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

# v28: modern Kart Kampanya visual system. Keep the existing data/auth/matching logic;
# only replace the global theme so every existing screen moves toward the new reference UI.
old = """      theme: ThemeData(\n        useMaterial3: true,\n        colorScheme: ColorScheme.fromSeed(\n          seedColor: const Color(0xFF5B4BDB),\n          brightness: Brightness.dark,\n        ),\n        scaffoldBackgroundColor: const Color(0xFF081120),\n        appBarTheme: const AppBarTheme(\n          elevation: 0,\n          backgroundColor: const Color(0xFF081120),\n          foregroundColor: Colors.white,\n        ),\n        cardTheme: const CardThemeData(\n          elevation: 0,\n          margin: EdgeInsets.zero,\n          surfaceTintColor: Colors.transparent,\n        ),\n      ),"""
new = """      theme: ThemeData(\n        useMaterial3: true,\n        brightness: Brightness.light,\n        scaffoldBackgroundColor: const Color(0xFFF7F6FC),\n        colorScheme: ColorScheme.fromSeed(\n          seedColor: const Color(0xFF6D3DF5),\n          brightness: Brightness.light,\n          primary: const Color(0xFF6D3DF5),\n          secondary: const Color(0xFF9B6CFF),\n          surface: Colors.white,\n        ),\n        appBarTheme: const AppBarTheme(\n          elevation: 0,\n          scrolledUnderElevation: 0,\n          backgroundColor: Colors.transparent,\n          foregroundColor: Color(0xFF17152B),\n          centerTitle: false,\n        ),\n        inputDecorationTheme: InputDecorationTheme(\n          filled: true,\n          fillColor: Colors.white,\n          border: OutlineInputBorder(\n            borderRadius: BorderRadius.all(Radius.circular(18)),\n            borderSide: BorderSide(color: Color(0xFFE8E4F2)),\n          ),\n          enabledBorder: OutlineInputBorder(\n            borderRadius: BorderRadius.all(Radius.circular(18)),\n            borderSide: BorderSide(color: Color(0xFFE8E4F2)),\n          ),\n          focusedBorder: OutlineInputBorder(\n            borderRadius: BorderRadius.all(Radius.circular(18)),\n            borderSide: BorderSide(color: Color(0xFF6D3DF5), width: 1.5),\n          ),\n          contentPadding: EdgeInsets.symmetric(horizontal: 18, vertical: 16),\n        ),\n        cardTheme: const CardThemeData(\n          elevation: 0,\n          margin: EdgeInsets.zero,\n          color: Colors.white,\n          surfaceTintColor: Colors.transparent,\n          shape: RoundedRectangleBorder(\n            borderRadius: BorderRadius.all(Radius.circular(22)),\n          ),\n        ),\n        navigationBarTheme: NavigationBarThemeData(\n          height: 72,\n          backgroundColor: Colors.white,\n          elevation: 0,\n          indicatorColor: Color(0xFFE9DEFF),\n          labelTextStyle: WidgetStatePropertyAll(\n            TextStyle(fontSize: 11, fontWeight: FontWeight.w700),\n          ),\n        ),\n      ),"""
if old not in s:
    raise SystemExit('v28 theme anchor not found')
s = s.replace(old, new, 1)

# Replace the login page with the same clean purple/white visual language as the reference.
start = s.find('class LoginPage extends StatefulWidget {')
end = s.find('class MainShell extends StatefulWidget {', start)
if start < 0 or end < 0:
    raise SystemExit('login/main shell anchors not found')
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
  void dispose() { email.dispose(); password.dispose(); super.dispose(); }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFFF9F7FF), Color(0xFFEDE5FF)],
          ),
        ),
        child: SafeArea(
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.fromLTRB(24, 30, 24, 24),
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 430),
                child: Column(
                  children: [
                    Container(
                      width: 82, height: 82,
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(colors: [Color(0xFF8B5CF6), Color(0xFF5B21B6)]),
                        borderRadius: BorderRadius.circular(24),
                        boxShadow: const [BoxShadow(color: Color(0x336D3DF5), blurRadius: 22, offset: Offset(0, 10))],
                      ),
                      child: const Icon(Icons.credit_card_rounded, color: Colors.white, size: 44),
                    ),
                    const SizedBox(height: 18),
                    const Text('Kart Kampanya', style: TextStyle(fontSize: 30, fontWeight: FontWeight.w900, color: Color(0xFF17152B))),
                    const SizedBox(height: 5),
                    const Text('Tek Uygulamada, Tüm Fırsatlar', style: TextStyle(color: Color(0xFF77728C), fontWeight: FontWeight.w600)),
                    const SizedBox(height: 28),
                    Container(
                      padding: const EdgeInsets.all(5),
                      decoration: BoxDecoration(color: const Color(0xFFECE7F8), borderRadius: BorderRadius.circular(18)),
                      child: Row(children: [
                        Expanded(child: _modeButton('Giriş Yap', !register)),
                        Expanded(child: _modeButton('Kayıt Ol', register)),
                      ]),
                    ),
                    const SizedBox(height: 18),
                    TextField(controller: email, keyboardType: TextInputType.emailAddress, decoration: const InputDecoration(labelText: 'E-posta adresi', prefixIcon: Icon(Icons.mail_outline_rounded))),
                    const SizedBox(height: 12),
                    TextField(controller: password, obscureText: true, decoration: const InputDecoration(labelText: 'Şifre', prefixIcon: Icon(Icons.lock_outline_rounded))),
                    if (error != null) Padding(padding: const EdgeInsets.only(top: 12), child: Text(error!, style: const TextStyle(color: Color(0xFFD92D20), fontSize: 12))),
                    const SizedBox(height: 18),
                    SizedBox(width: double.infinity, height: 54, child: FilledButton(
                      style: FilledButton.styleFrom(shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18))),
                      onPressed: busy ? null : submit,
                      child: Text(busy ? 'Bekleyin...' : (register ? 'Kayıt Ol' : 'Giriş Yap'), style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800)),
                    )),
                    const SizedBox(height: 14),
                    TextButton(onPressed: busy ? null : () => setState(() { register = !register; error = null; }), child: Text(register ? 'Zaten hesabım var → Giriş Yap' : 'Hesabım yok → Kayıt Ol', style: const TextStyle(fontWeight: FontWeight.w700))),
                    const SizedBox(height: 20),
                    const Text('Güncel kampanyaları keşfet • Kartına uygun fırsatları yakala', textAlign: TextAlign.center, style: TextStyle(color: Color(0xFF77728C), fontSize: 12)),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _modeButton(String text, bool active) => GestureDetector(
    onTap: () => setState(() => register = text == 'Kayıt Ol'),
    child: AnimatedContainer(
      duration: const Duration(milliseconds: 180),
      padding: const EdgeInsets.symmetric(vertical: 12),
      decoration: BoxDecoration(color: active ? Colors.white : Colors.transparent, borderRadius: BorderRadius.circular(14), boxShadow: active ? const [BoxShadow(color: Color(0x12000000), blurRadius: 8)] : null),
      child: Text(text, textAlign: TextAlign.center, style: TextStyle(color: active ? const Color(0xFF5B21B6) : const Color(0xFF77728C), fontWeight: FontWeight.w800)),
    ),
  );
}

'''
s = s[:start] + login + s[end:]

p.write_text(s, encoding='utf-8')
print('v28 modern visual layer applied')
