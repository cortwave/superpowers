---
name: writer
mode: subagent
temperature: 0.5
permission:
  task:
    "*": deny
    "explore": allow
  skill:
    "*": deny
    "dispatching-parallel-agents": allow
    "using-superpower": allow
    "writing-skills": allow
---
