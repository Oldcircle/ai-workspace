# adopt: take over an existing workspace

Use when the root already holds projects, notes or rule files. Order is fixed: **inventory → report → confirm → back up → migrate → verify.** Nothing is deleted; things that are no longer needed move to `_archive/`.

`<skill>` is the folder holding SKILL.md.

## 1. Inventory (read-only)

Change nothing in this step.

1. `python3 <skill>/scripts/lint.py <root> --json --quiet > /tmp/aiws-before.json` (any scratch path).
2. Measure what every session loads: root `AGENTS.md`/`CLAUDE.md`, the user-level file (`~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`, `~/.gemini/GEMINI.md`, whichever exist), and any memory index. `wc -lc` is enough.
3. Find agent-private memory, which other agents cannot see: `~/.claude/projects/*/memory/` (Claude Code auto memory), and similar folders for other tools if the user mentions them.
4. List projects: folders with code, a README or a git repo. For each, note whether it has an instruction file, `STATUS.md`, `PLAN.md`, and whether it is a git repo with uncommitted changes.
5. Sample the same fact in several places: pick two or three active projects and grep their name across the root file, memory and notes.
6. Note folders that hold other people's code (clones, forks). Their rule files are off limits.

## 2. Report and plan

Show the user:

- the numbers: lines/KB of each always-loaded file against budget, count of projects without STATUS.md, lint errors and warnings by code;
- the risks: projects not under version control, MEMORY.md past 200 lines / 25 KB (entries are already being dropped), two diverging instruction files in one folder;
- a numbered plan of concrete moves, for example:
  1. Create `memory/`, move the 12 entries from `~/.claude/projects/.../memory/` into it (copies; originals stay until you confirm).
  2. Rewrite the root router from the template, keeping your project table and custom rules; old version saved to `_archive/`.
  3. Add `AGENTS.md -> CLAUDE.md` links in 27 projects.
  4. Add `STATUS.md` to the 5 projects marked active.

If the workspace is already in good shape (lint clean, root under budget), say so and stop. Wait for the user to confirm, or to strike items, before step 3.

## 3. Back up

- Make `_archive/<YYYY-MM-DD>-pre-adopt/` and copy every file you are about to rewrite, keeping relative paths.
- A file committed and clean in git is already backed up (`git -C <dir> status --porcelain -- <file>` prints nothing). Anything else gets copied.

## 4. Migrate

Work in this order, one kind of change at a time, so each can be checked:

1. **Root router.** Start from `templates/<lang>/workspace-root.md`. Merge the user's existing rules into it rather than replacing them; keep their folder names and status labels. Trim each project index line to name / path / one sentence / status; anything longer moves to that project's `AGENTS.md` or `STATUS.md`. If their root file is `CLAUDE.md`, keep it as the real file and link `AGENTS.md` to it.
2. **Links.** In each project with only `CLAUDE.md` or only `AGENTS.md`, add the other as a symlink (`ln -s CLAUDE.md AGENTS.md`), or an `@AGENTS.md` stub on native Windows. Where both exist as separate real files, show the diff, merge into one, and replace the other with a link.
3. **Memory.** Copy agent-private memory files into `<root>/memory/`, rewrite `MEMORY.md` as one hook line per entry, and offer to set Claude Code's `autoMemoryDirectory` to `<root>/memory` so future entries land there too. Leave the originals in place.
4. **Project files.** For active projects: add `STATUS.md` (from git log and existing notes) with "Current state" and "Next entry" at the top. In each project `AGENTS.md`, move dated progress and to-do lists into `STATUS.md`, move long reference material to `docs/` with a pointer, and add an "Active documents" section and the one-line pointer to the workspace root.
5. **Folders.** Only if the user agreed: move projects into `projects/`, `forks/`, `vendor/`. Update every path in the project index after moving.

Do not touch:

- rule files that came with someone else's repository (forks, vendor, cloned upstream projects);
- secrets, `.env` files, credentials;
- data folders the user did not mention.

## 5. Verify

1. Lint again and show before/after: errors, warnings, root router size, MEMORY.md size.
2. Spot-check "continue": read the root router as a new agent would and confirm it leads to the right STATUS.md.
3. Tell the user where the backups are and what is left (for example, oversized STATUS files to trim over the next sessions).
