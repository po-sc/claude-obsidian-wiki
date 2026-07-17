# Session Memory (mem-sync) — optional module

This folder adds a **local, free, zero-token memory layer** on top of the wiki.

The wiki (the base setup) is *curated* — Claude writes structured pages when
something significant happens. This module is the *safety net*: it captures
**every** session automatically so nothing is ever lost, even the sessions
Claude didn't think were worth a wiki page.

It works by parsing Claude Code's own transcripts — no LLM, no API key, 0 tokens.

## What it does

`mem-sync.py` reads `~/.claude/projects/**/*.jsonl` (Claude Code writes one
transcript per session there, regardless of whether you use the terminal, the
desktop app, or an IDE extension) and, for each project, writes one aggregated
file into your vault:

```
projects/<Project>/Session Log.md
```

Each session becomes a section: your requests, files read/edited/created, bash
commands run, and the final outcome. Your hand-written `projects/<Project>.md`
page is **never touched** — only `Session Log.md` is written.

It's **incremental**: `state.json` tracks each transcript's mtime, so a project
is only regenerated when one of its transcripts actually changed.

If the third-party [`claude-mem`](https://github.com/thedotmack/claude-mem)
plugin is installed, mem-sync also writes to its SQLite DB
(`~/.claude-mem/claude-mem.db`) so its viewer and MCP search work. This is
best-effort — if the DB isn't there, that step is skipped silently.

## Requirements

- **macOS** (the background scheduler uses `launchd`)
- **Python 3** (system `python3` is fine)
- Local **Claude Code** writing transcripts to `~/.claude/projects/`

> Not for the claude.ai web app or the Claude mobile chat app — those don't
> write local transcripts. This is tied to Claude **Code**.

## Install

The easiest path is `bash setup.sh` in the repo root and answering **yes** to
"enable session memory". That copies the script, writes the config, generates
the launchd plist from `mem-sync.plist.template`, and loads the agent.

To do it by hand:

```bash
DIR="$HOME/.claude-obsidian-wiki"
mkdir -p "$DIR"
cp memory/mem-sync.py "$DIR/"
echo '{"vault": "/path/to/your/vault/Claude"}' > "$DIR/config.json"

# generate the launchd plist from the template
PLIST="$HOME/Library/LaunchAgents/com.claude-obsidian-wiki.mem-sync.plist"
sed -e "s|__PYTHON__|$(command -v python3)|g" \
    -e "s|__SCRIPT__|$DIR/mem-sync.py|g" \
    -e "s|__WATCH__|$HOME/.claude/projects|g" \
    -e "s|__LOG__|$DIR/sync.log|g" \
    memory/mem-sync.plist.template > "$PLIST"

launchctl unload "$PLIST" 2>/dev/null
launchctl load "$PLIST"
```

## Configuration

All optional, resolved in this order:

- **Vault path** — env `MEMSYNC_VAULT`, else `~/.claude-obsidian-wiki/config.json` → `{"vault": "..."}`
- **Project mapping** — `~/.claude-obsidian-wiki/project-map.json`:

  ```json
  {
    "my-app": "MyApp",
    "acme/backend": "Acme Backend",
    "scripts": "Scripts"
  }
  ```

  Keys are lowercase substrings matched against each session's working
  directory; the first match wins. Any directory that matches nothing falls
  back to its **last path component** (e.g. `~/code/widgets` → `widgets`), and
  an empty/unknown cwd goes to `Misc`.

## Run it manually

```bash
python3 ~/.claude-obsidian-wiki/mem-sync.py            # incremental (default)
python3 ~/.claude-obsidian-wiki/mem-sync.py --all      # reprocess everything
python3 ~/.claude-obsidian-wiki/mem-sync.py --recent 7 # only last 7 days
python3 ~/.claude-obsidian-wiki/mem-sync.py --dry-run  # show, change nothing
python3 ~/.claude-obsidian-wiki/mem-sync.py --only my-app
python3 ~/.claude-obsidian-wiki/mem-sync.py --no-db    # vault only, skip claude-mem DB
```

## Uninstall

```bash
PLIST="$HOME/Library/LaunchAgents/com.claude-obsidian-wiki.mem-sync.plist"
launchctl unload "$PLIST"
rm -f "$PLIST"
rm -rf "$HOME/.claude-obsidian-wiki"   # config + state + logs (your vault stays)
```

The `Session Log.md` files already written to your vault stay put — delete them
by hand if you want them gone.
