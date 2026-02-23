#!/usr/bin/env bash

set -euo pipefail

# Clear files from any previous installation
./scripts/clear_existing.sh

# Ensure agents/ is empty (prevents global agent leaking)
mkdir -p ~/.config/opencode/agents

# Build agents-pool, skills-pool, and preset directories with symlinks
./scripts/install-presets.sh

# Install ocode function into ~/.bashrc
BASHRC="$HOME/.bashrc"
OCODE_MARKER_START="# >>> ocode function >>>"
OCODE_MARKER_END="# <<< ocode function <<<"

OCODE_BLOCK="$OCODE_MARKER_START
$(cat "$(dirname "$0")/scripts/bashrc-block.sh")
$OCODE_MARKER_END"

# Remove any existing ocode block
if grep -qF "$OCODE_MARKER_START" "$BASHRC" 2>/dev/null; then
  tmp=$(mktemp)
  awk "/$OCODE_MARKER_START/{found=1} !found{print} /$OCODE_MARKER_END/{found=0}" "$BASHRC" > "$tmp"
  mv "$tmp" "$BASHRC"
fi

# Append the new ocode block
printf '\n%s\n' "$OCODE_BLOCK" >> "$BASHRC"
echo "ocode function installed in $BASHRC"
