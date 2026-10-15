# The method

One sentence: **whatever an agent has to remember goes into files in the user's workspace, and an index tells the next agent which file to open.** Nothing important lives only in a chat, in an agent's private memory folder, or in one vendor's account.

## Layer 1: folders say what an agent may do

```
<root>/
├── AGENTS.md        # router: rules + project index (CLAUDE.md links here)
├── projects/        # the user's own work: change freely
├── forks/           # forked open source: keep changes mergeable, don't touch upstream rules
├── vendor/          # reference code: read-only
├── notes/           # cross-project notes, indexed by notes/_index.md
├── memory/          # preferences and lessons, indexed by memory/MEMORY.md
└── _archive/        # retired things: move in, never delete
```

An agent reading a path knows how careful to be. Non-developers can drop `forks/` and `vendor/` (`--layout minimal`). Names can change; the root router records whatever the user chose.

## Layer 2: rules travel with the folders

- **The root `AGENTS.md` is a router**, not a manual: how to continue, the folder table, the governance rules, and a project index with one line per project (name, path, one sentence, status).
- **Each project has its own `AGENTS.md`**: what it is, stack, how to run it, conventions, and an "Active documents" list so an agent reads `STATUS.md`/`PLAN.md` instead of guessing.
- **One real file, the rest are links.** `AGENTS.md` is the open standard most agents read; `CLAUDE.md` (and `GEMINI.md` if needed) is a symlink to it, or a one-line `@AGENTS.md` import where symlinks are unavailable. Workspaces that already use `CLAUDE.md` as the real file can keep that direction; what matters is that there is only one real file per folder.
- **Every project file points back to the root** with one line, because some agents (Codex, OpenCode) load only the nearest file or stop at the git root and never see the workspace router.

## Layer 3: memory is files with an index

| File | Holds | Read when |
|---|---|---|
| `STATUS.md` (per project) | current state, next entry, open decisions; archive at the bottom | starting or continuing work on the project |
| `PLAN.md` (per project) | goal, approach, phases, decisions | planning; changes rarely |
| `memory/MEMORY.md` | one hook line per preference or lesson | every session (it is short) |
| `memory/<entry>.md` | the detail behind one hook | when the hook applies |
| `notes/_index.md` + notes | cross-project knowledge | when a task needs background |

The pattern is always **index + read on demand**: small indexes load every time, details load only when needed.

Claude Code keeps its own auto memory in `~/.claude/projects/<project>/memory/`, outside the workspace, so other agents cannot see it. Point Claude Code at the workspace instead with `"autoMemoryDirectory": "<root>/memory"` in `~/.claude/settings.json` (ask the user first; it applies to every Claude Code session on the machine). Other agents read `memory/MEMORY.md` because the root router tells them to.

## Layer 4: governance, or why the first three rot

Left alone, the files grow: index lines turn into paragraphs, the same status is written in four places and they disagree, the root file grows until agents stop following it. Three facts set the rules:

1. **Root files load in full, every session.** Claude Code's docs recommend under 200 lines per CLAUDE.md because longer files "reduce adherence"; Codex stops adding instruction files past 32 KiB by default (`project_doc_max_bytes`).
2. **Claude Code loads only the first 200 lines or 25 KB of `MEMORY.md`** and drops the rest silently, so new entries appended at the end stop working without any error.
3. **Detail further down is cheap.** Claude Code, Gemini CLI, Cursor and Copilot load a sub-folder's instruction file only when they work there, and every agent can open a file the index points to.

So:

- **One home per fact.**

  | Information | Home | Elsewhere |
  |---|---|---|
  | What a project is, stack, commands | project `AGENTS.md` | one sentence in the root index |
  | Progress, next entry, open decisions | project `STATUS.md` | nowhere |
  | History, dated results | git log, STATUS archive | nowhere |
  | Preferences, cross-project lessons | `memory/<entry>.md` | one hook in `MEMORY.md` |

- **Budgets.** Root router ≤200 lines / 10 KB. `MEMORY.md` ≤150 lines / 12 KB (headroom under Claude Code's cut-off). Project `AGENTS.md` ≤200 lines. `STATUS.md` body ≤100 lines, ≤300 with archive. Over budget: trim first, then write.
- **Tense.** `AGENTS.md` is present tense (true in six months). `STATUS.md` is where things stand now. Dated past tense belongs to git log and the STATUS archive.
- **Update protocol**, bottom-up and thinner at each level: STATUS.md → project AGENTS.md (only if the project changed) → root index status cell → memory (only cross-project lessons).
- **Lint every week or two** (`scripts/lint.py`). The existing entries are the example the next agent copies, so one bloated line breeds more.

## What "continue" does

1. The agent loads the root `AGENTS.md` (or, inside a project, the project's file, which points to the root).
2. It reads `memory/MEMORY.md` for preferences.
3. It opens the project's `STATUS.md` and starts from "Next entry"; at the root it lists the most recently modified STATUS files and asks which one.
4. Before stopping it updates `STATUS.md`.

None of these steps depends on a particular agent, a skill being installed, or a chat history. That is the point.

## Optional: version the workspace

Rule files and memory are worth backing up. If projects are separate git repos, make the root a small repo that tracks `AGENTS.md`, `memory/` and `notes/` and ignores `projects/`, `forks/` and `vendor/`. Then the same memory follows the user to another machine.
