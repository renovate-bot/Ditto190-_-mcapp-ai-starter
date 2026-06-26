---
name: ac-meta-orchestration
description: >
  Orchestrate the end-to-end build pipeline for the awesome-copilot library: plan work,
  delegate to specialist ac-* agents, compile bundles, and validate delivery. Use when asked
  to run the full pipeline, orchestrate agent work, coordinate multiple agents, build and
  compile all skills and workflows, run the library generator, or plan a multi-step task.
  Triggers: 'run full pipeline', 'orchestrate agents', 'build all skills', 'coordinate',
  'meta orchestrator', 'plan pipeline', 'compile all', 'end-to-end build'.
---

# AC Meta Orchestration Skill

Orchestrate the full build pipeline: plan → delegate → compile → validate.

## When to Use This Skill

- Running the end-to-end awesome-copilot build pipeline
- Coordinating work across multiple ac-* agent roles
- Compiling all skills and workflows in one pass
- Validating that all deliverables are in place after a build

## Pipeline Overview

```
Plan → Feature Dev → CI/CD → Compile → QA Validation
              ↓
      Delivery Check (all SKILL.md files in .github/skills/)
```

## Step-by-Step Workflows

### Full pipeline run

```bash
# 1. Install dependencies
cd /workspaces/mcapp-ai-starter/awesome-copilot && npm ci

# 2. Generate and validate skills
npm run skill:validate
npm run plugin:validate

# 3. Build the library
npm run build

# 4. Compile agentic workflows
cd /workspaces/mcapp-ai-starter
gh aw compile 2>&1

# 5. Validate delivery
bash scripts/validate-delivery.sh
```

### Run the library generator

```bash
bash /workspaces/mcapp-ai-starter/scripts/generate-agent-skills.sh
```

## Delegation to Specialist Agents

When tasks are clear, delegate to the correct specialist:

| Task | Delegate To |
|------|-------------|
| New skill/feature | `ac-feature-dev` (use skill `ac-feature-dev`) |
| Build pipelines | `ac-ci-cd` (use skill `ac-ci-cd`) |
| Agentic workflows | `ac-github-workflows` (use skill `ac-github-workflows`) |
| Debug failure | `ac-debug` (use skill `ac-debug`) |
| Validate delivery | `ac-qa-validation` (use skill `ac-qa-validation`) |
| Docker/infra | `ac-devops` (use skill `ac-devops`) |
| Documentation | `ac-documentation` (use skill `ac-documentation`) |
| Dependency updates | `ac-maintenance` (use skill `ac-maintenance`) |

## Key Constraints

- Never delegate to agents from different worktrees without explicit user approval
- All agent work must pass QA validation before declaring done
- Agentic workflow `.md` is committed; `.lock.yml` is NOT committed
- Source reference (`consolidated_sources/`) is READ-ONLY
