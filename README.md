# Superpowers

A fork of [obra/superpowers](https://github.com/obra/superpowers), rebuilt exclusively for [OpenCode](https://opencode.ai) with specialized agents that replace the original monolithic workflow.

The key difference: instead of one agent doing everything, this fork splits work across **6 focused agents** with scoped skill permissions. Each agent has a defined role, temperature, and set of allowed skills -- preventing overreach and keeping context tight.

## Agents

| Agent | Mode | Role | Skills |
|-------|------|------|--------|
| **architect** | primary (0.7) | Designs solutions, explores trade-offs, produces design docs and implementation plans. Cannot write code. | brainstorming, writing-plans, dispatching-parallel-agents |
| **explorer** | primary (0.0) | Finds, extracts, and synthesizes information from code, docs, and the web. Cannot edit files. | exploring-codebases, dispatching-parallel-agents |
| **developer** | primary (0.0) | The main coding agent. Writes code, runs tests, manages branches, reviews work. | TDD, systematic-debugging, SDD, executing-plans, code-review, verification, python-development |
| **investigator** | all (0.5) | Finds and analyzes bugs and unexpected behavior. Cannot edit files without asking. | systematic-debugging, brainstorming |
| **code-reviewer** | subagent | Reviews completed steps against plans and coding standards. No external skills. | none |
| **writer** | subagent (0.5) | Writing subagent for docs and skills. | writing-skills |

**How agents interact:** The developer can launch code-reviewer as a subagent. The architect and investigator can request edits but need confirmation. The explorer is read-only. This separation enforces discipline -- the agent designing your system is not the same one implementing it.

## Workflow

1. **Design** -- `@architect` refines your idea through brainstorming, produces a design doc
2. **Plan** -- `@architect` breaks the design into implementation tasks with verification steps
3. **Build** -- `@developer` executes the plan using TDD and subagent-driven development
4. **Review** -- `@code-reviewer` checks each step against the plan
5. **Ship** -- `@developer` runs final verification, creates PR or merges

Use `@explorer` or `@investigator` at any point for research or debugging.

Skills trigger automatically. The agents check for relevant skills before every task.

## Presets

The installer creates two named presets, each launched via the `ocode` shell function:

| Preset | Agents | Skills | Usage |
|--------|--------|--------|-------|
| **swe** | all 6 agents | all skills | `ocode swe` |
| **default** | none (OpenCode built-ins) | none | `ocode` or `ocode default` |

Presets live in `~/.config/opencode/presets/<name>/`. Each preset has:
- `agents/` — symlinks into `~/.config/opencode/agents-pool/`
- `skills/` — symlinks into `~/.config/opencode/skills-pool/`
- `opencode.jsonc` — disables built-in agents when custom agents are present

To add a custom preset, create a YAML file in `.opencode/configs/` and re-run `./install.sh`:

```yaml
# .opencode/configs/mypreset.yaml
agents:
  - developer
  - explorer
skills:
  - "*"        # all skills, or list names explicitly
```

Then launch it with `ocode mypreset`.

## Installation

**IMPORTANT** running this installation will replace all your current skills, agents and config under `~/.config/opencode`

**IMPORTANT** update model names in `models.conf` to specify which models agents should use

Requires [OpenCode](https://opencode.ai).

```bash
./install.sh
```

The installer:
1. Copies all agents into `~/.config/opencode/agents-pool/`
2. Copies all skills into `~/.config/opencode/skills-pool/`
3. Creates a preset directory for each YAML in `.opencode/configs/`, with symlinks for the listed agents and skills
4. Installs an `ocode` shell function in `~/.bashrc` for launching presets

## License

MIT License -- see LICENSE file for details.

## Credits

Based on [obra/superpowers](https://github.com/obra/superpowers) by Jesse Vincent. This fork strips multi-tool support and adds the specialized agents system for OpenCode.

- **Original**: https://github.com/obra/superpowers
- **This fork**: https://github.com/cortwave/superpowers
