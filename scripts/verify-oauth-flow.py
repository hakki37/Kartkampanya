from pathlib import Path
import re

main = Path('lib/main.dart').read_text(encoding='utf-8')
manifest = Path('android/app/src/main/AndroidManifest.xml').read_text(encoding='utf-8')

required_main = {
    'signInWithOAuth': 'Supabase Google OAuth call',
    'OAuthProvider.google': 'Google provider',
    "redirectTo: 'io.supabase.flutter://login-callback/'": 'Android OAuth redirect',
    'onAuthStateChange': 'auth state listener',
    'currentSession': 'session gate',
}
for needle, label in required_main.items():
    if needle not in main:
        raise SystemExit(f'OAuth verification failed: missing {label}: {needle}')

if 'io.supabase.flutter' not in manifest:
    raise SystemExit('OAuth verification failed: callback scheme missing from AndroidManifest.xml')

if '<action android:name="android.intent.action.VIEW" />' not in manifest:
    raise SystemExit('OAuth verification failed: VIEW intent missing')

if '<category android:name="android.intent.category.BROWSABLE" />' not in manifest:
    raise SystemExit('OAuth verification failed: BROWSABLE category missing')

activities = re.findall(r'<activity\\b[^>]*android:name="([^"]+)"', manifest)
main_activities = [a for a in activities if a.endswith('.MainActivity') or a == 'MainActivity']
if len(main_activities) != 1:
    raise SystemExit(f'OAuth verification failed: expected exactly one MainActivity, found {len(main_activities)}')

print('OAuth verification passed: Google provider, signInWithOAuth, deep-link callback, and auth-state return are present.')
