import os
import re

VAULT_ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(VAULT_ROOT, "README.md")

EXCLUDED_DIRS = {".obsidian", ".git"}


def get_first_h1(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("# "):
                    return line[2:].strip()
    except Exception:
        pass
    return None


def get_relative_path(path):
    return os.path.relpath(path, VAULT_ROOT).replace("\\", "/")


def build_summary():
    lines = []

    # Titre principal depuis le README.md racine
    root_readme = os.path.join(VAULT_ROOT, "README.md")
    vault_title = get_first_h1(root_readme) or "Vault"

    lines.append(f"# {vault_title}\n")
    lines.append("---\n")

    # Parcours des dossiers de premier niveau
    entries = sorted(os.listdir(VAULT_ROOT))

    for entry in entries:
        dir_path = os.path.join(VAULT_ROOT, entry)

        if not os.path.isdir(dir_path):
            continue
        if entry in EXCLUDED_DIRS or entry.startswith("."):
            continue

        # Titre de la section = H1 du README.md du dossier
        dir_readme = os.path.join(dir_path, "README.md")
        if os.path.exists(dir_readme):
            section_title = get_first_h1(dir_readme) or entry
            rel_readme = get_relative_path(dir_readme)
            lines.append(f"## [{section_title}]({rel_readme})\n")
        else:
            lines.append(f"## {entry}\n")

        # Fichiers .md dans le dossier (hors README.md)
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

            file_title = get_first_h1(filepath) or filename.replace(".md", "")
            rel_path = get_relative_path(filepath)
            lines.append(f"- [{file_title}]({rel_path})\n")

        lines.append("\n")

    return "".join(lines)


if __name__ == "__main__":
    content = build_summary()
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"README.md generated at {OUTPUT_FILE}")
