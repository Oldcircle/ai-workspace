<div align="center">

# 🗂️ AI Workspace

**Keep your AI's memory in your own files. Switch to any agent, say "continue", and it picks up where the last one stopped.**

<p align="center">
  <a href="README.md"><img alt="English" src="https://img.shields.io/badge/English-1f6feb?style=flat-square"></a>
  <a href="README.zh-CN.md"><img alt="Simplified Chinese" src="https://img.shields.io/badge/%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87-dbeafe?style=flat-square"></a>
</p>

**Send this one sentence to your AI:**

```text
Set up my workspace with ai-workspace, following https://raw.githubusercontent.com/Oldcircle/ai-workspace/main/INSTALL.md
```

<p align="center">
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg"></a>
  <a href="https://agentskills.io"><img alt="Agent Skill: SKILL.md" src="https://img.shields.io/badge/Agent%20Skill-SKILL.md-8A2BE2.svg"></a>
  <a href="https://www.python.org/downloads/"><img alt="Python 3.8+" src="https://img.shields.io/badge/python-3.8%2B-blue.svg"></a>
  <img alt="Zero dependencies" src="https://img.shields.io/badge/dependencies-0-brightgreen.svg">
</p>

<p align="center">
  <b>Works with</b><br>
  <a href="https://code.claude.com/docs/en/memory"><img alt="Claude Code" src="https://img.shields.io/badge/Claude%20Code-D97757?style=for-the-badge&logo=claude&logoColor=white"></a>
  <a href="https://learn.chatgpt.com/docs/agent-configuration/agents-md"><img alt="Codex" src="https://img.shields.io/badge/Codex-000000?style=for-the-badge"></a>
  <a href="https://cursor.com/docs/context/rules"><img alt="Cursor" src="https://img.shields.io/badge/Cursor-000000?style=for-the-badge&logo=cursor&logoColor=white"></a>
  <a href="https://geminicli.com/docs/cli/gemini-md/"><img alt="Gemini CLI" src="https://img.shields.io/badge/Gemini%20CLI-1A73E8?style=for-the-badge&logo=googlegemini&logoColor=white"></a>
  <a href="https://opencode.ai/docs/rules/"><img alt="OpenCode" src="https://img.shields.io/badge/OpenCode-211E1E?style=for-the-badge"></a>
  <a href="https://docs.github.com/en/copilot/how-tos/copilot-cli/add-custom-instructions"><img alt="GitHub Copilot" src="https://img.shields.io/badge/GitHub%20Copilot-000000?style=for-the-badge&logo=githubcopilot&logoColor=white"></a>
  <br><sub>…and any other agent that can read files.</sub>
</p>

<img src="assets/readme/hero.png" width="880" alt="Left: a family-tree web app built with Claude Code. Right: Codex opened in the same project folder, told only 'continue' (接着做); it reads the workspace AGENTS.md, then CLAUDE.md, STATUS.md and PLAN.md, and reports where the work stopped and what comes next">

*An app built with Claude Code. Opened in Codex, it was told only "continue": Codex read the workspace rules and the project's STATUS.md and named the next step, exactly where the last session stopped.<br>(Screens are from the Chinese video this project accompanies.)*

</div>

---

## 30-second start

Paste this into any coding agent (Claude Code, Codex, Cursor, Gemini CLI, OpenCode, Copilot CLI…):

```text
Set up my workspace with ai-workspace, following https://raw.githubusercontent.com/Oldcircle/ai-workspace/main/INSTALL.md
```

The agent installs the skill, asks where your workspace is and which language you want, then either builds a new workspace or tidies the one you already have (it shows you a plan before moving anything). From then on, open any agent in that folder and say:

> continue

The link matters the first time: an agent that has never seen this project does not know what "ai-workspace" is. Once the skill is installed, the short form "set up my workspace with ai-workspace" is enough.

## Why

- **The memory is yours.** Rules, progress and lessons are plain markdown files in your folder. There is no account to log into, no export, and nothing stored only inside one vendor's product.
- **Any agent can pick up the work.** The rules live in `AGENTS.md`, which Codex, Cursor, OpenCode and Copilot read as-is. `CLAUDE.md` is a link to the same file for Claude Code, and Gemini CLI needs one setting.
- **"Continue" is written down, so every agent does it the same way.** The root file tells any agent what to do: read your preferences, find the most recent `STATUS.md`, start from its "Next entry".
- **The files stay small.** Size budgets, one place for each fact, and a lint that catches bloat early, before agents start ignoring a 600-line rule file.
- **It works on a workspace you already have.** Adopt mode takes inventory first, shows a plan, backs up, and never deletes a file.
- **Nothing runs in the background.** It is a skill (markdown) and two Python scripts that use only the standard library.

