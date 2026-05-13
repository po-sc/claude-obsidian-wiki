# Claude × Obsidian Wiki

Auto-updating knowledge base powered by Claude Code. Every significant task Claude completes is automatically written into your Obsidian vault — no reminders needed.

> **Inspired by** Andrej Karpathy's Claude memory gist — this repo expands the idea into a full Obsidian-based wiki with structured project/topic pages, a session log, raw source storage, and lint tooling.
> Original gist: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

---

## What this is

A global `CLAUDE.md` that teaches Claude Code to:
- **Auto-update** your Obsidian wiki after every meaningful task (without being asked)
- **Save raw sources** to `raw/` before processing them
- **Create topic pages** when working with a technology non-trivially
- **Maintain a chronological log** of everything done
- **Prevent broken links** — validates `[[links]]` before writing them

---

## Quick start — fresh install

### 1. Install Claude Code

```bash
npm install -g @anthropic/claude-code
```

### 2. Clone this repo and run setup

```bash
git clone https://github.com/po-sc/claude-obsidian-wiki
cd claude-obsidian-wiki
bash setup.sh
```

The script will ask where to put the vault, copy it there, install `~/.claude/CLAUDE.md`, and patch the vault path automatically.

### 3. Done

Start Claude Code in any project directory. It will read `index.md` at the start of each session and update the wiki after significant tasks — no commands needed.

---

## Adding to an existing Claude Code setup

If you already use Claude Code and don't want to run the full setup:

### Step 1 — Copy the vault template

```bash
# Pick any location inside or alongside your existing Obsidian vault
VAULT="$HOME/Documents/MyVault/Claude"

git clone https://github.com/po-sc/claude-obsidian-wiki /tmp/claude-wiki
cp -r /tmp/claude-wiki/vault/. "$VAULT/"
```

### Step 2 — Update your existing `~/.claude/CLAUDE.md`

**Option A — you don't have one yet:**
```bash
mkdir -p ~/.claude
cp /tmp/claude-wiki/claude/CLAUDE.md ~/.claude/CLAUDE.md
# Then edit it: set VAULT path and add your projects at the bottom
```

**Option B — you already have `~/.claude/CLAUDE.md`:**

Append the wiki rules to your existing file:
```bash
echo "" >> ~/.claude/CLAUDE.md
cat /tmp/claude-wiki/claude/CLAUDE.md >> ~/.claude/CLAUDE.md
```

Then open `~/.claude/CLAUDE.md` and:
1. Find the `VAULT=` line and set the correct path
2. Remove any duplicate sections if you had overlapping rules
3. Add your projects to the `## Project pages` section at the bottom

### Step 3 — Tell Claude about the wiki in your first session

On the first session after setup, say:

> "Read index.md and initialize the wiki for project X"

Claude will load the empty index, create the first project page, and from that point on updates happen automatically.

---

## Vault structure

```
vault/
├── index.md          # Master index — Claude reads this first every session
├── log.md            # Append-only session log
├── raw/              # Raw sources (Claude saves here on every Ingest)
│   └── README.md
├── projects/         # One page per project
└── topics/           # One page per technology / pattern
```

### How it grows

- `projects/<ProjectName>.md` — architecture, decisions, API, screens, history
- `topics/<Technology>.md` — non-obvious behavior, patterns, gotchas
- `log.md` — append-only record: what was done, which pages changed, key facts

### Operations

| Say this | What happens |
|---|---|
| *(just work normally)* | Claude auto-updates wiki after significant tasks |
| "Ingest this file / link / text" | Claude saves raw → writes structured page → updates index |
| "How did we do X?" / "Remind me of Y" | Claude reads relevant pages → answers with `[[citations]]` |
| "Lint the wiki" | Claude finds broken links, orphans, stale facts → fixes them |

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

- **Don't fight the automation** — if Claude writes something wrong, correct it and it won't repeat
- **`raw/` fills up over time** — intentional, these are your source-of-truth originals
- **Lint occasionally** — "lint the wiki" every few weeks catches stale facts and broken links
- **Cross-link liberally** — `[[topics/Foo]]` from any page; Claude creates the stub if it doesn't exist

---

## Requirements

- Claude Code (any version)
- Obsidian (optional — the vault is plain markdown, works without it)
- macOS / Linux (paths use Unix conventions)
