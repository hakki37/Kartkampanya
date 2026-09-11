from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')
lines = s.splitlines(keepends=True)
changed = 0
for i, line in enumerate(lines):
    if "TextButton(onPressed: () {}, child: const Text('Şifremi Unuttum?'" in line:
        if line.rstrip().endswith("))),"):
            lines[i] = line.rstrip()[:-1] + "),\n"
            changed += 1
    if "Text(googleBusy ? 'Google açılıyor...' : 'Google ile Giriş Yap'" in line:
        # The nested TextStyle/Text/Row/OutlinedButton/SizedBox expression needs one more close.
        if line.rstrip().endswith("])))),"):
            lines[i] = line.rstrip()[:-1] + "),\n"
            changed += 1
p.write_text(''.join(lines), encoding='utf-8')
print(f'Login parentheses repaired: {changed}')
