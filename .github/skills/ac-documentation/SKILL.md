---
name: ac-documentation
description: >
  Generate and maintain AGENTS.md documentation files for repositories. Use when asked to
  create AGENTS.md, generate documentation, run autogenerateagentsmd, update agent docs,
  document a codebase, create architecture docs for AI agents, or run the GenerateAgents CLI.
  Triggers: 'generate AGENTS.md', 'create docs', 'autogenerateagentsmd', 'document codebase',
  'update AGENTS.md', 'architecture docs', 'uv run autogenerateagentsmd'.
---

# AC Documentation Skill

Generate and maintain AGENTS.md documentation using the GenerateAgents.md CLI tool.

## When to Use This Skill

- Creating or updating an `AGENTS.md` file for a repository
- Running `uv run autogenerateagentsmd` against a codebase
- Documenting multi-agent architectures
- Keeping agent instructions up-to-date after code changes

## Prerequisites

- `uv` package manager installed
- GenerateAgents.md: `cd GenerateAgents.md && uv sync --extra dev`
- LLM API key (Gemini recommended)

## Step-by-Step Workflows

### Generate AGENTS.md for this repo

```bash
cd /workspaces/mcapp-ai-starter/GenerateAgents.md
export GEMINI_API_KEY="your-key"
uv run autogenerateagentsmd /workspaces/mcapp-ai-starter --style comprehensive
```

### Generate for a specific subfolder

```bash
uv run autogenerateagentsmd /workspaces/mcapp-ai-starter/awesome-copilot --style comprehensive
```

### Available styles

- `comprehensive` — full architecture docs (recommended for agent use)
- `strict` — minimal, constraint-focused docs

### Validate GenerateAgents tests

```bash
cd /workspaces/mcapp-ai-starter/GenerateAgents.md
uv run pytest -m 'not e2e' -q
```

## AGENTS.md Structure Template

```markdown
# AGENTS.md — <Project Name>

## Overview
Brief description of the project purpose and architecture.

## Repository Structure
Key directories and their roles.

## Agents
List of AI agents and their roles.

## Build Commands
Quick commands for CI tasks.

## Conventions
Code style, naming rules, and critical constraints.

## Important Notes
Security rules, gotchas, integration points.
```

## Important Notes

- Always use `uv run` — never use `python` or `pip` directly
- E2E tests require LLM API keys; skip with `-m 'not e2e'` in CI
- AGENTS.md files in `consolidated_sources/` are READ-ONLY references
