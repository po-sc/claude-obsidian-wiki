# Claude × Obsidian Wiki

Auto-updating knowledge base powered by Claude Code. Every significant task Claude completes is automatically written into your Obsidian vault — no reminders needed.

## What this is

A global `CLAUDE.md` that teaches Claude Code to:
- **Auto-update** your Obsidian wiki after every meaningful task (without being asked)
- **Save raw sources** to `raw/` before processing them
- **Create topic pages** when working with a technology non-trivially
- **Maintain a chronological log** of everything done
- **Prevent broken links** — validates `[[links]]` before writing them

## Setup

### 1. Install Claude Code

```bash
npm install -g @anthropic/claude-code
```

### 2. Set up the vault

Copy the `vault/` folder to wherever your Obsidian vault lives (or create a subfolder inside an existing vault):

```bash
cp -r vault/ ~/Documents/MyVault/Claude/
```

Open `vault/index.md` and update `VAULT` path at the top to match where you put it.

### 3. Install the global CLAUDE.md

```bash
mkdir -p ~/.claude
cp claude/CLAUDE.md ~/.claude/CLAUDE.md
```

Then edit `~/.claude/CLAUDE.md` and update:
- `VAULT` path to match where you put the vault in step 2
- The `## Страницы проектов` section at the bottom with your own projects

### 4. Done

Start Claude Code in any project. It will automatically read `index.md` at the start of each session and update the wiki after significant tasks.

---

## Vault structure

```
vault/
├── index.md          # Master index — read first every session
├── log.md            # Chronological log of all sessions
├── raw/              # Raw sources (Claude saves here automatically on Ingest)
│   └── README.md
├── projects/         # One page per project
└── topics/           # One page per technology/pattern
```

### How it grows

- `projects/<ProjectName>.md` — architecture, decisions, API, screens
- `topics/<Technology>.md` — non-obvious behavior, patterns, gotchas
- `log.md` — append-only record of what was done and when

### Operations

| Command | What happens |
|---|---|
| Just work | Claude auto-updates wiki after significant tasks |
| "Ingest this file/link/text" | Claude saves raw source → writes structured page → updates index |
| "Query: how did we do X?" | Claude reads index → reads pages → answers with citations |
| "Lint the wiki" | Claude finds broken links, orphans, contradictions → fixes |

---

## Example wiki page (topic)

```markdown
---
tags: [flutter, dio, http]
date: 2026-01-01
updated: 2026-01-01
source_count: 1
---

# Dio — Flutter HTTP Client

HTTP client for Flutter with interceptors and FormData support.

→ [[projects/MyApp]] — where we use it

## How we use it
## Non-obvious behavior
## Decisions and patterns
```

---

## Tips

- **Don't fight the automation** — if Claude writes something wrong to the wiki, just correct it and Claude will learn from the correction
- **`raw/` fills up over time** — it's intentional. These are your source documents for future re-ingestion
- **Lint occasionally** — ask Claude to "lint the wiki" every few weeks to catch stale facts and broken links
- **Cross-link liberally** — `[[topics/Foo]]` from any project page; Claude will create the page if it doesn't exist

---

## Requirements

- Claude Code (any version)
- Obsidian (optional — the vault is plain markdown, works without Obsidian)
- macOS / Linux (paths use Unix conventions)
