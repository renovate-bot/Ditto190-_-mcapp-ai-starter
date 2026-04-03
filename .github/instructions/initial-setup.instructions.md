---
description: Initial setup for multi-agent AI development with git worktrees, automatic commits, and coordinated reviews.
applyTo: '**'
---

# Initial Setup — Multi-Agent Orchestration & Git Worktrees

This file documents the foundation-level setup for enabling multiple AI agents to work in parallel on this repository through isolated git worktrees, automatic commit tracking, and coordinated code review workflows.

## Status: This Setup Enables

✅ **Agent Isolation**: Each agent gets its own worktree (branch + working directory)  
✅ **Automatic Commit Tracking**: Changes auto-staged, committed on-demand  
✅ **Coordinated Reviews**: Automatic draft PRs with agent-specific review requests  
✅ **GitLab Mirroring**: All changes propagated to `.gitlab-ci.yml` pipeline  
✅ **ContextStream Memory**: Multi-agent progress persisted across sessions  

---

## Phase 1: Foundation (One-Time)

Run these once after cloning the repo.

### 1.1 Clone & Configure

```bash
# Clone the repo
git clone https://github.com/Ditto190/mcapp-ai-starter.git
cd mcapp-ai-starter

# Configure git user for agent commits
git config user.name "Agent <name>"
git config user.email "agent+<name>@example.local"

# Verify
git config --local --list | grep user
```

### 1.2 Set up .env and dependencies

```bash
# Copy env template
cp .env.example .env

# Edit .env with your secrets (never commit)
# - N8N_ENCRYPTION_KEY: openssl rand -base64 32
# - N8N_USER_MANAGEMENT_JWT_SECRET: openssl rand -base64 32
# - CONTEXTSTREAM_API_KEY: from https://contextstream.io/settings
# - LLM provider keys (GEMINI_API_KEY, OPENAI_API_KEY, etc.)

# Verify .env is gitignored
grep "^\.env$" .gitignore
```

### 1.3 Install dependencies (all components)

```bash
# Root SDK + examples (Node)
npm install

# GenerateAgents.md (Python)
cd GenerateAgents.md && uv sync --extra dev && cd ..

# generateagents-mcp (Python)
cd generateagents-mcp && uv sync && cd ..

# prompt-registry (TypeScript)
cd prompt-registry && npm ci && cd ..

# awesome-copilot (Node)
cd awesome-copilot && npm ci && cd ..

# Return to root
cd /workspaces/mcapp-ai-starter
```

### 1.4 Start the Docker stack

```bash
# Verify compose config
docker compose config -q

# Start services (CPU mode)
docker compose up -d

# Or with NVIDIA GPU (if available)
docker compose --profile gpu-nvidia up -d

# Wait for services (30–60 seconds)
sleep 30 && docker compose ps
```

### 1.5 Verify all checks pass (optional but recommended)

```bash
# Run component CI pipeline
docker compose config -q && \
cd GenerateAgents.md && uv run pytest -m 'not e2e' -q && cd .. && \
cd generateagents-mcp && uv run python verify.py && cd .. && \
cd prompt-registry && npm run compile && npm run lint && cd .. && \
cd awesome-copilot && npm run build && cd .. && \
npm test:e2e 2>/dev/null || echo "(E2E tests require Playwright; skip if first run)"
```

---

## Phase 2: Multi-Agent Orchestration Setup

### 2.1 Understand the Worktree Architecture

Each AI agent runs in an **isolated worktree**:

```
main/                        # Main worktree (always clean)
├── .git/
├── src/
└── docs/

feature/agent-foo/           # Agent Foo's worktree
├── src/  (detached, in-progress changes)
├── docs/
├── .git -> ../../.git/link

feature/agent-bar/           # Agent Bar's worktree
├── src/
├── docs/
└── .git -> ../../.git/link
```

**Key properties:**
- Worktrees share a single git object database (`.git/` is a link)
- Each worktree has its own branch (e.g., `feature/agent-foo`)
- Changes in one worktree don't affect another
- Commits are independent per branch
- Merging is fast (no rebasing needed before merge)

### 2.2 Create Agent Worktrees

For each agent (e.g., `agent-foo`, `agent-bar`):

```bash
# Create worktree + branch
git worktree add ../mcapp-agent-foo -b feature/agent-foo

# Verify
git worktree list

# Output:
# /workspaces/mcapp-ai-starter                    0000000 [main]
# /workspaces/mcapp-agent-foo                     0000000 [feature/agent-foo]
```

**Agent naming convention**: lowercase-hyphen (`agent-name`). Maps to:
- Worktree: `../mcapp-agent-name`
- Branch: `feature/agent-name`
- Agent file: `.github/agents/agent-name.agent.md`

### 2.3 ContextStream Memory per Worktree

Each worktree gets its own ContextStream session for persistent memory:

```bash
# In worktree: /workspaces/mcapp-agent-foo
cd ../mcapp-agent-foo

# Initialize ContextStream (same workspace)
npx @contextstream/mcp-server@latest setup

# In agent code, use session_id tied to agent:
# session_id: "agent-foo-session-2026-04-03" (unique per agent + date)
```

---

## Phase 3: Automatic Commit & Review Workflow

### 3.1 Agent Workflow (Per Worktree)

