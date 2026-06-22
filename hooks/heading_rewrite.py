import re


def on_page_markdown(markdown, **kwargs):
    lines = markdown.split('\n')

    # Count H1s outside code fences
    in_code, h1_count = False, 0
    for line in lines:
        if re.match(r'^(`{3,}|~{3,})', line):
            in_code = not in_code
        if not in_code and re.match(r'^# (?!#)', line):
            h1_count += 1

    if h1_count <= 1:
        return markdown

    # Shift every heading after the first H1 down one level
    result = []
    in_code, first_h1_seen = False, False

    for line in lines:
        if re.match(r'^(`{3,}|~{3,})', line):
            in_code = not in_code
            result.append(line)
            continue

        if in_code:
            result.append(line)
            continue

        m = re.match(r'^(#{1,6}) (.+)', line)
        if m:
            level = len(m.group(1))
            if level == 1 and not first_h1_seen:
                first_h1_seen = True
                result.append(line)
            elif first_h1_seen:
                result.append('#' * min(level + 1, 6) + ' ' + m.group(2))
            else:
                result.append(line)
        else:
            result.append(line)

    return '\n'.join(result)
