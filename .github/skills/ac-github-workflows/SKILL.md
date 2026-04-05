---
name: ac-github-workflows
description: >
  Author, compile, and manage GitHub Agentic Workflows (.md → .lock.yml via gh aw compile).
  Use when asked to create a workflow, compile workflows, write agentic workflow files,
  use gh aw, build automation pipelines, write workflow .md files, or run gh aw compile.
  Triggers: 'agentic workflow', 'gh aw compile', 'workflow .md', 'create workflow',
  'automate with gh aw', 'build pipeline', 'workflow automation'.
---

# AC GitHub Workflows Skill

Author and compile GitHub Agentic Workflows. Converts `.github/workflows/*.md` files into
runnable GitHub Actions via `gh aw compile`.

## When to Use This Skill

- Writing a new agentic workflow `.md` file
- Running `gh aw compile` to generate `.lock.yml`
- Designing workflow triggers (schedule, slash_command, workflow_dispatch)
- Setting `safe-outputs` and `permissions` for a workflow
- Validating workflow configuration

## Prerequisites

- `gh extension install github/gh-aw` (v0.66.1+ installed in this repo)
- Workflows live in `.github/workflows/*.md`
- NEVER commit `.lock.yml` — only `.md` source files

## Agentic Workflow .md Format

```yaml
---
name: "My Workflow Name"
description: "What this workflow does"
on:
  schedule: daily on weekdays          # OR:
  # slash_command:
  #   name: my-command
  #   roles: [admin, maintainer, write]
  # workflow_dispatch: {}
permissions:
  contents: read
  issues: read                         # add as needed
safe-outputs:
  create-issue:                        # allowed output actions
    title-prefix: "[tag] "
    labels: [label1]
  # add-comment:
  #   max: 1
---

## Natural Language Workflow Body

Clear step-by-step instructions for the AI agent...
```

## Step-by-Step Workflows

### Create a new agentic workflow

1. Create `.github/workflows/<name>.md` with frontmatter + body
2. Compile: `gh aw compile <name>`
3. Verify `.lock.yml` generated (do NOT commit it)
4. Test: `gh aw run <name> --dry-run`

### Compile all workflows

```bash
cd /workspaces/mcapp-ai-starter
gh aw compile
```

### Compile a specific workflow

```bash
gh aw compile ac-skill-generator
```

## Permissions Reference

| Action | Permission Required |
|--------|-------------------|
| Read issues | `issues: read` |
| Create issues | `issues: write` |
| Comment on issues/PRs | `pull-requests: write` |
| Read/write files | `contents: write` |
| Read repo | `contents: read` |

## Safe Outputs Reference

| Output Type | Fields |
|-------------|--------|
| `create-issue` | `title-prefix`, `labels`, `assignees` |
| `add-comment` | `max` (integer) |
| `update-issue` | `state` |
| `create-pr` | `title-prefix`, `labels` |

## Security Rules

- Always use minimal permissions (contents: read by default)
- Elevate permissions per-job only when required
- Do NOT use `--force` or destructive operations without user confirmation
- DO NOT commit `.lock.yml` files — source-of-truth is `.md`
