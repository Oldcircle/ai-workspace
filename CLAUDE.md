# AI Workspace

<!-- Present tense only. Progress and open decisions live in STATUS.md (local only, git-ignored). -->

An agent-agnostic method for keeping an AI agent's memory in plain files, shipped as three things: an Agent Skill (`skills/ai-workspace/`), an install guide written for agents (`INSTALL.md`), and templates plus two stdlib Python scripts (scaffold, lint). The promise it has to keep: any agent, told "continue" in the workspace, picks up the work from files alone.

## Stack

Markdown and Python 3.8+ standard library. No packages, no build step. Tests use `unittest`.

## Running it

```bash
python3 -m unittest discover -s tests                                  # tests
python3 skills/ai-workspace/scripts/scaffold.py init /tmp/ws --lang zh  # try a scaffold
python3 skills/ai-workspace/scripts/lint.py /tmp/ws                    # lint it
```

## Layout

```
INSTALL.md                  read by agents during setup; the one sentence links here and must match both READMEs
README.md / README.zh-CN.md for people; images in assets/readme/
skills/ai-workspace/
  SKILL.md                  modes (init / adopt / maintain) and rules; under 500 lines
  references/               method, agents (per-vendor facts with sources), init, adopt, maintain, writing
  templates/{zh,en}/        workspace-root, project, PLAN, STATUS, MEMORY, memory-entry, notes-index
  scripts/scaffold.py       creates folders and files from templates; never overwrites
  scripts/lint.py           read-only health check; finding codes documented in references/maintain.md
tests/test_lint.py          scaffold + lint tests
_work/                      local test transcripts (git-ignored)
```

## Conventions

- **The workspace must not depend on the skill.** Anything an agent needs to resume work goes into the templates (the root router's "Continue" section), not only into SKILL.md.
- **Agent facts need a source.** Every claim about what an agent reads or where it looks for skills cites the vendor's docs in `references/agents.md`; anything not checked is written as "not verified". README, INSTALL.md and agents.md must agree.
- **Scripts stay standard-library only** and run on Python 3.8+, macOS, Linux and Windows.
- **Scaffold never overwrites or deletes.** Lint never writes.
- **The scaffold passes its own lint**: `TestScaffoldPassesItsOwnLint` must stay green for both languages.
- **A new lint rule needs two tests**: one that fails without it, one showing a clean workspace stays clean. Add its code to the table in `references/maintain.md`.
- **Template files are never named AGENTS.md or CLAUDE.md**, so agents working in this repo do not load them as instructions.
- **Public repo**: no personal paths, private project names or secrets. Examples use neutral names (`recipe-box`, `~/workspace`).
- Chinese text follows plain spoken style: direct, no parallel slogans.

## Active documents

- `STATUS.md` (local only, git-ignored): current state, next entry, open decisions, results of the last real-agent install test
- `skills/ai-workspace/references/agents.md`: per-agent facts; re-check before each release
