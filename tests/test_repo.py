from pathlib import Path


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
