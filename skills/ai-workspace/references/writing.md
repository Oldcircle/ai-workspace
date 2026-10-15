# Writing rule files, STATUS.md and index lines

Read this before writing or editing a root router, a project `AGENTS.md`, a `STATUS.md` or any index.

## Why this exists

Workspaces bloat the same way every time. An index line has no hard limit, so an agent afraid of losing information writes a paragraph and calls it one line. The next agent copies the format it sees, so a 500-character line produces a 600-character one. The same status gets written into the index, the memory, the project file and STATUS.md, and they start to disagree. None of this raises an error; agents just follow the files less.

## Four rules of thumb

1. **Every word in an always-loaded file is paid for in every session.** The root router and `MEMORY.md` are not documents, they are the opening speech of every meeting. The longer they are, the less of them is followed.
2. **Pushing detail down costs nothing.** Sub-folder files load only when needed; linked files load only when opened. The answer to "I don't want to lose this" is a file plus a pointer, never a longer index line.
3. **The reader is the next agent, not the user.** "All green", "shipped in one go", "verified live" tell the next session nothing it can act on. Write facts and entry points, not victory reports.
4. **What is already there is the example.** Before writing, look at the neighbouring entries. If one is bloated, trim it first, then write yours at the normal length.

## Tense decides where a sentence goes

- `AGENTS.md` is **present tense**: what the project is, how to run it, the conventions. Test: will this still be true in six months? If not, it does not belong here.
- `STATUS.md` is **where things stand now**: what is done, what is next, what is undecided. When newer progress supersedes an entry, move it to `## Archive` at the bottom with a date.
- **Dated past tense** ("on 3 May we migrated…") goes only into git log and the STATUS archive.

## Index lines

Root project index, `MEMORY.md`, `notes/_index.md` all follow the same rule: a hook lets the next session decide whether to open something; it does not replace opening it.

- Allowed: name, path or link, one sentence (about 30 Chinese / 60 Latin characters), status label or a short "next" phrase.
- Not allowed: dates, versions, feature lists, the whole tech stack, test counts, adjectives of achievement.
- Good: `| Recipe box | projects/recipe-box | Offline recipe app for one family | 🚧 |`
- Bad: `| Recipe box | projects/recipe-box | Offline-first SwiftUI + SwiftData recipe app, v0.3 shipped 2026-04-02 with 112 tests green, next: sync, sharing, widgets, Android port… | 🚧 |`

## STATUS.md shape

```markdown
# <project> status

## Current state
- what works now, what is half done (a few bullets)

## Next entry
- the first concrete thing the next session should do, with file paths

## Open decisions
- questions only the user can answer

## Archive
- 2026-05-03 superseded entry, one line
```

A new session reads the first 20 lines and knows where to start. If it has to read 300 lines of history first, the hand-off failed.

## Self-check before writing (four questions)

1. Where is the **one home** of this fact? Is it already written there?
2. Is the target file **over budget**? If so, trim before adding.
3. Am I writing **present or past tense**? Past tense goes to git log or the archive.
4. Will my entry be **longer than its neighbours**? Then I am packing in detail; move it down and leave a hook.