## How it works

<div align="center"><img src="assets/readme/layers.png" width="820" alt="Three layer cards: 01 folders (what the AI may change), 02 rules (one manual per project), 03 memory (where the work is, where to pick up). Middle: projects/ change freely, forks/ change carefully, vendor/ read only; the AI reads the path and knows a project folder may be changed. Right: STATUS.md with two lines, now and next, the file Codex just read"></div>

<div align="center"><sub>Folders tell the AI what it may change (projects/ freely, forks/ carefully, vendor/ read only). STATUS.md holds two things: where the work is now, and where to pick up next.</sub></div>

Three layers hold the memory, and a fourth keeps them from going stale:

| Layer | Files | What it fixes |
|---|---|---|
| **1. Folders** | `projects/` `forks/` `vendor/` `notes/` `memory/` `_archive/` | The agent knows from the path what it may change: your code freely, forks carefully, reference code never. |
| **2. Rules** | root `AGENTS.md` (router + project index), one `AGENTS.md` per project, `CLAUDE.md` → `AGENTS.md` | You stop explaining the project every session, and every agent reads the same rules. |
| **3. Memory** | `STATUS.md` per project, `PLAN.md`, `memory/MEMORY.md` + entries, `notes/_index.md` | Progress and lessons survive the end of a chat, a new session, a new tool. |
| **4. Governance** | one home per fact, size budgets, tense rules, an update protocol, `lint.py` | Layers 1–3 don't slowly grow into files nobody follows. |

```
~/workspace/
├── AGENTS.md            # the router: how to continue, the rules, one line per project
├── CLAUDE.md -> AGENTS.md
├── memory/
│   ├── MEMORY.md        # one line per preference or lesson
│   └── prefers-short-commits.md
├── notes/_index.md
├── projects/
│   └── recipe-box/
│       ├── AGENTS.md    # what it is, how to run it, conventions
│       ├── CLAUDE.md -> AGENTS.md
│       ├── PLAN.md      # goal and phases
│       └── STATUS.md    # current state · next entry · open decisions
├── forks/  vendor/  _archive/
```

### Why many small files, not one big one

The model remembers nothing between messages: every message you send resends the whole conversation, so a long chat costs more each turn, and when the window fills up it gets compacted and the details are gone. A rule file loaded every session is paid for on every turn too, and the longer it is, the less of it gets followed.

So the memory is split up. At startup an agent reads only the files from the workspace root down to the current project; a sub-folder's file is read when the agent starts working there; details sit one link away and are opened only when needed. This is progressive loading, like reading a book: look at the table of contents, then open the chapter you need. The reasoning behind each rule, and which loading behaviour of each agent it relies on, is in [`references/method.md`](skills/ai-workspace/references/method.md).

## Switching agents

<div align="center"><img src="assets/readme/switch.png" width="820" alt="Left, layer 02 rules: Claude Code reads CLAUDE.md (stack, how to run, known traps), Codex reads AGENTS.md, which is a symlink to CLAUDE.md made with ln -s; both read the same file. Right, layer 03 memory: STATUS.md says MVP done, next static deploy and PWA offline; below, the Codex log line that read it"></div>

<div align="center"><sub>Claude Code reads CLAUDE.md, Codex reads AGENTS.md: write one, link the other, and every agent reads the same rules. The workspace in the video keeps CLAUDE.md as the real file; new workspaces default to AGENTS.md. Either direction works as long as there is only one real file.</sub></div>

Say "continue" in any agent and this happens:

1. The agent loads the root `AGENTS.md` (Claude Code reaches it through the `CLAUDE.md` link).
2. It reads `memory/MEMORY.md` for your preferences.
3. Inside a project, it opens that project's `STATUS.md` and starts from "Next entry". At the root, it lists the two or three most recently updated projects and asks which one.
4. Before it stops, it updates `STATUS.md` for whoever comes next.

None of these steps depends on a particular vendor, on this skill being installed, or on any chat history. If you lose access to one tool tomorrow, the next one reads the same files.

## Before and after

