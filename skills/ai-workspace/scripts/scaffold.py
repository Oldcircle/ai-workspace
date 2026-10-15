#!/usr/bin/env python3
"""ai-workspace scaffold: create a workspace or project skeleton from the bundled templates.

It never overwrites or deletes anything. Existing files are reported as skipped.

Usage:
    python3 scaffold.py init ROOT [--lang zh|en] [--name NAME] [--layout dev|minimal]
                                  [--gemini] [--no-symlink] [--dry-run]
    python3 scaffold.py project PATH [--lang zh|en] [--name NAME] [--root ROOT]
                                  [--gemini] [--no-symlink] [--dry-run]

Exit codes: 0 = done, 2 = bad usage, 3 = refused (would need adopt, not init).
"""
from __future__ import annotations

import argparse
import datetime
import os
import sys
from pathlib import Path

VERSION = "0.1.0"
TEMPLATES = Path(__file__).resolve().parent.parent / "templates"
LAYOUTS = {
    "dev": ["projects", "forks", "vendor", "notes", "memory", "_archive"],
    "minimal": ["projects", "notes", "memory", "_archive"],
}
INSTRUCTION_FILES = ("AGENTS.md", "CLAUDE.md", "GEMINI.md")


class Plan:
    def __init__(self, dry_run: bool, no_symlink: bool):
        self.dry_run = dry_run
        self.no_symlink = no_symlink
        self.log = []

    def mkdir(self, path: Path):
        if path.is_dir():
            return
        self.log.append(("mkdir", path))
        if not self.dry_run:
            path.mkdir(parents=True, exist_ok=True)

    def write(self, path: Path, text: str):
        if path.exists() or path.is_symlink():
            self.log.append(("skip", path))
            return False
        self.log.append(("create", path))
        if not self.dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(text)
        return True

    def link(self, folder: Path, name: str, target: str, stub: str):
        """Make folder/name point at folder/target: a symlink, or an import stub if symlinks fail."""
        path = folder / name
        if path.exists() or path.is_symlink():
            self.log.append(("skip", path))
            return
        if not self.no_symlink:
            if self.dry_run:
                self.log.append(("link", path, target))
                return
            try:
                os.symlink(target, path)
                self.log.append(("link", path, target))
                return
            except (OSError, NotImplementedError, AttributeError):
                pass
        if stub is None:
            self.log.append(("manual", path, target))
            return
        self.log.append(("stub", path, target))
        if not self.dry_run:
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(stub + "\n")

    def report(self, base: Path):
        for entry in self.log:
            kind, path = entry[0], entry[1]
            try:
                shown = os.path.relpath(path, base)
            except ValueError:
                shown = str(path)
            if kind == "link":
                print(f"  link    {shown} -> {entry[2]}")
            elif kind == "stub":
                print(f"  import  {shown} (one line: @{entry[2]}; symlinks unavailable)")
            elif kind == "manual":
                print(f"  manual  {shown}: symlinks unavailable. Rename {entry[2]} to AGENTS.md, then "
                      f"run this again so {entry[2]} becomes a one-line import")
            elif kind == "skip":
                print(f"  skip    {shown} (already exists)")
            else:
                print(f"  {kind:<7} {shown}")
        if self.dry_run:
            print("(dry run: nothing written)")


def render(lang: str, name: str, values: dict) -> str:
    path = TEMPLATES / lang / name
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def link_instruction_files(plan: Plan, folder: Path, gemini: bool):
    """Point CLAUDE.md (and GEMINI.md) at the folder's real instruction file."""
    agents, claude = folder / "AGENTS.md", folder / "CLAUDE.md"
    if claude.exists() and not claude.is_symlink() and not agents.exists():
        # Keep the user's direction: CLAUDE.md is the real file.
        plan.link(folder, "AGENTS.md", "CLAUDE.md", None)  # AGENTS.md has no import syntax
        real = "CLAUDE.md"
    else:
        plan.link(folder, "CLAUDE.md", "AGENTS.md", "@AGENTS.md")
        real = "AGENTS.md"
    if gemini:
        plan.link(folder, "GEMINI.md", real, "@./" + real)


