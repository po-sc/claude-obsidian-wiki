# Claude — Global Instructions

## Obsidian Wiki

**Vault path — update this after setup:**
```bash
VAULT='/path/to/your/obsidian/vault/Claude'
```
> Always use single quotes — the path may contain spaces.

---

## HARD RULE — wiki updates automatically, without reminders

**A task is not complete until the wiki is updated.**

### What counts as significant (always update):
- Added/changed a screen, endpoint, or data model
- Fixed an architectural bug or race condition
- Made a decision about structure, pattern, or stack
- Discovered non-obvious framework behavior
- Created/changed an important file (config, script, CLAUDE.md)

### What does NOT need an update:
- Typo / color / text fix
- Discussion without a concrete outcome
- Answering a question without changing code

### Order after a significant task:
1. Update the project page in `projects/` — add facts, decisions, changes
2. If worked with a technology non-trivially → create/update `topics/<tech>.md`
3. If a new page was created → add to `index.md` immediately + update page count
4. Append to `log.md`

---

## Start — beginning of each session (automatic)

1. Read `index.md`
2. Find the working directory in the **Project pages** table below → read all project pages in the listed order
3. Begin work — don't ask "what are we doing?", context is already loaded

---

## Project pages

Map your working directories to wiki pages. Claude reads this at session start to know what to load.

| Working directory (partial match) | Wiki pages to read (in order) |
|---|---|
| `/path/to/my-project/` | `projects/MyProject/Overview.md`, `projects/MyProject/Backend.md` |
| `/path/to/other/` | `projects/OtherProject.md` |

**Reference — all wiki pages:**
```
projects/<ProjectName>/Overview.md   — architecture, stack, roles
projects/<ProjectName>/Frontend.md   — screens, API calls, patterns
projects/<ProjectName>/Backend.md    — endpoints, DB, security
```

When adding a new project: create wiki page(s) + add a row to the table above + add to `index.md`.

---

## Ingest — adding a new source

**When:** user provides a file, link, or text to study.

**Algorithm (strict order):**
1. **Create a source note in `raw/`** — FIRST, before any processing.
   `raw/` is Claude's **extra memory about sources**, not a dump of copies:
   - Name: `raw/YYYY-MM-DD-short-description.md`
   - Header:
     - `**Source:**` — absolute path to the file on disk (do NOT copy binaries / PDFs / large files — reference the path); if it's a link, the URL. A small text paste / chat can be included inline.
     - `**Project:**` — `[[projects/...]]`, which project it belongs to
   - Body: a **detailed extract of everything useful** from the source — facts, numbers, requirements, decisions, wording. Enough to answer questions later without reopening the original. Not a one-line "what is this file".
   - If a note already exists — extend it, don't duplicate
2. Study the source fully
3. Write/update page in `projects/` or `topics/`
4. Update `index.md` — entry + page count + date
5. Append to `log.md`

---

## After a task — log.md format

```
## [YYYY-MM-DD] <type> | <What was done>
**Pages:** [[page1]], [[page2]]
**Key facts:**
- <fact 1>
- <fact 2>
- <fact 3>
```

Types: `ingest` · `fix` · `feature` · `lint` · `query` · `refactor`

---

## Query — knowledge base lookup

**When:** "how did we do X", "what do we know about Y", "remind me of Z's architecture".

1. Read `index.md` → find relevant pages
2. Read those pages
3. Answer with `[[citations]]`
4. If the answer revealed something new and valuable → update/create a page + append to log.md
5. If just answering from already-documented info — no log entry needed

---

## Lint — wiki health check

**When:** "lint the wiki" / "check the wiki" / approximately every 20 sessions.

**Check for:**
- Contradictions between pages
- Stale facts (old versions, removed features)
- Orphan pages (no incoming links)
- Broken links (`[[topics/]]` is broken; `[[topics/Foo]]` without `Foo.md` is broken)
- Missing cross-references

**Algorithm:** read all pages → list problems → fix → append to log.md (type `lint`).

---

## Topics — technology knowledge

The `topics/` folder is about technologies, not projects.

**Create when:**
- Non-obvious framework behavior
- A solution that will be reused
- A pattern used in multiple places

**Format:**
```markdown
---
tags: [<tech>, ...]
date: YYYY-MM-DD
updated: YYYY-MM-DD
source_count: N
---

# <Technology>

Short description.

→ [[projects/...]] — where we use it

## How we use it
## Non-obvious behavior
## Decisions and patterns
```

---

## Project page format

```yaml
---
tags: [<project>, <tech>, ...]
date: YYYY-MM-DD
updated: YYYY-MM-DD
source_count: N
---
```

Structure: title → description → `→ [[links]]` → content → `## Decisions` → `## Changelog`

---

## raw/ — rules

`raw/` is Claude's **extra memory about studied sources**, not a folder of copies.

- On every Ingest, Claude writes a note `raw/YYYY-MM-DD-description.md`:
  - `**Source:**` — path to the file on disk (for binaries / PDFs — path only, no copy) or a URL
  - `**Project:**` — `[[projects/...]]`, what it relates to
  - below — a **detailed extract of everything useful** (so the original never needs re-reading)
- Claude **reads** `raw/` to recall a source's contents
- Claude **extends** old notes, never rewrites them without reason
- Naming: `YYYY-MM-DD-short-description.md`

---

## Rules for [[links]]

1. File must exist before writing the link
2. `[[topics/Foo]]` → file `topics/Foo.md` must exist
3. `[[topics/]]` — **FORBIDDEN** (folder reference is invalid in Obsidian)
4. If topic doesn't exist → create a stub immediately OR write plain text without `[[]]`
5. When creating a new page → add it to `index.md` immediately
