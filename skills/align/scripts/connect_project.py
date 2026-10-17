#!/usr/bin/env python3
"""Plan or safely connect one canonical instruction file. Python stdlib only."""
import argparse
import json
import os
from pathlib import Path
import sys

FILES = {"codex": "AGENTS.md", "claude-code": "CLAUDE.md"}
BEGIN = "<!-- align:begin -->"
END = "<!-- align:end -->"
TEMPLATE = Path(__file__).resolve().parent.parent / "assets/instruction-block.md"


def connect(project, primary, others=(), apply=False):
    root = Path(project).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Project must be a directory")
    canonical = root / FILES[primary]
    clients = list(dict.fromkeys([primary, *others]))
    conflicts = []
    if (root / "ALIGN.md").exists():
        conflicts.append("Legacy ALIGN.md exists; review and migrate it to ALIGNS.md before updating instructions")
    for name in ("AGENTS.override.md", ".claude/CLAUDE.md"):
        path = root / name
        affected = "codex" if name == "AGENTS.override.md" else "claude-code"
        if affected in clients and os.path.lexists(path):
            conflicts.append(f"Review additional instruction source: {name}")
    if canonical.is_symlink() or (canonical.exists() and not canonical.is_file()):
        conflicts.append(f"Canonical path is not a regular file: {canonical.name}")
        original = None
    else:
        original = canonical.read_bytes() if canonical.exists() else b""
    content = None
    if original is not None:
        try:
            text = original.decode("utf-8")
        except UnicodeDecodeError:
            conflicts.append("Canonical instructions are not UTF-8; preserve and edit manually")
        else:
            newline = "\r\n" if "\r\n" in text else "\n"
            block = TEMPLATE.read_text().strip().replace("\n", newline)
            if BEGIN in text or END in text:
                if text.count(BEGIN) != 1 or text.count(END) != 1 or text.index(BEGIN) > text.index(END):
                    conflicts.append("Malformed or repeated align markers; reconcile manually")
                else:
                    start, end = text.index(BEGIN), text.index(END) + len(END)
                    content = (text[:start] + block + text[end:]).encode("utf-8")
            else:
                separator = "" if not text else (newline if text.endswith("\n") else newline * 2)
                content = (text + separator + block + newline).encode("utf-8")
    links = []
    for client in clients:
        if client == primary:
            continue
        path = root / FILES[client]
        if os.path.lexists(path):
            if path.is_symlink() and os.readlink(path) == canonical.name:
                continue
            conflicts.append(f"Preserve existing {path.name}; review before replacing it")
        else:
            links.append(path)
    plan = {
        "project": str(root), "primary": primary, "canonical": canonical.name,
        "update_canonical": content is not None and content != original,
        "create_links": {path.name: canonical.name for path in links},
        "conflicts": conflicts, "applied": False,
    }
    if apply and not conflicts:
        # Recheck before mutation, and create absent paths exclusively.
        current = canonical.read_bytes() if canonical.is_file() and not canonical.is_symlink() else b""
        if canonical.is_symlink() or current != original:
            raise ValueError("Canonical instructions changed after planning; inspect again")
        created = []
        try:
            for path in links:
                path.symlink_to(canonical.name)
                created.append(path)
            if content != original:
                if canonical.exists():
                    canonical.write_bytes(content)
                else:
                    with canonical.open("xb") as handle:
                        handle.write(content)
        except (OSError, ValueError):
            for path in created:
                if path.is_symlink() and os.readlink(path) == canonical.name:
                    path.unlink()
            raise
        plan["applied"] = True
    return plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True)
    parser.add_argument("--primary", choices=FILES, required=True)
    parser.add_argument("--also", choices=FILES, nargs="*", default=[])
    parser.add_argument("--apply", action="store_true", help="Apply a conflict-free plan")
    args = parser.parse_args()
    try:
        result = connect(args.project, args.primary, args.also, args.apply)
    except (OSError, ValueError) as error:
        print(json.dumps({"error": str(error), "applied": False}))
        return 1
    print(json.dumps(result, indent=2))
    return 2 if result["conflicts"] else 0


if __name__ == "__main__":
    sys.exit(main())
