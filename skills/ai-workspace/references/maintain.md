# maintain: health check and fixes

```bash
python3 <skill>/scripts/lint.py <root>                 # report
python3 <skill>/scripts/lint.py <root> --json --quiet  # warnings and errors as JSON
python3 <skill>/scripts/lint.py <root> --strict        # exit 1 on warnings too (CI)
```

Options: `--memory PATH` when `MEMORY.md` is not at `<root>/memory/MEMORY.md`; `--exclude NAME` / `--include NAME` to change which folder names are skipped (default skips hidden folders, `node_modules`, `vendor`, `_archive`, build output); `--max-depth N` (default 4); `--stale-days N` (default 30).

Lint never writes. Fix in this order: errors, then warnings, then info. Ask before rewriting text the user wrote; mechanical fixes (adding a symlink, adding a missing heading) can be listed and done together after one confirmation.

## Findings

| Code | Level | Meaning | Fix |
|---|---|---|---|
| R001 | error | no `AGENTS.md`/`CLAUDE.md` at the root | run init or adopt |
| L201 | error | two real instruction files in one folder | diff them, merge into one, replace the other with a symlink or `@AGENTS.md` stub |
| L202 | error | broken symlink, or a stub importing a missing file | re-point at the sibling real file |
| L203 | warn | `CLAUDE.md` but no `AGENTS.md` (info inside a project that already has one) | `ln -s CLAUDE.md AGENTS.md` |
| L204 | info | instruction file links outside its folder | fine if intended |
| L205 | info | `AGENTS.md` but no `CLAUDE.md` | `ln -s AGENTS.md CLAUDE.md` for Claude Code before v2.1.277 |
| B101/B102 | warn | root router over 200 lines / 10 KB | shorten index lines; move sections into notes or project files with a pointer |
| B111 | warn | `MEMORY.md` over 150 lines / 12 KB | merge related entries, retire stale ones to `_archive/` |
| B112 | error | `MEMORY.md` over 200 lines / 25 KB: Claude Code is already dropping the tail | same, urgently |
| B121 | warn | project instruction file over 200 lines | progress → STATUS.md; reference material → `docs/` + pointer |
| B131 | warn | STATUS body over 100 lines | move superseded entries into `## Archive` at the bottom |
| B132 | warn | STATUS over 300 lines with archive | delete the oldest archive entries (git log has them) |
| S301/S302 | warn | STATUS.md lacks "Current state" / "Next entry" in its first sections | add the heading; rewrite the top as a hand-off |
| S303 | warn | `PLAN.md` but no `STATUS.md` | add STATUS.md from the template |
| S304 | info | project file has no "Active documents" section | list STATUS.md, PLAN.md and any other live docs |
| S305 | info | project marked 🚧 but STATUS.md untouched for 30+ days | update STATUS or change the status label |
| S306 | info | project marked 🚧 has no STATUS.md | add one |
| I401 | warn | index line wider than about 30 Chinese / 60 Latin characters | one sentence; details into the project |
| I402 | warn | date in an index line | remove; history lives in STATUS archive or git log |
| I403 | warn | memory hook too long | say when to open the file, not what it says |
| I404 | info | a `MEMORY.md` line that is not a `- [title](file.md) — hook` line | convert, or move the content into an entry file |
| P501 | warn | index path does not exist | fix the path, or archive the row |
| P502 | warn | broken markdown link | fix or remove |
| M600 | info | no memory index found | create `memory/MEMORY.md`, or pass `--memory` |
| M601 | warn | memory file not linked from `MEMORY.md` | add a hook line, or archive the file |
| D701 | warn | the same line in two governed files | keep it in its home (see the ownership table in method.md) and link to it |
| T801 | warn | unfilled `{{PLACEHOLDER}}` from a template | fill it in |
| T802 | info | more than three dated lines in an instruction file | move dated progress to STATUS.md |

Duplicate detection (D701) compares the root router, `MEMORY.md`, top-level project instruction files and STATUS bodies. Lines shipped in the templates are ignored, so every project repeating the same template sentence is not a finding. Instruction files nested inside a project that already has one are usually upstream's and are only checked for links and size.

## Routine

Every week or two, or when the user says the agent "forgot" something:

1. Run lint, fix errors.
2. Trim the longest root index line and the longest `MEMORY.md` hook, even if under budget.
3. For each project marked active, read the top of its STATUS.md: is "Next entry" still true? If not, ask the user or update it.
4. Move finished projects' status labels to ✅/📦/🧊 so "continue" at the root does not offer them.