```bash
# cd into worktree
cd ../mcapp-agent-foo

# Make changes, run tests
# ...your code edits...

# Commit (agent auto-generates commit message via git hooks or manual)
git add .
git commit -m "feat(component): description per Conventional Commits"

# OR use gitlens commit composer (if available)
# gitlens commit-composer (opens UI for interactive commit crafting)
```

### 3.2 Coordinator Agent — Merge & Push

The **multi-agent-orchestrator** agent (when created) will:

1. Poll all agent worktrees for new commits
2. For each commit, create a **draft PR** to `main`
3. Request review from:
   - Code review agent (`@code-reviewer`)
   - Security agent (`@security-reviewer` — CodeQL)
4. On approval, merge to `main` (or request another review round)
5. Push to both GitHub and GitLab

**Manual trigger** (for testing):

```bash
# From main worktree
git pull origin main  # Sync latest

# Create featureish PR (example)
git checkout -b pr/agent-foo-merge
git merge feature/agent-foo
git push --set-upstream origin pr/agent-foo-merge

# Create PR via GitHub CLI (if installed)
# gh pr create --base main --head pr/agent-foo-merge --draft
```

### 3.3 GitLab Mirroring

The `.gitlab-ci.yml` pipeline is configured to:
- Mirror commits from GitHub → GitLab (via webhook)
- Run same checks (lint, test, security scan)
- Report back to GitHub PR via GitLab status checks

**Setup** (once per GitLab project):

```bash
# In GitLab project → Settings → Integrations → Add GitHub
# - Webhook URL: https://gitlab.example.com/api/v4/projects/:id/repository/sync
# - Events: Push, Pull Request

# Or set mirror branch in GitLab:
# Settings → Repository → Mirroring Repositories → Add mirror
# - URL: https://github.com/Ditto190/mcapp-ai-starter.git
# - Direction: Pull
# - Auth: Personal access token
```

---

## Phase 4: Agent-Specific Instructions Files

After creating each worktree, create a `.instructions.md` file scoped to that agent's workflow:

**Example: `.github/instructions/agent-foo.instructions.md`**

```markdown
---
description: Agent Foo's workflow for feature X
applyTo: '**' # or specific globs: 'src/components/**', 'docs/**'
---

# Agent Foo — Feature X Development

## Your Worktree
- Location: `/workspaces/mcapp-agent-foo`
- Branch: `feature/agent-foo`
- Session ID: `agent-foo-session-2026-04-03`

## Assigned Task
[Summary of what Agent Foo is building]

## Success Criteria
- [ ] Tests pass: `cd ../../ && npm test:e2e`
- [ ] Lint passes: `npm run lint:foo`
- [ ] Code review approved
- [ ] PR merged to main
```

---

## Phase 5: Session Persistence with ContextStream

Each agent session saves memory to ContextStream:

```bash
# At start of session (in worktree)
contextstream-mcp init --folder-path=$(pwd)

# In your agent code:
async function saveProgress() {
  await contextstream.memory.create_task({
    title: "Implement feature X",
    description: "Working on component Y",
    status: "in_progress",
    plan_id: "your-plan-id"
  });
}

# At end of session:
await contextstream.session.capture({
  event_type: "session_snapshot",
  title: "Agent Foo progress checkpoint",
  content: { summary, active_files, next_steps }
});
```

---

## Common Tasks

### Sync a Worktree with Latest Main

```bash
cd ../mcapp-agent-foo
git fetch origin main
git rebase origin/main
# OR
git merge origin/main --no-ff  # Preserves merge commit
```

### Delete a Worktree (after merge)

```bash
# From main worktree
git worktree remove ../mcapp-agent-foo
# This also cleans up the branch (after it's merged)
```

### Check All Worktree Status

```bash
git worktree list --porcelain
# Output: <path> <branch> <sha>
```

### Force Push a Worktree (use with caution!)

```bash
cd ../mcapp-agent-foo
git push --force-with-lease origin feature/agent-foo
```

---

## Troubleshooting

### "Worktree locked" Error

```bash
# If a worktree is locked (e.g., after a crash):
git worktree unlock ../mcapp-agent-foo
```

### "Cannot create worktree: branch already exists"

```bash
# Branch exists on origin; fetch and checkout
git fetch origin
git worktree add ../mcapp-agent-foo feature/agent-foo
```

### ContextStream sync issues

```bash
# Reinitialize ContextStream in worktree
cd ../mcapp-agent-foo
contextstream-mcp setup --force
```

---

## Next Steps

1. **Run Phase 1** (foundation setup) once
2. **Create your first agent worktree** (Phase 2.2)
3. **Run tutorial: 5-minute multi-agent flow** (see separate `/create-prompt` workflow)
4. **Enable automatic commits** (create a `.github/workflows/auto-commit.yml` task)
5. **Set up agent teams** (multi-agent-orchestrator agent + role-based instructions)

---

## Related Files

- [.github/copilot-instructions.md](../copilot-instructions.md) — Compact agent guide
- [DEVELOPER-QUICKSTART.md](../../DEVELOPER-QUICKSTART.md) — Per-component commands
- [.gitlab-ci.yml](../../.gitlab-ci.yml) — GitLab pipeline config
- [.github/agents/migration-analyst.agent.md](../agents/migration-analyst.agent.md) — Migration workflow
- [.github/agents/multi-agent-orchestrator.agent.md](../agents/multi-agent-orchestrator.agent.md) — Coming soon
