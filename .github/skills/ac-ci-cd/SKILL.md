---
name: ac-ci-cd
description: >
  Build and maintain CI/CD GitHub Actions pipelines (.yml). Use when asked to create a
  CI workflow, update GitHub Actions, configure pipeline stages, add lint/test/build/deploy
  steps, set up matrix builds, configure secrets for workflows, or manage .github/workflows/*.yml
  files. Triggers: 'ci pipeline', 'github actions', 'create workflow yml', 'add build step',
  'configure secrets', 'matrix build', 'deploy pipeline', 'ci/cd'.
---

# AC CI/CD Skill

Build and maintain CI/CD pipelines as GitHub Actions YAML (`.github/workflows/*.yml`).
Distinct from agentic workflows (`.md` + `gh aw compile`) — this skill is for standard
GitHub Actions yaml pipelines.

## When to Use This Skill

- Creating a new `.github/workflows/*.yml` pipeline
- Adding lint, test, build, or deploy steps
- Configuring matrix builds or environment secrets
- Setting up dependency caching
- Configuring workflow permissions

## Prerequisites

- GitHub Actions knowledge
- `.env` / secrets configured in repo settings

## Step-by-Step Workflows

### New CI workflow skeleton

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm test
```

### Add a Python test step

```yaml
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install uv && uv sync --extra dev
      - run: uv run pytest -m 'not e2e' -q
```

## Permissions Convention

- Default: `permissions: contents: read` at workflow scope
- Elevate per-job only when required
- Never grant `contents: write` globally

## Caching Pattern

```yaml
      - uses: actions/cache@v4
        with:
          path: ~/.npm
          key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
          restore-keys: ${{ runner.os }}-node-
```
