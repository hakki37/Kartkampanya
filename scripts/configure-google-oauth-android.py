from pathlib import Path
import re

p = Path('android/app/src/main/AndroidManifest.xml')
s = p.read_text(encoding='utf-8')

CALLBACK = '''
            <intent-filter>
                <action android:name="android.intent.action.VIEW" />
                <category android:name="android.intent.category.DEFAULT" />
                <category android:name="android.intent.category.BROWSABLE" />
                <data android:scheme="io.supabase.flutter" android:host="login-callback" />
            </intent-filter>'''

# Flutter creates MainActivity for us. Collapse any duplicate MainActivity
# declarations left by older repair scripts, then keep the callback filter
# inside the one remaining activity.
activity_re = re.compile(
    r'<activity\b[^>]*android:name=["\'][^"\']*MainActivity["\'][^>]*>.*?</activity>',
    flags=re.IGNORECASE | re.DOTALL,
)
activities = list(activity_re.finditer(s))

if not activities:
    raise SystemExit('generated MainActivity not found; refusing to invent an activity')

first = activities[0]
first_block = first.group(0)
if 'io.supabase.flutter' not in first_block:
    first_block = first_block.replace('</activity>', CALLBACK + '\n        </activity>', 1)

parts = []
last = 0
for index, match in enumerate(activities):
    parts.append(s[last:match.start()])
    if index == 0:
        parts.append(first_block)
    last = match.end()
parts.append(s[last:])
s = ''.join(parts)

# Remove any duplicate copies of the exact Supabase callback filter from the
# retained MainActivity. This makes the script idempotent.
main_match = re.search(
    r'<activity\b[^>]*android:name=["\'][^"\']*MainActivity["\'][^>]*>.*?</activity>',
    s,
    flags=re.IGNORECASE | re.DOTALL,
)
if not main_match:
    raise SystemExit('MainActivity disappeared during manifest cleanup')

main_block = main_match.group(0)
callback_re = re.compile(
    r'\s*<intent-filter>\s*<action android:name="android.intent.action.VIEW"\s*/>\s*'
    r'<category android:name="android.intent.category.DEFAULT"\s*/>\s*'
    r'<category android:name="android.intent.category.BROWSABLE"\s*/>\s*'
    r'<data android:scheme="io\.supabase\.flutter" android:host="login-callback"\s*/>\s*'
    r'</intent-filter>',
    flags=re.IGNORECASE,
)
filters = list(callback_re.finditer(main_block))
if len(filters) > 1:
    first_filter = filters[0].group(0)
    main_block = callback_re.sub('', main_block)
    main_block = main_block.replace('</activity>', first_filter + '\n        </activity>', 1)

s = s[:main_match.start()] + main_block + s[main_match.end():]
p.write_text(s, encoding='utf-8')

print('Google OAuth Android callback configured with exactly one MainActivity')
