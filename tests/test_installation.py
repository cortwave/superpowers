import re


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

    def test_no_extra_skills_or_agents(
        self,
        repo_root,
        repo_agent_files,
        installed_agent_files,
        installed_skill_dirs,
    ) -> None:
        # No extra agents
        repo_agent_names_set = {f.name for f in repo_agent_files}
        installed_agent_names_set = {f.name for f in installed_agent_files}
        extra_agents = installed_agent_names_set - repo_agent_names_set
        assert not extra_agents, f"Extra agents found in installation: {extra_agents}"

        # No extra skills
        repo_skill_dirs = {
            d.name for d in (repo_root / "skills").iterdir() if d.is_dir()
        }
        installed_skill_names = {d.name for d in installed_skill_dirs}
        extra_skills = installed_skill_names - repo_skill_dirs
        assert not extra_skills, f"Extra skills found in installation: {extra_skills}"


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
