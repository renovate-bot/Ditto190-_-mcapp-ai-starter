---
description: >
  Complete multi-agent setup and workflow reference. Covers foundation (Phase 1),
  worktree creation (Phase 2), automatic commits (Phase 3), persistence (Phase 5),
  and troubleshooting.
applyTo: '**'
---

# Multi-Agent Development — Complete Setup & Workflow Reference

## Quick Links
- [Initial Setup Instructions](./../instructions/initial-setup.instructions.md) — Foundation (Phases 1–5)
- [Multi-Agent Orchestrator](./../agents/multi-agent-orchestrator.agent.md) — Automated PR/merge coordination
- [Migration Analyst](./../agents/migration-analyst.agent.md) — Code recycling from `migration/` folder
- [Copilot Instructions](./../copilot-instructions.md) — Compact agent guide

---

## Priority 1: Multi-Agent Git Worktrees & Automatic Commits

### Why This Matters
- **Isolation**: Each AI agent works in its own worktree (branch + directory) without blocking others
- **Parallel speed**: Multiple agents commit independently; no rebasing bottlenecks
- **Automatic tracking**: Changes auto-committed, PRs auto-created, reviews auto-requested
- **Auditability**: Full git history with agent identity, committer info, and timestamps

### Foundation Setup (Run Once)

```bash
# Phase 1: Clone & dependencies
cd /workspaces/mcapp-ai-starter
cp .env.example .env
# Edit .env with secrets (N8N keys, LLM provider keys, ContextStream API key)

# Install all components
npm install && \
  cd GenerateAgents.md && uv sync --extra dev && cd .. && \
  cd generateagents-mcp && uv sync && cd .. && \
  cd prompt-registry && npm ci && cd .. && \
  cd awesome-copilot && npm ci && cd ..

# Phase 2: Start Docker stack
docker compose config -q && docker compose up -d && sleep 30
```

### Create an Agent Worktree

```bash
# For agent "foo" working on "feature-x"
git worktree add ../mcapp-agent-foo -b feature/agent-foo

# Verify
git worktree list
# /workspaces/mcapp-ai-starter                main
# /workspaces/mcapp-agent-foo                 feature/agent-foo

# Switch into the worktree
cd ../mcapp-agent-foo
```

### Agent Workflow Loop

```bash
# Inside worktree: ../mcapp-agent-foo

# 1. Make changes
# ... edit src/components/MyComponent.ts
# ... add tests in tests/MyComponent.test.ts

# 2. Test locally
npm test               # Unit tests
npm run lint           # Type check & lint

# 3. Commit (auto-message or manual)
git add .
git commit -m "feat(components): add MyComponent with tests"

# 4. Push to GitHub
git push --set-upstream origin feature/agent-foo

# (Multi-Agent Orchestrator now creates PR, requests reviews, merges)
```

### Multi-Agent Orchestrator Coordination

The **multi-agent-orchestrator** agent runs on a schedule (e.g., every 15 minutes) and:

1. **Detects new commits** in all worktrees
2. **Creates draft PRs** with auto-generated titles and descriptions
3. **Requests reviews**:
   - Code review: `@code-reviewer`
   - Security: `@security-reviewer` (CodeQL + artifact scanning)
   - Performance: `@perf-reviewer` (if benchmarks affected)
4. **Merges on approval**:
   - Squash merge to clean history
   - Delete branch after merge
   - Trigger GitLab mirror (webhook)
   - Tag release if applicable
5. **Syncs all worktrees** to latest main after merge

---

## How It Works: DETAI

### Git Worktree Architecture

```
.git/                             # Shared object database
├── HEAD, config, refs/
├── objects/, refs/heads/, etc.

worktree-main/
├── .git -> ../.git (symbolic link)
├── src/
├── package.json
└── HEAD -> main

worktree-agent-foo/
├── .git -> ../.git
├── src/  (checked out to feature/agent-foo)
└── HEAD -> feature/agent-foo

worktree-agent-bar/
├── .git -> ../.git
├── src/  (checked out to feature/agent-bar)
└── HEAD -> feature/agent-bar
```

**Benefits:**
- Shared git objects → zero duplicate storage
- Independent branches → no interference
- Fast checkout → no rebasing needed before merge
- Atomic merges → all-or-nothing consistency

### Automatic Commit Flow

```
Agent Foo makes edits in ../mcapp-agent-foo
         ↓
Tests pass (npm test, npm run lint)
         ↓
Agent commits: git add . && git commit -m "..."
         ↓
Agent pushes: git push origin feature/agent-foo
         ↓
Multi-Agent Orchestrator detects new commit
         ↓
Creates draft PR: feature/agent-foo → main
         ↓
Requests reviews (@code-reviewer, @security-reviewer)
         ↓
Reviews complete → "Approve" comment added
         ↓
Orchestrator merges: gh pr merge --squash --delete-branch
         ↓
GitHub webhook triggers GitLab mirroring
         ↓
GitLab runs .gitlab-ci.yml pipeline (same tests)
         ↓
Both GitHub + GitLab status checks pass
         ↓
All agents sync: git fetch origin main && git rebase origin/main
         ↓
Next round ready
```

