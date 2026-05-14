#!/usr/bin/env bash
# Claude × Obsidian Wiki — setup script

set -e

echo "=== Claude × Obsidian Wiki Setup ==="
echo ""

# 1. Ask for vault path
read -rp "Where should the vault live? (e.g. ~/Documents/MyVault/Claude): " VAULT_PATH
VAULT_PATH="${VAULT_PATH/#\~/$HOME}"

# 2. Copy vault
if [ -d "$VAULT_PATH" ]; then
  echo "Directory already exists at $VAULT_PATH"
  read -rp "Overwrite? (y/N): " CONFIRM
  [[ "$CONFIRM" != "y" ]] && echo "Aborted." && exit 1
fi

mkdir -p "$VAULT_PATH"
cp -r vault/. "$VAULT_PATH/"
echo "✓ Vault copied to $VAULT_PATH"

# 3. Install CLAUDE.md
mkdir -p ~/.claude
CLAUDE_DST="$HOME/.claude/CLAUDE.md"
CLAUDE_INSTALLED=false

if [ -f "$CLAUDE_DST" ]; then
  echo ""
  echo "~/.claude/CLAUDE.md already exists."
  echo "Recommendation: merge manually (see README — 'Adding to existing setup')."
  read -rp "Overwrite anyway? (y/N): " CONFIRM
  if [[ "$CONFIRM" == "y" ]]; then
    cp claude/CLAUDE.md "$CLAUDE_DST"
    CLAUDE_INSTALLED=true
    echo "✓ CLAUDE.md installed to ~/.claude/CLAUDE.md"
  else
    echo "Skipped — open ~/.claude/CLAUDE.md and claude/CLAUDE.md side-by-side to merge."
  fi
else
  cp claude/CLAUDE.md "$CLAUDE_DST"
  CLAUDE_INSTALLED=true
  echo "✓ CLAUDE.md installed to ~/.claude/CLAUDE.md"
fi

# 4. Patch the VAULT path (only if we installed it)
if [ "$CLAUDE_INSTALLED" = true ]; then
  sed -i.bak "s|/path/to/your/obsidian/vault/Claude|$VAULT_PATH|g" "$CLAUDE_DST"
  rm -f "$CLAUDE_DST.bak"
  echo "✓ VAULT path set to: $VAULT_PATH"
fi

echo ""
echo "=== Done ==="
echo ""
echo "Next steps:"
echo "  1. Open $VAULT_PATH in Obsidian (optional)"
echo "  2. Edit ~/.claude/CLAUDE.md — fill in the '## Project pages' table:"
echo "     Map your project directories to wiki pages so Claude knows what to read"
echo "     Example:  /Users/me/my-app/  →  projects/MyApp/Overview.md, projects/MyApp/Backend.md"
echo "  3. Run 'claude' inside a mapped project directory"
echo ""
echo "Claude will auto-update the wiki after every significant task."
