#!/usr/bin/env bash

set -euo pipefail

# Ensure agents/ is empty (prevents global agent leaking)
rm -rf ~/.config/opencode/agents
mkdir -p ~/.config/opencode/agents

# Build agents-pool, skills-pool, and preset directories with symlinks
./scripts/install-presets.sh

# Install ocode function into ~/.bashrc
BASHRC="$HOME/.bashrc"
OCODE_MARKER_START="# >>> ocode function >>>"
OCODE_MARKER_END="# <<< ocode function <<<"

OCODE_BLOCK="$OCODE_MARKER_START
ocode() {
  local preset=\"\${1:-superpowers}\"
  local dir=\"\$HOME/.config/opencode/presets/\$preset\"
  if [ ! -d \"\$dir\" ]; then
    echo \"Unknown preset: \$preset\" >&2
    return 1
  fi
  OPENCODE_CONFIG_DIR=\"\$dir\" opencode
}
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
