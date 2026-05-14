# Claude × Obsidian Wiki

Auto-updating knowledge base powered by Claude Code. Every significant task Claude completes is automatically written into your Obsidian vault — no reminders needed.

> **Inspired by** Andrej Karpathy's Claude memory gist — this repo expands the idea into a full Obsidian-based wiki with structured project/topic pages, a session log, raw source storage, and lint tooling.
> Original gist: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

---

## What this is

A global `CLAUDE.md` that teaches Claude Code to:
- **Auto-update** your Obsidian wiki after every meaningful task (without being asked)
- **Know what to read** at session start based on the working directory
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

The script will:
- Ask where to put the vault and copy it there
- Install `~/.claude/CLAUDE.md` and patch the vault path automatically

### 3. Map your projects

Open `~/.claude/CLAUDE.md` and fill in the **Project pages** table:

```
| Working directory (partial match) | Wiki pages to read (in order) |
|---|---|
| /Users/me/my-app/                 | projects/MyApp/Overview.md, projects/MyApp/Backend.md |
| /Users/me/scripts/whisper/        | projects/Whisper.md |
```

This is what lets Claude know which wiki pages to load when you open a project.

### 4. First session

Start Claude Code inside any mapped project directory. It will automatically read the wiki and begin with full context — no commands needed.

---

## Adding to an existing Claude Code setup

If you already use Claude Code and have a `~/.claude/CLAUDE.md`:

### Step 1 — Copy the vault template

```bash
VAULT="$HOME/Documents/MyVault/Claude"   # change this

git clone https://github.com/po-sc/claude-obsidian-wiki /tmp/claude-wiki
cp -r /tmp/claude-wiki/vault/. "$VAULT/"
```

### Step 2 — Merge CLAUDE.md manually

**Don't blindly append** — it will duplicate sections. Instead, open both files and copy the sections you want:

```bash
open ~/.claude/CLAUDE.md
open /tmp/claude-wiki/claude/CLAUDE.md
```

Copy these sections into your existing file:
- `## HARD RULE` — the auto-update rule
- `## Start` — the session start behavior  
- `## Project pages` — the directory→wiki mapping table (fill in your own projects)
- `## Ingest / Query / Lint` — the wiki operations
- `## raw/ — rules` and `## Rules for [[links]]`

Then set the `VAULT=` path at the top.

### Step 3 — Done

Claude will now auto-update the wiki after significant tasks. The first session in each project directory will automatically load the right wiki pages.

---

## Vault structure

```
vault/
├── index.md          # Master index — Claude reads this first every session
├── log.md            # Append-only session log
├── raw/              # Raw sources (Claude saves here on every Ingest)
│   └── README.md
├── projects/         # One page per project (or a folder with multiple pages)
└── topics/           # One page per technology / pattern
```

### How it grows

- `projects/<Name>.md` or `projects/<Name>/` — architecture, decisions, API, history
- `topics/<Technology>.md` — non-obvious behavior, patterns, gotchas
- `log.md` — append-only: what changed, which pages updated, key facts

### Operations

| Say this | What happens |
|---|---|
| *(just work normally)* | Claude auto-updates wiki after significant tasks |
| "Ingest this file / link / text" | Claude saves raw → writes structured page → updates index |
| "How did we do X?" / "Remind me of Y" | Claude reads relevant pages → answers with `[[citations]]` |
| "Lint the wiki" | Claude finds broken links, orphans, stale facts → fixes them |

---

## Example project with multiple wiki pages

For a project with backend + frontend, create a folder:

```
projects/MyApp/
├── Overview.md     ← start here (architecture, roles, stack)
├── Frontend.md     ← screens, routing, API calls
└── Backend.md      ← endpoints, DB schema, auth
```

Then in `## Project pages`:
```
| /Users/me/my-app/ | projects/MyApp/Overview.md, projects/MyApp/Frontend.md, projects/MyApp/Backend.md |
```

Claude reads them in that order at session start.

---

## Tips

- **Don't fight the automation** — if Claude writes something wrong, correct it and it won't repeat
- **`raw/` fills up over time** — intentional, these are your source-of-truth originals
- **Lint occasionally** — "lint the wiki" every few weeks catches stale facts and broken links
- **Cross-link liberally** — `[[topics/Foo]]` from any page; Claude creates the stub if missing

---

## Requirements

- Claude Code (any version)
- Obsidian (optional — the vault is plain markdown, works without it)
- macOS / Linux (paths use Unix conventions)
