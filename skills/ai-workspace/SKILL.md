---
name: ai-workspace
description: Set up and maintain a workspace where an AI agent's memory lives in plain files any agent can read, so the user can switch between Claude Code, Codex, Cursor, Gemini CLI, OpenCode or Copilot and continue by saying "continue". init builds a new workspace from templates; adopt takes over an existing messy one (inventory, plan, migrate, nothing deleted); maintain runs a read-only lint for oversized rule files, duplicated facts, stale STATUS.md, broken paths and missing AGENTS.md/CLAUDE.md links. Use when the user names ai-workspace (e.g. "set up my workspace with ai-workspace", "帮我按 ai-workspace 把工作区搭好"), asks to set up, organize or check a workspace for AI agents (搭工作区, 整理工作区, 给工作区体检), wants agents to remember progress across sessions or tools, wants to stop depending on one vendor's memory, or says their AGENTS.md/CLAUDE.md/memory files are bloated or out of date.
license: MIT
---

# AI Workspace

Keep everything an agent has to remember in files inside the user's workspace: rules in `AGENTS.md`, progress in each project's `STATUS.md`, cross-project lessons in `memory/`. Then any agent that can read files can pick up the work, and nothing important lives only in a chat or in one vendor's account.

Talk to the user in their language. The templates come in Chinese (`zh`) and English (`en`).

## The method

| Layer | Files | What it stops |
|---|---|---|
| 1. Folders | `projects/` `forks/` `vendor/` `notes/` `memory/` `_archive/` | Agents editing reference code, files landing in random places |
| 2. Rules | root `AGENTS.md` (router + project index), one `AGENTS.md` per project, `CLAUDE.md`/`GEMINI.md` linked to it | Re-explaining the project every session; each agent seeing different rules |
| 3. Memory | `STATUS.md` (hand-off), `PLAN.md`, `memory/MEMORY.md` + entry files, `notes/_index.md` | Losing progress between sessions or when switching agents |
| 4. Governance | one home per fact, budgets, tense rules, update protocol, `scripts/lint.py` | Layers 1–3 slowly bloating until agents stop following them |

Loading is progressive: an agent starts with only the files from the workspace root down to the current project (Claude Code reads `CLAUDE.md`, Codex and most others `AGENTS.md`; one is a link to the other), reads a sub-folder's file when it works there, and opens details only when an index points to them. `STATUS.md` holds two things at the top: where the work is now, and where the next session starts.

Why each rule exists, and the loading behaviour it relies on: `references/method.md`. Which agent reads which file: `references/agents.md`.

## Before any mode

1. **Find the skill folder.** You need its absolute path to run `scripts/` and read `templates/`. It is the folder this SKILL.md is in.
2. **Ask for the workspace root** if the user has not given it. Never assume a path. Suggest `~/workspace` for a new one; if they already keep projects in one folder, that folder is the root.
3. **Check the OS.** macOS, Linux and WSL support symlinks. Native Windows usually does not without Developer Mode; use `--no-symlink` there (see `references/agents.md`, "Windows").
4. **Pick the mode:**
   - root has no `AGENTS.md`/`CLAUDE.md` and holds few or no files → **init**
   - root has projects, notes or rule files already → **adopt**
   - root already has a router with a budgets section → **maintain**

Python 3.8+ runs both scripts with no packages. If Python is missing, do the same steps by hand from the templates.

## init: a new workspace

Full steps: `references/init.md`. In short:

1. Ask two things in one message: template language (zh/en) and folder layout (`dev` = projects/forks/vendor/notes/memory/_archive, `minimal` = projects/notes/memory/_archive for non-developers).
2. `python3 <skill>/scripts/scaffold.py init <root> --lang zh --layout dev` (add `--no-symlink` on native Windows, `--gemini` if the user runs Gemini CLI without changing its settings).
3. For each existing project the user wants tracked: `python3 <skill>/scripts/scaffold.py project <root>/projects/<name> --lang zh`, then fill its `AGENTS.md` from the code (stack, how to run it) and add one row to the root project index.
4. Run lint until it reports 0 errors.
5. Tell the user the one thing to remember: open any agent in the workspace and say "continue".

## adopt: take over an existing workspace

Full steps: `references/adopt.md`. The order is fixed and nothing is deleted:

1. **Inventory (read-only).** Run lint, measure the files every session loads, find projects without `STATUS.md`, facts kept in several places, memory that lives only inside one agent's private folder.
2. **Report and plan.** Show the numbers and a concrete list of moves. Wait for the user to confirm before changing anything.
3. **Back up.** Copy every file you will rewrite into `_archive/<date>-pre-adopt/` unless it is committed in git.
4. **Migrate**: write the root router (merge, keep the user's content), link instruction files, add `STATUS.md` where work is in progress, move agent-private memory into `memory/`.
5. **Verify.** Lint again and show before/after numbers.

Keep the user's existing conventions where they work (folder names, `CLAUDE.md` as the real file, language). Never edit rule files that belong to an upstream project in `forks/` or `vendor/`.

## maintain: health check

Full steps and how to fix each finding: `references/maintain.md`.

```bash
python3 <skill>/scripts/lint.py <root>                       # human-readable
python3 <skill>/scripts/lint.py <root> --json --quiet        # for you to parse
```

Lint is read-only. Fix errors first (broken links, two diverging instruction files, MEMORY.md past the truncation line), then warnings, smallest change first. Ask before rewriting anything the user wrote. Suggest running it every week or two.

## Rules for any agent working in the workspace

These are also written into the root template, so agents without this skill follow them too.

1. On "continue": read `memory/MEMORY.md`, then the project's `AGENTS.md` and `STATUS.md`, and start from "Next entry". At the root with no project named, list the 2–3 most recently modified `STATUS.md` files and ask.
2. After real progress, update from the bottom up: `STATUS.md` → project `AGENTS.md` (only if the project itself changed) → root index status cell → `memory/` (only for lessons that apply elsewhere).
3. One home per fact. Present tense in `AGENTS.md`; dated history only in git log or the STATUS archive.
4. Preferences and cross-project lessons go into `<root>/memory/` (one file per entry, one hook line in `memory/MEMORY.md`), never only into an agent's private memory folder such as Claude Code's `~/.claude/projects/<project>/memory/`: the next agent cannot read that.
5. Over budget means trim first, then write. Writing guide: `references/writing.md`.

## Safety

- Never delete user files: move them to `_archive/`. Never overwrite a file without showing the diff or the plan first.
- Ask before changing any agent's settings (`~/.claude/settings.json`, `~/.gemini/settings.json`, `~/.codex/config.toml`).
- Do not copy secrets, tokens or credentials into any markdown file.

## Files in this skill

| Path | Use |
|---|---|
| `scripts/scaffold.py` | `init` / `project`: create folders and files from templates; never overwrites |
| `scripts/lint.py` | read-only health check; `--json`, `--quiet`, `--strict`, `--memory PATH` |
| `templates/{zh,en}/` | `workspace-root.md`, `project.md`, `PLAN.md`, `STATUS.md`, `MEMORY.md`, `memory-entry.md`, `notes-index.md` |
| `references/method.md` | the four layers and why each rule exists |
| `references/agents.md` | which agent reads which instruction file and skill folder, with sources; Windows |
| `references/init.md` `adopt.md` `maintain.md` | step-by-step for each mode |
| `references/writing.md` | how to write rule files, STATUS.md and index lines |
