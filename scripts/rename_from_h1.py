import os
import re
import sys

DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs")

H1_RE = re.compile(r"^# (?!#)")
FENCE_RE = re.compile(r"^(`{3,}|~{3,})")

INVALID_CHARS_RE = re.compile(r'[\\/:*?"<>|]')


def get_first_h1(text):
    in_code = False
    for line in text.split("\n"):
        if FENCE_RE.match(line):
            in_code = not in_code
        if not in_code and H1_RE.match(line):
            return line[2:].strip()
    return None


def h1_to_filename(h1):
    name = INVALID_CHARS_RE.sub("", h1)
    name = name.strip()
    return name + ".md"


def collect_renames(docs_dir, ignored_dirs=None):
    ignored = {d.lower() for d in (ignored_dirs or [])}
    renames = []
    seen_targets = {}

    for root, dirs, files in os.walk(docs_dir):
        dirs[:] = [d for d in dirs if d.lower() not in ignored]
        for filename in sorted(files):
            if not filename.endswith(".md"):
                continue
            filepath = os.path.join(root, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()

            h1 = get_first_h1(text)
            if h1 is None:
                print(f"skip (no H1): {os.path.relpath(filepath, docs_dir)}")
                continue

            new_name = h1_to_filename(h1)
            new_path = os.path.join(root, new_name)

            if new_name == filename:
                continue

            # Detect conflicts within the same directory
            key = new_path.lower()
            if key in seen_targets:
                if seen_targets[key] is None:
                    # Already marked as conflicted, skip silently
                    continue
                # First conflict: remove the already-queued entry and mark as conflicted
                print(
                    f"conflict: '{new_name}' targeted by both "
                    f"'{os.path.relpath(seen_targets[key], docs_dir)}' and "
                    f"'{os.path.relpath(filepath, docs_dir)}' — skipping both"
                )
                renames[:] = [r for r in renames if r[2].lower() != key]
                seen_targets[key] = None
                continue

            seen_targets[key] = filepath
            renames.append((filepath, filename, new_path, new_name))

    return renames


def process_docs(docs_dir, dry_run=False, ignored_dirs=None):
    renames = collect_renames(docs_dir, ignored_dirs=ignored_dirs)

    if not renames:
        print("Nothing to rename.")
        return

    for src, old_name, dst, new_name in renames:
        rel = os.path.relpath(src, docs_dir)
        if dry_run:
            print(f"[dry-run] {old_name}  →  {new_name}  ({os.path.dirname(rel) or '.'})")
        else:
            os.rename(src, dst)
            print(f"renamed:  {old_name}  →  {new_name}  ({os.path.dirname(rel) or '.'})")

    print(f"\n{'Would rename' if dry_run else 'Renamed'} {len(renames)} file(s).")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    ignored = [
        sys.argv[i + 1]
        for i, a in enumerate(sys.argv)
        if a == "--ignore" and i + 1 < len(sys.argv)
    ]
    process_docs(DOCS_DIR, dry_run=dry_run, ignored_dirs=ignored)