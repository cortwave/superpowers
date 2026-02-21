# Agent Presets via `OPENCODE_CONFIG_DIR`

**Date:** 2026-02-21
**Status:** Approved

## Problem

OpenCode discovers all agent `.md` files from `~/.config/opencode/agents/` unconditionally. The `disable: true` flag in JSONC config does not prevent markdown-defined agents from appearing in the TUI. This makes it impossible to switch between different agent sets (presets) using config overrides alone.

The current approach generates per-preset JSONC files with `disable: true/false` flags and uses `OPENCODE_CONFIG` to select one, but the agents still leak through because discovery is unconditional.

## Solution

Use `OPENCODE_CONFIG_DIR` (documented OpenCode feature) to point at a preset-specific directory that contains only the agents for that preset. Keep `~/.config/opencode/agents/` empty so no agents leak globally.

Agent `.md` files are stored once in an `agents-pool/` directory. Each preset's `agents/` directory contains symlinks into the pool, so agents can be shared across presets without duplication.

## Architecture

### Installed Directory Layout

```
~/.config/opencode/
  opencode.jsonc              # shared base config (providers, theme, model)
  plugins/superpowers.js      # always active
  skills/                     # always active
  agents/                     # EMPTY - prevents global agent leaking

  agents-pool/                # single source of truth for processed agent .md files
    architect.md              # has placeholders replaced + UsingSuperpowers appended
    code-reviewer.md
    developer.md
    explorer.md
    investigator.md
    writer.md

  presets/
    superpowers/
      agents/
        architect.md     -> ../../agents-pool/architect.md
        code-reviewer.md -> ../../agents-pool/code-reviewer.md
        developer.md     -> ../../agents-pool/developer.md
        explorer.md      -> ../../agents-pool/explorer.md
        investigator.md  -> ../../agents-pool/investigator.md
        writer.md        -> ../../agents-pool/writer.md
    default/
      agents/                 # empty - only built-in agents
```

### Repo Layout

```
superpowers/
  agents/                              # agent source files (unprocessed)
    architect.md
    code-reviewer.md
    developer.md
    explorer.md
    investigator.md
    writer.md
  .opencode/configs/                   # preset definitions (YAML manifests)
    superpowers.yaml                   # agents: [architect, code-reviewer, ...]
    default.yaml                       # agents: [] (empty = built-ins only)
  install.sh
  scripts/
    install-presets.sh                 # NEW: reads YAML manifests, creates pool + symlinks
    update-opencode-agents.sh          # MODIFIED: targets agents-pool/ instead of agents/
```

### `ocode` Bash Function

```bash
ocode() {
  local preset="${1:-superpowers}"
  local dir="$HOME/.config/opencode/presets/$preset"
  if [ ! -d "$dir" ]; then
    echo "Unknown preset: $preset" >&2
    return 1
  fi
  OPENCODE_CONFIG_DIR="$dir" opencode
}
```

- `ocode` -> superpowers agents (default)
- `ocode default` -> built-in agents only
- `ocode <name>` -> any custom preset
- Concurrent-safe: no global state mutation, just an env var per process

### Install Flow

1. Copy `agents/*.md` -> `~/.config/opencode/agents-pool/`
2. Run `update-opencode-agents.sh` against `agents-pool/` (placeholder replacement + UsingSuperpowers.md append)
3. For each `.opencode/configs/*.yaml`:
   - Create `~/.config/opencode/presets/<name>/agents/`
   - For each agent listed in the YAML, create symlink: `presets/<name>/agents/<agent>.md -> ../../agents-pool/<agent>.md`
4. Ensure `~/.config/opencode/agents/` exists but is empty
5. Copy skills and plugins (as today)
6. Install `ocode` bash function into `~/.bashrc` (using `OPENCODE_CONFIG_DIR` instead of `OPENCODE_CONFIG`)

### Adding a New Preset

1. Create `.opencode/configs/lite.yaml`:
   ```yaml
   agents:
     - architect
     - developer
   ```
