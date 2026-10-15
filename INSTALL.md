# Install ai-workspace

> **Human?** You don't need to read this. Send this sentence to your AI (Claude Code, Codex, Cursor, Gemini CLI, OpenCode, Copilot CLI…):
>
> ```text
> Set up my workspace with ai-workspace, following https://raw.githubusercontent.com/Oldcircle/ai-workspace/main/INSTALL.md
> ```
>
> **中文用户**：把下面这句发给你的 AI 就行，不用往下看：
>
> ```text
> 帮我按 ai-workspace 把工作区搭好，照这份说明做：https://raw.githubusercontent.com/Oldcircle/ai-workspace/main/INSTALL.md
> ```
>
> Keep the link the first time: an agent that has never seen this project does not know what "ai-workspace" means. Once the skill is installed, the short form ("set up my workspace with ai-workspace", 「帮我按 ai-workspace 把工作区搭好」) is enough.

---

**Agent: these instructions are for you.** Follow the steps in order. Speak to the user in the language they used. Ask before anything that deletes, overwrites or moves the user's files, or changes an agent's settings.

## Step 1: Know where you are

1. **Which agent are you?** You know your own product name. If you are not sure, ask the user. Look up your row in the table in step 2.
2. **Which OS?** Run `uname -s` (macOS: `Darwin`, Linux: `Linux`). On Linux, `grep -qi microsoft /proc/version` succeeding means WSL. In PowerShell or cmd you are on native Windows.
3. **Tools.** Check `python3 --version` (3.8+; on Windows try `py -3 --version`) and `git --version`. Python runs the setup and lint scripts; without it you can still follow the templates by hand.

## Step 2: Install the skill

Get the repository into a temporary folder:

```bash
git clone --depth 1 https://github.com/Oldcircle/ai-workspace "${TMPDIR:-/tmp}/ai-workspace"
```

No git? Download and unpack `https://github.com/Oldcircle/ai-workspace/archive/refs/heads/main.tar.gz` (or `.zip` on Windows) instead.

Copy the folder `skills/ai-workspace` (the whole folder, including `scripts/`, `templates/`, `references/`) to the skill folder of your agent. User-wide is the default:

| You are | Copy to (user-wide) | Verified |
|---|---|---|
| Claude Code | `~/.claude/skills/ai-workspace/` | [docs](https://code.claude.com/docs/en/skills) |
| Codex | `~/.agents/skills/ai-workspace/` | [docs](https://learn.chatgpt.com/docs/build-skills) |
| Gemini CLI | `~/.gemini/skills/ai-workspace/` or `~/.agents/skills/ai-workspace/` | [docs](https://geminicli.com/docs/cli/skills/) |
| Cursor | `~/.cursor/skills/ai-workspace/` or `~/.agents/skills/ai-workspace/` | [docs](https://cursor.com/docs/skills) |
| OpenCode | `~/.config/opencode/skills/ai-workspace/` or `~/.agents/skills/ai-workspace/` | [docs](https://opencode.ai/docs/skills/) |
| GitHub Copilot | `~/.copilot/skills/ai-workspace/` or `~/.agents/skills/ai-workspace/` | [docs](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills) |
| Anything else | not verified: ask the user where their agent looks for skills, or skip installing and read `SKILL.md` straight from the clone | — |

If the user works with more than one agent, install once for all of them:

```bash
mkdir -p ~/.agents/skills ~/.claude/skills
cp -R "${TMPDIR:-/tmp}/ai-workspace/skills/ai-workspace" ~/.agents/skills/
ln -s ~/.agents/skills/ai-workspace ~/.claude/skills/ai-workspace   # Claude Code
```

`~/.agents/skills/` is read by Codex, Gemini CLI, Cursor, OpenCode and Copilot; `~/.claude/skills/` by Claude Code. On native Windows, copy the folder twice instead of using `ln -s`.

If a folder named `ai-workspace` already exists there, show the user and ask before replacing it.

**If you cannot write to the skill folder** (a sandbox blocks your home folder or `.agents/`, or the user says no): ask the user to approve the copy, or give them the one `cp -R` line above to run themselves. Meanwhile run the scripts straight from the temporary clone and keep that clone until step 6. The workspace itself does not need the skill: everything an agent needs to continue is written into the workspace files. Do not write installer scripts, notes about the install, or paths to the clone into the user's workspace.

Check the install:

```bash
python3 ~/.agents/skills/ai-workspace/scripts/lint.py --version    # use the path you installed to
```

Many agents only discover new skills at startup. You do not need a restart: from here on, read `SKILL.md` from the installed folder yourself and follow it. Call that folder `<skill>` below (the clone's `skills/ai-workspace` if you could not install).

## Step 3: Ask the user (one message)

Skip any question the user's message already answers (for example "in the current folder", "two projects: a budget app and a blog"). If you cannot ask at all (a non-interactive run), use the defaults below and list them in your hand-over.

1. **Where is your workspace?** The folder that holds (or will hold) all your projects. Suggest `~/workspace`; if they already keep projects in one folder, that is the one.
2. **Chinese or English templates?** Default to the language they are writing in.
3. **Which other AI agents do you use?** You need this for step 5. Default: assume Claude Code too (the `CLAUDE.md` links cost nothing) and change no agent settings.
4. **Which projects should it track?** Existing folders to bring in, or new ones to start. Default: the ones they mentioned, none otherwise.

## Step 4: Set it up

Read `<skill>/SKILL.md`, then pick the mode by looking at the folder the user named:

- **The folder does not exist, or is empty or nearly empty** → init. Follow `<skill>/references/init.md`. The core command:

  ```bash
  python3 <skill>/scripts/scaffold.py init <root> --lang zh --dry-run   # preview
  python3 <skill>/scripts/scaffold.py init <root> --lang zh
  ```

  On native Windows add `--no-symlink`. Then, for each project from step 3:

  ```bash
  python3 <skill>/scripts/scaffold.py project <root>/projects/<name> --lang zh
  ```

  and fill in its `AGENTS.md`, `PLAN.md` and `STATUS.md` from what you know (for a brand-new project, "Next entry" is the first question to settle with the user), then add one row per project to the root project index.

- **The folder already has projects, notes or an `AGENTS.md`/`CLAUDE.md`** → adopt. Follow `<skill>/references/adopt.md`: inventory read-only, show the user a plan, wait for a yes, back up, then migrate. Do not delete anything.

- **It already has a root router with a budgets section** → maintain. Run the lint (`references/maintain.md`) and offer fixes.

## Step 5: Make the other agents see the same files

The workspace uses `AGENTS.md` as the real rule file and `CLAUDE.md` as a link to it. For the agents the user named in step 3:

| Agent | What it needs | Source |
|---|---|---|
| Claude Code | Nothing: it reads `CLAUDE.md` (the link). Optional, ask first: `"autoMemoryDirectory": "<root>/memory"` in `~/.claude/settings.json`, so Claude's own memory is written into the workspace where other agents can read it. | [memory docs](https://code.claude.com/docs/en/memory) |
| Codex | Nothing: reads `AGENTS.md`. It loads from the git root down to the start folder, so inside a project repo it sees only that project's file; the project template points back to the root. | [AGENTS.md guide](https://learn.chatgpt.com/docs/agent-configuration/agents-md) |
| Gemini CLI | Reads `GEMINI.md` by default. Ask, then add `"context": {"fileName": ["AGENTS.md", "GEMINI.md"]}` to `~/.gemini/settings.json`; or create `GEMINI.md` links with `scaffold.py ... --gemini`. | [GEMINI.md docs](https://geminicli.com/docs/cli/gemini-md/) |
| Cursor | Nothing: reads `AGENTS.md` in the root and sub-folders. | [rules docs](https://cursor.com/docs/context/rules) |
| OpenCode | Nothing: reads `AGENTS.md` (nearest one). | [rules docs](https://opencode.ai/docs/rules/) |
| Copilot CLI | Nothing: reads `AGENTS.md`, `CLAUDE.md` and `GEMINI.md`. | [CLI docs](https://docs.github.com/en/copilot/how-tos/copilot-cli/add-custom-instructions) |
| Others | Not verified. If it reads `AGENTS.md`, nothing to do; otherwise ask the user which file name it reads and link that name to `AGENTS.md`. | — |

## Step 6: Verify and hand over

```bash
python3 <skill>/scripts/lint.py <root>
```

Fix anything reported as an error. Then tell the user, in their language and in a few lines:

- where the workspace is and what was created or changed (and where backups are, if you adopted);
- the one habit: **open any agent in that folder and say "continue"** (「接着做」); it reads the rules, finds the latest `STATUS.md` and picks up from "Next entry";
- that `python3 <skill>/scripts/lint.py <root>` checks the files every week or two;
- anything you skipped or assumed (the skill not installed, defaults you picked, settings you did not change);
- if a user-level instruction file (`~/.codex/AGENTS.md`, `~/.claude/CLAUDE.md`, `~/.gemini/GEMINI.md`) points agents to a different workspace, say so: agents will read both, and the user should decide which one is current.

Delete the temporary clone when done (keep it only if the skill is not installed yet and the user still needs it).

## Windows notes

- WSL behaves like Linux: run everything inside WSL, symlinks work.
- Native Windows needs Developer Mode (or an administrator shell) to create symlinks ([Microsoft](https://blogs.windows.com/windowsdeveloper/2016/12/02/symlinks-windows-10/)). Git for Windows checks symlinks out as plain text files unless `core.symlinks=true` ([Git for Windows](https://gitforwindows.org/symbolic-links)).
- Without symlinks, `scaffold.py --no-symlink` writes `CLAUDE.md` as one line, `@AGENTS.md`, which Claude Code expands as an import. Never keep two separate copies; lint flags that as L201.
- Use `py -3` if `python3` is not found.

---

## 中文速览（给 agent）

1. 判断自己是哪个 agent、什么系统（macOS / Linux / WSL / 原生 Windows），有没有 Python 3.8+。
2. 把仓库 clone 到临时目录，把 `skills/ai-workspace` 整个文件夹复制到自己的 skill 目录（见上面的表；多个 agent 都用就放 `~/.agents/skills/`，再给 `~/.claude/skills/` 建个软链）。已有同名文件夹先问。写不进去（沙箱拦了家目录或 `.agents/`）就请用户批准或自己跑那行 `cp -R`，先直接用临时 clone 里的脚本；别往用户工作区里写安装脚本或 clone 的路径。工作区本身不依赖 skill。
3. 一次问清：工作区放哪、模板用中文还是英文、平时还用哪些 AI、要管哪些项目。用户话里已经说了的不再问；没法问（非交互运行）就用默认值，交接时说明。
4. 看工作区现状选模式：空的走 init（`scaffold.py init`，再给每个项目跑 `scaffold.py project`、填好三份文件、在根目录索引加一行），已经有项目的走 adopt（先盘点、出计划、用户点头、备份，再迁移，不删任何文件），已经搭好的走 maintain（跑 lint）。
5. 按第 5 步让其他 agent 也读到同一份 `AGENTS.md`。改任何 agent 的 settings 之前先问。
6. 跑 `lint.py` 到 0 个 error，告诉用户：以后打开任何 AI，在工作区里说「接着做」就行；没装上的、用了默认值的要说；用户级规则文件（如 `~/.codex/AGENTS.md`）指向别的工作区也要提醒。
