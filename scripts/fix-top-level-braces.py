from pathlib import Path

p = Path('lib/main.dart')
lines = p.read_text(encoding='utf-8').splitlines(keepends=True)

# Remove only standalone closing braces that occur while already at top level.
# The reference generators have occasionally emitted an extra class-level brace.
out = []
depth = 0
in_single = False
in_double = False
in_triple_single = False
in_triple_double = False
escape = False
line_comment = False
block_comment = False

for line in lines:
    stripped = line.strip()
    if stripped == '}' and depth == 0 and not block_comment and not in_single and not in_double:
        continue

    out.append(line)
    i = 0
    line_comment = False
    while i < len(line):
        ch = line[i]
        nxt = line[i + 1] if i + 1 < len(line) else ''

        if line_comment:
            break
        if block_comment:
            if ch == '*' and nxt == '/':
                block_comment = False
                i += 2
                continue
            i += 1
            continue
        if not (in_single or in_double) and ch == '/' and nxt == '/':
            line_comment = True
            break
        if not (in_single or in_double) and ch == '/' and nxt == '*':
            block_comment = True
            i += 2
            continue
        if not in_double and ch == "'" and not escape:
            in_single = not in_single
        elif not in_single and ch == '"' and not escape:
            in_double = not in_double
        elif not in_single and not in_double:
            if ch == '{':
                depth += 1
            elif ch == '}' and depth > 0:
                depth -= 1
        escape = (ch == '\\' and not escape)
        if ch != '\\':
            escape = False
        i += 1

p.write_text(''.join(out), encoding='utf-8')
print('top-level brace repair applied')
