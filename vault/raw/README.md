# raw/ — Original Sources

This folder stores raw source documents that Claude has ingested.

**Rules:**
- Claude saves sources here automatically as the first step of every Ingest operation
- Never modify files already here — they are source-of-truth originals
- Claude reads from here when re-processing is needed
- You can drop files here manually and ask Claude to "ingest this"

**Naming convention:** `YYYY-MM-DD-short-description.ext`

Examples:
- `2026-01-15-api-design-notes.md`
- `2026-02-03-chat-export-architecture-discussion.md`
- `2026-03-20-library-docs.pdf`
