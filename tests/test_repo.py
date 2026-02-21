from pathlib import Path
import re

from tests.conftest import parse_preset_yaml, parse_preset_yaml_skills


class TestSkillPermissions:
    def test_all_skills_denied_by_default(
        self, repo_agents: list[tuple[Path, dict]]
    ) -> None:
        for path, fm in repo_agents:
            agent_name = fm["name"]
            permission = fm.get("permission", {})
            skill_perms = permission.get("skill")
            assert skill_perms is not None, (
                f"Agent '{agent_name}' ({path.name}) has no skill permission block"
            )
            assert skill_perms.get("*") == "deny", (
                f"Agent '{agent_name}' ({path.name}) does not deny all skills by default"
            )

    def test_allowed_skills_exist(
        self, repo_agents: list[tuple[Path, dict]], repo_skill_names: set[str]
    ) -> None:
        for path, fm in repo_agents:
            agent_name = fm["name"]
            skill_perms = fm.get("permission", {}).get("skill", {})
            allowed = [k for k, v in skill_perms.items() if v == "allow"]
            for skill_name in allowed:
                assert skill_name in repo_skill_names, (
                    f"Agent '{agent_name}' ({path.name}) allows skill "
                    f"'{skill_name}' which does not exist in skills/"
                )


class TestTaskPermissions:
    def test_all_agents_denied_by_default_in_task(
        self, repo_agents: list[tuple[Path, dict]]
    ) -> None:
        for path, fm in repo_agents:
            agent_name = fm["name"]
            permission = fm.get("permission", {})
            task_perms = permission.get("task")
            assert task_perms is not None, (
                f"Agent '{agent_name}' ({path.name}) has no task permission block"
            )
            assert task_perms.get("*") == "deny", (
                f"Agent '{agent_name}' ({path.name}) does not deny all agents by default in task permissions"
            )

    def test_allowed_task_agents_exist(
        self, repo_agents: list[tuple[Path, dict]], repo_agent_names: set[str]
    ) -> None:
        for path, fm in repo_agents:
            agent_name = fm["name"]
            task_perms = fm.get("permission", {}).get("task", {})
            allowed = [k for k, v in task_perms.items() if v == "allow"]
            for allowed_agent in allowed:
                assert allowed_agent in repo_agent_names, (
                    f"Agent '{agent_name}' ({path.name}) allows task agent "
                    f"'{allowed_agent}' which does not exist in agents/"
                )


class TestModelPlaceholders:
    PLACEHOLDER_RE = re.compile(r"^<([A-Z_]+)>$")

    def test_model_placeholder_matches_models_conf(
        self, repo_agents: list[tuple[Path, dict]], models_conf_keys: set[str]
    ) -> None:
        for path, fm in repo_agents:
            agent_name = fm["name"]
            model = fm.get("model")
            assert model is not None, (
                f"Agent '{agent_name}' ({path.name}) has no model field"
            )
            match = self.PLACEHOLDER_RE.match(model)
            assert match is not None, (
                f"Agent '{agent_name}' ({path.name}) model '{model}' "
                f"is not a valid placeholder (expected <KEY_NAME>)"
            )
            key = match.group(1)
            assert key in models_conf_keys, (
                f"Agent '{agent_name}' ({path.name}) model placeholder "
                f"'{model}' references key '{key}' not found in models.conf. "
                f"Available keys: {models_conf_keys}"
            )


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

    def test_all_preset_skills_exist(
        self,
        preset_yaml_files: list[Path],
        repo_root: Path,
    ) -> None:
        repo_skill_names = {
            d.name for d in (repo_root / "skills").iterdir() if d.is_dir()
        }
        for yaml_file in preset_yaml_files:
            skills = parse_preset_yaml_skills(yaml_file)
            for skill_name in skills:
                if skill_name == "*":
                    continue
                assert skill_name in repo_skill_names, (
                    f"Preset '{yaml_file.name}' references skill '{skill_name}' "
                    f"which does not exist in skills/"
                )
