import re
from pathlib import Path

from tests.conftest import (
    parse_opencode_jsonc,
    parse_preset_yaml,
    parse_preset_yaml_skills,
)

OPENCODE_BUILTIN_AGENTS: frozenset[str] = frozenset(
    {"plan", "build", "general", "explore"}
)


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
        assert not missing_agents, f"Agents not copied to agents-pool: {missing_agents}"

        # agents/ must exist and be empty
        agents_dir = install_dir / "agents"
        assert agents_dir.is_dir(), "agents/ directory does not exist"
        md_files = list(agents_dir.glob("*.md"))
        assert not md_files, (
            f"agents/ must be empty but contains: {[f.name for f in md_files]}"
        )

        # Skills are in skills-pool, not skills/
        repo_skill_names = {
            d.name for d in (repo_root / "skills").iterdir() if d.is_dir()
        }
        installed_skill_names = {d.name for d in installed_skill_dirs}
        missing_skills = repo_skill_names - installed_skill_names
        assert not missing_skills, f"Skills not copied to skills-pool: {missing_skills}"

        # Each installed skill has SKILL.md
        for skill_dir in installed_skill_dirs:
            assert (skill_dir / "SKILL.md").is_file(), (
                f"Skill '{skill_dir.name}' missing SKILL.md"
            )

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

        # No extra skills in pool
        repo_skill_names = {
            d.name for d in (repo_root / "skills").iterdir() if d.is_dir()
        }
        installed_skill_names = {d.name for d in installed_skill_dirs}
        extra_skills = installed_skill_names - repo_skill_names
        assert not extra_skills, f"Extra skills found in skills-pool: {extra_skills}"


class TestModelReplacement:
    PLACEHOLDER_RE = re.compile(r"^<.+>$")

    def test_model_placeholders_replaced(
        self, installed_agents, models_conf_values
    ) -> None:
        for path, fm, _text in installed_agents:
            agent_name = fm["name"]
            model = fm.get("model")
            assert model is not None, (
                f"Installed agent '{agent_name}' ({path.name}) has no model field"
            )
            assert not self.PLACEHOLDER_RE.match(model), (
                f"Installed agent '{agent_name}' ({path.name}) still has "
                f"unreplaced placeholder: {model}"
            )
            assert model in models_conf_values, (
                f"Installed agent '{agent_name}' ({path.name}) has model "
                f"'{model}' which is not a value in models.conf. "
                f"Expected one of: {models_conf_values}"
            )


class TestUsingSuperpowersAppended:
    def test_using_superpowers_appended_once(
        self, installed_agents, using_superpowers_content
    ) -> None:
        marker = using_superpowers_content.splitlines()[0]
        for path, fm, text in installed_agents:
            agent_name = fm["name"]
            assert using_superpowers_content in text, (
                f"Installed agent '{agent_name}' ({path.name}) does not "
                f"contain UsingSuperpowers.md content"
            )
            count = text.count(marker)
            assert count == 1, (
                f"Installed agent '{agent_name}' ({path.name}) contains "
                f"UsingSuperpowers marker {count} times (expected exactly 1)"
            )


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
        assert not missing, f"Preset directories not created for: {missing}"

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
            installed_agents = {f.stem for f in (preset_dir / "agents").glob("*.md")}
            assert expected_agents == installed_agents, (
                f"Preset '{preset_dir.name}': expected agents {expected_agents}, "
                f"got {installed_agents}"
            )

    def test_preset_agent_symlinks_valid(
        self,
        install_dir: Path,
        installed_preset_dirs: list[Path],
    ) -> None:
        pool_dir = install_dir / "agents-pool"
        for preset_dir in installed_preset_dirs:
            for symlink in (preset_dir / "agents").glob("*.md"):
                assert symlink.is_symlink(), f"{symlink} is not a symlink"
                assert symlink.resolve().parent == pool_dir.resolve(), (
                    f"{symlink} does not point into agents-pool/"
                )
                assert symlink.exists(), (
                    f"Symlink {symlink} is broken (target does not exist)"
                )

    def test_preset_skills_match_yaml(
        self,
        repo_root: Path,
        install_dir: Path,
        installed_preset_dirs: list[Path],
    ) -> None:
        yaml_dir = repo_root / ".opencode" / "configs"
        all_pool_skills = {
            d.name for d in (install_dir / "skills-pool").iterdir() if d.is_dir()
        }
        for preset_dir in installed_preset_dirs:
            yaml_file = yaml_dir / f"{preset_dir.name}.yaml"
            if not yaml_file.exists():
                continue
            skills_spec = parse_preset_yaml_skills(yaml_file)
            if skills_spec == ["*"]:
                expected_skills = all_pool_skills
            else:
                expected_skills = set(skills_spec)
            installed_skills = (
                {d.name for d in (preset_dir / "skills").iterdir() if d.is_dir()}
                if (preset_dir / "skills").is_dir()
                else set()
            )
            assert expected_skills == installed_skills, (
                f"Preset '{preset_dir.name}': expected skills {expected_skills}, "
                f"got {installed_skills}"
            )

    def test_preset_skill_symlinks_valid(
        self,
        install_dir: Path,
        installed_preset_dirs: list[Path],
    ) -> None:
        pool_dir = install_dir / "skills-pool"
        for preset_dir in installed_preset_dirs:
            skills_dir = preset_dir / "skills"
            if not skills_dir.is_dir():
                continue
            for symlink in skills_dir.iterdir():
                if not symlink.is_symlink():
                    continue
                assert symlink.resolve().parent == pool_dir.resolve(), (
                    f"{symlink} does not point into skills-pool/"
                )
                assert symlink.exists(), (
                    f"Symlink {symlink} is broken (target does not exist)"
                )

    def test_preset_jsonc_exists(
        self,
        installed_preset_dirs: list[Path],
    ) -> None:
        for preset_dir in installed_preset_dirs:
            assert (preset_dir / "opencode.jsonc").is_file(), (
                f"Preset '{preset_dir.name}' is missing opencode.jsonc"
            )

    def test_preset_jsonc_disables_builtins_when_agents_present(
        self,
        repo_root: Path,
        installed_preset_dirs: list[Path],
    ) -> None:
        yaml_dir = repo_root / ".opencode" / "configs"
        for preset_dir in installed_preset_dirs:
            yaml_file = yaml_dir / f"{preset_dir.name}.yaml"
            if not yaml_file.exists():
                continue
            expected_agents = parse_preset_yaml(yaml_file)
            config = parse_opencode_jsonc(preset_dir / "opencode.jsonc")
            agent_block = config.get("agent", {})
            if not expected_agents:
                assert not agent_block, (
                    f"Preset '{preset_dir.name}' has no agents but opencode.jsonc "
                    f"contains an agent block: {agent_block}"
                )
            else:
                for builtin in OPENCODE_BUILTIN_AGENTS:
                    entry = agent_block.get(builtin, {})
                    assert entry.get("disable") is True, (
                        f"Preset '{preset_dir.name}': built-in agent '{builtin}' "
                        f"is not disabled in opencode.jsonc"
                    )
