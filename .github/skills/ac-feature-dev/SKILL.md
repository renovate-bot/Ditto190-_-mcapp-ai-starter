---
name: ac-feature-dev
description: >
  Build new agent skills, plugins, and Node.js features for the awesome-copilot library.
  Use when asked to scaffold a new skill, create a plugin, add a Node.js feature, run the
  awesome-copilot build pipeline, or generate SKILL.md files from templates.
  Triggers: 'create skill', 'new plugin', 'scaffold agent feature', 'skill:create', 'plugin:create',
  'npm run build', 'generate skill', 'add feature to awesome-copilot'.
---

# AC Feature Dev Skill

Build and scaffold new agent skills, plugins, and Node.js features inside the `awesome-copilot` library.

## When to Use This Skill

- Scaffolding a new SKILL.md or plugin
- Running `npm run skill:create` or `npm run plugin:create`
- Adding a Node.js npm feature to awesome-copilot
- Generating a marketplace entry via `npm run build`

## Prerequisites

- Node.js 20+
- Run from `awesome-copilot/` directory
- `npm ci` already run

## Step-by-Step Workflows

### Create a new skill

```bash
cd /workspaces/mcapp-ai-starter/awesome-copilot
npm run skill:create
# Follow prompts for name and description
```

### Create a new plugin

```bash
cd /workspaces/mcapp-ai-starter/awesome-copilot
npm run plugin:create
# Follow prompts
```

### Build the full library

```bash
cd /workspaces/mcapp-ai-starter/awesome-copilot
npm run build
```

### Validate skills

```bash
npm run skill:validate
npm run plugin:validate
```

## Skill SKILL.md Template

```yaml
---
name: my-skill-name        # lowercase-hyphen, max 64 chars
description: >             # WHAT it does + WHEN to use it + keywords
  Describe capabilities clearly. Use when asked to X, Y, or Z.
  Supports: tool1, tool2.
---

# Skill Title

Brief overview.

## When to Use This Skill

- Scenario 1
- Scenario 2

## Prerequisites

- Tool/env requirements

## Step-by-Step Workflows

1. Step one
2. Step two
```

## Conventions

- Skill names: lowercase-hyphen, ≤64 chars
- `description` is the PRIMARY discovery mechanism — include `Use when asked to...` and keywords
- Body ≤500 lines; large content splits into `references/` subdirectory
- No hardcoded credentials or secrets
- Relative paths only
