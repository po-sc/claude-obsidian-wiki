#!/usr/bin/env bash
# Claude × Obsidian Wiki — setup script
#
# Installs the wiki (always) and, optionally, the local Session Memory module
# (mem-sync + claude-mem). Both modes are offered — you choose during setup.

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DST="$HOME/.claude/CLAUDE.md"
MEM_DIR="$HOME/.claude-obsidian-wiki"
PLIST_LABEL="com.claude-obsidian-wiki.mem-sync"
PLIST_DST="$HOME/Library/LaunchAgents/$PLIST_LABEL.plist"

echo "=== Claude × Obsidian Wiki Setup ==="
echo ""

# ---------------------------------------------------------------------------
# 1. Vault
# ---------------------------------------------------------------------------
read -rp "Where should the vault live? (e.g. ~/Documents/MyVault/Claude): " VAULT_PATH
VAULT_PATH="${VAULT_PATH/#\~/$HOME}"

if [ -d "$VAULT_PATH" ] && [ -n "$(ls -A "$VAULT_PATH" 2>/dev/null)" ]; then
  echo "Directory already exists and is not empty at $VAULT_PATH"
  read -rp "Copy vault files into it anyway? (y/N): " CONFIRM
  [[ "$CONFIRM" != "y" ]] && echo "Aborted." && exit 1
fi

mkdir -p "$VAULT_PATH"
cp -R "$REPO_DIR/vault/." "$VAULT_PATH/"
# Don't leave scaffolding artifacts in the user's vault
find "$VAULT_PATH" -name .DS_Store -delete 2>/dev/null || true
find "$VAULT_PATH" -name .gitkeep -delete 2>/dev/null || true
echo "✓ Vault copied to $VAULT_PATH"

# ---------------------------------------------------------------------------
# 2. CLAUDE.md (base wiki instructions)
# ---------------------------------------------------------------------------
mkdir -p "$HOME/.claude"
CLAUDE_INSTALLED=false

if [ -f "$CLAUDE_DST" ]; then
  echo ""
  echo "~/.claude/CLAUDE.md already exists."
  echo "Recommendation: merge manually (see README — 'Option 3')."
  read -rp "Overwrite anyway? (y/N): " CONFIRM
  if [[ "$CONFIRM" == "y" ]]; then
    cp "$REPO_DIR/claude/CLAUDE.md" "$CLAUDE_DST"
    CLAUDE_INSTALLED=true
    echo "✓ CLAUDE.md installed to ~/.claude/CLAUDE.md"
  else
    echo "Skipped — open ~/.claude/CLAUDE.md and claude/CLAUDE.md side-by-side to merge."
  fi
else
  cp "$REPO_DIR/claude/CLAUDE.md" "$CLAUDE_DST"
  CLAUDE_INSTALLED=true
  echo "✓ CLAUDE.md installed to ~/.claude/CLAUDE.md"
fi

# Patch the VAULT path (only if we own the installed file)
if [ "$CLAUDE_INSTALLED" = true ]; then
  sed -i.bak "s|/path/to/your/obsidian/vault/Claude|$VAULT_PATH|g" "$CLAUDE_DST"
  rm -f "$CLAUDE_DST.bak"
  echo "✓ VAULT path set to: $VAULT_PATH"
fi

# ---------------------------------------------------------------------------
# 3. Session Memory module (optional)
# ---------------------------------------------------------------------------
echo ""
echo "--- Optional: Session Memory (mem-sync) ---"
echo "Auto-captures EVERY Claude Code session into the vault as a safety net."
echo "Local, free, 0 tokens. Requires macOS + python3."
read -rp "Enable session memory? (y/N): " MEM_CONFIRM

if [[ "$MEM_CONFIRM" == "y" ]]; then
  if [[ "$(uname)" != "Darwin" ]]; then
    echo "⚠ Session memory uses launchd (macOS only) — skipping the background agent."
    echo "  You can still run memory/mem-sync.py manually on other platforms."
    MEM_ENABLED=false
  elif ! command -v python3 >/dev/null 2>&1; then
    echo "⚠ python3 not found — skipping session memory."
    MEM_ENABLED=false
  else
    MEM_ENABLED=true
  fi

  if [ "${MEM_ENABLED:-false}" = true ] || [[ "$(uname)" != "Darwin" ]]; then
    mkdir -p "$MEM_DIR"
    cp "$REPO_DIR/memory/mem-sync.py" "$MEM_DIR/mem-sync.py"
    chmod +x "$MEM_DIR/mem-sync.py"
    printf '{\n  "vault": "%s"\n}\n' "$VAULT_PATH" > "$MEM_DIR/config.json"
    echo "✓ mem-sync.py installed to $MEM_DIR"
    echo "✓ config written ($MEM_DIR/config.json)"
  fi

  if [ "${MEM_ENABLED:-false}" = true ]; then
    PY="$(command -v python3)"
    mkdir -p "$HOME/Library/LaunchAgents"
    sed -e "s|__PYTHON__|$PY|g" \
        -e "s|__SCRIPT__|$MEM_DIR/mem-sync.py|g" \
        -e "s|__WATCH__|$HOME/.claude/projects|g" \
        -e "s|__LOG__|$MEM_DIR/sync.log|g" \
        "$REPO_DIR/memory/mem-sync.plist.template" > "$PLIST_DST"
    launchctl unload "$PLIST_DST" 2>/dev/null || true
    launchctl load "$PLIST_DST"
    echo "✓ launchd agent loaded ($PLIST_LABEL)"

    # First run to populate the vault right away
    echo "  Running an initial sync..."
    "$PY" "$MEM_DIR/mem-sync.py" --recent 30 || true
  fi

  # Append the memory section to CLAUDE.md (only if we own it)
  if [ "$CLAUDE_INSTALLED" = true ]; then
    if ! grep -q "## Session Memory — automatic capture" "$CLAUDE_DST"; then
      cat "$REPO_DIR/claude/CLAUDE.session-memory.md" >> "$CLAUDE_DST"
      echo "✓ Session Memory section appended to ~/.claude/CLAUDE.md"
    fi
  else
    echo "ℹ Append memory/../claude/CLAUDE.session-memory.md to your CLAUDE.md by hand."
  fi
fi

# ---------------------------------------------------------------------------
# 4. Done
# ---------------------------------------------------------------------------
echo ""
echo "=== Done ==="
echo ""
echo "Next steps:"
echo "  1. Open $VAULT_PATH in Obsidian (optional)"
echo "  2. Edit ~/.claude/CLAUDE.md — fill in the '## Project pages' table:"
echo "     Map your project directories to wiki pages so Claude knows what to read."
echo "     Example:  /Users/me/my-app/  →  projects/MyApp/Overview.md, projects/MyApp/Backend.md"
if [[ "$MEM_CONFIRM" == "y" ]]; then
  echo "  3. (Optional) Edit $MEM_DIR/project-map.json to give sessions nicer project names"
  echo "     (unmapped directories fall back to the folder's basename)."
fi
echo ""
echo "Claude will auto-update the wiki after every significant task."
