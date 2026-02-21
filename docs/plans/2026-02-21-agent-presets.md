# Agent Presets Implementation Plan

**Goal:** Replace the broken `disable`-flag approach with `OPENCODE_CONFIG_DIR`-based agent presets, where each preset directory has symlinks into a shared `agents-pool/`.

**Architecture:** Skills and plugins stay global in `~/.config/opencode/`. Agents are copied once to `~/.config/opencode/agents-pool/` (with placeholders replaced + UsingSuperpowers appended). Each preset in `~/.config/opencode/presets/<name>/agents/` contains only symlinks into the pool. `OPENCODE_CONFIG_DIR` points opencode at a preset directory, so only that preset's agents are discovered. `~/.config/opencode/agents/` is kept empty to prevent global agent leaking.

**Tech Stack:** bash, Python/pytest (tests), YAML (preset manifests)

---

### Task 1: Rename preset YAML files

The current YAML files have awkward names. Rename them to match the preset names we'll use.

**Files:**
- Rename: `.opencode/configs/opencode.yaml` → `.opencode/configs/superpowers.yaml`
- Rename: `.opencode/configs/opencode_default.yaml` → `.opencode/configs/default.yaml`

**Step 1: Rename the files**

```bash
git mv .opencode/configs/opencode.yaml .opencode/configs/superpowers.yaml
git mv .opencode/configs/opencode_default.yaml .opencode/configs/default.yaml
```

**Step 2: Verify contents look correct**

`superpowers.yaml` should list: architect, code-reviewer, developer, explorer, investigator, writer
`default.yaml` should list nothing (empty agents, built-ins only):

```yaml
agents: []
```

**Step 3: Commit**

```bash
git add .opencode/configs/
git commit -m "chore: rename preset yaml files to match preset names"
```

---

### Task 2: Update repo-level tests for preset YAMLs

Before touching any scripts, write the tests that verify the YAML manifests themselves are valid. These are repo-state tests (no install required).

**Files:**
- Modify: `tests/test_repo.py`
- Modify: `tests/conftest.py`

**Step 1: Add a YAML parsing helper to `conftest.py`**

Add after the `parse_models_conf` function (after line 34):

```python
def parse_preset_yaml(path: Path) -> list[str]:
    """Parse the agents list from a preset YAML file.

    Returns a list of agent names (may be empty).
    """
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    agents = raw.get("agents") or []
    return [str(a) for a in agents]
```

Also add a fixture for discovering preset YAMLs (after the `models_conf_values` fixture, around line 78):

```python
@pytest.fixture(scope="session")
def preset_yaml_files(repo_root: Path) -> list[Path]:
    return sorted((repo_root / ".opencode" / "configs").glob("*.yaml"))
```

**Step 2: Add `TestPresetYamls` class to `tests/test_repo.py`**

Add at the bottom of the file:

```python
from tests.conftest import parse_preset_yaml


class TestPresetYamls:
    def test_yaml_files_exist(self, preset_yaml_files: list[Path]) -> None:
        assert len(preset_yaml_files) > 0, (
            "No preset YAML files found in .opencode/configs/"
        )

    def test_all_preset_agents_exist(
        self,
        preset_yaml_files: list[Path],
        repo_agent_files: list[Path],
    ) -> None:
        repo_agent_names_set = {f.stem for f in repo_agent_files}
        for yaml_file in preset_yaml_files:
            agents = parse_preset_yaml(yaml_file)
            for agent_name in agents:
                assert agent_name in repo_agent_names_set, (
                    f"Preset '{yaml_file.name}' references agent '{agent_name}' "
                    f"which does not exist in agents/"
                )
```

**Step 3: Run the new tests to make sure they pass**

```bash
python -m pytest tests/test_repo.py::TestPresetYamls -v
```

Expected: PASS (both files exist, and all agent names in them are valid)

**Step 4: Commit**

```bash
git add tests/conftest.py tests/test_repo.py
git commit -m "test: add TestPresetYamls repo-state tests"
```

---

### Task 3: Remove obsolete `TestAgentDisableConfig` from repo tests

The `test_repo.py::TestAgentDisableConfig` class validates the `.opencode/opencode.jsonc` disable-flag config, which we're removing. Delete it.

**Files:**
- Modify: `tests/test_repo.py`

**Step 1: Remove `TestAgentDisableConfig` from `test_repo.py`**

Delete lines 90–97 (the entire `TestAgentDisableConfig` class):

