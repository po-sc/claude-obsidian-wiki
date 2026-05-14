# Claude × Obsidian Wiki

> A global `CLAUDE.md` that gives Claude Code a persistent memory — automatically maintained, zero effort on your part.

**Inspired by** Andrej Karpathy's Claude memory gist:
https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

---

## The problem

Claude Code is incredibly capable — but it starts every session from zero. It doesn't remember what you built last week, why you made a particular architectural decision, or that you already spent two hours debugging that exact issue. You end up re-explaining your project from scratch, and Claude re-discovers the same things over and over.

The usual workaround is to dump context into the prompt manually. That's tedious, easy to forget, and doesn't scale.

## The solution

This repo gives Claude Code a **persistent wiki** — a structured Obsidian vault that Claude reads at the start of every session and updates automatically after every meaningful task.

You don't maintain it. Claude does.

After a week of working together, your wiki looks like this:

```
projects/
  MyApp/
    Overview.md      ← architecture, roles, stack decisions
    Frontend.md      ← every screen, every API call, patterns used
    Backend.md       ← endpoints, DB schema, auth, known issues

topics/
  Dio.md             ← non-obvious behavior of your HTTP client
  Spring Boot.md     ← CORS gotchas, transaction patterns
  python-docx.md     ← how you generate Word docs, the patching trick

log.md               ← chronological record of everything done
raw/                 ← original sources Claude ingested
```

Every page written by Claude, from your actual work. No copy-paste, no manual documentation.

---

## What Claude does automatically

**At the start of every session** — reads `index.md` and all pages for your current project (detected from the working directory). Begins with full context, never asks "remind me what we're building".

**After every significant task** — updates the relevant project page, creates a topic page if you used a technology non-trivially, appends to `log.md`. All without being asked.

**When you give it a source** ("ingest this file / link / doc") — saves the raw source to `raw/`, writes a structured wiki page, updates the index.

**When you ask a question** ("how did we handle auth?", "what was the decision on X?") — reads the wiki, answers with citations like `[[Flutter.md]]`, and documents new findings if any.

**Occasionally** ("lint the wiki") — finds broken links, orphan pages, stale facts, missing cross-references, and fixes them.

---

## Real example

Here's what happens when you open a project:

```
You:    [opens Claude Code in ~/my-project/]

Claude: [reads index.md → reads MyApp/Overview.md, MyApp/Frontend.md, 
         MyApp/Backend.md automatically]
        
        Ready. We're working on MyApp — Flutter frontend + Spring Boot backend.
        Last session: fixed the CORS issue in SecurityConfig and added 
        conflict detection for bookings (HTTP 409). Open tasks: payment 
        integration is still a stub.
        
        What are we doing today?
```

Then after you work together for an hour:

```
Claude: [updates MyApp/Backend.md with the new endpoint]
        [creates topics/WebSocket.md because you set up STOMP for the first time]
        [appends to log.md:
          ## [2026-05-15] feature | WebSocket chat on bookings
          **Pages:** [[MyApp/Backend]], [[topics/WebSocket]]
          **Key facts:**
          - STOMP over WebSocket, endpoint /ws
          - Group thread per booking: client + engineer + owner
          - Reconnect logic in Flutter: exponential backoff, max 5 attempts
        ]
```

---

## Setup

### Option 1 — Ask Claude Code to do it for you

Open Claude Code in any directory and say:

> "Set up the Obsidian wiki integration from https://github.com/po-sc/claude-obsidian-wiki — clone it, run setup, and help me configure the project mapping for this project"

Claude will handle the rest: clone the repo, run `setup.sh`, ask where your vault is, and help you fill in the project table.

### Option 2 — Run setup yourself

**Prerequisites:** Claude Code installed (`npm install -g @anthropic/claude-code`)

```bash
git clone https://github.com/po-sc/claude-obsidian-wiki
cd claude-obsidian-wiki
bash setup.sh
```

The script asks where to put the vault, copies it there, installs `~/.claude/CLAUDE.md`, and patches the vault path.

### Option 3 — Already have Claude Code set up?

```bash
VAULT="$HOME/Documents/MyVault/Claude"

git clone https://github.com/po-sc/claude-obsidian-wiki /tmp/claude-wiki
cp -r /tmp/claude-wiki/vault/. "$VAULT/"
```

Then open both files side by side and merge the sections you want into your existing `~/.claude/CLAUDE.md`:

```bash
open ~/.claude/CLAUDE.md
open /tmp/claude-wiki/claude/CLAUDE.md
```

### After setup — one required step

Open `~/.claude/CLAUDE.md` and fill in the **Project pages** table. This is what tells Claude which wiki pages to load when you open a project:

```
| Working directory       | Wiki pages to read (in order)                        |
|-------------------------|------------------------------------------------------|
| /Users/me/my-app/       | projects/MyApp/Overview.md, projects/MyApp/Backend.md|
| /Users/me/scripts/      | projects/Scripts.md                                  |
```

Without this table, Claude won't know which project you're in. Takes 2 minutes.

---

## Vault structure

```
vault/
├── index.md          ← master index, read first every session
├── log.md            ← append-only chronological log
├── raw/              ← original sources Claude ingested (never edited)
├── projects/         ← one page or folder per project
└── topics/           ← one page per technology / pattern
```

Projects with multiple pages use a folder:

```
projects/MyApp/
├── Overview.md     ← read first (architecture, roles, key decisions)
├── Frontend.md     ← screens, routing, API calls
└── Backend.md      ← endpoints, DB schema, security
```

Single-file projects just use `projects/ProjectName.md`.

---

## How to use it day-to-day

**Just work normally.** Claude handles the wiki.

A few phrases worth knowing:

| Say this | What happens |
|---|---|
| "Ingest this" + file/link/text | Claude saves raw → writes structured wiki page → updates index |
| "How did we handle X?" | Claude reads wiki → answers with page citations |
| "Remind me of the architecture" | Claude reads all project pages → gives full summary |
| "Lint the wiki" | Claude audits all pages → fixes broken links, stale facts, orphans |

---

## Tips

**Don't fight the automation.** If Claude writes something wrong to the wiki, just correct it and say why. It will update the page and won't make the same mistake again.

**The `raw/` folder fills up over time.** That's intentional — these are your source-of-truth originals. If you ever re-process a document, the raw version is there.

**Works without Obsidian.** The vault is plain markdown. Any editor works. Obsidian just gives you a nice graph view and backlink navigation.

**Lint occasionally.** Once every few weeks, say "lint the wiki" — Claude will find pages that reference removed features, broken `[[links]]`, and pages no one links to anymore.

**The log is searchable.** `log.md` has a consistent format: `## [YYYY-MM-DD] type | title`. After a month, it becomes a useful record of what was actually built and when.

---

## Requirements

- Claude Code (any version) — https://claude.ai/code
- macOS or Linux (paths use Unix conventions)
- Obsidian (optional) — https://obsidian.md
