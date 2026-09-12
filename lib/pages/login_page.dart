import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../services/auth_service.dart';
import '../services/guest_session.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final email = TextEditingController();
  final password = TextEditingController();
  bool register = false, busy = false, googleBusy = false;
  String? error;

  @override
  void dispose() {
    email.dispose();
    password.dispose();
    super.dispose();
  }

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
      if (register) {
        await AuthService.instance.signUp(email.text, password.text);
        if (mounted) setState(() => error = 'Kayıt tamamlandı. E-postanı doğrula, sonra giriş yap.');
      } else {
        await AuthService.instance.signIn(email.text, password.text);
      }
    } on AuthException catch (e) {
      if (mounted) setState(() => error = e.message);
    } catch (e) {
      if (mounted) setState(() => error = 'İşlem başarısız: $e');
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
      await AuthService.instance.signInWithGoogle();
    } on AuthException catch (e) {
      if (mounted) setState(() => error = e.message);
    } catch (e) {
      if (mounted) setState(() => error = 'Google ile giriş başlatılamadı: $e');
    } finally {
      if (mounted) setState(() => googleBusy = false);
    }
  }

  void enterAsGuest() {
    GuestSession.enter();
  }

  @override
  Widget build(BuildContext context) {
    const primary = Color(0xFF6D3DF5);
    return Scaffold(
      body: Container(
        width: double.infinity,
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFF6D3DF5), Color(0xFF8B6AF7)],
          ),
        ),
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.fromLTRB(28, 36, 28, 28),
            child: ConstrainedBox(
              constraints: const BoxConstraints(minHeight: 650),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Container(
                    width: 86,
                    height: 86,
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(.16),
                      borderRadius: BorderRadius.circular(24),
                    ),
                    child: const Icon(Icons.credit_card_rounded, color: Colors.white, size: 42),
                  ),
                  const SizedBox(height: 22),
                  const Text('Kart Kampanya', style: TextStyle(color: Colors.white, fontSize: 28, fontWeight: FontWeight.w900)),
                  const SizedBox(height: 7),
                  const Text('Tüm kart avantajları tek uygulamada', textAlign: TextAlign.center, style: TextStyle(color: Colors.white70, fontSize: 15)),
                  const SizedBox(height: 28),
                  _field(email, 'E-posta', Icons.email_outlined),
                  const SizedBox(height: 10),
                  _field(password, 'Şifre', Icons.lock_outline, obscure: true),
                  if (error != null) ...[
                    const SizedBox(height: 12),
                    Text(error!, textAlign: TextAlign.center, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w700, fontSize: 12)),
                  ],
                  const SizedBox(height: 16),
                  SizedBox(
                    width: double.infinity,
                    height: 52,
                    child: ElevatedButton(
                      onPressed: busy || googleBusy ? null : submit,
                      style: ElevatedButton.styleFrom(backgroundColor: Colors.white, foregroundColor: primary, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15))),
                      child: Text(busy ? 'Bekleyin...' : (register ? 'Kayıt Ol' : 'Giriş Yap'), style: const TextStyle(fontWeight: FontWeight.w900)),
                    ),
                  ),
                  const SizedBox(height: 10),
                  SizedBox(
                    width: double.infinity,
                    height: 52,
                    child: OutlinedButton.icon(
                      onPressed: busy || googleBusy ? null : signInWithGoogle,
                      icon: googleBusy ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)) : const Icon(Icons.g_mobiledata_rounded, color: Colors.white, size: 28),
                      label: Text(googleBusy ? 'Google açılıyor...' : 'Google ile Giriş Yap', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w800)),
                      style: OutlinedButton.styleFrom(side: const BorderSide(color: Colors.white54), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15))),
                    ),
                  ),
                  TextButton(
                    onPressed: busy ? null : () => setState(() {
                      register = !register;
                      error = null;
                    }),
                    child: Text(register ? 'Zaten hesabım var → Giriş Yap' : 'Hesabım yok → Kayıt Ol', style: const TextStyle(color: Colors.white70)),
                  ),
                  const SizedBox(height: 2),
                  SizedBox(
                    width: double.infinity,
                    height: 48,
                    child: TextButton.icon(
                      onPressed: busy || googleBusy ? null : enterAsGuest,
                      icon: const Icon(Icons.visibility_outlined, color: Colors.white70, size: 20),
                      label: const Text('Üye Olmadan Devam Et', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w800)),
                      style: TextButton.styleFrom(
                        side: const BorderSide(color: Colors.white38),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15)),
                      ),
                    ),
                  ),
                  const SizedBox(height: 6),
                  const Text('Ziyaretçi olarak kampanyaları inceleyebilirsin. Kart eklemek için üye olmalısın.', textAlign: TextAlign.center, style: TextStyle(color: Colors.white60, fontSize: 11)),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _field(TextEditingController c, String hint, IconData icon, {bool obscure = false}) => TextField(
        controller: c,
        obscureText: obscure,
        keyboardType: hint == 'E-posta' ? TextInputType.emailAddress : TextInputType.text,
        style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600),
        decoration: InputDecoration(
          hintText: hint,
          hintStyle: const TextStyle(color: Colors.white70),
          prefixIcon: Icon(icon, color: Colors.white70),
          filled: true,
          fillColor: Colors.white12,
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(15), borderSide: BorderSide.none),
        ),
      );
}