```python
class TestAgentDisableConfig:
    def test_all_agents_explicitly_disabled_in_config(
        self,
        repo_agent_names: set[str],
        repo_opencode_config: dict,
    ) -> None:
        agent_config: dict = repo_opencode_config.get("agent", {})
        assert_agents_explicitly_disabled(agent_config, repo_agent_names)
```

Also remove the import of `assert_agents_explicitly_disabled` from the top of `test_repo.py` (line 4) since it'll be unused after this.

**Step 2: Run tests to verify nothing is broken**

```bash
python -m pytest tests/test_repo.py -v
```

Expected: PASS (TestAgentDisableConfig no longer exists, others pass)

**Step 3: Commit**

```bash
git add tests/test_repo.py
git commit -m "test: remove TestAgentDisableConfig from repo tests"
```

---

### Task 4: Write `scripts/install-presets.sh`

This new script reads all `.opencode/configs/*.yaml` files, copies agents to `agents-pool/`, runs placeholder replacement, and creates preset directories with symlinks.

**Files:**
- Create: `scripts/install-presets.sh`

**Step 1: Write the script**

```bash
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
    ln -sf "../../agents-pool/${agent_name}.md" "$preset_agents_dir/${agent_name}.md"
  done

  printf 'Created preset "%s" with %d agent(s)\n' "$preset_name" "${#agents[@]}"
done
```

**Step 2: Make the script executable**

```bash
chmod +x scripts/install-presets.sh
```

**Step 3: Commit**

```bash
git add scripts/install-presets.sh
git commit -m "feat: add install-presets.sh for OPENCODE_CONFIG_DIR preset setup"
```

---

### Task 5: Update `update-opencode-agents.sh` to accept `AGENTS_DIR` override

The script currently hardcodes `AGENTS_DIR="$HOME/.config/opencode/agents"`. We need it to accept an override via environment variable so `install-presets.sh` can pass `AGENTS_DIR="$POOL_DIR"`.

**Files:**
- Modify: `scripts/update-opencode-agents.sh`

**Step 1: Change line 28 to use env override with fallback**

Replace:
```bash
AGENTS_DIR="$HOME/.config/opencode/agents"
```

With:
```bash
AGENTS_DIR="${AGENTS_DIR:-$HOME/.config/opencode/agents}"
```

**Step 2: Verify the script still works standalone (no env override)**

```bash
# Run without override — should still default to ~/.config/opencode/agents
bash scripts/update-opencode-agents.sh
```

Expected: runs normally (or fails gracefully if `~/.config/opencode/agents` doesn't exist yet — that's fine)

**Step 3: Commit**

```bash
git add scripts/update-opencode-agents.sh
git commit -m "feat: allow AGENTS_DIR override in update-opencode-agents.sh"
```

---

### Task 6: Rewrite `install.sh`

Replace the old agent-copy + yaml-configs-to-jsonc flow with the new presets flow. Also update the `ocode` bash function to use `OPENCODE_CONFIG_DIR`.

**Files:**
- Modify: `install.sh`

**Step 1: Write the new `install.sh`**

```bash
#!/usr/bin/env bash

set -euo pipefail

# skills
rm -rf ~/.config/opencode/skills
cp -r skills ~/.config/opencode/skills

# Ensure agents/ is empty (prevents global agent leaking)
rm -rf ~/.config/opencode/agents
mkdir -p ~/.config/opencode/agents

# Build agents-pool and preset directories with symlinks
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
```

**Step 2: Make it executable and run it**

```bash
chmod +x install.sh
./install.sh
```

Expected output:
```
Populated agents-pool at ~/.config/opencode/agents-pool
Created preset "default" with 0 agent(s)
Created preset "superpowers" with 6 agent(s)
ocode function installed in ~/.bashrc
```

**Step 3: Verify the installed layout**

```bash
ls ~/.config/opencode/agents/          # should be empty
ls ~/.config/opencode/agents-pool/     # should have 6 .md files
ls ~/.config/opencode/presets/         # should show default/ and superpowers/
ls -la ~/.config/opencode/presets/superpowers/agents/  # should show symlinks
```

**Step 4: Commit**

```bash
git add install.sh
git commit -m "feat: rewrite install.sh to use OPENCODE_CONFIG_DIR preset layout"
```

---

### Task 7: Remove `scripts/yaml-configs-to-jsonc.sh` and `.opencode/opencode.jsonc`

These are now dead code.

**Files:**
- Delete: `scripts/yaml-configs-to-jsonc.sh`
- Delete: `.opencode/opencode.jsonc`

**Step 1: Delete the files**

