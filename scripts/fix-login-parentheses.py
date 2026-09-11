from pathlib import Path

p = Path('lib/main.dart')
if not p.exists():
    raise SystemExit('lib/main.dart not found')

# The reference login generator already emits balanced Dart. Do not mutate
# individual closing parentheses here; that caused the previous build failure.
print('Login parentheses normalization skipped: reference login is syntax-safe')
