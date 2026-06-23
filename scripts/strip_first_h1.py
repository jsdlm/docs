import os
import re
import sys

DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs")

H1_RE = re.compile(r"^# (?!#)")
FENCE_RE = re.compile(r"^(`{3,}|~{3,})")


def strip_first_h1(text):
    lines = text.split("\n")
    in_code = False

    # Condition 1: the first H1 must be at the very top of the file
    # (only blank lines may precede it)
    first_h1_index = None
    for i, line in enumerate(lines):
        if FENCE_RE.match(line):
            in_code = not in_code
        if in_code:
            continue
        if H1_RE.match(line):
            # All lines before this must be blank
            if all(l.strip() == "" for l in lines[:i]):
                first_h1_index = i
            break
        elif line.strip() != "":
            # Non-blank, non-H1 content found before any H1 → do not strip
            break

    if first_h1_index is None:
        return text, False

    # Condition 2: the very next non-blank line after the first H1 must itself be an H1
    next_non_blank = next(
        (line for line in lines[first_h1_index + 1 :] if line.strip() != ""),
        None,
    )
    has_second_h1 = next_non_blank is not None and H1_RE.match(next_non_blank)

    if not has_second_h1:
        return text, False

    result = lines[:first_h1_index]
    rest = lines[first_h1_index + 1 :]

    # Drop the single blank line immediately after the H1
    if rest and rest[0].strip() == "":
        rest = rest[1:]

    result.extend(rest)
    return "\n".join(result), True


def process_docs(docs_dir, dry_run=False):
    modified = 0
    for root, _, files in os.walk(docs_dir):
        for filename in sorted(files):
            if not filename.endswith(".md"):
                continue
            filepath = os.path.join(root, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                original = f.read()

            updated, changed = strip_first_h1(original)
            if not changed:
                continue

            rel = os.path.relpath(filepath, docs_dir)
            if dry_run:
                print(f"[dry-run] {rel}")
            else:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(updated)
                print(f"stripped: {rel}")
            modified += 1

    print(f"\n{'Would modify' if dry_run else 'Modified'} {modified} file(s).")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    process_docs(DOCS_DIR, dry_run=dry_run)
