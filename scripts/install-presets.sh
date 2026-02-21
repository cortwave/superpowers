#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIGS_DIR="$ROOT_DIR/.opencode/configs"
INSTALL_DIR="$HOME/.config/opencode"
POOL_DIR="$INSTALL_DIR/agents-pool"
PRESETS_DIR="$INSTALL_DIR/presets"

# Parse a simple yaml list under an "agents:" key.
# Supports both block style ("  - name") and inline style ("agents: [a, b]").
# Prints one agent name per line.
parse_agents_from_yaml() {
  local file="$1"
  local in_agents_block=0

  while IFS= read -r line || [[ -n "$line" ]]; do
    if [[ "$line" =~ ^agents:[[:space:]]*$ ]]; then
      in_agents_block=1
      continue
    fi

    if [[ "$line" =~ ^agents:[[:space:]]*\[(.+)\] ]]; then
      local inline="${BASH_REMATCH[1]}"
      IFS=',' read -ra items <<< "$inline"
      for item in "${items[@]}"; do
        item="${item// /}"
        item="${item//\"/}"
        [[ -n "$item" ]] && printf '%s\n' "$item"
      done
      in_agents_block=0
      continue
    fi

    if [[ "$in_agents_block" -eq 1 ]]; then
      if [[ "$line" =~ ^[[:space:]]*-[[:space:]]+([^[:space:]#]+) ]]; then
        printf '%s\n' "${BASH_REMATCH[1]}"
      elif [[ "$line" =~ ^[^[:space:]#] ]]; then
        in_agents_block=0
      fi
    fi
  done < "$file"
}

# --- 1. Populate agents-pool from repo agents/ ---
rm -rf "$POOL_DIR"
cp -r "$ROOT_DIR/agents" "$POOL_DIR"
printf 'Populated agents-pool at %s\n' "$POOL_DIR"

# --- 2. Run placeholder replacement + UsingSuperpowers append on pool ---
AGENTS_DIR="$POOL_DIR" "$ROOT_DIR/scripts/update-opencode-agents.sh"

# --- 3. Build preset directories ---
rm -rf "$PRESETS_DIR"
mkdir -p "$PRESETS_DIR"

shopt -s nullglob
yaml_files=("$CONFIGS_DIR"/*.yaml)
shopt -u nullglob

if [[ "${#yaml_files[@]}" -eq 0 ]]; then
  printf 'No yaml files found in %s — no presets created.\n' "$CONFIGS_DIR"
  exit 0
fi

for yaml_file in "${yaml_files[@]}"; do
  preset_name="$(basename "$yaml_file" .yaml)"
  preset_agents_dir="$PRESETS_DIR/$preset_name/agents"
  mkdir -p "$preset_agents_dir"

  mapfile -t agents < <(parse_agents_from_yaml "$yaml_file")

  for agent_name in "${agents[@]}"; do
    pool_file="$POOL_DIR/${agent_name}.md"
    if [[ ! -f "$pool_file" ]]; then
      printf 'Warning: preset "%s" references unknown agent "%s" — skipping\n' \
        "$preset_name" "$agent_name" >&2
      continue
    fi
    ln -sf "../../../agents-pool/${agent_name}.md" "$preset_agents_dir/${agent_name}.md"
  done

  printf 'Created preset "%s" with %d agent(s)\n' "$preset_name" "${#agents[@]}"
done
