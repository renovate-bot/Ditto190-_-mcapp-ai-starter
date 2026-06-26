---
name: "AC Delivery Validator"
description: "Validates that all agent skills and workflow files are correctly delivered to their target agents. Reports a full delivery matrix and fails if any required skill is missing from .github/skills/."
on:
  workflow_dispatch: {}
permissions:
  contents: read
safe-outputs:
  create-issue:
    title-prefix: "[ac-delivery] "
    labels: [validation, agent-skills]
---

## AC Delivery Validator

You are the AC Delivery Validator. Validate that all generated agent skills and workflow files reached their target agents correctly.

## Validation Checklist

### 1. Skills Delivery Check

For each of the following, confirm the file exists and has valid frontmatter:

| Skill | Expected Location |
|-------|------------------|
| ac-feature-dev | `.github/skills/ac-feature-dev/SKILL.md` |
| ac-github-workflows | `.github/skills/ac-github-workflows/SKILL.md` |
| ac-qa-validation | `.github/skills/ac-qa-validation/SKILL.md` |
| ac-ci-cd | `.github/skills/ac-ci-cd/SKILL.md` |
| ac-debug | `.github/skills/ac-debug/SKILL.md` |
| ac-devops | `.github/skills/ac-devops/SKILL.md` |
| ac-documentation | `.github/skills/ac-documentation/SKILL.md` |
| ac-maintenance | `.github/skills/ac-maintenance/SKILL.md` |
| ac-meta-orchestration | `.github/skills/ac-meta-orchestration/SKILL.md` |

### 2. Agent Files Check

Confirm all 9 agent files exist in `awesome-copilot/agents/`:

- `awesome-copilot-meta-architect.agent.md`
- `ac-feature-dev.agent.md`
- `ac-maintenance.agent.md`
- `ac-devops.agent.md`
- `ac-ci-cd.agent.md`
- `ac-debug.agent.md`
- `ac-github-workflows.agent.md`
- `ac-documentation.agent.md`
- `ac-qa.agent.md`

### 3. Workflow Files Check

Confirm workflow `.md` files exist in `.github/workflows/`:

- `ac-skill-generator.md`
- `ac-workflow-compiler.md`
- `ac-delivery-validator.md`

### 4. Schema Validation

Run: `bash scripts/validate-delivery.sh`

### 5. Output Report

Create a GitHub issue summarizing:

- PASS/FAIL status for each check
- Count of skills present vs missing
- Count of agent files present vs missing
- Any schema errors found
- Recommended fixes for any failures

## Pass Criteria

All 9 skills must be present, all 9 agent files must exist, and all workflow `.md` files
must be compilable with `gh aw compile`.
