class TestFilesCopied:
    def test_all_files_copied(
        self,
        repo_root,
        repo_agent_files,
        install_dir,
        installed_agent_files,
        installed_skill_dirs,
    ) -> None:
        # Agents
        repo_agent_names_set = {f.name for f in repo_agent_files}
        installed_agent_names_set = {f.name for f in installed_agent_files}
        missing_agents = repo_agent_names_set - installed_agent_names_set
        assert not missing_agents, (
            f"Agents not copied to installation: {missing_agents}"
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

        # opencode.jsonc
        assert (install_dir / "opencode.jsonc").is_file(), (
            "opencode.jsonc not copied to installation"
        )
