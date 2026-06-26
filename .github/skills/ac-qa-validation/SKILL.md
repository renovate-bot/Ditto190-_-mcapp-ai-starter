---
name: ac-qa-validation
description: >
  Validate agent skills, plugin schemas, workflow delivery, and agent file integrity for the
  awesome-copilot library. Use when asked to validate skills, run QA checks, verify skill
  delivery to agents, audit schema compliance, run npm run skill:validate, or confirm that
  generated files reach their target agents.
  Triggers: 'validate skills', 'skill delivery', 'qa check', 'plugin:validate',
  'verify agents', 'confirm delivery', 'audit schema', 'check skill integrity'.
---

# AC QA Validation Skill

Validate that agent skills, plugins, and generated workflow files are correctly structured,
schema-compliant, and properly delivered to their target agents.

## When to Use This Skill

- Running `npm run skill:validate` or `npm run plugin:validate`
- Verifying that SKILL.md files are correctly linked to `.agent.md` files
- Auditing frontmatter completeness (name, description, tools fields)
- Confirming workflow `.md` files compile cleanly with `gh aw compile`
- Checking that all generated files are in correct locations

## Prerequisites

- `npm ci` run in `awesome-copilot/` directory
- `gh aw` CLI available

## Step-by-Step Workflows

### Full validation suite

```bash
cd /workspaces/mcapp-ai-starter/awesome-copilot
npm run skill:validate
npm run plugin:validate
```

### Validate workflow compilation

```bash
cd /workspaces/mcapp-ai-starter
gh aw compile 2>&1
```

### Check agent-skill delivery

```bash
# Run the delivery validator
bash /workspaces/mcapp-ai-starter/scripts/validate-delivery.sh
```

### Manual audit checklist

- [ ] Each `.agent.md` has `name`, `description` frontmatter
- [ ] Each `SKILL.md` has `name` (≤64 chars) and `description` frontmatter
- [ ] Skills in `.github/skills/<name>/SKILL.md` for all ac-* agents
- [ ] Workflow `.md` files in `.github/workflows/` compile without errors
- [ ] No `.lock.yml` committed to git
- [ ] `npm run skill:validate` passes

## Delivery Validation Matrix

| Agent | Skill Location | Status Check |
|-------|---------------|--------------|
| `ac-feature-dev` | `.github/skills/ac-feature-dev/SKILL.md` | `test -f` check |
| `ac-github-workflows` | `.github/skills/ac-github-workflows/SKILL.md` | `test -f` check |
| `ac-qa-validation` | `.github/skills/ac-qa-validation/SKILL.md` | `test -f` check |
| `ac-ci-cd` | `.github/skills/ac-ci-cd/SKILL.md` | `test -f` check |
| `ac-debug` | `.github/skills/ac-debug/SKILL.md` | `test -f` check |
| `ac-devops` | `.github/skills/ac-devops/SKILL.md` | `test -f` check |
| `ac-documentation` | `.github/skills/ac-documentation/SKILL.md` | `test -f` check |
| `ac-maintenance` | `.github/skills/ac-maintenance/SKILL.md` | `test -f` check |

## Common Validation Failures

| Failure | Root Cause | Fix |
|---------|-----------|-----|
| `name` > 64 chars | Skill name too long | Shorten to ≤64 chars |
| Missing `description` | Frontmatter incomplete | Add clear description |
| `skill:validate` parse error | Invalid YAML frontmatter | Fix YAML syntax |
| Workflow compile error | Invalid frontmatter or safe-outputs | Check gh aw format |
| Skill not discovered | Vague description | Add "Use when asked to..." triggers |
