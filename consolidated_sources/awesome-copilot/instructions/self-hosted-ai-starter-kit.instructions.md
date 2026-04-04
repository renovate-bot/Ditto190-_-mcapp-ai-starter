---
description: "Coding & agent instructions for the self-hosted-ai-starter-kit repo"
applyTo: "**/*"
---

## Purpose

This instructions file encodes repository-wide conventions and agent behaviors for contributors and Copilot-style agents operating on this repository. It is derived from `.github/copilot-instructions.md` and the project's top-level README; follow it when editing, generating agents, or authoring agent prompts.

## Key rules (enforced)

- Python: target Python 3.12+. Use explicit type hints on all public function signatures and return types.
- Naming: snake_case for functions and variables, PascalCase for classes, ALL_CAPS_WITH_UNDERSCORES for constants.
- Imports: group and order imports as (1) standard library, (2) third-party, (3) local packages.
- File naming: lowercase with hyphens for files added under `awesome-copilot/` (e.g., `my-agent.agent.md`).
- Front matter strings in `.agent.md`, `SKILL.md`, and `*.instructions.md` must use single quotes.
- .env: never commit `.env` files or secrets; prefer `.env.example` and load secrets via `python-dotenv` or CI secrets.
- Tests: mark integration tests that require API keys with `@pytest.mark.e2e`; CI should skip e2e by default.

## Agent & content conventions

- Agents: store agents in `awesome-copilot/agents/` using `.agent.md` with front matter including `description` (required) and `tools`/`model` (recommended).
- Instructions files: put repo-scoped or file-pattern-scoped guidance in `awesome-copilot/instructions/` with `applyTo` patterns. Prefer narrow applyTo where possible.
- Skills: each skill folder must include `SKILL.md` with front matter `name` and `description`; folder name must match the `name` field (lowercase-hyphen).
- Plugins: manifest files under `plugins/` and `.github/plugin/` must validate during `npm run build` for `awesome-copilot`.

## How to use these instructions

- When opening a file, agents should first consult this instructions file and `.github/copilot-instructions.md`.
- For code generation: follow the repo coding conventions above; include type hints and tests for new features.
- For creating agents/skills: follow the content types and front-matter rules; run `npm run build` in `awesome-copilot` to validate marketplace artifacts.

## Example prompts for testing

- "Create a new agent that analyzes Git history and outputs AGENTS.md; follow repository naming, front-matter, and Python typing rules."
- "Generate a `SKILL.md` skeleton for a Terraform skill named 'terraform-azurerm-set-diff-analyzer' with front matter fields `name` and `description` using single quotes."

## Notes & rationale

These instructions capture the repository's explicit conventions (type hints, naming, import grouping), safety rules (never commit secrets), and the expected layout for agents/skills/plugins used across the mono-repo. Keep them concise and reference `.github/copilot-instructions.md` for the full developer guide.

If anything here should apply only to a subset of files (e.g., only `GenerateAgents.md` Python code), tell me which patterns to narrow `applyTo` to and I'll update the file.
