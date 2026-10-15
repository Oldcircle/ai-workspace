# {{WORKSPACE_NAME}} workspace rules

<!-- The workspace router. Every session loads this whole file. Budget: 200 lines / 10 KB;
     over budget means trim first, then write. AGENTS.md is the real file; CLAUDE.md (and
     GEMINI.md) is a symlink to it or a one-line @AGENTS.md import.
     Present tense only. Project progress lives in each project's STATUS.md, never here. -->

Everything an agent needs to remember in this workspace is in files: rules in AGENTS.md, progress in each project's STATUS.md, cross-project lessons and preferences in `memory/`. Whichever agent you are, follow this file and you can pick up the work.

## Continue

When the user says "continue" or "pick up where we left off":

1. Read `memory/MEMORY.md` first: the user's preferences and cross-project lessons, one line each. Open a linked file only when it applies.
2. Already inside a project folder: read that project's `AGENTS.md` and `STATUS.md`, then start from "Next entry".
3. At the workspace root with no project named: find the 2–3 most recently modified `STATUS.md` files (projects marked 🚧 in the index first), tell the user each project's name and "Next entry", and ask which one. If there is only one candidate, start on it.
4. Before you stop, update STATUS.md as described in "Update protocol". The next person or agent starts from it.

## Folders

| Folder | What goes in | Rule |
|--------|--------------|------|
| `projects/` | Your own projects, optionally grouped in sub-folders | Change freely |
| `forks/` | Forked open-source projects | Keep changes mergeable upstream; never edit upstream's AGENTS.md |
| `vendor/` | Reference code you read but never change | Read-only |
| `notes/` | Cross-project notes, indexed by `notes/_index.md` | Check the index first; update before creating |
| `memory/` | Preferences and cross-project lessons, indexed by `memory/MEMORY.md` | One file per entry, one line in the index |
| `_archive/` | Things no longer in use | Move in; never delete |

A new project goes into the matching folder with its own `AGENTS.md` (`CLAUDE.md` linked to it) and one line in the project index below.

## One home per fact

| Information | Its home | Allowed elsewhere |
|-------------|----------|-------------------|
| What a project is, its stack, how to run it | the project's `AGENTS.md` | one sentence in the project index |
| Where the work is, where to start next, open decisions | the project's `STATUS.md` | nowhere |
| What was done and when | git log, the archive at the bottom of STATUS.md | nowhere |
| Preferences, cross-project lessons | files in `memory/` | one hook line in `MEMORY.md` |

Never write the same paragraph in two places.

## Budgets

| File | Limit | When over |
|------|-------|-----------|
| This file | 200 lines / 10 KB | Move detail into project files or notes; keep a sentence and a path here |
| `memory/MEMORY.md` | 150 lines / 12 KB | Merge or retire entries (Claude Code reads only the first 200 lines or 25 KB and silently drops the rest) |
| A project's `AGENTS.md` | 200 lines | Move reference material to docs/, progress to STATUS.md |
| A project's `STATUS.md` | 100-line body | Move superseded progress to the archive at the bottom |

Over budget means trim first, then write. Never just append.

## Update protocol

After real progress, update from the bottom up, writing less at each level:

1. The project's `STATUS.md`: the details go here and only here.
2. The project's `AGENTS.md`: only when the project itself changed (dependencies, commands, layout, active documents).
3. The project index in this file: only the status cell, only when the status changed.
4. `memory/`: only for a lesson or preference that applies beyond this project, plus one line in `MEMORY.md`. Write it in the workspace's `memory/`, not only in an agent's own memory folder (such as Claude Code's `~/.claude/projects/…/memory/`): the next agent cannot read that.

## Writing rules

- AGENTS.md is present tense: write only what will still be true in six months. STATUS.md says where things stand now. Dated past tense goes to git log and the archive.
- An index line helps the next session decide whether to open something: name, path, one sentence (about 60 characters), status. No dates, versions, feature lists or adjectives.
- Before writing, look at how long the neighbouring entries are and do not exceed them. If an old entry is bloated, trim it first.

## Safety

- Before deleting or overwriting a file, list what will change and ask. "Delete" means move to `_archive/`.
- No keys, tokens or passwords in any markdown file.
- `vendor/` is read-only; leave upstream rule files in `forks/` alone.

## Project index

> Status: 🔬 research 🚧 active ✅ done 📦 shipped 🧊 paused ⛔ stopped. Progress lives in each project's STATUS.md.

| Project | Path | What | Status |
|---------|------|------|--------|
