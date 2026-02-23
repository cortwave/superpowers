ocode() {
  local preset="${1:-superpowers}"
  local dir="$HOME/.config/opencode/presets/$preset"
  if [ ! -d "$dir" ]; then
    echo "Unknown preset: $preset" >&2
    return 1
  fi
  OPENCODE_CONFIG_DIR="$dir" opencode
}

gitree() {
  if [ -z "${1:-}" ]; then
    echo "Usage: gitree <branch-name>" >&2
    return 1
  fi
  local branch="$1"
  local root
  root=$(git rev-parse --show-toplevel 2>/dev/null) || { echo "Not inside a git repository" >&2; return 1; }
  local worktree_dir="$root/.worktrees/$branch"
  git worktree add "$worktree_dir" -b "$branch"
  cd "$worktree_dir"
}
