# Agents directory — guidance for `awesome-copilot/agents/`

## Purpose

This file gives quick, folder-scoped rules for creating and maintaining `.agent.md` files inside `awesome-copilot/agents/`.

## What to read first

- `awesome-copilot/AGENTS.md` — global agent library guidance
- Existing `.agent.md` files in this folder — follow their metadata/frontmatter as examples

## File conventions

- Filenames: lowercase with hyphens (e.g., `api-architect.agent.md`).
- Front matter: include `description` (required), `tools` (if needed), and `model` (recommended).
- Keep the `description` concise and include trigger keywords that agents might use to discover the file.

## Validation

- Run `npm run build` in `awesome-copilot/` to regenerate marketplace files and validate plugin manifests.

## Tips

- Test new agents locally by referencing them from the Prompt Registry or by opening files that should trigger the instruction (ensures `applyTo` patterns match).
- Keep examples short and include usage scenarios and limitations.
