from pathlib import Path
import re

p = Path('android/app/src/main/AndroidManifest.xml')
s = p.read_text(encoding='utf-8')

# The source owns the UI; this script only prepares Android's OAuth callback.
# Keep it idempotent so every build starts from a deterministic manifest.
activity_re = re.compile(
    r'<activity\b[^>]*android:name=["\'][^"\']*MainActivity["\'][^>]*>.*?</activity>',
    flags=re.IGNORECASE | re.DOTALL,
)
activities = list(activity_re.finditer(s))
if not activities:
    raise SystemExit('generated MainActivity not found')

main = activities[0].group(0)
# Keep exactly one MainActivity declaration.
s = s[:activities[0].start()] + main + s[activities[-1].end():]

# MainActivity must be externally launchable for the Supabase deep link.
if 'android:exported=' in main:
    main = re.sub(r'android:exported=["\'][^"\']*["\']', 'android:exported="true"', main, count=1)
else:
    main = main.replace('<activity ', '<activity android:exported="true" ', 1)

callback = '''
            <intent-filter>
                <action android:name="android.intent.action.VIEW" />
                <category android:name="android.intent.category.DEFAULT" />
                <category android:name="android.intent.category.BROWSABLE" />
                <data android:scheme="io.supabase.flutter" android:host="login-callback" />
            </intent-filter>'''

callback_re = re.compile(
    r'\s*<intent-filter>\s*<action android:name="android.intent.action.VIEW"\s*/>\s*'
    r'<category android:name="android.intent.category.DEFAULT"\s*/>\s*'
    r'<category android:name="android.intent.category.BROWSABLE"\s*/>\s*'
    r'<data android:scheme="io\.supabase\.flutter" android:host="login-callback"\s*/>\s*'
    r'</intent-filter>',
    flags=re.IGNORECASE,
)
main = callback_re.sub('', main)
main = main.replace('</activity>', callback + '\n        </activity>', 1)

s = s[:activities[0].start()] + main + s[activities[0].end():]

permission = '    <uses-permission android:name="android.permission.INTERNET" />\n'
if 'android.permission.INTERNET' not in s:
    s = s.replace('    <application', permission + '    <application', 1)

p.write_text(s, encoding='utf-8')
print('Deterministic Google OAuth Android manifest configured')
