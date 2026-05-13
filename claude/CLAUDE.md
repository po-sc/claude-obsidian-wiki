# Claude — Global Instructions

## Obsidian Wiki

**Vault path — update this to match your setup:**

```bash
VAULT='/path/to/your/obsidian/vault/Claude'
```

> Always use single quotes — the path may contain spaces.

---

## HARD RULE — wiki updates automatically, without reminders

**A task is not complete until the wiki is updated.**

This is not optional. This is not "when I have time". It is the last step of every task.

### What counts as a significant task (always update):
- Added/changed a screen, endpoint, or data model
- Fixed an architectural bug or race condition
- Made a decision about structure, pattern, or stack
- Discovered non-obvious framework behavior
- Created/changed an important file (config, script, CLAUDE.md)

### What does NOT need a wiki update:
- Typo / color / text fix
- Discussion without a concrete outcome
- Answering "how does X work" without code changes

### Order after a significant task (always, in this order):
1. Update the project page in `projects/` — add facts, decisions, changes
2. If worked with a technology non-trivially → create/update `topics/<tech>.md`
3. If a new page was created → add to `index.md` immediately + update page count
4. Append to `log.md` (format below)

---

## Start — beginning of each session (automatic)

1. Read `index.md` — load general context
2. If the working project is known → read **all** pages for that project:
   - If it's a folder `projects/<Project>/` — read every `.md` file inside
   - If it's a single file `projects/<Project>.md` — read that file
3. Begin work with full context already loaded

---

## Ingest — adding a new source

**When:** user provides a file, link, or text to study.

**Algorithm (strict order):**

1. **Save the raw source to `raw/`** — FIRST step, before any processing:
   - File at a path → copy it: `cp <path> "$VAULT/raw/YYYY-MM-DD-topic.ext"`
   - Text / chat / paste → write it as `"$VAULT/raw/YYYY-MM-DD-topic.md"`
   - Naming: `YYYY-MM-DD-<short-description>.<ext>`
   - If source already exists in `raw/` — don't duplicate, update if needed
2. Study the source fully
3. Write/update the page in `projects/` or `topics/`
4. Update `index.md` — add/refine the entry, update page count and date
5. Append to `log.md`

**log.md format:**
```
## [YYYY-MM-DD] ingest | <Title>
**Source:** raw/<filename> or <url>
**Pages:** [[page1]], [[page2]]
**Key facts:**
- <fact 1>
- <fact 2>
- <fact 3>
```

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

1. Read `index.md` → identify relevant pages
2. Read relevant pages
3. Answer with `[[citations]]`
4. If the answer is valuable and not yet documented → create a page
5. Append to log.md (type `query`)

---

## Lint — wiki health check

**When:** user asks "lint the wiki" / "check the wiki", or approximately every 20 sessions.

**What to check:**
- Contradictions between pages
- Stale facts (old versions, removed features)
- Orphan pages (no incoming links)
- Broken links (`[[topics/]]` is broken; `[[topics/Foo]]` without `Foo.md` is broken)
- Missing cross-references (A knows about B, B doesn't know about A)

**Algorithm:** read all pages → list problems → fix → append to log.md (type `lint`).

---

## Topics — technology knowledge

The `topics/` folder is about technologies, not projects. Grows organically.

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

Short description — what it is and how we use it.

→ [[projects/...]] — where we use it

## How we use it

## Non-obvious behavior

## Decisions and patterns
```

---

## Project page format

### YAML frontmatter (required)
```yaml
---
tags: [<project>, <tech>, ...]
date: YYYY-MM-DD
updated: YYYY-MM-DD
source_count: N
---
```

### Structure
- **Title** = project name
- Short description (1–2 sentences)
- Links: `→ [[Related Page]]`
- `## Decisions` — architectural decisions with date and rationale
- `## Changelog` — key changes by date

---

## raw/ — rules

- Claude **saves** raw sources to `raw/` on every Ingest (step 1)
- Claude **reads** `raw/` when needed
- Claude **never modifies** files already there (only adds new ones)
- Naming: `YYYY-MM-DD-short-description.ext`

---

## Rules for [[links]] — preventing broken links

**Before writing any `[[link]]`:**

1. The file must exist — verify before writing
2. `[[topics/Foo]]` → file `topics/Foo.md` must exist
3. `[[topics/]]` — **FORBIDDEN** (folder link is invalid in Obsidian)
4. If topic doesn't exist → create a stub immediately OR write plain text without `[[]]`
5. When creating a new page → add it to `index.md` immediately

---

## Project pages

Add your projects here as you create pages for them:

```
projects/<ProjectName>    — description
```

When working on a project — update its page.
When starting a new project — create `projects/<ProjectName>.md` + add to `index.md`.
