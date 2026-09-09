from pathlib import Path
p=Path('lib/main.dart')
s=p.read_text(encoding='utf-8')
# Final visual lock: force the reference's light purple Material theme.
s=s.replace("brightness: Brightness.dark", "brightness: Brightness.light")
s=s.replace("scaffoldBackgroundColor: const Color(0xFF081120)", "scaffoldBackgroundColor: const Color(0xFFF4F3FB)")
s=s.replace("backgroundColor: const Color(0xFF081120)", "backgroundColor: const Color(0xFFF4F3FB)")
s=s.replace("foregroundColor: Colors.white", "foregroundColor: const Color(0xFF1E1B3A)", 1)
s=s.replace("seedColor: const Color(0xFF5B4BDB)", "seedColor: const Color(0xFF6C5CE7)")
# Keep the existing Supabase/business implementation intact; reference-ui-final handles the screen classes.
print('Reference v40 visual lock applied')
p.write_text(s,encoding='utf-8')
