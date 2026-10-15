# Which agent reads what

Checked against each vendor's documentation in October 2026. Agents change quickly; if behaviour differs from this table, trust the agent's current docs and tell the user.

## Instruction files

| Agent | Reads natively | How it loads them | Source |
|---|---|---|---|
| Claude Code | `CLAUDE.md`; `AGENTS.md` directly since v2.1.277 when no `CLAUDE.md` exists in the folder or above | every file from the start folder up loads at launch; sub-folder files load when Claude works there | [memory docs](https://code.claude.com/docs/en/memory) |
| Codex | `AGENTS.override.md`, else `AGENTS.md`, plus names in `project_doc_fallback_filenames`; global `~/.codex/AGENTS.md` | from the project root (usually the git root) down to the start folder, one file per folder (the docs describe no loading below the start folder); 32 KiB total by default | [AGENTS.md guide](https://learn.chatgpt.com/docs/agent-configuration/agents-md) |
| Gemini CLI | `GEMINI.md` by default; other names via `context.fileName` in `settings.json`; supports `@file.md` imports | global `~/.gemini/GEMINI.md`, the workspace and its parents, and sub-folders just in time when a tool touches them | [GEMINI.md docs](https://geminicli.com/docs/cli/gemini-md/) |
| Cursor | `AGENTS.md` in the project root and sub-folders; project rules in `.cursor/rules/*.mdc` | nested files combine with parents, the more specific wins | [rules docs](https://cursor.com/docs/context/rules) |
| OpenCode | `AGENTS.md`, `CLAUDE.md` only if no `AGENTS.md`; global `~/.config/opencode/AGENTS.md`, falls back to `~/.claude/CLAUDE.md` | walks up from the start folder; "the first matching file wins" | [rules docs](https://opencode.ai/docs/rules/) |
| GitHub Copilot CLI | `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`; user-level `~/.copilot/copilot-instructions.md` | repo root, start folder and folders between; identical files are de-duplicated | [CLI instructions](https://docs.github.com/en/copilot/how-tos/copilot-cli/add-custom-instructions) |
| GitHub Copilot cloud agent | `AGENTS.md` anywhere (nearest wins); `CLAUDE.md` or `GEMINI.md` at the repo root | — | [repository instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions) |
| Windsurf, Aider, others | not verified | — | — |

What this means for the workspace:

- `AGENTS.md` as the real file plus a `CLAUDE.md` link covers every verified agent. Claude Code reads the linked content once (its docs: "A CLAUDE.md symlinked to AGENTS.md: nothing [to do]... Claude reads the content once").
- **Gemini CLI** needs one of: `{"context": {"fileName": ["AGENTS.md", "GEMINI.md"]}}` in `~/.gemini/settings.json` (ask first), or `GEMINI.md` links/`@./AGENTS.md` stubs next to each `AGENTS.md` (`scaffold.py --gemini`).
- **Codex and OpenCode may never see the root router** when started inside a project (Codex stops at the git root; OpenCode takes the nearest file). That is why each project's `AGENTS.md` carries a one-line pointer to the workspace root, and why "continue" at the root works best.

## Skill folders

| Agent | User-wide | Per project | Source |
|---|---|---|---|
| Claude Code | `~/.claude/skills/` | `.claude/skills/` | [skills docs](https://code.claude.com/docs/en/skills) |
| Codex | `~/.agents/skills/` (admin: `/etc/codex/skills`) | `.agents/skills/` from the start folder up to the repo root | [skills docs](https://learn.chatgpt.com/docs/build-skills) |
| Gemini CLI | `~/.gemini/skills/` or `~/.agents/skills/` | `.gemini/skills/` or `.agents/skills/` | [skills docs](https://geminicli.com/docs/cli/skills/) |
| Cursor | `~/.cursor/skills/` or `~/.agents/skills/`; also reads `~/.claude/skills/`, `~/.codex/skills/` | `.cursor/skills/`, `.agents/skills/`, `.claude/skills/`, `.codex/skills/` | [skills docs](https://cursor.com/docs/skills) |
| OpenCode | `~/.config/opencode/skills/`, `~/.claude/skills/` or `~/.agents/skills/` | `.opencode/skills/`, `.claude/skills/`, `.agents/skills/` | [skills docs](https://opencode.ai/docs/skills/) |
| GitHub Copilot | `~/.copilot/skills/` or `~/.agents/skills/` | `.github/skills/`, `.claude/skills/`, `.agents/skills/` | [agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills) |
| Windsurf, Aider, others | not verified | not verified | — |

`~/.agents/skills/` covers Codex, Gemini CLI, Cursor, OpenCode and Copilot; `~/.claude/skills/` covers Claude Code (and is also read by Cursor and OpenCode). Installing to both, with one a symlink to the other, covers every verified agent. An agent that does not support skills can still read `SKILL.md` from a clone and follow it.

## Windows

- **WSL, macOS, Linux**: symlinks work; nothing special.
- **Native Windows**: creating a symlink needs Administrator rights or Developer Mode (Settings → For developers). Git for Windows checks symlinks out as plain text files unless `core.symlinks=true` and the user can create them; Git Bash's `ln -s` makes a copy by default. Sources: [Git for Windows: symbolic links](https://gitforwindows.org/symbolic-links), [Microsoft: symlinks without elevation](https://blogs.windows.com/windowsdeveloper/2016/12/02/symlinks-windows-10/).
- Without symlinks, use `scaffold.py --no-symlink`: it writes `CLAUDE.md` containing just `@AGENTS.md` (Claude Code expands `@` imports) and `GEMINI.md` containing `@./AGENTS.md` (Gemini CLI does too). Lint accepts these stubs.
- A copy of `AGENTS.md` named `CLAUDE.md` is the one thing to avoid: the two drift apart, and lint reports it as an error (L201).
