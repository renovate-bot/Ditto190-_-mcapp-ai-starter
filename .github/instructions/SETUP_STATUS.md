# Multi-Agent AI Setup — Complete Status & Next Steps

**Date**: April 3, 2026  
**Repository**: Ditto190/mcapp-ai-starter  
**Current Branch**: main  
**Latest Commits**:

- `be15e3e` feat(agents): add multi-agent orchestrator and workflow documentation
- `8b8eba9` chore(setup): add multi-agent orchestration foundational setup

---

## ✅ Complete — Foundation Layer

### 1. Agent Folder Structure

- ✅ `.github/agents/` directory created
- ✅ `migration-analyst.agent.md` — analyzes `migration/` folder for reusable code
- ✅ `multi-agent-orchestrator.agent.md` — coordinates parallel worktree agents, PRs, reviews, merges

### 2. Instructions Files

- ✅ `.github/copilot-instructions.md` — compact 2-page guide (469 lines)
  - Mandatory ContextStream startup protocol
  - Build/test commands per component
  - CI/CD pipeline overview
  - Agent folder layout + naming conventions
  - Migration folder rules (gated integration pattern)
  - Git worktree conventions
- ✅ `.github/instructions/initial-setup.instructions.md` — foundation setup (Phases 1–5)
  - Clone, .env, dependency installation
  - Docker stack startup
  - Worktree architecture & creation
  - Multi-agent orchestration workflow
  - ContextStream memory per worktree
  - Troubleshooting (locked worktrees, conflicts, sync issues)
- ✅ `.github/instructions/multi-agent-workflow.instructions.md` — complete workflow reference
  - Priority 1: git worktrees, automatic commits, parallel agents
  - Practical example: 2 agents in parallel
  - Automatic commit flow (edit → test → commit → push → PR → merge → sync)
  - Troubleshooting (unlocking, conflicts, GitLab mirroring delays)

### 3. Security & CI/CD

- ✅ `.github/workflows/codeql.yml` — CodeQL security scanning
  - JavaScript/TypeScript + Python analysis
  - Runs on push, PR, weekly schedule
  - Least-privilege permissions (security-events: write only at job level)

### 4. GitLab Integration

- ✅ `.gitlab-ci.yml` already configured (no changes needed)
  - Mirror integration ready (GitHub → GitLab webhook)
  - Pipeline stages: validate → test → audit → build

---

## 🚀 Immediate Next Steps (Priority 1)

### Step 1: Run Foundation Setup (Phase 1)

**Time**: ~10–15 min

```bash
cd /workspaces/mcapp-ai-starter

# 1. Clone + env
cp .env.example .env
# Edit .env with secrets (N8N_ENCRYPTION_KEY, LLM API keys, ContextStream key)

# 2. Install dependencies
npm install && \
  cd GenerateAgents.md && uv sync --extra dev && cd .. && \
  cd generateagents-mcp && uv sync && cd .. && \
  cd prompt-registry && npm ci && cd .. && \
  cd awesome-copilot && npm ci && cd ..

# 3. Start Docker stack
docker compose config -q && docker compose up -d && sleep 30

# 4. Verify (optional)
docker compose ps
```

### Step 2: Create First Agent Worktree

**Time**: ~5 min

```bash
# Example: agent "sandbox" for testing the multi-agent flow

git worktree add ../mcapp-agent-sandbox -b feature/agent-sandbox
cd ../mcapp-agent-sandbox

# This is now isolated; any changes here don't affect main
```

### Step 3: Test the Workflow Loop

**Time**: ~5 min

```bash
# Inside worktree: ../mcapp-agent-sandbox

# Make a test change
echo "// test" >> README.md

# Stage, test, commit
git add .
git commit -m "docs(test): verify multi-agent commit workflow"
git push --set-upstream origin feature/agent-sandbox

# Now the multi-agent-orchestrator will detect this commit and create a PR
# (when enabled via scheduled workflow)
```

### Step 4: Enable Scheduled Orchestrator (Optional, but recommended)

**Time**: ~5 min

Create `.github/workflows/multi-agent-orchestrator.yml`:

```yaml
name: Multi-Agent Orchestrator
on:
  schedule:
    - cron: "*/15 * * * *" # Run every 15 minutes
  workflow_dispatch:

permissions:
  contents: write
pull-requests: write

jobs:
  orchestrate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - run: |
          git config user.name "Agent Orchestrator"
          git config user.email "orchestrator@agents.local"
      - run: npm install -g gh
      - run: bash .github/scripts/orchestrator.sh
```

(Script: `.github/scripts/orchestrator.sh` — to be created in Step 5)

---

## 📋 Phase 2: Multi-Agent Orchestration Scripts

### Step 5: Create Orchestrator Script

**Time**: ~20 min

Create `.github/scripts/orchestrator.sh`:

