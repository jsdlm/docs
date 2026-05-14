#!/usr/bin/env python3
"""
Generate OSCP exam notes folder structure for Obsidian.

Usage:
    python generate_oscp_notes.py -n "OSCP_Exam_2026"
    python generate_oscp_notes.py -n "OSCP_Exam_2026" -p "C:/Users/jules/Obsidian"
"""

import argparse
import os
import sys


STANDALONE_MACHINES = ["01_Machine_A", "02_Machine_B", "03_Machine_C"]
AD_MACHINES        = ["01_Machine_A", "02_Machine_B", "03_Machine_C"]

MD_FILES = [
    "01_service_enumeration",
    "02_initial_access",
    "03_privilege_escalation",
    "04_post_exploitation",
]


TEMPLATES = {
    "01_service_enumeration": """\
# TODO Target Name (TODO IP Address)

**Severity:**

## Service Enumeration

### Port Scan Results

```bash
# comma-separated TCP ports
nmap -Pn -n <IP> | grep open | cut -d/ -f1 | sed 'N;s/\\n/, /g'

# comma-separated UDP ports
nmap -sU -Pn -n <IP> | grep open | cut -d/ -f1 | sed 'N;s/\\n/, /g'
```

TODO further enumeration results
""",
    "02_initial_access": """\
## Initial Access

**Vulnerability Explanation:** TODO

**Vulnerability Fix:** TODO

**Steps to reproduce the attack:** TODO

**Proof of Concept Code:** TODO
""",
    "03_privilege_escalation": """\
## Privilege Escalation

**Vulnerability Explanation:** TODO

**Vulnerability Fix:** TODO

**Steps to reproduce the attack:** TODO

**Proof of Concept Code:** TODO
""",
    "04_post_exploitation": """\
## Post-Exploitation

**System Proof Screenshot:** TODO
""",
}


def create_machine_folder(base: str, machine: str) -> None:
    machine_path = os.path.join(base, machine)
    os.makedirs(machine_path, exist_ok=True)
    for name in MD_FILES:
        with open(os.path.join(machine_path, f"{name}.md"), "w", encoding="utf-8") as f:
            f.write(TEMPLATES[name])


def generate(exam_name: str, output_path: str) -> None:
    root = os.path.join(output_path, exam_name)

    if os.path.exists(root):
        print(f"[!] Folder already exists: {root}")
        print("    Choose a different name or remove the existing folder first.")
        sys.exit(1)

    standalone_path = os.path.join(root, "01_Standalone")
    ad_path         = os.path.join(root, "02_Active_Directory")

    os.makedirs(standalone_path, exist_ok=True)
    os.makedirs(ad_path, exist_ok=True)

    for machine in STANDALONE_MACHINES:
        create_machine_folder(standalone_path, machine)

    for machine in AD_MACHINES:
        create_machine_folder(ad_path, machine)

    print(f"[+] Notes generated at: {root}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate OSCP exam notes folder structure for Obsidian."
    )
    parser.add_argument(
        "-n", "--name",
        required=True,
        help='Exam name used as the root folder (e.g. "OSCP_Exam_2026")',
    )
    parser.add_argument(
        "-p", "--path",
        default=None,
        help="Parent directory where the exam folder will be created (default: user Desktop)",
    )
    args = parser.parse_args()

    exam_name = args.name.replace(" ", "_")
    output_path = os.path.expanduser(args.path) if args.path else os.path.join(os.path.expanduser("~"), "Desktop")

    if not os.path.isdir(output_path):
        print(f"[!] Output path does not exist: {output_path}")
        answer = input("Create it? [y/N] ").strip().lower()
        if answer != "y":
            print("Aborted.")
            sys.exit(1)
        os.makedirs(output_path, exist_ok=True)

    generate(exam_name, output_path)


if __name__ == "__main__":
    main()
