#!/usr/bin/env bash

set -euo pipefail

INSTALL_DIR="$HOME/.config/opencode"

remove_dir() {
  local dir="$1"
  if [[ -d "$dir" ]]; then
    rm -rf "$dir"
    echo "Removed: $dir"
  fi
}

echo "Clearing previous installation..."

remove_dir "$INSTALL_DIR/agents-pool"
remove_dir "$INSTALL_DIR/skills-pool"
remove_dir "$INSTALL_DIR/presets"
remove_dir "$INSTALL_DIR/agents"

echo "Done clearing previous installation."
