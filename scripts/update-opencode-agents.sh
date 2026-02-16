#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODELS_CONF="$ROOT_DIR/models.conf"
APPEND_FILE="$ROOT_DIR/.opencode/UsingSuperpowers.md"

if [[ ! -f "$MODELS_CONF" ]]; then
  printf 'Missing models.conf at %s\n' "$MODELS_CONF" >&2
  exit 1
fi

if [[ ! -f "$APPEND_FILE" ]]; then
  printf 'Missing UsingSuperpowers.md at %s\n' "$APPEND_FILE" >&2
  exit 1
fi

set -a
source "$MODELS_CONF"
set +a

if [[ -z "${HIGH_EFFORT:-}" || -z "${MEDIUM_EFFORT:-}" ]]; then
  printf 'HIGH_EFFORT or MEDIUM_EFFORT missing in %s\n' "$MODELS_CONF" >&2
  exit 1
fi

AGENTS_DIR="$HOME/.config/opencode/agents"
if [[ ! -d "$AGENTS_DIR" ]]; then
  printf 'Agents directory not found at %s\n' "$AGENTS_DIR" >&2
  exit 1
fi

append_text="$(<"$APPEND_FILE")"
marker_line=""
if [[ -n "$append_text" ]]; then
  IFS= read -r marker_line <<<"$append_text"
fi

escape_sed_replacement() {
  local value="$1"
  value="${value//\\/\\\\}"
  value="${value//&/\\&}"
  value="${value//|/\\|}"
  printf '%s' "$value"
}

high_effort_escaped="$(escape_sed_replacement "$HIGH_EFFORT")"
medium_effort_escaped="$(escape_sed_replacement "$MEDIUM_EFFORT")"

shopt -s nullglob
for agent_file in "$AGENTS_DIR"/*.md; do
  sed -i "s|<HIGH_EFFORT>|${high_effort_escaped}|g" "$agent_file"
  sed -i "s|<MEDIUM_EFFORT>|${medium_effort_escaped}|g" "$agent_file"

  if [[ -n "$marker_line" ]] && grep -Fq "$marker_line" "$agent_file"; then
    continue
  fi

  if [[ -n "$append_text" ]]; then
    printf '\n%s\n' "$append_text" >> "$agent_file"
  fi
done
