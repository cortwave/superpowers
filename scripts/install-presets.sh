#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIGS_DIR="$ROOT_DIR/.opencode/configs"
INSTALL_DIR="$HOME/.config/opencode"
POOL_DIR="$INSTALL_DIR/agents-pool"
SKILLS_POOL_DIR="$INSTALL_DIR/skills-pool"
PRESETS_DIR="$INSTALL_DIR/presets"

# Parse a simple yaml list under a given key.
# Supports both block style ("  - name") and inline style ("key: [a, b]").
# Prints one item per line.
parse_list_from_yaml() {
  local file="$1"
  local key="$2"
  local in_block=0

  while IFS= read -r line || [[ -n "$line" ]]; do
    if [[ "$line" =~ ^${key}:[[:space:]]*$ ]]; then
      in_block=1
      continue
    fi

    if [[ "$line" =~ ^${key}:[[:space:]]*\[(.+)\] ]]; then
      local inline="${BASH_REMATCH[1]}"
      IFS=',' read -ra items <<< "$inline"
      for item in "${items[@]}"; do
        item="${item// /}"
        item="${item//\"/}"
        [[ -n "$item" ]] && printf '%s\n' "$item"
      done
      in_block=0
      continue
    fi

    if [[ "$in_block" -eq 1 ]]; then
      if [[ "$line" =~ ^[[:space:]]*-[[:space:]]+([^[:space:]#]+) ]]; then
        local val="${BASH_REMATCH[1]}"
        val="${val//\"/}"
        printf '%s\n' "$val"
      elif [[ "$line" =~ ^[^[:space:]#] ]]; then
        in_block=0
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

# --- 3. Populate skills-pool from repo skills/ ---
rm -rf "$SKILLS_POOL_DIR"
cp -r "$ROOT_DIR/skills" "$SKILLS_POOL_DIR"
printf 'Populated skills-pool at %s\n' "$SKILLS_POOL_DIR"

# OpenCode built-in agents that must be disabled when a preset supplies its own agents.
OPENCODE_BUILTIN_AGENTS=(plan build general explore)

# Write opencode.jsonc for a preset.
# If the preset has custom agents, disables all built-ins and enables each custom agent.
# If the preset has no custom agents (default), writes a minimal config (no agent block).
write_preset_jsonc() {
  local preset_dir="$1"
  shift
  local agents=("$@")
  local out="$preset_dir/opencode.jsonc"

  if [[ "${#agents[@]}" -eq 0 ]]; then
    printf '{\n  "$schema": "https://opencode.ai/config.json"\n}\n' > "$out"
    return
  fi

  {
    printf '{\n  "$schema": "https://opencode.ai/config.json",\n  "agent": {\n'
    printf '    // OpenCode built-in agents\n'
    for builtin in "${OPENCODE_BUILTIN_AGENTS[@]}"; do
      printf '    "%s": { "disable": true },\n' "$builtin"
    done
    printf '    // Preset agents\n'
    local last_idx=$(( ${#agents[@]} - 1 ))
    for i in "${!agents[@]}"; do
      if [[ "$i" -eq "$last_idx" ]]; then
        printf '    "%s": { "disable": false }\n' "${agents[$i]}"
      else
        printf '    "%s": { "disable": false },\n' "${agents[$i]}"
      fi
    done
    printf '  }\n}\n'
  } > "$out"
}

# --- 4. Build preset directories ---
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
  preset_dir="$PRESETS_DIR/$preset_name"
  preset_agents_dir="$preset_dir/agents"
  preset_skills_dir="$preset_dir/skills"
  mkdir -p "$preset_agents_dir"
  mkdir -p "$preset_skills_dir"

  mapfile -t agents < <(parse_list_from_yaml "$yaml_file" "agents")
  mapfile -t skills_spec < <(parse_list_from_yaml "$yaml_file" "skills")

  # Resolve skills_spec: ["*"] means all skills in pool, otherwise named list
  skills=()
  if [[ "${#skills_spec[@]}" -eq 1 && "${skills_spec[0]}" == "*" ]]; then
    for skill_dir in "$SKILLS_POOL_DIR"/*/; do
      [[ -d "$skill_dir" ]] && skills+=("$(basename "$skill_dir")")
    done
  else
    skills=("${skills_spec[@]}")
  fi

  for agent_name in "${agents[@]}"; do
    pool_file="$POOL_DIR/${agent_name}.md"
    if [[ ! -f "$pool_file" ]]; then
      printf 'Warning: preset "%s" references unknown agent "%s" — skipping\n' \
        "$preset_name" "$agent_name" >&2
      continue
    fi
    ln -sf "../../../agents-pool/${agent_name}.md" "$preset_agents_dir/${agent_name}.md"
  done

  for skill_name in "${skills[@]}"; do
    pool_skill_dir="$SKILLS_POOL_DIR/${skill_name}"
    if [[ ! -d "$pool_skill_dir" ]]; then
      printf 'Warning: preset "%s" references unknown skill "%s" — skipping\n' \
        "$preset_name" "$skill_name" >&2
      continue
    fi
    ln -sf "../../../skills-pool/${skill_name}" "$preset_skills_dir/${skill_name}"
  done

  write_preset_jsonc "$preset_dir" "${agents[@]}"

  printf 'Created preset "%s" with %d agent(s) and %d skill(s)\n' \
    "$preset_name" "${#agents[@]}" "${#skills[@]}"
done
