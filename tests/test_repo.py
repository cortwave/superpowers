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