2. Run `install.sh`
3. Use: `ocode lite`

### Adding a New Agent

1. Create `agents/new-agent.md` in the repo
2. Add it to whichever preset YAMLs should include it
3. Run `install.sh`

## What Changes

### New Files

- `scripts/install-presets.sh` - reads YAML manifests, creates `agents-pool/`, creates preset dirs with symlinks

### Modified Files

- `install.sh` - new flow: agents-pool, presets, empty agents/, updated ocode function
- `scripts/update-opencode-agents.sh` - target `~/.config/opencode/agents-pool/` instead of `~/.config/opencode/agents/`
- `.opencode/configs/opencode.yaml` -> rename to `superpowers.yaml` (cleaner naming)
- `.opencode/configs/opencode_default.yaml` -> rename to `default.yaml`

### Removed Files

- `scripts/yaml-configs-to-jsonc.sh` - no longer needed
- `.opencode/opencode.jsonc` - the repo-level project config with disable flags is no longer needed (or simplify to shared base config without agent disable flags)

### Test Changes

#### `tests/conftest.py`

- `installed_agent_files` fixture: change from `install_dir / "agents"` to `install_dir / "agents-pool"` (this is where processed agents live)
- `installed_opencode_config` fixture: may need updating if we remove the JSONC or change its content
- `OPENCODE_DEFAULT_AGENTS` constant: unchanged
- `assert_agents_explicitly_disabled` helper: **remove entirely** - no longer generating disable flag configs
- `parse_opencode_jsonc` helper: keep (may still be useful) but no longer used for disable-flag validation

#### `tests/test_installation.py`

- `TestFilesCopied.test_all_files_copied`:
  - Change agent check to verify agents in `agents-pool/` instead of `agents/`
  - Add: verify `agents/` dir exists and is empty
  - Add: verify preset directories exist with correct symlinks
- `TestFilesCopied.test_no_extra_skills_or_agents`:
  - Change to check `agents-pool/` for extra agents
- `TestModelReplacement.test_model_placeholders_replaced`: update to read from `agents-pool/`
- `TestUsingSuperpowersAppended.test_using_superpowers_appended_once`: update to read from `agents-pool/`
- `TestAgentDisableConfig`: **remove entirely** - no more disable flag configs

New tests to add:
- `TestPresets.test_preset_dirs_exist` - verify each YAML manifest has a corresponding preset dir
- `TestPresets.test_preset_symlinks_valid` - verify symlinks point to agents-pool and resolve correctly
- `TestPresets.test_preset_agents_match_yaml` - verify each preset contains exactly the agents listed in its YAML
- `TestPresets.test_agents_dir_is_empty` - verify `~/.config/opencode/agents/` has no .md files

#### `tests/test_repo.py`

- `TestAgentDisableConfig`: **remove entirely** - no more `.opencode/opencode.jsonc` with disable flags
- `TestSkillPermissions`, `TestTaskPermissions`, `TestModelPlaceholders`: unchanged (operate on repo source agents)

New tests to add:
- `TestPresetYamls.test_all_preset_agents_exist` - every agent name in a YAML manifest must have a corresponding `.md` in `agents/`
- `TestPresetYamls.test_yaml_files_valid` - each YAML file parses correctly and has an `agents` key

#### `tests/test_conftest.py`

- Unchanged (tests parse_frontmatter and parse_models_conf which are unaffected)

## Risks

1. **`OPENCODE_CONFIG_DIR` behavior**: We rely on this env var causing OpenCode to scan `agents/` inside the pointed directory. The docs explicitly state this, but it's a relatively newer feature. If it doesn't work as expected, fallback is Approach 1 (symlink swap of the entire `~/.config/opencode/` directory).

2. **Symlinks through `sed`**: `update-opencode-agents.sh` uses `sed -i` which operates on the target file through symlinks on Linux. This is the desired behavior (edit the pool file once, all presets see the change). Verified: `sed -i` follows symlinks on Linux by default.
