
---

## Session Memory — automatic capture (mem-sync + claude-mem)

A local, free, zero-token layer that captures **every** Claude Code session
into the vault as a safety net. No LLM, no API key — pure transcript parsing.

- **Source:** Claude Code transcripts `~/.claude/projects/**/*.jsonl` (every prompt, file, command, outcome).
- **Parser:** `~/.claude-obsidian-wiki/mem-sync.py` — incremental (state.json by mtime).
- **Mapping:** session `cwd` → project folder name (via `~/.claude-obsidian-wiki/project-map.json`; unmatched → basename of cwd; empty → `Misc`).
- **Output:** one aggregated `projects/<Project>/Session Log.md` per project (a section per session: requests, files, commands, outcome). The hand-written page for humans is NOT touched.
- **Optional DB:** if the `claude-mem` plugin is installed, also writes `~/.claude-mem/claude-mem.db` → its viewer and MCP search light up.
- **Autostart:** launchd agent `com.claude-obsidian-wiki.mem-sync` (every 10 min + on changes to `~/.claude/projects`). Log: `~/.claude-obsidian-wiki/sync.log`.
- **Manual run:** `python3 ~/.claude-obsidian-wiki/mem-sync.py` (flags: `--all`, `--recent N`, `--dry-run`, `--only <substr>`, `--no-db`).

**Two files per project:** the curated `projects/<Project>/<Project>.md` (or
single-file page) that I maintain by hand per the HARD RULE, and the auto
`projects/<Project>/Session Log.md` that accumulates on its own as the
"nothing is lost" backup.

**How I use it:** to recall past work on a project, I read
`projects/<Project>/Session Log.md` (or search via claude-mem) instead of
re-reading the whole codebase — saves tokens.

### Start — add one step

At the start of a session, after reading the project's curated pages, if a
`projects/<Project>/Session Log.md` exists I may skim it to recall what past
sessions did — without re-reading the code.
