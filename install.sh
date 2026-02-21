#!/usr/bin/env bash

set -euo pipefail

rm -rf ~/.config/opencode/superpowers

# skills
rm -rf ~/.config/opencode/skills
cp -r skills ~/.config/opencode/skills

# Copy OpenCode config
cp .opencode/opencode.jsonc ~/.config/opencode/opencode.jsonc

# Copy agents
rm -rf ~/.config/opencode/agents
cp -r agents ~/.config/opencode/agents

# Update agent placeholders and append instructions
./scripts/update-opencode-agents.sh

# Install ocode function into ~/.bashrc
BASHRC="$HOME/.bashrc"
OCODE_MARKER_START="# >>> ocode function >>>"
OCODE_MARKER_END="# <<< ocode function <<<"

OCODE_BLOCK="$OCODE_MARKER_START
ocode() {
  if [ -n \"\${1:-}\" ]; then
    OPENCODE_CONFIG=\"\$HOME/.config/opencode/opencode_\${1}.jsonc\" opencode
  else
    opencode
  fi
}
$OCODE_MARKER_END"

# Remove any existing ocode block
if grep -qF "$OCODE_MARKER_START" "$BASHRC" 2>/dev/null; then
  # Use a temp file to strip the block between markers (inclusive)
  tmp=$(mktemp)
  awk "/$OCODE_MARKER_START/{found=1} !found{print} /$OCODE_MARKER_END/{found=0}" "$BASHRC" > "$tmp"
  mv "$tmp" "$BASHRC"
fi

# Append the new ocode block
printf '\n%s\n' "$OCODE_BLOCK" >> "$BASHRC"
echo "ocode function installed in $BASHRC"
