---
name: writer
mode: subagent
model: <HIGH_EFFORT>
temperature: 0.5
permission:
  task:
    "*": deny
    "explorer": allow
  skill:
    "*": deny
    "dispatching-parallel-agents": allow
    "writing-skills": allow
---
