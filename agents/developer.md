---
name: developer
mode: primary
temperature: 0.0
color: "#d48104"
model: <MEDIUM_EFFORT>
permission:
  task:
    "*": deny
    "code-reviewer": allow
    "explorer": allow
    "developer": allow
  skill:
    "*": deny
    "dispatching-parallel-agents": allow
    "finishing-a-development-branch": allow
    "executing-plans": allow
    "receiving-code-review": allow
    "requesting-code-review": allow
    "subagent-driven-development": allow
    "systematic-debugging": allow
    "test-driven-development": allow
    "using-git-worktrees": allow
    "verification-before-completion": allow 
    "python-development": allow
---
