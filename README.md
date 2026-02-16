# Superpowers

A fork of [obra/superpowers](https://github.com/obra/superpowers), rebuilt exclusively for [OpenCode](https://opencode.ai) with specialized agents that replace the original monolithic workflow.

The key difference: instead of one agent doing everything, this fork splits work across **6 focused agents** with scoped skill permissions. Each agent has a defined role, temperature, and set of allowed skills -- preventing overreach and keeping context tight.

## Agents

| Agent | Mode | Role | Skills |
|-------|------|------|--------|
| **architect** | primary (0.7) | Designs solutions, explores trade-offs, produces design docs and implementation plans. Cannot write code. | brainstorming, writing-plans, dispatching-parallel-agents |
| **ask** | primary (0.0) | Finds, extracts, and synthesizes information from code, docs, and the web. Cannot edit files. | exploring-codebases, dispatching-parallel-agents |
| **developer** | primary (0.0) | The main coding agent. Writes code, runs tests, manages branches, reviews work. | TDD, systematic-debugging, SDD, executing-plans, git-worktrees, code-review, verification, python-development |
| **investigator** | all (0.5) | Finds and analyzes bugs and unexpected behavior. Cannot edit files without asking. | systematic-debugging, brainstorming |
| **code-reviewer** | subagent | Reviews completed steps against plans and coding standards. No external skills. | none |
| **writer** | subagent (0.5) | Writing subagent for docs and skills. | writing-skills |

**How agents interact:** The developer can launch code-reviewer as a subagent. The architect and investigator can request edits but need confirmation. The ask agent is read-only. This separation enforces discipline -- the agent designing your system is not the same one implementing it.

## Workflow

1. **Design** -- `@architect` refines your idea through brainstorming, produces a design doc
2. **Plan** -- `@architect` breaks the design into implementation tasks with verification steps
3. **Build** -- `@developer` executes the plan using TDD and subagent-driven development
4. **Review** -- `@code-reviewer` checks each step against the plan
5. **Ship** -- `@developer` runs final verification, creates PR or merges

Use `@ask` or `@investigator` at any point for research or debugging.

Skills trigger automatically. The agents check for relevant skills before every task.

## Installation

**IMPORTANT** running this installation will replace all your current skills, agents and config under `~/.config/opencode`

Requires [OpenCode](https://opencode.ai) and Git.

```bash

# remove existing installation
rm -rf ~/.config/opencode/superpowers

# Clone
git clone https://github.com/cortwave/superpowers.git ~/.config/opencode/superpowers

# Symlink skills
mkdir -p ~/.config/opencode/skills
rm -rf ~/.config/opencode/skills/superpowers
cp -r ~/.config/opencode/superpowers/skills ~/.config/opencode/skills

# Copy OpenCode config
cp ~/.config/opencode/superpowers/.opencode/opencode.jsonc ~/.config/opencode/opencode.jsonc

# Copy agents
rm -rf ~/.config/opencode/agents
cp -r ~/.config/opencode/superpowers/agents ~/.config/opencode/agents

# Restart OpenCode
```

## Repo Structure

```
agents/     6 specialized agent definitions
skills/     16 composable skills
.opencode/  Plugin, config, install docs
lib/        Shared JS utilities
docs/       Extended documentation
tests/      Test suites
```

## Philosophy

- **Test-Driven Development** -- Write tests first, always
- **Systematic over ad-hoc** -- Process over guessing
- **Complexity reduction** -- Simplicity as primary goal
- **Evidence over claims** -- Verify before declaring success
- **Separation of concerns** -- Agents with scoped roles prevent context pollution and enforce discipline

## Contributing

1. Fork the repository
2. Create a branch
3. Follow the `writing-skills` skill for new skills, or model new agents on existing ones in `agents/`
4. Submit a PR

See `skills/writing-skills/SKILL.md` for the skill authoring guide.

## License

MIT License -- see LICENSE file for details.

## Credits

Based on [obra/superpowers](https://github.com/obra/superpowers) by Jesse Vincent. This fork strips multi-tool support and adds the specialized agents system for OpenCode.

- **Original**: https://github.com/obra/superpowers
- **This fork**: https://github.com/cortwave/superpowers
- **Issues**: https://github.com/cortwave/superpowers/issues
