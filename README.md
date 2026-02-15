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

## Skills

16 composable skills that agents invoke automatically based on context.

**Design and Planning**
- **brainstorming** -- Socratic design refinement before code
- **writing-plans** -- Detailed implementation plans with exact file paths and verification steps
- **executing-plans** -- Batch execution with human checkpoints

**Development**
- **test-driven-development** -- RED-GREEN-REFACTOR cycle
- **subagent-driven-development** -- Fast iteration with two-stage review (spec compliance, then code quality)
- **python-development** -- Python-specific practices (uv, pyrefly, pydantic, ruff)
- **using-git-worktrees** -- Isolated development branches

**Quality**
- **systematic-debugging** -- 4-phase root cause process
- **verification-before-completion** -- Ensure fixes are actually fixed
- **requesting-code-review** -- Pre-review checklist
- **receiving-code-review** -- Responding to feedback with technical rigor

**Coordination**
- **dispatching-parallel-agents** -- Concurrent subagent workflows
- **finishing-a-development-branch** -- Merge/PR decision workflow

**Meta**
- **using-superpowers** -- Introduction to the skills system
- **writing-skills** -- Create new skills following best practices
- **exploring-codebases** -- Structured codebase exploration

## Workflow

1. **Design** -- `@architect` refines your idea through brainstorming, produces a design doc
2. **Plan** -- `@architect` breaks the design into implementation tasks with verification steps
3. **Build** -- `@developer` executes the plan using TDD and subagent-driven development
4. **Review** -- `@code-reviewer` checks each step against the plan
5. **Ship** -- `@developer` runs final verification, creates PR or merges

Use `@ask` or `@investigator` at any point for research or debugging.

Skills trigger automatically. The agents check for relevant skills before every task -- mandatory workflows, not suggestions.

## Installation

Requires [OpenCode](https://opencode.ai) and Git.

```bash
# Clone
git clone https://github.com/cortwave/superpowers.git ~/.config/opencode/superpowers

# Symlink plugin
mkdir -p ~/.config/opencode/plugins
rm -f ~/.config/opencode/plugins/superpowers.js
ln -s ~/.config/opencode/superpowers/.opencode/plugins/superpowers.js ~/.config/opencode/plugins/superpowers.js

# Symlink skills
mkdir -p ~/.config/opencode/skills
rm -rf ~/.config/opencode/skills/superpowers
ln -s ~/.config/opencode/superpowers/skills ~/.config/opencode/skills/superpowers

# Copy OpenCode config
cp ~/.config/opencode/superpowers/.opencode/opencode.jsonc ~/.config/opencode/opencode.jsonc

# Copy agents
cp -r ~/.config/opencode/superpowers/agents ~/.config/opencode/agents

# Restart OpenCode
```

For Windows instructions or troubleshooting, see [docs/README.opencode.md](docs/README.opencode.md).

### Updating

```bash
cd ~/.config/opencode/superpowers && git pull
```

Restart OpenCode to load updates.

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
