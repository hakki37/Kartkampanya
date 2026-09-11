from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

if 'class KartKampanyaApp extends StatelessWidget {' not in s:
    raise SystemExit('KartKampanyaApp not found')
if 'class MainShell extends StatefulWidget {' not in s:
    raise SystemExit('MainShell not found')

# Keep the existing login UI intact, but make the Google action a real,
# deterministic Supabase OAuth flow. All replacements are idempotent.
if 'Future<void> signInWithGoogle() async {' not in s:
    anchor = '  String? error;\n\n  Future<void> submit() async {'
    replacement = '''  String? error;\n  bool googleBusy = false;\n\n  Future<void> signInWithGoogle() async {\n    if (googleBusy) return;\n    setState(() {\n      googleBusy = true;\n      error = null;\n    });\n\n    try {\n      await Supabase.instance.client.auth.signInWithOAuth(\n        OAuthProvider.google,\n        redirectTo: 'io.supabase.flutter://login-callback/',\n        authScreenLaunchMode: LaunchMode.externalApplication,\n      );\n    } catch (e) {\n      if (mounted) {\n        setState(() => error = 'Google ile giriş başlatılamadı: $e');\n      }\n    } finally {\n      if (mounted) {\n        setState(() => googleBusy = false);\n      }\n    }\n  }\n\n  Future<void> submit() async {'''
    if anchor not in s:
        raise SystemExit('Login state anchor not found')
    s = s.replace(anchor, replacement, 1)

if "'Google ile Giriş Yap'" not in s:
    anchor = '''                TextButton(\n                  onPressed: busy\n'''
    button = '''                const SizedBox(height: 10),\n\n                SizedBox(\n                  width: double.infinity,\n                  height: 50,\n                  child: OutlinedButton(\n                    onPressed: busy || googleBusy ? null : signInWithGoogle,\n                    style: OutlinedButton.styleFrom(\n                      backgroundColor: Colors.white,\n                      side: const BorderSide(color: Color(0xFFE1DDEA)),\n                      shape: RoundedRectangleBorder(\n                        borderRadius: BorderRadius.circular(15),\n                      ),\n                    ),\n                    child: Row(\n                      mainAxisAlignment: MainAxisAlignment.center,\n                      children: [\n                        const Text(\n                          'G',\n                          style: TextStyle(\n                            fontSize: 19,\n                            fontWeight: FontWeight.w900,\n                            color: Color(0xFF4285F4),\n                          ),\n                        ),\n                        const SizedBox(width: 8),\n                        Text(\n                          googleBusy ? 'Google açılıyor...' : 'Google ile Giriş Yap',\n                          style: const TextStyle(\n                            fontWeight: FontWeight.w800,\n                            color: Color(0xFF3F394B),\n                          ),\n                        ),\n                      ],\n                    ),\n                  ),\n                ),\n\n                TextButton(\n                  onPressed: busy\n'''
    if anchor not in s:
        raise SystemExit('Google button insertion anchor not found')
    s = s.replace(anchor, button, 1)

if 'void dispose() {' not in s[s.index('class _LoginPageState'):s.index('class MainShell')]:
    anchor = '''\n\n  @override\n  Widget build(BuildContext context) {'''
    replacement = '''\n\n  @override\n  void dispose() {\n    email.dispose();\n    password.dispose();\n    super.dispose();\n  }\n\n  @override\n  Widget build(BuildContext context) {'''
    s = s.replace(anchor, replacement, 1)

p.write_text(s, encoding='utf-8')
print('Google OAuth login implementation locked: Supabase provider, exact redirect URI, external browser launch, and functional button.')
