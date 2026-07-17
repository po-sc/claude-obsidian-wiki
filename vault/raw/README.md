# raw/ — Source Memory

This folder is Claude's **extra memory about the sources it has studied** — not
a dump of file copies.

For every source you ask Claude to "ingest" (a file, a link, a pasted doc), it
writes a **note** here summarizing everything useful, so the original never
needs to be re-read.

**Each note (`YYYY-MM-DD-short-description.md`) has:**
- `**Source:**` — absolute path to the file on disk (for binaries / PDFs / large
  files: the path only, never a copy) or a URL if it came from the web. A small
  text paste can be inlined.
- `**Project:**` — `[[projects/...]]`, which project it belongs to.
- Body — a detailed extract of the facts, numbers, requirements, decisions, and
  wording that might be needed later.

**Rules:**
- Claude writes a note here as the first step of every Ingest
- Claude extends existing notes instead of rewriting them
- Claude reads from here when it needs to recall a source
- You can drop a note here manually and ask Claude to build a page from it

**Naming convention:** `YYYY-MM-DD-short-description.md`

Examples:
- `2026-01-15-api-design-notes.md`
- `2026-02-03-chat-export-architecture-discussion.md`
- `2026-03-20-library-docs.md`  ← notes about a PDF, referencing its path
