from pathlib import Path
import re

p = Path('android/app/src/main/AndroidManifest.xml')
s = p.read_text(encoding='utf-8')

scheme = 'io.supabase.flutter'
if scheme not in s:
    oauth_filter = '''\n            <intent-filter>\n                <action android:name="android.intent.action.VIEW" />\n                <category android:name="android.intent.category.DEFAULT" />\n                <category android:name="android.intent.category.BROWSABLE" />\n                <data android:scheme="io.supabase.flutter" android:host="login-callback" />\n            </intent-filter>'''

    # flutter create already creates MainActivity. Find that exact existing
    # activity and put the Supabase callback filter inside it.
    activity_match = re.search(
        r'<activity\\b[^>]*android:name=["\'](?:\\.MainActivity|com\\.example\\.[^"\']*MainActivity)["\'][^>]*>',
        s,
        flags=re.IGNORECASE,
    )
    if not activity_match:
        activity_match = re.search(
            r'<activity\\b[^>]*android:name=["\'][^"\']*MainActivity["\'][^>]*>',
            s,
            flags=re.IGNORECASE,
        )

    if not activity_match:
        raise SystemExit('generated MainActivity not found; refusing to create a duplicate')

    insert_at = activity_match.end()
    s = s[:insert_at] + oauth_filter + s[insert_at:]
    p.write_text(s, encoding='utf-8')

print('Google OAuth Android callback configured inside existing MainActivity')
