from pathlib import Path
import re

source = '\n'.join(p.read_text(encoding='utf-8') for p in Path('lib').rglob('*.dart'))
manifest = Path('android/app/src/main/AndroidManifest.xml').read_text(encoding='utf-8')
required = {
    'signInWithOAuth':'Supabase Google OAuth call',
    'OAuthProvider.google':'Google provider',
    "redirectTo: 'io.supabase.flutter://login-callback/'":'Android OAuth redirect',
    'authScreenLaunchMode: LaunchMode.externalApplication':'external browser OAuth launch',
    'Google ile Giriş Yap':'Google login button',
    'onAuthStateChange':'auth state listener',
    'currentSession':'session gate',
}
for needle,label in required.items():
    if needle not in source: raise SystemExit(f'OAuth verification failed: missing {label}: {needle}')
if 'io.supabase.flutter' not in manifest: raise SystemExit('OAuth verification failed: callback scheme missing')
if 'android.intent.action.VIEW' not in manifest: raise SystemExit('OAuth verification failed: VIEW intent missing')
if 'android.intent.category.BROWSABLE' not in manifest: raise SystemExit('OAuth verification failed: BROWSABLE category missing')
if not re.search(r'<data[^>]*android:scheme="io\.supabase\.flutter"[^>]*android:host="login-callback"',manifest): raise SystemExit('OAuth verification failed: exact callback missing')
activities=re.findall(r'<activity\\b[^>]*android:name="([^"]+)"',manifest); mains=[a for a in activities if a.endswith('.MainActivity') or a=='MainActivity']
if len(mains)!=1: raise SystemExit(f'OAuth verification failed: expected exactly one MainActivity, found {len(mains)}')
print('OAuth verification passed.')
