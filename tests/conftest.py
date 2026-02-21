import json
import re
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent


def parse_frontmatter(path: Path) -> dict:
    """Parse YAML frontmatter from a markdown file.

    Expects the file to start with '---', followed by YAML,
    followed by another '---'.
    """
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"No valid frontmatter in {path}")
    return yaml.safe_load(parts[1])


def parse_models_conf(path: Path) -> dict[str, str]:
    """Parse models.conf KEY=value lines into a dict."""
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        result[key.strip()] = value.strip()
    return result


def parse_preset_yaml(path: Path) -> list[str]:
    """Parse the agents list from a preset YAML file.

    Returns a list of agent names (may be empty).
    """
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    agents = raw.get("agents") or []
    return [str(a) for a in agents]


def parse_preset_yaml_skills(path: Path) -> list[str]:
    """Parse the skills list from a preset YAML file.

    Returns a list of skill names or ["*"] for all skills (may be empty).
    """
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    skills = raw.get("skills") or []
    return [str(s) for s in skills]


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def repo_agent_files(repo_root: Path) -> list[Path]:
    return sorted((repo_root / "agents").glob("*.md"))


@pytest.fixture(scope="session")
def repo_agents(repo_agent_files: list[Path]) -> list[tuple[Path, dict]]:
    return [(f, parse_frontmatter(f)) for f in repo_agent_files]


@pytest.fixture(scope="session")
def repo_skill_names(repo_root: Path) -> set[str]:
    names: set[str] = set()
    for skill_file in (repo_root / "skills").glob("*/SKILL.md"):
        fm = parse_frontmatter(skill_file)
        names.add(fm["name"])
    return names


@pytest.fixture(scope="session")
def repo_agent_names(repo_agents: list[tuple[Path, dict]]) -> set[str]:
    return {fm["name"] for _, fm in repo_agents}


@pytest.fixture(scope="session")
def models_conf(repo_root: Path) -> dict[str, str]:
    return parse_models_conf(repo_root / "models.conf")


@pytest.fixture(scope="session")
def models_conf_keys(models_conf: dict[str, str]) -> set[str]:
    return set(models_conf.keys())


@pytest.fixture(scope="session")
def models_conf_values(models_conf: dict[str, str]) -> set[str]:
    return set(models_conf.values())


@pytest.fixture(scope="session")
def preset_yaml_files(repo_root: Path) -> list[Path]:
    return sorted((repo_root / ".opencode" / "configs").glob("*.yaml"))


@pytest.fixture(scope="session")
def install_dir() -> Path:
    return Path.home() / ".config" / "opencode"


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


@pytest.fixture(scope="session")
def installed_agents(
    installed_agent_files: list[Path],
) -> list[tuple[Path, dict, str]]:
    result: list[tuple[Path, dict, str]] = []
    for f in installed_agent_files:
        text = f.read_text(encoding="utf-8")
        fm = parse_frontmatter(f)
        result.append((f, fm, text))
    return result


@pytest.fixture(scope="session")
def installed_skill_dirs(install_dir: Path) -> list[Path]:
    pool_dir = install_dir / "skills-pool"
    if not pool_dir.is_dir():
        pytest.skip("skills-pool not found — run install.sh first")
    return sorted([d for d in pool_dir.iterdir() if d.is_dir()])


@pytest.fixture(scope="session")
def installed_skill_pool_dirs(install_dir: Path) -> list[Path]:
    pool_dir = install_dir / "skills-pool"
    if not pool_dir.is_dir():
        pytest.skip("skills-pool not found — run install.sh first")
    return sorted([d for d in pool_dir.iterdir() if d.is_dir()])


@pytest.fixture(scope="session")
def using_superpowers_content(repo_root: Path) -> str:
    return (repo_root / ".opencode" / "UsingSuperpowers.md").read_text(encoding="utf-8")


def _strip_jsonc(text: str) -> str:
    """Strip single-line comments and trailing commas from JSONC text."""
    # Use a tokenising approach: skip over string literals so we don't touch
    # URLs or other // sequences inside strings.
    result: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == '"':
            # Consume the whole string literal verbatim.
            result.append(ch)
            i += 1
            while i < n:
                c = text[i]
                result.append(c)
                if c == "\\" and i + 1 < n:
                    i += 1
                    result.append(text[i])
                elif c == '"':
                    break
                i += 1
            i += 1
        elif ch == "/" and i + 1 < n and text[i + 1] == "/":
            # Single-line comment: skip to end of line.
            while i < n and text[i] != "\n":
                i += 1
        else:
            result.append(ch)
            i += 1
    stripped = "".join(result)
    # Remove trailing commas before } or ]
    stripped = re.sub(r",\s*([}\]])", r"\1", stripped)
    return stripped


def parse_opencode_jsonc(path: Path) -> dict:
    """Parse a JSONC file (strips comments and trailing commas)."""
    raw = path.read_text(encoding="utf-8")
    return json.loads(_strip_jsonc(raw))