<div align="center"><img src="assets/readme/before-after.png" width="820" alt="Left: 'accounts get banned, conversations get compacted': the conversation shrinks to a one-line summary and falls apart, while AGENTS.md, CLAUDE.md and STATUS.md sit unchanged. Right: the same files, and the line 'but the files stay'"></div>

<div align="center"><sub>Accounts get banned and conversations get compacted, but the files stay.</sub></div>

| | Before | After |
|---|---|---|
| New session | You re-explain the project | "continue" |
| Where progress lives | Scrolled away in a chat | `STATUS.md`, top 20 lines |
| Your preferences | In one product's memory, invisible to other tools | `memory/`, read by every agent |
| Switching tools | Start over | Same files, same next step |
| Rule file | Grows to hundreds of lines, half of it stale | Router under 200 lines; details one link away |
| Same status in four places | They disagree | One home per fact; lint flags copies |

## Three modes

| Mode | When | Say |
|---|---|---|
| **init** | New or empty folder | "Set up an AI workspace in ~/workspace" |
| **adopt** | You already have projects and rule files | "Take over my workspace at ~/code and tidy it up" |
| **maintain** | Every week or two | "Check my workspace" |

Adopt never deletes: it inventories read-only, shows numbers and a plan, waits for your yes, backs up everything it will rewrite, then migrates one kind of change at a time.

## Health check

```console
$ python3 ~/.agents/skills/ai-workspace/scripts/lint.py ~/workspace
ai-workspace lint 0.1.0 · /home/you/workspace
  ERROR L201  projects/api/AGENTS.md  AGENTS.md, CLAUDE.md are separate files in one folder: they will drift apart
               -> keep one real file and make the others symlinks to it (ln -s AGENTS.md CLAUDE.md), or a one-line '@AGENTS.md' import on Windows
  WARN  I401  AGENTS.md:83  index line is too long (82 wide, budget 60): Offline recipe app for one family, with ...
               -> one sentence of what it is; details go in the project's own files
  WARN  B131  projects/web/STATUS.md  STATUS body is 123 lines (budget 100)
               -> move superseded progress into the '## Archive' (## 归档) section at the bottom
  WARN  S302  projects/web/STATUS.md  no 'Next entry' heading near the top
               -> add '## Next entry' (## 下次入口): where the next session starts

1 error, 3 warnings, 0 info · 4 folders with instruction files
```

It is read-only, needs only Python 3.8+, and checks size budgets, `AGENTS.md`/`CLAUDE.md` links, STATUS hand-off headings, index line length and dates, broken paths and links, memory files nothing points to, and the same line written in two files. `--json` for agents, `--strict` for CI. Every code is explained in [`references/maintain.md`](skills/ai-workspace/references/maintain.md).

## Supported agents

Checked against each vendor's documentation in October 2026.