```bash
git rm scripts/yaml-configs-to-jsonc.sh
git rm .opencode/opencode.jsonc
```

**Step 2: Commit**

```bash
git commit -m "chore: remove yaml-configs-to-jsonc.sh and opencode.jsonc (replaced by preset layout)"
```

---

### Task 8: Update installation tests in `conftest.py`

Update fixtures to point at `agents-pool/` and add a new `installed_pool_agent_files` fixture.

**Files:**
- Modify: `tests/conftest.py`

**Step 1: Replace `installed_agent_files` fixture (lines 86–91)**

Replace:
```python
@pytest.fixture(scope="session")
def installed_agent_files(install_dir: Path) -> list[Path]:
    agents_dir = install_dir / "agents"
    if not agents_dir.is_dir():
        pytest.skip("Installation directory not found — run install.sh first")
    return sorted(agents_dir.glob("*.md"))
```

With:
```python
@pytest.fixture(scope="session")
def installed_agent_files(install_dir: Path) -> list[Path]:
    pool_dir = install_dir / "agents-pool"
    if not pool_dir.is_dir():
        pytest.skip("agents-pool not found — run install.sh first")
    return sorted(pool_dir.glob("*.md"))


@pytest.fixture(scope="session")
def installed_preset_dirs(install_dir: Path) -> list[Path]:
    presets_dir = install_dir / "presets"
    if not presets_dir.is_dir():
        pytest.skip("presets/ not found — run install.sh first")
    return sorted([d for d in presets_dir.iterdir() if d.is_dir()])
```

**Step 2: Remove `assert_agents_explicitly_disabled` and `OPENCODE_DEFAULT_AGENTS` (lines 161–184)**

These are no longer used anywhere. Delete:
```python
# Default OpenCode built-in agents that must be explicitly configured.
OPENCODE_DEFAULT_AGENTS: frozenset[str] = frozenset(
    {"plan", "build", "general", "explore"}
)


def assert_agents_explicitly_disabled(
    agent_config: dict, repo_agent_names: set[str]
) -> None:
    ...
```

**Step 3: Remove `repo_opencode_config` and `installed_opencode_config` fixtures (lines 187–197)**

These parsed `opencode.jsonc` for disable-flag validation. Both are now unused:
```python
@pytest.fixture(scope="session")
def repo_opencode_config(repo_root: Path) -> dict:
    ...

@pytest.fixture(scope="session")
def installed_opencode_config(install_dir: Path) -> dict:
    ...
```

> Note: keep `parse_opencode_jsonc` and `_strip_jsonc` — they're tested in `test_conftest.py` and may be useful in the future.

**Step 4: Run the conftest unit tests to verify no breakage**

```bash
python -m pytest tests/test_conftest.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add tests/conftest.py
git commit -m "test: update conftest fixtures for agents-pool and preset layout"
```

---

### Task 9: Update `test_installation.py`

Replace the old agent-copy assertions and `TestAgentDisableConfig` with new pool and preset assertions.

**Files:**
- Modify: `tests/test_installation.py`

**Step 1: Update `TestFilesCopied.test_all_files_copied`**

Replace the agents section (currently checks `installed_agent_files` vs `repo_agent_files`):

```python
class TestFilesCopied:
    def test_all_files_copied(
        self,
        repo_root,
        repo_agent_files,
        install_dir,
        installed_agent_files,
        installed_skill_dirs,
    ) -> None:
        # Agents are in agents-pool, not agents/
        repo_agent_names_set = {f.name for f in repo_agent_files}
        installed_agent_names_set = {f.name for f in installed_agent_files}
        missing_agents = repo_agent_names_set - installed_agent_names_set
        assert not missing_agents, (
            f"Agents not copied to agents-pool: {missing_agents}"
        )

        # agents/ must exist and be empty
        agents_dir = install_dir / "agents"
        assert agents_dir.is_dir(), "agents/ directory does not exist"
        md_files = list(agents_dir.glob("*.md"))
        assert not md_files, (
            f"agents/ must be empty but contains: {[f.name for f in md_files]}"
        )

        # Skills
        repo_skill_dirs = {
            d.name for d in (repo_root / "skills").iterdir() if d.is_dir()
        }
        installed_skill_names = {d.name for d in installed_skill_dirs}
        missing_skills = repo_skill_dirs - installed_skill_names
        assert not missing_skills, (
            f"Skills not copied to installation: {missing_skills}"
        )

        # Each installed skill has SKILL.md
        for skill_dir in installed_skill_dirs:
            assert (skill_dir / "SKILL.md").is_file(), (
                f"Skill '{skill_dir.name}' missing SKILL.md"
            )
```

