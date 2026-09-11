from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

start = s.find('class KartKampanyaApp extends StatelessWidget {')
end = s.find('class MainShell extends StatefulWidget {')
if start < 0 or end < 0 or end <= start:
    raise SystemExit('KartKampanyaApp/MainShell boundaries not found')

# Rebuild the complete top-level app/auth/login section in one deterministic
# block. This prevents earlier UI repair passes from leaving LoginPage or its
# State nested inside KartKampanyaApp.
block = r'''class KartKampanyaApp extends StatelessWidget {
  const KartKampanyaApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Kart Kampanya',
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF6D3DF5),
          brightness: Brightness.light,
        ),
        scaffoldBackgroundColor: const Color(0xFFF7F5FC),
        appBarTheme: const AppBarTheme(
          elevation: 0,
          backgroundColor: Color(0xFFF7F5FC),
          foregroundColor: Color(0xFF211B2D),
        ),
        cardTheme: const CardThemeData(
          elevation: 0,
          margin: EdgeInsets.zero,
          surfaceTintColor: Colors.transparent,
        ),
      ),
      home: const AuthGate(),
    );
  }
}

class AuthGate extends StatelessWidget {
  const AuthGate({super.key});

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<AuthState>(
      stream: Supabase.instance.client.auth.onAuthStateChange,
      builder: (_, __) {
        return Supabase.instance.client.auth.currentSession == null
            ? const LoginPage()
            : const MainShell();
      },
    );
  }
}

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final email = TextEditingController();
  final password = TextEditingController();
  bool register = false;
  bool busy = false;
  bool googleBusy = false;
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
      if (mounted) setState(() => error = e.toString());
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  Future<void> signInWithGoogle() async {
    if (googleBusy) return;
    setState(() {
      googleBusy = true;
      error = null;
    });
    try {
      await Supabase.instance.client.auth.signInWithOAuth(
        OAuthProvider.google,
        redirectTo: 'io.supabase.flutter://login-callback/',
        authScreenLaunchMode: LaunchMode.externalApplication,
      );
    } catch (e) {
      if (mounted) {
        setState(() => error = 'Google ile giriş başlatılamadı: $e');
      }
    } finally {
      if (mounted) setState(() => googleBusy = false);
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
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(26, 42, 26, 28),
          child: Column(
            children: [
              Container(
                width: 64,
                height: 64,
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF8C7CFF), Color(0xFF5A47D6)],
                  ),
                  borderRadius: BorderRadius.circular(18),
                ),
                child: const Icon(
                  Icons.credit_card_rounded,
                  color: Colors.white,
                  size: 31,
                ),
              ),
              const SizedBox(height: 14),
              const Text(
                'Kart Kampanya',
                style: TextStyle(
                  fontSize: 19,
                  fontWeight: FontWeight.w800,
                  color: Color(0xFF1E1B3A),
                ),
              ),
              const SizedBox(height: 4),
              const Text(
                'Tek Uygulamada, Tüm Fırsatlar',
                style: TextStyle(fontSize: 12.5, color: Color(0xFF7C7A94)),
              ),
              const SizedBox(height: 22),
              Container(
                padding: const EdgeInsets.all(4),
                decoration: BoxDecoration(
                  color: const Color(0xFFEAE8F7),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Row(
                  children: [
                    Expanded(
                      child: _tab(
                        'Giriş Yap',
                        !register,
                        () => setState(() => register = false),
                      ),
                    ),
                    Expanded(
                      child: _tab(
                        'Kayıt Ol',
                        register,
                        () => setState(() => register = true),
                      ),
                    ),
                  ],
                ),
              ),
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
              Row(
                children: [
                  SizedBox(
                    width: 22,
                    height: 22,
                    child: Checkbox(
                      value: remember,
                      onChanged: (v) =>
                          setState(() => remember = v ?? true),
                      activeColor: const Color(0xFF6C5CE7),
                      visualDensity: VisualDensity.compact,
                    ),
                  ),
                  const SizedBox(width: 5),
                  const Text(
                    'Beni hatırla',
                    style: TextStyle(
                      fontSize: 12,
                      color: Color(0xFF7C7A94),
                    ),
                  ),
                  const Spacer(),
                  TextButton(
                    onPressed: () {},
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
              ),
              const SizedBox(height: 6),
              SizedBox(
                width: double.infinity,
                height: 50,
                child: FilledButton(
                  onPressed: busy || googleBusy ? null : submit,
                  style: FilledButton.styleFrom(
                    backgroundColor: const Color(0xFF6C5CE7),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  child: Text(
                    busy
                        ? 'Bekleyin...'
                        : (register ? 'Kayıt Ol' : 'Giriş Yap'),
                    style: const TextStyle(fontWeight: FontWeight.w800),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              const Row(
                children: [
                  Expanded(child: Divider()),
                  Padding(
                    padding: EdgeInsets.symmetric(horizontal: 10),
                    child: Text(
                      'veya',
                      style: TextStyle(
                        fontSize: 12,
                        color: Color(0xFF7C7A94),
                      ),
                    ),
                  ),
                  Expanded(child: Divider()),
                ],
              ),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                height: 50,
                child: OutlinedButton(
                  onPressed: busy ? null : signInWithGoogle,
                  style: OutlinedButton.styleFrom(
                    side: const BorderSide(color: Color(0xFFE6E3F5)),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Text(
                        'G',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w900,
                          color: Color(0xFF4285F4),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        googleBusy
                            ? 'Google açılıyor...'
                            : 'Google ile Giriş Yap',
                        style: const TextStyle(
                          fontSize: 13.5,
                          fontWeight: FontWeight.w700,
                          color: Color(0xFF1E1B3A),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _tab(String text, bool active, VoidCallback onTap) => InkWell(
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
      );

  Widget _field(
    TextEditingController controller,
    IconData icon,
    String hint, {
    bool obscure = false,
    Widget? suffix,
  }) => Container(
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
          decoration: InputDecoration(
            prefixIcon: Icon(icon, size: 17),
            suffixIcon: suffix,
            hintText: hint,
            border: InputBorder.none,
          ),
        ),
      );
}

'''

s = s[:start] + block + s[end:]

# Hard validation: each authentication class must now be top-level and unique.
for marker in (
    'class KartKampanyaApp extends StatelessWidget {',
    'class AuthGate extends StatelessWidget {',
    'class LoginPage extends StatefulWidget {',
    'class _LoginPageState extends State<LoginPage> {',
    'class MainShell extends StatefulWidget {',
):
    if s.count(marker) != 1:
        raise SystemExit(f'Expected exactly one {marker!r}, found {s.count(marker)}')

p.write_text(s, encoding='utf-8')
print('Deterministic top-level app/auth/login section restored with Google OAuth')
