from pathlib import Path

p = Path('android/app/src/main/AndroidManifest.xml')
s = p.read_text(encoding='utf-8')
marker = '<intent-filter>\n                <action android:name="android.intent.action.MAIN" />'
if 'io.supabase.flutter' not in s:
    block = '''<intent-filter>
                <action android:name="android.intent.action.VIEW" />
                <category android:name="android.intent.category.DEFAULT" />
                <category android:name="android.intent.category.BROWSABLE" />
                <data android:scheme="io.supabase.flutter" android:host="login-callback" />
            </intent-filter>
            '''
    if marker in s:
        s = s.replace(marker, block + marker, 1)
    else:
        app = s.find('<application')
        if app < 0:
            raise SystemExit('application tag not found')
        end = s.find('>', app)
        if end < 0:
            raise SystemExit('application opening tag end not found')
        block = '''\n        <activity android:name=".MainActivity" android:exported="true">\n            <intent-filter>\n                <action android:name="android.intent.action.VIEW" />\n                <category android:name="android.intent.category.DEFAULT" />\n                <category android:name="android.intent.category.BROWSABLE" />\n                <data android:scheme="io.supabase.flutter" android:host="login-callback" />\n            </intent-filter>\n        </activity>'''
        s = s[:end+1] + block + s[end+1:]
    p.write_text(s, encoding='utf-8')
print('Google OAuth Android callback configured')