**Step 2: Update `test_no_extra_skills_or_agents`**

The agents check should still compare pool against repo:

```python
    def test_no_extra_skills_or_agents(
        self,
        repo_root,
        repo_agent_files,
        installed_agent_files,
        installed_skill_dirs,
    ) -> None:
        # No extra agents in pool
        repo_agent_names_set = {f.name for f in repo_agent_files}
        installed_agent_names_set = {f.name for f in installed_agent_files}
        extra_agents = installed_agent_names_set - repo_agent_names_set
        assert not extra_agents, f"Extra agents found in agents-pool: {extra_agents}"

        # No extra skills
        repo_skill_dirs = {
            d.name for d in (repo_root / "skills").iterdir() if d.is_dir()
        }
        installed_skill_names = {d.name for d in installed_skill_dirs}
        extra_skills = installed_skill_names - repo_skill_dirs
        assert not extra_skills, f"Extra skills found in installation: {extra_skills}"
```

**Step 3: Add `TestPresets` class**

```python
from tests.conftest import parse_preset_yaml


class TestPresets:
    def test_preset_dirs_exist(
        self,
        repo_root: Path,
        installed_preset_dirs: list[Path],
    ) -> None:
        yaml_files = sorted((repo_root / ".opencode" / "configs").glob("*.yaml"))
        expected_names = {f.stem for f in yaml_files}
        installed_names = {d.name for d in installed_preset_dirs}
        missing = expected_names - installed_names
        assert not missing, (
            f"Preset directories not created for: {missing}"
        )

    def test_preset_agents_match_yaml(
        self,
        repo_root: Path,
        installed_preset_dirs: list[Path],
    ) -> None:
        yaml_dir = repo_root / ".opencode" / "configs"
        for preset_dir in installed_preset_dirs:
            yaml_file = yaml_dir / f"{preset_dir.name}.yaml"
            if not yaml_file.exists():
                continue
            expected_agents = set(parse_preset_yaml(yaml_file))
            installed_agents = {
                f.stem for f in (preset_dir / "agents").glob("*.md")
            }
            assert expected_agents == installed_agents, (
                f"Preset '{preset_dir.name}': expected agents {expected_agents}, "
                f"got {installed_agents}"
            )

    def test_preset_symlinks_valid(
        self,
        install_dir: Path,
        installed_preset_dirs: list[Path],
    ) -> None:
        pool_dir = install_dir / "agents-pool"
        for preset_dir in installed_preset_dirs:
            for symlink in (preset_dir / "agents").glob("*.md"):
                assert symlink.is_symlink(), (
                    f"{symlink} is not a symlink"
                )
                assert symlink.resolve().parent == pool_dir.resolve(), (
                    f"{symlink} does not point into agents-pool/"
                )
                assert symlink.exists(), (
                    f"Symlink {symlink} is broken (target does not exist)"
                )
```

**Step 4: Remove `TestAgentDisableConfig` entirely** (delete the class at the bottom of the file, currently lines 108–115)

**Step 5: Run all installation tests**

```bash
python -m pytest tests/test_installation.py -v
```

Expected: PASS for all classes. `TestAgentDisableConfig` no longer exists.

**Step 6: Commit**

```bash
git add tests/test_installation.py
git commit -m "test: update test_installation.py for preset layout"
```

---

### Task 10: Run full test suite and verify

**Step 1: Run all tests**

```bash
python -m pytest tests/ -v
```

Expected: all tests pass, no references to `assert_agents_explicitly_disabled`, `repo_opencode_config`, or `installed_opencode_config`.

**Step 2: Manually smoke-test the presets**

```bash
source ~/.bashrc

# Verify ocode function is defined
type ocode

# Verify preset dirs exist
ls ~/.config/opencode/presets/

# Verify symlinks in superpowers preset
ls -la ~/.config/opencode/presets/superpowers/agents/

# Verify default preset is empty
ls ~/.config/opencode/presets/default/agents/

# Verify agents-pool has processed content (no placeholders, has UsingSuperpowers)
grep -L "<HIGH_EFFORT>" ~/.config/opencode/agents-pool/*.md  # all files should appear
grep -c "EXTREMELY-IMPORTANT" ~/.config/opencode/agents-pool/architect.md  # should print 1

# Check ocode rejects bad preset
ocode nonexistent  # should print "Unknown preset: nonexistent"
```

**Step 3: Commit if any fixups were needed, then tag**

```bash
git add -A
git commit -m "chore: fixups from smoke test"
```