| Agent | Reads rules from | Skill folder (user-wide) | Extra step |
|---|---|---|---|
| [Claude Code](https://code.claude.com/docs/en/memory) | `CLAUDE.md` (link to `AGENTS.md`); `AGENTS.md` directly since v2.1.277 | `~/.claude/skills/` | Optional: `autoMemoryDirectory` → `<workspace>/memory` |
| [Codex](https://learn.chatgpt.com/docs/agent-configuration/agents-md) | `AGENTS.md`, git root down to the current folder | `~/.agents/skills/` | — |
| [Gemini CLI](https://geminicli.com/docs/cli/gemini-md/) | `GEMINI.md`; `AGENTS.md` once listed in `context.fileName` | `~/.gemini/skills/` or `~/.agents/skills/` | One setting, or `GEMINI.md` links |
| [Cursor](https://cursor.com/docs/context/rules) | `AGENTS.md`, root and sub-folders | `~/.cursor/skills/` or `~/.agents/skills/` | — |
| [OpenCode](https://opencode.ai/docs/rules/) | nearest `AGENTS.md` (`CLAUDE.md` as fallback) | `~/.config/opencode/skills/` or `~/.agents/skills/` | — |
| [GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/add-custom-instructions) | `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` | `~/.copilot/skills/` or `~/.agents/skills/` | — |
| Windsurf, Aider, others | not verified | not verified | If it reads `AGENTS.md`, nothing |

Per-agent loading details and sources: [`references/agents.md`](skills/ai-workspace/references/agents.md).

## Manual install

```bash
git clone https://github.com/Oldcircle/ai-workspace
mkdir -p ~/.agents/skills ~/.claude/skills
cp -R ai-workspace/skills/ai-workspace ~/.agents/skills/            # Codex, Gemini CLI, Cursor, OpenCode, Copilot
ln -s ~/.agents/skills/ai-workspace ~/.claude/skills/ai-workspace   # Claude Code
```

Then ask your agent to "set up an AI workspace", or run the scaffold yourself:

```bash
python3 ~/.agents/skills/ai-workspace/scripts/scaffold.py init ~/workspace --lang en
```

## FAQ

<details>
<summary><b>Why isn't this just a skill?</b></summary>

A skill is only loaded by an agent that has it installed. If resuming your work depended on the skill, losing the agent would lose the method too. So the skill does the setup and the checking, and everything needed to resume is written into the workspace itself: the root `AGENTS.md` tells any agent how to continue, even one that has never heard of this project.
</details>

<details>
<summary><b>How is this different from Claude Code's memory, or ChatGPT's?</b></summary>

Built-in memory belongs to one product. Claude Code's auto memory sits in `~/.claude/projects/…`, outside your project, and other tools don't read it; ChatGPT's memory sits in your account. Both are useful, but they don't move with you. Here the memory is a folder you own, versionable with git, readable by any agent. If you use Claude Code, you can point its auto memory at the workspace (`autoMemoryDirectory`) so it writes into the same `memory/` folder everyone else reads.
</details>

<details>
<summary><b>I switched from Claude Code to Codex and it doesn't know my preferences. Why?</b></summary>

Claude Code's own memory (`MEMORY.md` and its entries) is kept in `~/.claude/projects/<project>/memory/`, a private folder only Claude Code reads. Anything written there is gone the day you switch tools. Keep preferences and cross-project lessons in the workspace's `memory/` folder instead: the root `AGENTS.md` tells every agent to read `memory/MEMORY.md`. When adopting an existing workspace, the agent copies those private entries into `memory/` (originals stay). To make Claude Code write new entries there as well, set `"autoMemoryDirectory": "<workspace>/memory"` in `~/.claude/settings.json`.
</details>

<details>
<summary><b>Does it work on Windows?</b></summary>

Yes. In WSL everything works as on Linux. On native Windows, creating symlinks needs Developer Mode or an administrator shell, and Git for Windows checks symlinks out as text files unless `core.symlinks=true`. Without symlinks the scaffold writes `CLAUDE.md` as a single `@AGENTS.md` line, which Claude Code reads as an import. Avoid keeping two separate copies; lint reports that as an error.
</details>

<details>
<summary><b>Do I have to be a programmer?</b></summary>

No. The `minimal` layout (projects, notes, memory, archive) suits writing, research or any work you do with an agent. You never need to run the scripts yourself; the agent does.
</details>

<details>
<summary><b>Will it touch my existing files?</b></summary>

Init never overwrites. Adopt reads everything first, shows a plan, and changes nothing until you agree; files it rewrites are backed up to `_archive/`, and "delete" always means "move to `_archive/`". Rule files that came with someone else's repository are left alone.
</details>

<details>
<summary><b>Doesn't loading all these files cost tokens?</b></summary>

Less than what most people have now. Only the router (under 200 lines) and the memory index (under 150 lines) load every session; project files load when the agent works in that project, and details load only when a hook points to them. The budgets exist because long always-loaded files cost tokens on every turn and get followed less.
</details>

<details>
<summary><b>Can I use it in a shared team repository?</b></summary>

The project-level parts, yes: `AGENTS.md`, `STATUS.md` and `PLAN.md` work in any repo, and the lint runs in CI with `--strict`. Personal preferences belong in your own `memory/`, not in the team's files.
</details>

## Repository layout

```
ai-workspace/
├── INSTALL.md                 # read by agents during setup
├── skills/ai-workspace/       # the skill: copy this folder
│   ├── SKILL.md
│   ├── references/            # method, agents, init, adopt, maintain, writing
│   ├── templates/{zh,en}/     # root router, project, PLAN, STATUS, MEMORY, memory entry, notes index
│   └── scripts/               # scaffold.py, lint.py (standard library only)
├── tests/                     # python3 -m unittest discover -s tests
└── assets/readme/
```

## Contributing

Issues and pull requests are welcome. Agent behaviour changes often: if a vendor's docs now say something different from [`references/agents.md`](skills/ai-workspace/references/agents.md), a PR with the link is the most useful contribution. Changes to `lint.py` need a test that fails without the change and one showing a clean workspace stays clean.

## License

MIT, see [LICENSE](LICENSE).