def cmd_init(args) -> int:
    root = Path(args.root).expanduser().absolute()
    lang = args.lang
    name = args.name or root.name
    plan = Plan(args.dry_run, args.no_symlink)
    agents, claude = root / "AGENTS.md", root / "CLAUDE.md"
    has_real_rules = any(
        (root / n).exists() and not (root / n).is_symlink() for n in ("AGENTS.md", "CLAUDE.md"))
    if has_real_rules:
        print(f"{root} already has root rules ({'AGENTS.md' if agents.exists() else 'CLAUDE.md'}).")
        print("This is an existing workspace: use the adopt steps in the ai-workspace skill instead of init.")
        return 3
    plan.mkdir(root)
    for d in LAYOUTS[args.layout]:
        plan.mkdir(root / d)
    text = render(lang, "workspace-root.md", {"WORKSPACE_NAME": name})
    if args.layout == "minimal":
        text = "\n".join(l for l in text.splitlines() if "`forks/`" not in l and "`vendor/`" not in l) + "\n"
    plan.write(agents, text)
    link_instruction_files(plan, root, args.gemini)
    plan.write(root / "memory" / "MEMORY.md", render(lang, "MEMORY.md", {}))
    plan.write(root / "notes" / "_index.md", render(lang, "notes-index.md", {}))
    print(f"workspace: {root}")
    plan.report(root)
    return 0


def find_workspace_root(start: Path):
    for parent in [start.parent] + list(start.parent.parents):
        if (parent / "memory" / "MEMORY.md").exists() and any(
                (parent / n).exists() for n in INSTRUCTION_FILES):
            return parent
    return None


def cmd_project(args) -> int:
    path = Path(args.path).expanduser().absolute()
    lang = args.lang
    name = args.name or path.name
    root = Path(args.root).expanduser().absolute() if args.root else find_workspace_root(path)
    rel = os.path.relpath(root, path).replace(os.sep, "/") if root else ".."
    today = datetime.date.today().isoformat()
    values = {"PROJECT_NAME": name, "WORKSPACE_REL": rel, "DATE": today}
    plan = Plan(args.dry_run, args.no_symlink)
    plan.mkdir(path)
    claude = path / "CLAUDE.md"
    if not (claude.exists() and not claude.is_symlink()):
        plan.write(path / "AGENTS.md", render(lang, "project.md", values))
    link_instruction_files(plan, path, args.gemini)
    plan.write(path / "PLAN.md", render(lang, "PLAN.md", values))
    plan.write(path / "STATUS.md", render(lang, "STATUS.md", values))
    print(f"project: {path}")
    if root is None:
        print("  note    no workspace root found above; the pointer line uses '..'")
    plan.report(path)
    return 0


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    ap = argparse.ArgumentParser(prog="scaffold.py", description="Create an AI workspace or project skeleton. Never overwrites.")
    ap.add_argument("--version", action="version", version=VERSION)
    sub = ap.add_subparsers(dest="cmd")

    def common(p):
        p.add_argument("--lang", choices=("zh", "en"), default="en", help="template language (default en)")
        p.add_argument("--name", help="display name (default: folder name)")
        p.add_argument("--gemini", action="store_true", help="also create GEMINI.md pointing at AGENTS.md")
        p.add_argument("--no-symlink", action="store_true",
                       help="write one-line '@AGENTS.md' import files instead of symlinks (Windows without Developer Mode)")
        p.add_argument("--dry-run", action="store_true", help="print what would happen, write nothing")

    p_init = sub.add_parser("init", help="create a new workspace")
    p_init.add_argument("root")
    p_init.add_argument("--layout", choices=sorted(LAYOUTS), default="dev",
                        help="dev: projects/forks/vendor/notes/memory/_archive; minimal: projects/notes/memory/_archive")
    common(p_init)

    p_proj = sub.add_parser("project", help="add the standard files to a project folder")
    p_proj.add_argument("path")
    p_proj.add_argument("--root", help="workspace root (default: nearest parent with memory/MEMORY.md)")
    common(p_proj)

    args = ap.parse_args(argv)
    if args.cmd == "init":
        return cmd_init(args)
    if args.cmd == "project":
        return cmd_project(args)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
