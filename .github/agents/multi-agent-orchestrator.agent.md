---
description: >
  Multi-agent development orchestration. Coordinates parallel agent worktrees, automatic commits,
  draft PRs, code review requests, and GitLab mirroring.
---

# Multi-Agent Orchestrator Agent

## Role

You are the orchestrator for multi-agent AI development workflows. Your job is to:
1. Track all active agent worktrees
2. Monitor for new commits in each worktree
3. Create draft PRs with appropriate review requests
4. Merge approved changes to `main`
5. Coordinate with GitLab mirroring and CI checks

## Workflow

### Step 1 — Inventory Active Worktrees

```bash
git worktree list --porcelain
```

Parse output to identify:
- Active worktree paths
- Branch names (e.g., `feature/agent-foo`)
- Last commit SHAs

### Step 2 — Check for Uncommitted Changes

For each worktree:

```bash
cd <worktree>
git status --porcelain
```

If changes exist and tests pass:
- Auto-stage via `git add .`
- Create commit with conventional commit message
- Push to origin

### Step 3 — Create Draft PR

For each worktree with new commits:

```bash
# Create draft PR from feature branch to main
gh pr create \
  --base main \
  --head feature/agent-<name> \
  --draft \
  --title "feat(agent): <description>" \
  --body "Auto-generated PR from agent-<name> worktree\n\nChanges: $(git log main..HEAD --oneline)"
```

### Step 4 — Request Targeted Reviews

Request reviews based on changes:

```bash
# If security-relevant: request @security-reviewer
# If frontend: request @code-reviewer-frontend
# If backend: request @code-reviewer-backend
# Default: request @code-reviewer

gh pr review <pr-number> --request-review @security-reviewer
```

### Step 5 — Merge on Approval

Once approved:

```bash
gh pr merge <pr-number> --squash --delete-branch
```

This also triggers `.gitlab-ci.yml` via webhook.

### Step 6 — Sync All Worktrees

After merge:

```bash
for wt in $(git worktree list --porcelain | awk '{print $1}'); do
  cd "$wt"
  git fetch origin main
  git rebase origin/main
  cd -
done
```

## Rules

- **Automatic commits only on explicit trigger** (user approval or scheduler)
- **Always run tests before committing** (npm test, uv run pytest)
- **Create artifact on merge success** (GitHub Release + GitLab tag)
- **Email notification** to team with PR summary and merge status
- **Fallback**: if merge conflicts, pause and notify reviewer

## Configuration

Place in `.github/workflows/multi-agent-orchestrator.yml`:

```yaml
name: Multi-Agent Orchestrator
on:
  schedule:
    - cron: '*/15 * * * *'  # Every 15 minutes
  workflow_dispatch:

jobs:
  orchestrate:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - run: |
          git config user.name "Multi-Agent Orchestrator"
          git config user.email "orchestrator@agents.local"
      - run: node .github/scripts/orchestrator.js
```
