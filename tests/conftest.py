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
def install_dir() -> Path:
    return Path.home() / ".config" / "opencode"


@pytest.fixture(scope="session")
def installed_agent_files(install_dir: Path) -> list[Path]:
    agents_dir = install_dir / "agents"
    if not agents_dir.is_dir():
        pytest.skip("Installation directory not found — run install.sh first")
    return sorted(agents_dir.glob("*.md"))


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
    skills_dir = install_dir / "skills"
    if not skills_dir.is_dir():
        pytest.skip("Installation directory not found — run install.sh first")
    return sorted([d for d in skills_dir.iterdir() if d.is_dir()])


@pytest.fixture(scope="session")
def using_superpowers_content(repo_root: Path) -> str:
    return (repo_root / ".opencode" / "UsingSuperpowers.md").read_text(encoding="utf-8")
