#!/usr/bin/env python3
"""ai-workspace lint: a zero-dependency health check for an AI workspace.

It reads the files agents load (root AGENTS.md/CLAUDE.md, project instruction
files, STATUS.md, memory/MEMORY.md) and reports what has grown too big, what is
written in two places, what has gone stale, and which links are broken.
It never writes anything.

Usage:
    python3 lint.py [ROOT] [--memory PATH] [--json] [--strict] [--quiet]

Exit codes: 0 = no errors (warnings allowed), 1 = errors found (or warnings
with --strict), 2 = bad usage.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import unicodedata
from pathlib import Path

VERSION = "0.1.0"

INSTRUCTION_FILES = ("AGENTS.md", "CLAUDE.md", "GEMINI.md")

DEFAULT_EXCLUDES = {
    "node_modules", "vendor", "_archive", "archive", "dist", "build", "target",
    "venv", "env", "__pycache__", "site-packages", "Pods", "DerivedData",
}

DEFAULTS = {
    "root_lines": 200,
    "root_bytes": 10 * 1024,
    "memory_lines": 150,
    "memory_bytes": 12 * 1024,
    # Claude Code loads only the first 200 lines or 25KB of MEMORY.md.
    "memory_hard_lines": 200,
    "memory_hard_bytes": 25_000,
    "project_lines": 200,
    "status_body_lines": 100,
    "status_total_lines": 300,
    # Widths count CJK characters as 2: 60 = about 30 Chinese characters.
    "purpose_width": 60,
    "hook_width": 80,
    "dup_min_chars": 40,
    "stale_days": 30,
    "max_depth": 4,
}

PATH_COLS = {"路径", "path", "目录", "location", "dir"}
PURPOSE_COLS = {"定位", "一句话", "简介", "what", "purpose", "description", "summary"}
STATUS_COLS = {"状态", "status"}

ACTIVE_STATUS = "🚧"

DATE_RE = re.compile(r"\b20\d\d-[01]\d-[0-3]\d\b")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
TABLE_SEP_RE = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")
LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HOOK_RE = re.compile(r"^\s*[-*]\s+\[[^\]]+\]\([^)]+\)")
PLACEHOLDER_RE = re.compile(r"\{\{[A-Z_]+\}\}")
ARCHIVE_RE = re.compile(r"(归档|历史|archive|history)", re.I)
ACTIVE_DOCS_RE = re.compile(r"^#{2,3}\s*(活跃文档|active doc)", re.I)
CURRENT_KEYS = ("当前", "现状", "目前", "现在", "进度", "在哪", "current", "now", "state", "where", "progress")
NEXT_KEYS = ("下次", "下一步", "接下来", "入口", "next", "entry", "pick up", "resume")

LEVELS = ("error", "warn", "info")


class Finding:
    __slots__ = ("level", "code", "path", "line", "message", "hint")

    def __init__(self, level, code, path, message, hint="", line=0):
        self.level = level
        self.code = code
        self.path = path
        self.line = line
        self.message = message
        self.hint = hint

    def as_dict(self):
        return {k: getattr(self, k) for k in self.__slots__}


# ---------------------------------------------------------------- helpers

def width(text: str) -> int:
    """Display width: wide (CJK, emoji) characters count as 2."""
    return sum(2 if unicodedata.east_asian_width(c) in ("W", "F") else 1 for c in text)


def read_text(path: Path) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def count_lines(text: str) -> int:
    if not text:
        return 0
    return text.count("\n") + (0 if text.endswith("\n") else 1)


def plain(cell: str) -> str:
    """Markdown cell -> visible text."""
    cell = LINK_RE.sub(lambda m: m.group(1), cell)
    cell = cell.replace("`", "").replace("**", "").replace("__", "")
    return cell.strip()


def content_lines(text: str):
    """Yield (lineno, line) outside code fences and HTML comments."""
    in_fence = False
    in_comment = False
    for i, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if s.startswith("```") or s.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if in_comment:
            if "-->" in s:
                in_comment = False
            continue
        if s.startswith("<!--"):
            if "-->" not in s:
                in_comment = True
            continue
        yield i, line


def instruction_imports(path: Path):
    """Sibling instruction files a CLAUDE.md / GEMINI.md pulls in with '@AGENTS.md' or '@./AGENTS.md'."""
    out = []
    for _, line in content_lines(read_text(path)):
        s = line.strip()
        if s.startswith("@"):
            target = s[1:].strip()
            if target.startswith("./"):
                target = target[2:]
            if target in INSTRUCTION_FILES:
                out.append(target)
    return out


def norm_header(h: str) -> str:
    h = re.sub(r"[*`]|\(.*?\)|（.*?）", "", h)
    return h.strip().lower()


def split_row(line: str):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", s)]


def parse_tables(text: str):
    """Yield dicts: header, rows [(lineno, cells)], context (nearest heading)."""
    lines = text.splitlines()
    heading = ""
    in_fence = False
    i = 0
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if s.startswith("```"):
            in_fence = not in_fence
            i += 1
            continue
        if in_fence:
            i += 1
            continue
        m = HEADING_RE.match(s)
        if m:
            heading = m.group(2)
            i += 1
            continue
        if s.startswith("|") and i + 1 < len(lines) and TABLE_SEP_RE.match(lines[i + 1]):
            header = [norm_header(c) for c in split_row(s)]
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                rows.append((j + 1, split_row(lines[j])))
                j += 1
            yield {"header": header, "rows": rows, "context": heading}
            i = j
            continue
        i += 1


def find_col(header, names):
    for idx, h in enumerate(header):
        if h in names:
            return idx
    return -1


def load_template_patterns():
    """Lines shipped in templates are expected to repeat across projects."""
    tdir = Path(__file__).resolve().parent.parent / "templates"
    pats = []
    if not tdir.is_dir():
        return pats
    for f in sorted(tdir.rglob("*.md")):
        for _, line in content_lines(read_text(f)):
            s = line.strip()
            if len(s) < 20:
                continue
            esc = re.escape(s)
            esc = re.sub(r"\\\{\\\{[A-Z_]+\\\}\\\}", ".*", esc)
            try:
                pats.append(re.compile("^" + esc + "$"))
            except re.error:
                continue
    return pats


# ---------------------------------------------------------------- linter

class Linter:
    def __init__(self, root, memory=None, excludes=None, cfg=None, now=None):
        self.root = Path(root).expanduser().absolute()
        self.cfg = dict(DEFAULTS)
        if cfg:
            self.cfg.update({k: v for k, v in cfg.items() if v is not None})
        self.excludes = set(DEFAULT_EXCLUDES if excludes is None else excludes)
        self.memory = Path(memory).expanduser().absolute() if memory else self.root / "memory" / "MEMORY.md"
        self.now = now if now is not None else time.time()
        self.findings = []
        self.governed = []  # (path, text, body_end_line) for duplicate detection
        self.dirs_with_instructions = 0
        self.template_patterns = load_template_patterns()

    # ---- reporting
    def rel(self, p: Path) -> str:
        try:
            r = os.path.relpath(str(p), str(self.root))
        except ValueError:
            return str(p)
        if r.startswith(".."):
            home = str(Path.home())
            s = str(p)
            return "~" + s[len(home):] if s.startswith(home) else s
        return r.replace(os.sep, "/")

    def add(self, level, code, path, message, hint="", line=0):
        self.findings.append(Finding(level, code, self.rel(path), message, hint, line))

    # ---- walk
    def iter_dirs(self):
        root = str(self.root)
        for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
            rel = os.path.relpath(dirpath, root)
            depth = 0 if rel == "." else rel.count(os.sep) + 1
            dirnames[:] = sorted(
                d for d in dirnames
                if not d.startswith(".") and d not in self.excludes
            )
            if depth >= self.cfg["max_depth"]:
                dirnames[:] = []
            yield Path(dirpath), depth, set(filenames)

    # ---- run
    def run(self):
        if not self.root.is_dir():
            raise SystemExit(f"not a directory: {self.root}")
        root_present = [n for n in INSTRUCTION_FILES if (self.root / n).exists()]
        if not root_present:
            self.add("error", "R001", self.root,
                     "no AGENTS.md or CLAUDE.md at the workspace root",
                     "set up the workspace first (ai-workspace skill: init or adopt)")
        owners = set()  # folders below the root that have their own instruction files
        for d, depth, names in self.iter_dirs():
            is_root = depth == 0
            present = [n for n in INSTRUCTION_FILES if n in names]
            # nested: inside a project that already has instruction files (often upstream-owned)
            nested = any(a in owners for a in d.parents)
            if present:
                self.dirs_with_instructions += 1
                if not is_root:
                    owners.add(d)
                real = self.check_links(d, present, nested)
                for f in real:
                    self.check_instruction(f, is_root, d, names, nested)
            if "STATUS.md" in names:
                self.check_status(d / "STATUS.md", nested)
            elif "PLAN.md" in names and not is_root:
                self.add("warn", "S303", d / "PLAN.md",
                         "PLAN.md without STATUS.md: the next session has no hand-off",
                         "add STATUS.md with 'Current state' and 'Next entry' at the top")
        if self.memory.is_file():
            self.check_memory()
        else:
            self.add("info", "M600", self.memory,
                     "no memory index found",
                     "cross-project memory lives in memory/MEMORY.md; pass --memory PATH if it is elsewhere")
        notes_index = self.root / "notes" / "_index.md"
        if notes_index.is_file():
            self.check_links_in(notes_index)
        self.check_duplicates()
        order = {lvl: i for i, lvl in enumerate(LEVELS)}
        self.findings.sort(key=lambda f: (order[f.level], f.path, f.line, f.code))
        return self.findings

    # ---- AGENTS.md / CLAUDE.md / GEMINI.md
    def check_links(self, d: Path, present, nested=False):
        alive = []
        for n in present:
            p = d / n
            if p.is_symlink() and not p.exists():
                self.add("error", "L202", p, f"{n} is a broken symlink (-> {os.readlink(p)})",
                         "point it at the real instruction file in the same folder, or remove it")
                continue
            for t in instruction_imports(p):
                if not (d / t).exists():
                    self.add("error", "L202", p, f"{n} imports @{t}, which does not exist",
                             f"create {t} or fix the import")
            alive.append(n)
        # distinct real files (symlinks and import stubs collapse onto their target)
        real = {}
        for n in alive:
            p = d / n
            if p.is_symlink():
                target = Path(os.path.realpath(p))
                if target.parent != Path(os.path.realpath(d)):
                    self.add("info", "L204", p, f"{n} links outside its folder (-> {os.readlink(p)})",
                             "fine if intended; most setups link to a sibling file")
                continue
            if any(t != n for t in instruction_imports(p)):
                continue  # a pointer ('@AGENTS.md' plus optional agent-specific lines), not a copy
            real.setdefault(os.path.realpath(p), p)
        if len(real) > 1:
            names = ", ".join(sorted(p.name for p in real.values()))
            self.add("error", "L201", d / sorted(real.values())[0].name,
                     f"{names} are separate files in one folder: they will drift apart",
                     "keep one real file and make the others symlinks to it (ln -s AGENTS.md CLAUDE.md), "
                     "or a one-line '@AGENTS.md' import on Windows")
        if "AGENTS.md" not in alive:
            self.add("info" if nested else "warn", "L203", d / alive[0] if alive else d,
                     "no AGENTS.md here: Codex, Cursor, OpenCode and Copilot will not see these rules",
                     "ln -s CLAUDE.md AGENTS.md")
        if "CLAUDE.md" not in alive:
            self.add("info", "L205", d / "AGENTS.md",
                     "no CLAUDE.md here: Claude Code before v2.1.277 reads only CLAUDE.md",
                     "ln -s AGENTS.md CLAUDE.md")
        return list(real.values())

    def check_instruction(self, f: Path, is_root: bool, d: Path, names, nested=False):
        text = read_text(f)
        lines = count_lines(text)
        size = len(text.encode("utf-8"))
        if is_root:
            if lines > self.cfg["root_lines"]:
                self.add("warn", "B101", f, f"root rules are {lines} lines (budget {self.cfg['root_lines']})",
                         "every session loads this file; move detail into project files or notes and link to it")
            if size > self.cfg["root_bytes"]:
                self.add("warn", "B102", f, f"root rules are {size / 1024:.1f} KB (budget {self.cfg['root_bytes'] // 1024} KB)",
                         "trim index lines to name / path / one sentence / status")
            self.check_index_tables(f, text)
            self.check_links_in(f, text)
        else:
            if lines > self.cfg["project_lines"]:
                self.add("warn", "B121", f, f"{lines} lines (budget {self.cfg['project_lines']})",
                         "move reference material to docs/ and progress to STATUS.md")
            if ("STATUS.md" in names or "PLAN.md" in names) and not any(
                    ACTIVE_DOCS_RE.match(l.strip()) for _, l in content_lines(text)):
                self.add("info", "S304", f, "no 'Active documents' section",
                         "list the docs a new session should read (STATUS.md, PLAN.md, ...)")
            dated = [n for n, l in content_lines(text) if DATE_RE.search(l)]
            if len(dated) > 3:
                self.add("info", "T802", f, f"{len(dated)} dated lines in an instruction file",
                         "instruction files are present tense; dated progress belongs in STATUS.md or git log",
                         dated[0])
        self.check_placeholders(f, text)
        if not nested:
            self.governed.append((f, text, None))

    def check_placeholders(self, f, text):
        for n, l in content_lines(text):
            if PLACEHOLDER_RE.search(l):
                self.add("warn", "T801", f, "unfilled template placeholder", l.strip()[:80], n)
                return

    # ---- index tables in the root file
    def check_index_tables(self, f: Path, text: str):
        for table in parse_tables(text):
            header = table["header"]
            pcol = find_col(header, PURPOSE_COLS)
            if pcol < 0:
                continue
            path_col = find_col(header, PATH_COLS)
            status_col = find_col(header, STATUS_COLS)
            prefixes = re.findall(r"`([^`]+/)`", table["context"])
            for lineno, cells in table["rows"]:
                if pcol < len(cells):
                    purpose = plain(cells[pcol])
                    if width(purpose) > self.cfg["purpose_width"]:
                        self.add("warn", "I401", f,
                                 f"index line is too long ({width(purpose)} wide, budget {self.cfg['purpose_width']}): {purpose[:40]}...",
                                 "one sentence of what it is; details go in the project's own files", lineno)
                if any(DATE_RE.search(c) for c in cells):
                    self.add("warn", "I402", f, "date in an index line",
                             "index lines carry no dates; history goes to STATUS.md archive or git log", lineno)
                if path_col < 0 or path_col >= len(cells):
                    continue
                raw = plain(cells[path_col])
                token = re.split(r"[\s(（]", raw, maxsplit=1)[0].strip()
                if not token or token in ("-", "—"):
                    continue
                target = self.resolve(token, prefixes)
                if target is None:
                    self.add("warn", "P501", f, f"index path not found: {token}",
                             "fix the path, or move the row to an archive section if the project is gone", lineno)
                    continue
                status = cells[status_col] if 0 <= status_col < len(cells) else ""
                if ACTIVE_STATUS in status and target.is_dir():
                    st = target / "STATUS.md"
                    if not st.is_file():
                        self.add("info", "S306", f, f"active project without STATUS.md: {token}",
                                 "add STATUS.md so another agent can pick it up", lineno)
                    else:
                        age = (self.now - st.stat().st_mtime) / 86400
                        if age > self.cfg["stale_days"]:
                            self.add("info", "S305", st,
                                     f"marked {ACTIVE_STATUS} in the index but STATUS.md is {int(age)} days old",
                                     "update STATUS.md, or change the status label (e.g. paused)")

    def resolve(self, token: str, prefixes):
        token = token.rstrip("/")
        cands = [self.root / token] + [self.root / p / token for p in prefixes]
        for c in cands:
            if c.exists():
                return c
        return None

    # ---- markdown links
    def check_links_in(self, f: Path, text: str = None):
        text = read_text(f) if text is None else text
        for n, l in content_lines(text):
            l = re.sub(r"`[^`]*`", "", l)  # examples in inline code are not links
            for m in LINK_RE.finditer(l):
                url = m.group(2)
                if re.match(r"^[a-z][a-z0-9+.-]*:", url, re.I) or url.startswith("#") or url.startswith("<"):
                    continue
                path = url.split("#", 1)[0]
                if not path:
                    continue
                target = (f.parent / path) if not path.startswith("/") else Path(path)
                if not target.exists():
                    self.add("warn", "P502", f, f"broken link: {url}", "fix or remove the link", n)

    # ---- STATUS.md
    def check_status(self, f: Path, nested=False):
        text = read_text(f)
        total = count_lines(text)
        body_end = total
        headings = []
        in_fence = False
        for n, line in enumerate(text.splitlines(), 1):
            s = line.strip()
            if s.startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            m = HEADING_RE.match(s)
            if not m:
                continue
            level, title = len(m.group(1)), m.group(2)
            if level >= 2 and ARCHIVE_RE.search(title):
                body_end = n - 1
                break
            if level <= 2:
                headings.append(title.lower())
        top = headings[:5]  # the title plus the first four sections
        if not any(any(k in h for k in CURRENT_KEYS) for h in top):
            self.add("warn", "S301", f, "no 'Current state' heading near the top",
                     "put '## Current state' (## 当前状态) in the first sections")
        if not any(any(k in h for k in NEXT_KEYS) for h in top):
            self.add("warn", "S302", f, "no 'Next entry' heading near the top",
                     "add '## Next entry' (## 下次入口): where the next session starts")
        if body_end > self.cfg["status_body_lines"]:
            self.add("warn", "B131", f, f"STATUS body is {body_end} lines (budget {self.cfg['status_body_lines']})",
                     "move superseded progress into the '## Archive' (## 归档) section at the bottom")
        if total > self.cfg["status_total_lines"]:
            self.add("warn", "B132", f, f"STATUS.md is {total} lines including archive (cap {self.cfg['status_total_lines']})",
                     "delete the oldest archive entries; git log keeps the history")
        self.check_placeholders(f, text)
        if not nested:
            self.governed.append((f, text, body_end))

    # ---- memory index
    def check_memory(self):
        f = self.memory
        text = read_text(f)
        lines = count_lines(text)
        size = len(text.encode("utf-8"))
        if lines > self.cfg["memory_hard_lines"] or size > self.cfg["memory_hard_bytes"]:
            self.add("error", "B112", f,
                     f"MEMORY.md is {lines} lines / {size / 1024:.1f} KB: Claude Code silently drops everything past 200 lines or 25 KB",
                     "compress entries to one-line hooks; details live in the linked files")
        elif lines > self.cfg["memory_lines"] or size > self.cfg["memory_bytes"]:
            self.add("warn", "B111", f,
                     f"MEMORY.md is {lines} lines / {size / 1024:.1f} KB (budget {self.cfg['memory_lines']} lines / {self.cfg['memory_bytes'] // 1024} KB)",
                     "merge or retire old entries")
        linked = set()
        for n, l in content_lines(text):
            s = l.strip()
            if not s or s.startswith("#") or s.startswith(">"):
                continue
            for m in LINK_RE.finditer(s):
                linked.add(m.group(2).split("#", 1)[0])
            if HOOK_RE.match(s):
                hook = LINK_RE.sub("", s, count=1).lstrip("-* ").lstrip("—–-: ").strip()
                if width(hook) > self.cfg["hook_width"]:
                    self.add("warn", "I403", f,
                             f"memory hook is {width(hook)} wide (budget {self.cfg['hook_width']})",
                             "a hook says when to open the file, not what is in it", n)
            else:
                self.add("info", "I404", f, "line is not a one-line hook '- [title](file.md) — hook'",
                         s[:60], n)
        self.check_links_in(f, text)
        for sub in sorted(f.parent.glob("*.md")):
            if sub.name == f.name:
                continue
            if sub.name not in linked and ("./" + sub.name) not in linked:
                self.add("warn", "M601", sub, "memory file is not linked from MEMORY.md, so no session will find it",
                         "add a one-line hook to MEMORY.md, or move the file to _archive/")
        self.check_placeholders(f, text)
        self.governed.append((f, text, None))

    # ---- the same fact in two places
    def check_duplicates(self):
        seen = {}
        min_chars = self.cfg["dup_min_chars"]
        done = set()
        for f, text, body_end in self.governed:
            rp = os.path.realpath(f)
            if rp in done:
                continue
            done.add(rp)
            for n, line in content_lines(text):
                if body_end is not None and n > body_end:
                    break
                s = line.strip()
                if TABLE_SEP_RE.match(s) or HEADING_RE.match(s):
                    continue
                key = re.sub(r"^([-*+>]|\d+\.)\s+", "", s)
                key = re.sub(r"\s+", " ", key).strip()
                if len(key) < min_chars:
                    continue
                if any(p.match(s) for p in self.template_patterns):
                    continue
                seen.setdefault(key, []).append((f, n))
        pairs = {}
        for key, places in seen.items():
            by_file = {}
            for p, ln in places:
                by_file.setdefault(os.path.realpath(p), (p, ln))
            if len(by_file) < 2:
                continue
            ordered = sorted(by_file.values(), key=lambda x: self.rel(x[0]))
            first = ordered[0]
            for other in ordered[1:]:
                pairs.setdefault((first[0], other[0]), []).append((first[1], other[1], key))
        for (a, b), shared in sorted(pairs.items(), key=lambda kv: (self.rel(kv[0][0]), self.rel(kv[0][1]))):
            shared.sort()
            la, lb, key = shared[0]
            n = len(shared)
            what = "1 line" if n == 1 else f"{n} lines"
            self.add("warn", "D701", a,
                     f"{what} also in {self.rel(b)} (e.g. line {la} = {self.rel(b)}:{lb}: {key[:40]}...)",
                     "keep each fact in its one home and link to it from the other file", la)


# ---------------------------------------------------------------- output

def render_text(linter: Linter, quiet: bool) -> str:
    marks = {"error": "ERROR", "warn": "WARN ", "info": "INFO "}
    out = [f"ai-workspace lint {VERSION} · {linter.root}"]
    shown = [f for f in linter.findings if not (quiet and f.level == "info")]
    for f in shown:
        loc = f"{f.path}:{f.line}" if f.line else f.path
        out.append(f"  {marks[f.level]} {f.code}  {loc}  {f.message}")
        if f.hint:
            out.append(f"               -> {f.hint}")
    c = summary(linter)
    out.append("")
    def n(k, word):
        return f"{c[k]} {word}" + ("" if c[k] == 1 else "s")
    out.append(f"{n('error', 'error')}, {n('warn', 'warning')}, {c['info']} info · "
               f"{linter.dirs_with_instructions} folder{'' if linter.dirs_with_instructions == 1 else 's'} with instruction files")
    if not shown:
        out.append("clean.")
    return "\n".join(out)


def summary(linter: Linter):
    c = {lvl: 0 for lvl in LEVELS}
    for f in linter.findings:
        c[f.level] += 1
    return c


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="lint.py", description="Health check for an AI workspace (read-only).")
    ap.add_argument("root", nargs="?", default=".", help="workspace root (default: current folder)")
    ap.add_argument("--memory", help="path to MEMORY.md (default: ROOT/memory/MEMORY.md)")
    ap.add_argument("--exclude", action="append", default=[], metavar="NAME",
                    help="extra folder name to skip (repeatable)")
    ap.add_argument("--include", action="append", default=[], metavar="NAME",
                    help="folder name to stop skipping, e.g. --include vendor")
    ap.add_argument("--max-depth", type=int, help=f"folder depth to scan (default {DEFAULTS['max_depth']})")
    ap.add_argument("--stale-days", type=int, help=f"STATUS.md age that counts as stale (default {DEFAULTS['stale_days']})")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--quiet", action="store_true", help="hide info-level findings")
    ap.add_argument("--strict", action="store_true", help="exit 1 on warnings too")
    ap.add_argument("--version", action="version", version=VERSION)
    args = ap.parse_args(argv)

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    root = Path(args.root).expanduser()
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    excludes = (DEFAULT_EXCLUDES | set(args.exclude)) - set(args.include)
    linter = Linter(root, memory=args.memory, excludes=excludes,
                    cfg={"max_depth": args.max_depth, "stale_days": args.stale_days})
    linter.run()
    c = summary(linter)
    if args.json:
        print(json.dumps({
            "version": VERSION,
            "root": str(linter.root),
            "summary": c,
            "findings": [f.as_dict() for f in linter.findings
                         if not (args.quiet and f.level == "info")],
        }, ensure_ascii=False, indent=2))
    else:
        print(render_text(linter, args.quiet))
    if c["error"] or (args.strict and c["warn"]):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