### ContextStream Memory Persistence

Each worktree session saves progress:

```bash
# At start
cd ../mcapp-agent-foo
contextstream-mcp init --folder-path=$(pwd)

# During work (in agent code)
async function onCommit(message) {
  await contextstream.session.capture({
    event_type: "operation",
    title: `Commit: ${message}`,
    content: { files_changed, tests_passed, next_task }
  });
}

# At end of session
await contextstream.session.capture({
  event_type: "session_snapshot",
  title: f"Agent Foo session {date}",
  content: {
    summary: "Completed feature X",
    active_files: ["src/MyComponent.ts", "tests/..."],
    next_steps: ["Review pending", "Merge when approved"],
    blockers: []
  }
});
```

---

## Practical Example: Two Agents in Parallel

### Setup

```bash
cd /workspaces/mcapp-ai-starter

# Agent Foo: working on auth feature
git worktree add ../mcapp-agent-foo -b feature/auth

# Agent Bar: working on UI components
git worktree add ../mcapp-agent-bar -b feature/ui
```

### Agent Foo's Session

```bash
cd ../mcapp-agent-foo

# Make changes to auth
echo "export const authenticate = async () => {...}" > src/auth.ts
npm test  # ✓ All pass

git add . && git commit -m "feat(auth): add authentication module"
git push origin feature/auth

# Sleeps—orchestrator will handle PR creation
```

### Agent Bar's Session (Simultaneous)

```bash
cd ../mcapp-agent-bar

# Make changes to UI (independent branch)
echo "<Button>Click me</Button>" > src/Button.tsx
npm test  # ✓ All pass

git add . && git commit -m "feat(ui): add Button component"
git push origin feature/ui

# Both PRs are now open
```

### Orchestrator Runs

```
Schedule: Every 15 minutes

1. Detects feature/auth has new commit → creates PR #123
   - Requests: @code-reviewer, @security-reviewer

2. Detects feature/ui has new commit → creates PR #124
   - Requests: @code-reviewer

3. Monitors PR status:
   - PR #123: 1/2 reviews approved → wait
   - PR #124: approved → merge
     - Triggers: gh pr merge #124 --squash --delete-branch
     - GitLab mirrors: new commit on main

4. Syncs all worktrees:
   - agent-foo: git fetch origin main && git rebase origin/main
   - agent-bar: git fetch origin main && git rebase origin/main (branch deleted)

5. agent-bar removed (branch merged), creates new worktree if next task assigned
```

---

## Troubleshooting

### Q: Worktree is locked (crash recovery)

```bash
git worktree unlock ../mcapp-agent-foo
```

### Q: Branch conflicts during merge

```bash
# Orchestrator detects conflict → creates regular (non-draft) PR
# Reviewer resolves conflict manually, re-requests review
# Orchestrator re-checks and merges on approval
```

### Q: Agent changes are not auto-committed

Ensure:
1. Tests pass: `npm test && npm run lint`
2. .git/config has correct user.name/email (per-worktree)
3. Commit message follows Conventional Commits: `feat|fix|chore|docs(...)`
4. Push succeeds: `git push origin feature/...`

### Q: GitLab mirroring is delayed

Check GitLab webhook status:
1. Go to GitLab project → Integrations → GitHub
2. View recent deliveries (should be <5 sec latency)
3. If failed, re-trigger manually or adjust webhook settings

### Q: How do I manually trigger a PR merge?

```bash
# If orchestrator is stuck, manually merge:
gh pr merge <pr-number> --squash --delete-branch

# Or via GitHub UI: Squash and merge on PR page
```

---

## Next Steps

1. **Run Phase 1 setup** (clone, dependencies, Docker stack)
2. **Create first agent worktree** for a task (e.g., `git worktree add ../mcapp-agent-foo -b feature/foo`)
3. **Test the loop**: edit → commit → push → orchestrator creates PR
4. **Enable scheduled orchestrator** (via `.github/workflows/multi-agent-orchestrator.yml`)
5. **Create per-agent instructions** (e.g., `.github/instructions/agent-foo.instructions.md`)

---

## Related Documentation

- [Initial Setup — Full Phases 1–5](./../instructions/initial-setup.instructions.md)
- [Copilot Instructions — Compact Guide](./../copilot-instructions.md)
- [GitLab Setup](../../GITLAB_SETUP.md)
- [Developer Quickstart](../../DEVELOPER-QUICKSTART.md)
- [n8n Component Notes](../../n8n/AGENTS.md)
