import os

VAULT_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs")
VAULT_ROOT = os.path.normpath(VAULT_ROOT)
OUTPUT_FILE = os.path.join(VAULT_ROOT, "README.md")

EXCLUDED_DIRS = {".obsidian", ".git"}


def stem(filename):
    return os.path.splitext(filename)[0]


def get_relative_path(path):
    return os.path.relpath(path, VAULT_ROOT).replace("\\", "/")


def build_summary():
    lines = []

    lines.append("# Table of Content\n")
    lines.append("\n")

    for entry in sorted(os.listdir(VAULT_ROOT), key=str.lower):
        dir_path = os.path.join(VAULT_ROOT, entry)

        if not os.path.isdir(dir_path):
            continue
        if entry in EXCLUDED_DIRS or entry.startswith("."):
            continue

        lines.append(f"## {entry}\n")

        try:
            files = sorted(os.listdir(dir_path))
        except Exception:
            files = []

        for filename in files:
            if not filename.endswith(".md"):
                continue
            if filename.lower() == "readme.md":
                continue

            filepath = os.path.join(dir_path, filename)
            if not os.path.isfile(filepath):
                continue

            rel_path = get_relative_path(filepath)
            lines.append(f"- [{stem(filename)}]({rel_path})\n")

        lines.append("\n")

    return "".join(lines)


if __name__ == "__main__":
    content = build_summary()
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"README.md generated at {OUTPUT_FILE}")