```bash
#!/bin/bash
set -e

# Orchestrator: detect commits, create PRs, merge on approval, sync worktrees

# 1. Fetch all branches from origin
git fetch origin

# 2. Identify all agent worktrees and their branches
WORKTREES=$(git worktree list --porcelain | grep -v "detached" | awk '{print $1}')

for wt in $WORKTREES; do
  BRANCH=$(git -C "$wt" rev-parse --abbrev-ref HEAD)
  MAIN_COMMIT=$(git log -1 --format=%H origin/main)
  WS_COMMIT=$(git -C "$wt" log -1 --format=%H)

  if [ "$MAIN_COMMIT" != "$WS_COMMIT" ]; then
    echo "Worktree $wt (branch $BRANCH) has new commits"

    # Create PR if none exists
    if ! gh pr list --head "$BRANCH" --base main | grep -q "$BRANCH"; then
      echo "Creating PR for $BRANCH"
      gh pr create \
        --base main \
        --head "$BRANCH" \
        --draft \
        --title "feat(agent): $BRANCH changes" \
        --body "Auto-generated PR from agent worktree\n\nChanges: $(git -C "$wt" log main..HEAD --oneline)"
    fi
  fi
done

# 3. Merge approved PRs
for pr in $(gh pr list --base main --label "approved" --json number -q '.[].number'); do
  echo "Merging PR #$pr"
  gh pr merge "$pr" --squash --delete-branch
done

# 4. Sync all worktrees to latest main
for wt in $WORKTREES; do
  echo "Syncing $wt to origin/main"
  cd "$wt"
  git fetch origin main
  git rebase origin/main || echo "Rebase failed for $wt; manual merge needed"
  cd -
done

echo "Orchestrator complete"
```

### Step 6: Create Git Hook for Auto-Commit (Optional)

**Time**: ~10 min

Create `.github/hooks/post-commit`:

```bash
#!/bin/bash

# Auto-push after commit (optional, disable if agent handles manually)
# Uncomment to enable:

# git push origin HEAD:$(git rev-parse --abbrev-ref HEAD)
# echo "Auto-pushed to origin"
```

Install:

```bash
chmod +x .github/hooks/post-commit
git config --global core.hooksPath "$(pwd)/.github/hooks"
```

---

## 📊 Manual Testing Checklist

- [ ] Run Phase 1 foundation setup
- [ ] Create sandbox worktree: `git worktree add ../mcapp-agent-sandbox -b feature/sandbox`
- [ ] Make test changes, commit, push
- [ ] Verify PR is created (manually or via orchestrator)
- [ ] Request review, approve, merge
- [ ] Verify all worktrees sync to main
- [ ] Delete worktree: `git worktree remove ../mcapp-agent-sandbox`

---

## 🎯 Priority 2: Per-Agent Instructions (After Multi-Agent Base is Running)

For each agent (e.g., `agent-foo`), create:

**`.github/instructions/agent-foo.instructions.md`**

```markdown
---
description: Agent Foo's workflow for specific task
applyTo: "**"
---

# Agent Foo — Task Description

## Your Setup

- Worktree: `/workspaces/mcapp-agent-foo`
- Branch: `feature/agent-foo`
- Session ID: `agent-foo-session-2026-04-03`
- ContextStream workspace: `mcpapp-monorepo` (e76de4e7-5d4b-40c0-9023-10172088310c)

## Assigned Task

[Summary of what Agent Foo is building]

## Success Criteria

- [ ] Tests pass: `npm test` OR `uv run pytest -m 'not e2e' -q`
- [ ] Lint passes: `npm run lint`
- [ ] All component CI passes (in .github/workflows/repo-ci.yml)
- [ ] Code review approved
- [ ] Security review approved (CodeQL + artifact scan)
- [ ] PR merged to main
- [ ] Branch deleted

## How to Commit

1. Edit files in your worktree
2. Run tests: `npm test && npm run lint`
3. Stage all: `git add .`
4. Commit: `git commit -m "feat(component): description"`
5. Push: `git push origin feature/agent-foo`
6. Wait for Multi-Agent Orchestrator to create PR + request reviews

## If Blocked

- Conflicts during merge? Request manual merge help from @code-reviewer
- Tests failing? Check `.github/workflows/repo-ci.yml` for reproduction steps
- ContextStream unreachable? Try: `contextstream-mcp setup --force`
```

---

## 🔗 Documentation Links

- [Initial Setup — Full Phases 1–5](.github/instructions/initial-setup.instructions.md)
- [Multi-Agent Workflow Reference](.github/instructions/multi-agent-workflow.instructions.md)
- [Copilot Compact Instructions](.github/copilot-instructions.md)
- [Developer Quickstart](DEVELOPER-QUICKSTART.md)
- [GitLab Setup Guide](GITLAB_SETUP.md)
- [n8n Component Notes](n8n/AGENTS.md)

---

## 🛠️ Troubleshooting Quick Reference

| Problem                  | Command                                                                     |
| ------------------------ | --------------------------------------------------------------------------- |
| Worktree locked          | `git worktree unlock ../mcapp-agent-<name>`                                 |
| Branch exists already    | `git fetch origin && git worktree add ../mcapp-agent-<name> feature/<name>` |
| Tests failing            | `cd ../../ && npm test:e2e` (from worktree parent)                          |
| ContextStream not init   | `contextstream-mcp init --folder-path=$(pwd)`                               |
| GitLab mirroring delayed | Check GitLab webhook status in project settings                             |
| Can't push               | `git push --force-with-lease origin feature/<name>` (use with caution)      |

---

## 📝 Git Commit History (Setup)

```
be15e3e fut(agents): add multi-agent orchestrator and workflow documentation
8b8eba9 chore(setup): add multi-agent orchestration foundational setup
```

---

**Status**: Foundation layer **complete**. Ready for multi-agent agent assignment and Phase 2 testing.  
**Next**: Run Phase 1 setup, create first sandbox worktree, test commit → PR → merge loop.  
**Estimated Time to Full Setup**: 30–45 min (including Docker startup and dependency install).
