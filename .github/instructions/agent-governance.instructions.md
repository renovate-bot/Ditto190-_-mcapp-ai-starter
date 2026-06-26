---
description: "Govern authoring of agents, instructions, skills, prompts, and workflow definitions by separating planner/orchestrator roles from bounded worker roles and using explicit trigger surfaces."
applyTo: "{.github/agents/**/*.agent.md,.github/instructions/**/*.instructions.md,.github/prompts/**/*.prompt.md,.github/skills/**/SKILL.md,.github/workflows/**/*.yml,awesome-copilot/agents/**/*.agent.md,awesome-copilot/skills/**/SKILL.md,consolidated_sources/awesome-copilot/agents/**/*.agent.md,consolidated_sources/awesome-copilot/skills/**/SKILL.md}"
---

# Agent Governance

## Primitive Separation

- Use instructions for always-on guidance and scoped file behavior.
- Use agents for isolated roles with distinct expertise, tool access, or delegation boundaries.
- Use skills for reusable, invoked workflows with concrete triggers and bundled assets.
- Use prompts for single focused tasks with minimal orchestration.
- Use workflows for staged automation and CI/CD execution paths.

## Authoring Rules

- Treat `description` as the discovery surface; include concrete trigger phrases and use cases.
- Keep agent roles explicit: orchestrators plan and delegate; worker agents execute bounded tasks.
- Prefer narrow tool lists for worker agents and broader tool lists only for orchestrators.
- Use `runSubagent` for bounded execution work; use `switch_agent` only when architectural planning or approach selection is genuinely required.
- When authoring repo or CI automation agents, prefer GitHub and workflow-native tools for run, job, and artifact inspection before generic web fetches.
- Keep workflow steps verifiable with explicit acceptance criteria, validation commands, or artifact checks.

## Pattern Guidance

- Orchestrator agents should define phases such as analysis, delegation, synthesis, and quality gate.
- Worker agents should focus on one domain, one outcome, and one return format.
- Governance or review agents should emphasize fail-closed decisions, explicit trust boundaries, and auditability.
- Generation-oriented agents should prefer scaffolding existing structures before inventing new ones from scratch.

## GenerateAgents Usage

- For new agent, team, or workflow scaffolding, prefer GenerateAgents or create-agentsmd-style generation flows as the starting point.
- Generated assets must still be reviewed for repository-specific tools, validation commands, and trigger phrases before adoption.
