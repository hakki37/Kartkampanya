from pathlib import Path

main = Path('lib/main.dart')
s = main.read_text(encoding='utf-8')


def block_end(src, start):
    brace = src.find('{', start)
    if brace < 0:
        raise SystemExit('opening brace not found')
    depth = 0
    quote = None
    esc = False
    line_comment = False
    block_comment = False
    i = brace
    while i < len(src):
        ch = src[i]
        nxt = src[i + 1] if i + 1 < len(src) else ''
        if line_comment:
            if ch == '\n':
                line_comment = False
        elif block_comment:
            if ch == '*' and nxt == '/':
                block_comment = False
                i += 1
        elif quote:
            if esc:
                esc = False
            elif ch == '\\':
                esc = True
            elif ch == quote:
                quote = None
        else:
            if ch == '/' and nxt == '/':
                line_comment = True
                i += 1
            elif ch == '/' and nxt == '*':
                block_comment = True
                i += 1
            elif ch in "'\"":
                quote = ch
            elif ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    return i + 1
        i += 1
    raise SystemExit('closing brace not found')


def remove_class(src, name):
    marker = 'class ' + name
    start = src.find(marker)
    if start < 0:
        return src
    end = block_end(src, start)
    return src[:start] + src[end:]


def remove_duplicate_class(src, name):
    marker = 'class ' + name
    first = src.find(marker)
    if first < 0:
        return src
    while True:
        second = src.find(marker, first + 1)
        if second < 0:
            return src
        src = src[:second] + src[block_end(src, second):]

# Remove generated duplicate declarations and the unused legacy summary card.
for name in ('_LoginPageState', '_MainShellState', '_HomeCat'):
    s = remove_duplicate_class(s, name)
s = remove_class(s, '_PlanSummaryCard')

# Keep the campaign merchant local: the card renderer uses it for merchant
# branding/domain resolution. Removing it leaves undefined identifiers.

main.write_text(s, encoding='utf-8')

# The Flutter template test references the old MyApp class and is not part of the app.
test = Path('test/widget_test.dart')
if test.exists():
    test.unlink()

print('v41 analysis cleanup applied')
