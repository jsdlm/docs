import os
import re

FENCE_RE = re.compile(r'^(`{3,}|~{3,})')
HEADING_RE = re.compile(r'^(#{1,6}) (.+)')


def on_page_markdown(markdown, page, **_kwargs):
    lines = markdown.split('\n')
    result = []
    in_code = False

    for line in lines:
        if FENCE_RE.match(line):
            in_code = not in_code
            result.append(line)
            continue

        if in_code:
            result.append(line)
            continue

        m = HEADING_RE.match(line)
        if m:
            level = len(m.group(1))
            result.append('#' * min(level + 1, 6) + ' ' + m.group(2))
        else:
            result.append(line)

    filename = os.path.splitext(os.path.basename(page.file.src_path))[0]
    return '# ' + filename + '\n\n' + '\n'.join(result)