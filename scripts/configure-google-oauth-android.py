from pathlib import Path
import re

p = Path('android/app/src/main/AndroidManifest.xml')
s = p.read_text(encoding='utf-8')

scheme = 'io.supabase.flutter'
if scheme not in s:
    oauth_filter = '''
            <intent-filter>
                <action android:name="android.intent.action.VIEW" />
                <category android:name="android.intent.category.DEFAULT" />
                <category android:name="android.intent.category.BROWSABLE" />
                <data android:scheme="io.supabase.flutter" android:host="login-callback" />
            </intent-filter>'''

    # flutter create already provides MainActivity. Add the OAuth intent-filter
    # inside that existing activity instead of creating a second MainActivity.
    activity_match = re.search(
        r'<activity\b[^>]*android:name=["\'](?:\\.|)MainActivity["\'][^>]*>',
        s,
        flags=re.IGNORECASE,
    )
    if activity_match:
        insert_at = activity_match.end()
        s = s[:insert_at] + oauth_filter + s[insert_at:]
    else:
        app_match = re.search(r'<application\b[^>]*>', s, flags=re.IGNORECASE)
        if not app_match:
            raise SystemExit('application tag not found')
        block = '''
        <activity android:name=".MainActivity" android:exported="true">''' + oauth_filter + '''
        </activity>'''
        insert_at = app_match.end()
        s = s[:insert_at] + block + s[insert_at:]

    p.write_text(s, encoding='utf-8')

print('Google OAuth Android callback configured without duplicating MainActivity')
