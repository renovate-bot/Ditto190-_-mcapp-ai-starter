---
description: Quick reference card for AI agents starting work on mcapp-ai-starter
applyTo: '**'
---

# AI Agent Quick Reference Card

**Repository**: Ditto190/mcapp-ai-starter  
**Workspace ID**: e76de4e7-5d4b-40c0-9023-10172088310c  

## Before You Start (5 min)

```bash
# 1. Clone + setup foundations (if not done)
cd /workspaces/mcapp-ai-starter

# 2. Verify Docker stack is running
docker compose ps | grep -E "healthy|Up"

# 3. ContextStream init (CRITICAL)
contextstream-mcp init --folder-path=$(pwd)
export SESSION_ID="agent-<yourname>-session-$(date +%Y-%m-%d)"

# 4. Your worktree
git worktree list | grep feature/
```

## Your First Commands

### Read the Rules

- **Workspace**: [.github/copilot-instructions.md](.github/copilot-instructions.md)
- **Setup**: [.github/instructions/initial-setup.instructions.md](.github/instructions/initial-setup.instructions.md)
- **Workflow**: [.github/instructions/multi-agent-workflow.instructions.md](.github/instructions/multi-agent-workflow.instructions.md)

### Understand Your Environment

```bash
# Python projects: 3.12+
cd GenerateAgents.md && uv sync && cd ..

# Node projects: 20+
npm install && npm test

# Docker available
docker compose ps

# Git remotes configured
git remote -v
```

### Build, Test, Deploy (Per Component)

| Component | Build | Test | Deploy |
|-----------|-------|------|--------|
| Root SDK | `npm run build` | `npm test` | `npm run build:all` |
| GenerateAgents | `cd GenerateAgents.md && uv sync` | `uv run pytest -q` | N/A |
| generateagents-mcp | `cd generateagents-mcp && uv sync` | `uv run python verify.py` | `uv run server.py` |
| prompt-registry | `cd prompt-registry && npm ci` | `npm run test:unit` | `npm run compile` |
| awesome-copilot | `cd awesome-copilot && npm ci` | `npm run skill:validate` | `npm run build` |

## Your Workflow

### 1. **Get Work Assignment**

```bash
# Your task is described here (agent-specific .instructions.md)
cat .github/instructions/agent-<yourname>.instructions.md
```

### 2. **Create Your Worktree** (if new)

```bash
git worktree add ../mcapp-agent-<yourname> -b feature/agent-<yourname>
cd ../mcapp-agent-<yourname>

# Initialize ContextStream memory
contextstream-mcp init --folder-path=$(pwd)
SESSION_ID="agent-<yourname>-session-2026-04-03"
```

### 3. **Make Changes**

```bash
# Edit files, run tests
npm test && npm run lint

# If components break:
cd ../../ && npm install  # Reload root SDK
rm -rf node_modules package-lock.json && npm install  # Full reset
```

### 4. **Commit & Push**

```bash
git add .
git commit -m "feat(component): your description here"
git push origin feature/agent-<yourname>

# Multi-Agent Orchestrator detects changes → creates PR automatically
```

### 5. **Wait for Review & Merge**

- PR will be created by orchestrator
- Reviews requested automatically
- On approval → auto-merged to main
- Your worktree auto-synced to latest main

## Key Rules

⚠️ **DO NOT**:

- Commit directly to `main`
- Use `git push -f` without `--force-with-lease`
- Test in Docker without running `docker compose up -d` first
- Ignore failing tests (they **must** pass before commit)

✅ **DO**:

- Run tests locally: `npm test || uv run pytest -q`
- Commit early, often, with clear messages
- Use [Conventional Commits](https://www.conventionalcommits.org/):
  - `feat(component): add feature`
  - `fix(component): fix bug`
  - `test(component): add test coverage`
  - `docs(component): update docs`
  - `chore(component): maintenance`
- Push to your worktree's feature branch (never main)
- Save progress in ContextStream: `session.capture(...)`

## Git Worktree Commands

```bash
# List all worktrees
git worktree list

# Switch to your worktree
cd ../mcapp-agent-<yourname>

# Create worktree (if needed)
git worktree add ../mcapp-agent-<yourname> -b feature/agent-<yourname>

# Delete worktree (after PR merged)
git worktree remove ../mcapp-agent-<yourname>

# Trapped in detached state?
git switch feature/agent-<yourname>
```

## ContextStream Memory (Persist Progress)

```python
# At start
await contextstream.session.capture({
  "event_type": "operation",
  "title": f"Starting work on feature X",
  "content": {"task": "...", "status": "in_progress"}
})

# On completion
await contextstream.session.capture({
  "event_type": "session_snapshot",
  "title": f"Completed feature X",
  "content": {
    "summary": "What was done",
    "files_changed": ["src/...", "tests/..."],
    "next_steps": ["Waiting for review", "Merge pending"],
    "blockers": []
  }
})
```

## Troubleshooting

**Q: Tests are failing**

```bash
npm run lint  # Check syntax
npm test      # Run unit tests
npm test:e2e  # Run end-to-end tests (slow; Playwright)
```

**Q: Docker service not running**

```bash
docker compose up -d
docker compose ps
```

**Q: Git branch is behind main**

```bash
git fetch origin main
git rebase origin/main
```

**Q: PR was not auto-created**

```bash
# Manually create it:
gh pr create --base main --head feature/agent-<yourname> --draft

# Or check orchestrator logs:
git log --oneline | grep "orchestrator\|Merge\|Merge pull"
```

**Q: ContextStream not working**

```bash
# Reinit
contextstream-mcp setup --force

# Check connection
curl https://api.contextstream.io/health
```

## One-Liner Reference

```bash
# Setup (one time)
cp .env.example .env && npm install && cd GenerateAgents.md && uv sync && cd .. && docker compose up -d

# Create worktree
git worktree add ../mcapp-agent-myname -b feature/agent-myname && cd ../mcapp-agent-myname

# Test & commit
npm test && git add . && git commit -m "feat(component): description" && git push origin feature/agent-myname

# Merge when PR approved (manual or orchestrator auto)
gh pr merge <pr-number> --squash --delete-branch

# Cleanup
git worktree remove ../mcapp-agent-myname
```

## Critical Links

- 📖 **Setup Guide**: [Initial Setup](.github/instructions/initial-setup.instructions.md)
- 🔄 **Workflow Reference**: [Workflow Docs](.github/instructions/multi-agent-workflow.instructions.md)
- 📋 **Status & Next Steps**: [Setup Status](.github/instructions/SETUP_STATUS.md)
- 🎯 **Copilot Instructions**: [Instructions](.github/copilot-instructions.md)
- 🚀 **Quick Start**: [QUICKSTART.md](QUICKSTART.md)

---

**You're ready to go!** 🚀 Start by reading your task, creating your worktree, and committing code. The multi-agent orchestrator will handle PR creation and review coordination.

**Questions?** → Check the [Copilot Instructions](.github/copilot-instructions.md) or ask in your agent's instructions file.
