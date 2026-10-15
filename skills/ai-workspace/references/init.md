# init: a new workspace

Use when the root has no `AGENTS.md`/`CLAUDE.md` and little or nothing in it. If it already holds projects or rule files, use `adopt.md` instead; `scaffold.py init` refuses (exit 3) when root rules already exist.

`<skill>` below is the absolute path of the folder holding SKILL.md.

## 1. Ask (one message)

- Workspace root, if not given. Suggest `~/workspace`.
- Template language: `zh` or `en`. Default to the language the user is writing in.
- Layout: `dev` (projects, forks, vendor, notes, memory, _archive) or `minimal` (projects, notes, memory, _archive) for people who do not fork or study other code.
- Which agents they use, so you know whether Gemini CLI needs `--gemini` or a settings change.

## 2. Preview, then create

```bash
python3 <skill>/scripts/scaffold.py init <root> --lang zh --layout dev --dry-run
python3 <skill>/scripts/scaffold.py init <root> --lang zh --layout dev
```

Flags:

- `--name "My workspace"`: the title in the root router (default: folder name).
- `--no-symlink`: native Windows without Developer Mode. Writes `CLAUDE.md` as a one-line `@AGENTS.md` import.
- `--gemini`: also create `GEMINI.md` linking to `AGENTS.md`. Skip it if the user agrees to set `context.fileName` in `~/.gemini/settings.json` instead.

Result:

```
<root>/
├── AGENTS.md            # router from templates/<lang>/workspace-root.md
├── CLAUDE.md -> AGENTS.md
├── memory/MEMORY.md     # empty index
├── notes/_index.md      # empty index
├── projects/  forks/  vendor/  _archive/
```

## 3. Add projects

For each project the user wants tracked (new, or an existing folder they move into `projects/`):

```bash
python3 <skill>/scripts/scaffold.py project <root>/projects/<name> --lang zh
```

This adds `AGENTS.md` (or keeps an existing real `CLAUDE.md` and links `AGENTS.md` to it), `PLAN.md` and `STATUS.md`, never overwriting. Then:

1. Fill the project's `AGENTS.md` from what is actually there: README, package files, scripts. One sentence on what it is, stack, how to run it. Delete template comments you have answered.
2. Write a real `STATUS.md`: current state and next entry, from git log and the user's words. An empty "just created" STATUS is fine only for a brand-new project.
3. Add one row to the root project index: `| Name | projects/name | one sentence | 🚧 |`.

Moving existing folders into `projects/` is a move of user files: list the moves and ask first.

## 4. Optional, ask first

- **Claude Code memory in the workspace**: add `"autoMemoryDirectory": "<root>/memory"` to `~/.claude/settings.json`. Claude Code then writes its auto memory where other agents can read it. It applies to every Claude Code session on the machine.
- **Gemini CLI reads AGENTS.md**: add `"context": {"fileName": ["AGENTS.md", "GEMINI.md"]}` to `~/.gemini/settings.json`.
- **Back up rules and memory**: `git init` at the root with a `.gitignore` that excludes `projects/`, `forks/`, `vendor/` if those hold their own repos.

## 5. Verify and hand over

```bash
python3 <skill>/scripts/lint.py <root>
```

Expect `0 errors`. Then tell the user, in their language, roughly:

> Your workspace is at `<root>`. Rules are in `AGENTS.md`, each project's progress in its `STATUS.md`. Open any agent in this folder and say "continue"; it will find the latest work. Run the lint now and then to keep the files small.
