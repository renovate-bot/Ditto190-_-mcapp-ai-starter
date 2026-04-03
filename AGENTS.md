<contextstream>
# Workspace: mcpapp-monorepo
# Workspace ID: e76de4e7-5d4b-40c0-9023-10172088310c

# ContextStream Rules

**MANDATORY STARTUP:** On the first message of EVERY session call `init(...)` then `context(user_message="...")`. On subsequent messages, call `context(user_message="...")` first by default. A narrow bypass is allowed only for immediate read-only ContextStream calls when prior context is still fresh and no state-changing tool has run.

---
</contextstream>

# 🤖 Active Agents — mcapp-ai-starter

> **For all agents:** Before starting work on this project, **READ [AGENT_QUICKSTART.md](.github/instructions/AGENT_QUICKSTART.md) (5 minutes)** and check [SETUP_STATUS.md](.github/instructions/SETUP_STATUS.md) to know the current phase.

## Multi-Agent Orchestration Agents

### 🔄 multi-agent-orchestrator.agent.md

- **Symlink:** [→ .github/agents/multi-agent-orchestrator.agent.md](.github/agents/multi-agent-orchestrator.agent.md)
- **Type:** Coordination & Merge Management Agent
- **Primary Goal:** Detect ready-to-merge feature branches, create draft PRs, auto-merge on approval, coordinate across all active agents
- **Use When:**
  - Multiple agents have completed features (committed + pushed to feature/* branches)
  - A feature branch has passed code review and received approval
  - You need to coordinate parallel work across agent worktrees
  - GitLab mirroring requires a synchronized state

- **Required Reading (Read BEFORE using this agent):**
  1. [multi-agent-workflow.instructions.md](.github/instructions/multi-agent-workflow.instructions.md) — Phases 3–5 (Automatic Commits & Review Workflow, Multi-Agent Coordination, Session Persistence)
  2. [.github/copilot-instructions.md](.github/copilot-instructions.md) — Multi-Agent Orchestrator Agent section
  3. [AGENT_QUICKSTART.md](.github/instructions/AGENT_QUICKSTART.md) — Mandatory 5-minute onboarding

- **Tool Access Restrictions:**
  - Read-only git operations (can fetch/list branches, cannot force-push to main)
  - GitHub API access (PR creation, approval checks, merge)
  - ContextStream for state persistence and decision capture
  - NO direct write access to src/ (all code changes via agent worktrees)

- **Success Indicators:**
  - ✅ Draft PR auto-created when agent detects new commits
  - ✅ Code review agents automatically @-mentioned
  - ✅ PR merged on approval without manual intervention
  - ✅ All agent worktrees synced to latest main after merge

---

### 🔍 migration-analyst.agent.md

- **Symlink:** [→ .github/agents/migration-analyst.agent.md](.github/agents/migration-analyst.agent.md)
- **Type:** Code Review Gate & Recycling Analyst
- **Primary Goal:** Inspect migration/ folder for reusable patterns, flag security/logic issues, gate external code integration with tests
- **Use When:**
  - PR references code/configs from migration/ folder detected
  - External code or patterns from old projects need integration
  - Code review needs to verify safety + code quality before merge
  - You need structured analysis report (risk assessment + integration plan)

- **Required Reading (Read BEFORE using this agent):**
  1. [.github/copilot-instructions.md](.github/copilot-instructions.md) — Migration Folder Rules section
  2. [.github/agents/migration-analyst.agent.md](.github/agents/migration-analyst.agent.md) — Full workflow
  3. [AGENT_QUICKSTART.md](.github/instructions/AGENT_QUICKSTART.md) — Mandatory 5-minute onboarding

- **Tool Access Restrictions:**
  - Read-only access to migration/ folder
  - Cannot modify migration/ files (analysis-only)
  - GitHub PR comment API (can write review comments)
  - Terminal access for running tests (npm test, uv run pytest)
  - ContextStream for decision capture and risk assessment tracking

- **Success Indicators:**
  - ✅ Structured analysis report generated with: Content Type | Reuse Verdict | Risk Level | Proposed Action | Integration Tests
  - ✅ Security concerns (API keys, credentials) flagged as "DO NOT INTEGRATE"
  - ✅ Integration tests pass before code is approved for source/ directories
  - ✅ Gated integration plan created with ordered steps (dependencies between items)

---

## Skill Requirements for All Agents

**⚠️ Before any agent starts work:**

1. **Initialize ContextStream session:**

   ```bash
   # Run in your worktree
   contextstream-mcp init --folder-path=$(pwd)
   ```

2. **Enable git user config:**

   ```bash
   git config --local user.name "Agent <name>"
   git config --local user.email "agent+<name>@example.local"
   ```

3. **Verify Docker stack running (if code uses n8n):**

   ```bash
   docker compose ps | grep -E "n8n|postgres|ollama|qdrant"
   ```

4. **Check SETUP_STATUS.md for current phase and blockers:**

   ```
   Read: .github/instructions/SETUP_STATUS.md
   Know: What's done, what's in-progress, what's blocked, next immediate steps
   ```

---

## How Agents Are Coordinated

**Automatic Workflow (via multi-agent-orchestrator on scheduler):**

```
Scheduler (every 15 min) → Detects new commits
    ↓
multi-agent-orchestrator checks all worktrees
    ↓
For each ready-to-merge branch:
    1. Create draft PR (feature/* → main)
    2. Request code review (@code-reviewer)
    3. Request security review (@security-reviewer)
    4. Request migration analysis (@migration-analyst) if migration/ files present
    ↓
On approval:
    1. Squash merge to main
    2. Delete feature branch
    3. Sync all agent worktrees (git rebase)
    4. Trigger GitLab mirroring (webhook)
```

**Per-Agent Workflow (executed in agent's worktree):**

```
Agent creates/switches to worktree (feature/agent-name)
    ↓
Performs task + runs tests (npm test, uv run pytest)
    ↓
Commits + pushes to origin
    ↓
[Orchestrator detects] → Auto-creates PR
    ↓
[Orchestrator sees approval] → Auto-merges
    ↓
Agent syncs: git fetch origin main && git rebase origin/main
    ↓
Next task ready
```

---

## Proactive Agent Directives

**EVERY agent MUST follow these directives:**

### Before Starting Work

- [ ] **Read AGENT_QUICKSTART.md** (.github/instructions/AGENT_QUICKSTART.md) — 5 min mandatory
- [ ] **Check SETUP_STATUS.md** (.github/instructions/SETUP_STATUS.md) — Know current phase
- [ ] **Review multi-agent-workflow.instructions.md** (.github/instructions/multi-agent-workflow.instructions.md) — Understand your slot in 5-phase pipeline

### During Task Execution

- [ ] **Create/use designated worktree** (feature/agent-name, per initial-setup.instructions.md Phase 2)
- [ ] **Run full test suite** before committing (npm test && uv run pytest -m 'not e2e' -q)
- [ ] **Commit with conventional messages** (feat|fix|chore|docs: ...)
- [ ] **Push to origin** — orchestrator will auto-detect

### On Completion

- [ ] **Do NOT push/PR manually** — multi-agent-orchestrator handles this
- [ ] **Sync to latest main** (git fetch origin main && git rebase origin/main)
- [ ] **Capture session notes to ContextStream** (session(action="capture", event_type="session_snapshot", ...))
- [ ] **Check SETUP_STATUS.md for next phase** — know what comes next

### If Blocked or Error

- [ ] **Log decision/blockage to ContextStream** (memory(action="create_node", node_type="decision", ...))
- [ ] **Leave clear notes** in PR comments (migration-analyst or orchestrator will see them)
- [ ] **Escalate to human reviewer** if blockers exceed 30 minutes

---

## Related Documentation

- **Quick Start:** [AGENT_QUICKSTART.md](.github/instructions/AGENT_QUICKSTART.md) — 5-minute onboarding for all agents
- **Full Workflow:** [multi-agent-workflow.instructions.md](.github/instructions/multi-agent-workflow.instructions.md) — Complete 5-phase pipeline reference
- **Bootstrap Setup:** [initial-setup.instructions.md](.github/instructions/initial-setup.instructions.md) — Phase 1 (git config, worktree creation)
- **Knowledge Management:** [contextstream-knowledge-management.instructions.md](.github/instructions/contextstream-knowledge-management.instructions.md) — Session persistence & memory
- **Status Tracker:** [SETUP_STATUS.md](.github/instructions/SETUP_STATUS.md) — Current phase checklist
- **Copilot Conventions:** [.github/copilot-instructions.md](.github/copilot-instructions.md) — Project-wide agent rules & conventions

---

## MCP Apps SDK Documentation

### Architecture

MCP Apps SDK (`@modelcontextprotocol/ext-apps`) enables MCP servers to display interactive UIs in conversational clients.

Key abstractions:

- **View** - UI running in an iframe, uses `App` class with `PostMessageTransport` to communicate with host
- **Host** - Chat client embedding the iframe, uses `AppBridge` class to proxy MCP requests
- **Server** - MCP server that registers tools/resources with UI metadata

Specification (stable): `specification/2026-01-26/apps.mdx`

> **Note:** ContextStream Rules

---
</contextstream>

# 🤖 Active Agents — mcapp-ai-starter

> **For all agents:** Before starting work on this project, **READ [AGENT_QUICKSTART.md](.github/instructions/AGENT_QUICKSTART.md) (5 minutes)** and check [SETUP_STATUS.md](.github/instructions/SETUP_STATUS.md) to know the current phase.

## Multi-Agent Orchestration Agents

### 🔄 multi-agent-orchestrator.agent.md

- **Symlink:** [→ .github/agents/multi-agent-orchestrator.agent.md](.github/agents/multi-agent-orchestrator.agent.md)
- **Type:** Coordination & Merge Management Agent
- **Primary Goal:** Detect ready-to-merge feature branches, create draft PRs, auto-merge on approval, coordinate across all active agents
- **Use When:**
  - Multiple agents have completed features (committed + pushed to feature/* branches)
  - A feature branch has passed code review and received approval
  - You need to coordinate parallel work across agent worktrees
  - GitLab mirroring requires a synchronized state

- **Required Reading (Read BEFORE using this agent):**
  1. [multi-agent-workflow.instructions.md](.github/instructions/multi-agent-workflow.instructions.md) — Phases 3–5 (Automatic Commits & Review Workflow, Multi-Agent Coordination, Session Persistence)
  2. [.github/copilot-instructions.md](.github/copilot-instructions.md) — Multi-Agent Orchestrator Agent section
  3. [AGENT_QUICKSTART.md](.github/instructions/AGENT_QUICKSTART.md) — Mandatory 5-minute onboarding

- **Tool Access Restrictions:**
  - Read-only git operations (can fetch/list branches, cannot force-push to main)
  - GitHub API access (PR creation, approval checks, merge)
  - ContextStream for state persistence and decision capture
  - NO direct write access to src/ (all code changes via agent worktrees)

- **Success Indicators:**
  - ✅ Draft PR auto-created when agent detects new commits
  - ✅ Code review agents automatically @-mentioned
  - ✅ PR merged on approval without manual intervention
  - ✅ All agent worktrees synced to latest main after merge

---

### 🔍 migration-analyst.agent.md

- **Symlink:** [→ .github/agents/migration-analyst.agent.md](.github/agents/migration-analyst.agent.md)
- **Type:** Code Review Gate & Recycling Analyst
- **Primary Goal:** Inspect migration/ folder for reusable patterns, flag security/logic issues, gate external code integration with tests
- **Use When:**
  - PR references code/configs from migration/ folder detected
  - External code or patterns from old projects need integration
  - Code review needs to verify safety + code quality before merge
  - You need structured analysis report (risk assessment + integration plan)

- **Required Reading (Read BEFORE using this agent):**
  1. [.github/copilot-instructions.md](.github/copilot-instructions.md) — Migration Folder Rules section
  2. [.github/agents/migration-analyst.agent.md](.github/agents/migration-analyst.agent.md) — Full workflow
  3. [AGENT_QUICKSTART.md](.github/instructions/AGENT_QUICKSTART.md) — Mandatory 5-minute onboarding

- **Tool Access Restrictions:**
  - Read-only access to migration/ folder
  - Cannot modify migration/ files (analysis-only)
  - GitHub PR comment API (can write review comments)
  - Terminal access for running tests (npm test, uv run pytest)
  - ContextStream for decision capture and risk assessment tracking

- **Success Indicators:**
  - ✅ Structured analysis report generated with: Content Type | Reuse Verdict | Risk Level | Proposed Action | Integration Tests
  - ✅ Security concerns (API keys, credentials) flagged as "DO NOT INTEGRATE"
  - ✅ Integration tests pass before code is approved for source/ directories
  - ✅ Gated integration plan created with ordered steps (dependencies between items)

---

## Skill Requirements for All Agents

**⚠️ Before any agent starts work:**

1. **Initialize ContextStream session:**

   ```bash
   # Run in your worktree
   contextstream-mcp init --folder-path=$(pwd)
   ```

2. **Enable git user config:**

   ```bash
   git config --local user.name "Agent <name>"
   git config --local user.email "agent+<name>@example.local"
   ```

3. **Verify Docker stack running (if code uses n8n):**

   ```bash
   docker compose ps | grep -E "n8n|postgres|ollama|qdrant"
   ```

4. **Check SETUP_STATUS.md for current phase and blockers:**

   ```
   Read: .github/instructions/SETUP_STATUS.md
   Know: What's done, what's in-progress, what's blocked, next immediate steps
   ```

---

## How Agents Are Coordinated

**Automatic Workflow (via multi-agent-orchestrator on scheduler):**

```
Scheduler (every 15 min) → Detects new commits
    ↓
multi-agent-orchestrator checks all worktrees
    ↓
For each ready-to-merge branch:
    1. Create draft PR (feature/* → main)
    2. Request code review (@code-reviewer)
    3. Request security review (@security-reviewer)
    4. Request migration analysis (@migration-analyst) if migration/ files present
    ↓
On approval:
    1. Squash merge to main
    2. Delete feature branch
    3. Sync all agent worktrees (git rebase)
    4. Trigger GitLab mirroring (webhook)
```

**Per-Agent Workflow (executed in agent's worktree):**

```
Agent creates/switches to worktree (feature/agent-name)
    ↓
Performs task + runs tests (npm test, uv run pytest)
    ↓
Commits + pushes to origin
    ↓
[Orchestrator detects] → Auto-creates PR
    ↓
[Orchestrator sees approval] → Auto-merges
    ↓
Agent syncs: git fetch origin main && git rebase origin/main
    ↓
Next task ready
```

---

## Proactive Agent Directives

**EVERY agent MUST follow these directives:**

### Before Starting Work

- [ ] **Read AGENT_QUICKSTART.md** (.github/instructions/AGENT_QUICKSTART.md) — 5 min mandatory
- [ ] **Check SETUP_STATUS.md** (.github/instructions/SETUP_STATUS.md) — Know current phase
- [ ] **Review multi-agent-workflow.instructions.md** (.github/instructions/multi-agent-workflow.instructions.md) — Understand your slot in 5-phase pipeline

### During Task Execution

- [ ] **Create/use designated worktree** (feature/agent-name, per initial-setup.instructions.md Phase 2)
- [ ] **Run full test suite** before committing (npm test && uv run pytest -m 'not e2e' -q)
- [ ] **Commit with conventional messages** (feat|fix|chore|docs: ...)
- [ ] **Push to origin** — orchestrator will auto-detect

### On Completion

- [ ] **Do NOT push/PR manually** — multi-agent-orchestrator handles this
- [ ] **Sync to latest main** (git fetch origin main && git rebase origin/main)
- [ ] **Capture session notes to ContextStream** (session(action="capture", event_type="session_snapshot", ...))
- [ ] **Check SETUP_STATUS.md for next phase** — know what comes next

### If Blocked or Error

- [ ] **Log decision/blockage to ContextStream** (memory(action="create_node", node_type="decision", ...))
- [ ] **Leave clear notes** in PR comments (migration-analyst or orchestrator will see them)
- [ ] **Escalate to human reviewer** if blockers exceed 30 minutes

---

## Related Documentation

- **Quick Start:** [AGENT_QUICKSTART.md](.github/instructions/AGENT_QUICKSTART.md) — 5-minute onboarding for all agents
- **Full Workflow:** [multi-agent-workflow.instructions.md](.github/instructions/multi-agent-workflow.instructions.md) — Complete 5-phase pipeline reference
- **Bootstrap Setup:** [initial-setup.instructions.md](.github/instructions/initial-setup.instructions.md) — Phase 1 (git config, worktree creation)
- **Knowledge Management:** [contextstream-knowledge-management.instructions.md](.github/instructions/contextstream-knowledge-management.instructions.md) — Session persistence & memory
- **Status Tracker:** [SETUP_STATUS.md](.github/instructions/SETUP_STATUS.md) — Current phase checklist
- **Copilot Conventions:** [.github/copilot-instructions.md](.github/copilot-instructions.md) — Project-wide agent rules & conventions

---

## MCP Apps SDK Documentation

### Architecture

MCP Apps SDK (`@modelcontextprotocol/ext-apps`) enables MCP servers to display interactive UIs in conversational clients.

Key abstractions:

- **View** - UI running in an iframe, uses `App` class with `PostMessageTransport` to communicate with host
- **Host** - Chat client embedding the iframe, uses `AppBridge` class to proxy MCP requests
- **Server** - MCP server that registers tools/resources with UI metadata

Specification (stable): `specification/2026-01-26/apps.mdx`

> **Note:** ContextStream Rules

## Required Tool Calls

1. **First message in session**: Call `init(folder_path="<project_path>")` then `context(user_message="...", session_id="<id>")`
2. **Subsequent messages (default)**: Call `context(user_message="...", session_id="<id>")` first. Narrow bypass: immediate read-only ContextStream calls with fresh context + no state changes.
3. **Before file search**: Call `search(mode="auto", query="...")` before local tools

**Read-only examples** (default: call `context(...)` first; narrow bypass only for immediate read-only ContextStream calls when context is fresh and no state-changing tool has run): `workspace(action="list"|"get"|"create")`, `memory(action="list_docs"|"list_events"|"list_todos"|"list_tasks"|"list_transcripts"|"list_nodes"|"decisions"|"get_doc"|"get_event"|"get_task"|"get_todo"|"get_transcript")`, `session(action="get_lessons"|"get_plan"|"list_plans"|"recall")`, `help(action="version"|"tools"|"auth")`, `project(action="list"|"get"|"index_status")`, `reminder(action="list"|"active")`, any read-only data query

**Common queries — use these exact tool calls:**

- "list lessons" / "show lessons" → `session(action="get_lessons")`
- "list decisions" / "show decisions" / "how many decisions" → `memory(action="decisions")`
- "list docs" → `memory(action="list_docs")`
- "list tasks" → `memory(action="list_tasks")`
- "list todos" → `memory(action="list_todos")`
- "list plans" → `session(action="list_plans")`
- "list events" → `memory(action="list_events")`
- "show snapshots" / "list snapshots" → `memory(action="list_events", event_type="session_snapshot")`
- "save snapshot" → `session(action="capture", event_type="session_snapshot", title="...", content="...")`
- "list skills" / "show my skills" → `skill(action="list")`
- "create a skill" → `skill(action="create", name="...", instruction_body="...", trigger_patterns=[...])`
- "update a skill" → `skill(action="update", name="...", instruction_body="...", change_summary="...")`
- "run skill" / "use skill" → `skill(action="run", name="...")`
- "import skills" / "import my CLAUDE.md" → `skill(action="import", file_path="...", format="auto")`

Use `context(user_message="...", mode="fast")` for quick turns.
Use `context(user_message="...")` for deeper analysis and coding tasks.
If the `instruct` tool is available, run `instruct(action="get", session_id="...")` before `context(...)` on each turn, then `instruct(action="ack", session_id="...", ids=[...])` after using entries.

**Plan-mode guardrail:** Entering plan mode does NOT bypass search-first. Do NOT use Explore, Task subagents, Grep, Glob, Find, SemanticSearch, `code_search`, `grep_search`, `find_by_name`, or shell search commands (`grep`, `find`, `rg`, `fd`). Start with `search(mode="auto", query="...")` — it handles glob patterns, regex, exact text, file paths, and semantic queries. Only Read narrowed files/line ranges returned by search.

## Why These Rules?

- `context()` returns task-specific rules, lessons from past mistakes, and relevant decisions
- `search()` uses semantic understanding to find relevant code faster than file scanning
- Transcript capture is optional and OFF by default. Enable per session with `save_exchange=true` (and `session_id`), disable with `save_exchange=false`.
- Default context-first keeps state reliable; the narrow read-only bypass avoids unnecessary repeats

## Response to Notices

- `[LESSONS_WARNING]` → Apply the lessons shown to avoid repeating mistakes
- `[PREFERENCE]` → Follow user preferences exactly
- `[RULES_NOTICE]` → Run `generate_rules()` to update rules
- `[VERSION_NOTICE]` → Inform user about available updates

## System Reminders

`<system-reminder>` tags in messages contain injected instructions from hooks.
These should be followed exactly as they contain real-time context.

## Search Protocol

1. Check project index: `project(action="index_status")`
2. If indexed & fresh: `search(mode="auto", query="...")` before local tools
3. If NOT indexed or stale: wait for background refresh (up to ~20s, configurable), retry `search(mode="auto", ...)`, then use local tools only after the grace window elapses
4. If search returns 0 results after refresh/retry: local tools are allowed

### Search Mode Selection

- `auto` (recommended): query-aware mode selection
- `hybrid`: mixed semantic + keyword retrieval for broad discovery
- `semantic`: conceptual/natural-language questions ("how does auth work?")
- `keyword`: exact text or quoted string
- `pattern`: glob/regex queries (`*.sql`, `foo\s+bar`)
- `refactor`: symbol usage / rename-safe lookup (`UserService`, `snake_case`)
- `exhaustive`: all occurrences / complete match sets
- `team`: cross-project team search

### Output Format Hints

- `output_format="paths"` for file lists and rename targets
- `output_format="count"` for "how many" queries

### Two-Phase Search Playbook (recommended)

1. **Discovery pass**: run `search(mode="auto", query="<concept + module>", output_format="paths", limit=10)`
2. **Precision pass**: use symbols from pass 1 with a specific mode:
   - Exact symbol/text: `search(mode="keyword", query="\"my_symbol\"", include_content=true, file_types=["rs"], limit=20)`
   - Symbol usage/rename-safe lookup: `search(mode="refactor", query="MySymbol", output_format="paths")`
   - Complete usage sweep: `search(mode="exhaustive", query="my_symbol", file_types=["rs"])`
3. **Read locally only after narrowing**: use Read/Grep on returned paths, not the full repo.

## Plans and Tasks

**ALWAYS** use ContextStream for plans and tasks — do NOT create markdown plan files or use built-in todo tools:

- Plans: `session(action="capture_plan", title="...", steps=[...])`
- Tasks: `memory(action="create_task", title="...", description="...")`
- Link tasks to plans: `memory(action="create_task", plan_id="...")`

## Memory, Docs & Todos

**ALWAYS** use ContextStream for memory, documents, and todos — NOT editor built-in tools or local files:

- Decisions: `session(action="capture", event_type="decision", title="...", content="...")`
- Notes/insights: `session(action="capture", event_type="note|insight", title="...", content="...")`
- Facts/preferences: `memory(action="create_node", node_type="fact|preference", title="...", content="...")`
- Documents: `memory(action="create_doc", title="...", content="...", doc_type="spec|general")`
- Todos: `memory(action="create_todo", title="...", todo_priority="high|medium|low")`
Do NOT use `create_memory`, `TodoWrite`, `todo_list`, or local file writes for persistence.

## Skills

Reusable instruction + action bundles that persist across projects and sessions:

- Browse: `skill(action="list")` or `skill(action="list", scope="team")`
- Create: `skill(action="create", name="...", instruction_body="...", trigger_patterns=[...])`
- Update: `skill(action="update", name="...", instruction_body="...", change_summary="...")` (name or `skill_id`)
- Run: `skill(action="run", name="...")` — executes the skill's action pipeline
- Import: `skill(action="import", file_path="CLAUDE.md", format="auto")` — imports from any rules file
- Skills auto-activate when their trigger keywords match the user's message. No explicit call needed.

## Code Search

**ALWAYS** use ContextStream `search()` before Glob, Grep, Read, SemanticSearch, `code_search`, `grep_search`, or `find_by_name`.
Do NOT launch Task/explore subagents for code search — use `search(mode="auto", query="...")` directly.
ContextStream search results contain **real file paths, line numbers, and code content** — they ARE code results.
**NEVER** dismiss ContextStream results as "non-code" — use the returned file paths to `read_file` the relevant code.
Use `search(include_content=true)` to get inline code snippets in results.

## Context Pressure

When `context()` returns `context_pressure.level: "high"`:

- Save a session snapshot before compaction
- `session(action="capture", event_type="session_snapshot", title="...", content="...")`
- After compaction: `init(folder_path="...", is_post_compact=true)` to restore

---

## IMPORTANT: No Hooks Available

**This editor does NOT have hooks to enforce ContextStream behavior.**
You MUST follow these rules manually - there is no automatic enforcement.

---

## SESSION START PROTOCOL

**On EVERY new session, you MUST:**

1. **Call `init(folder_path="<project_path>")`** FIRST
   - This triggers project indexing
   - Check response for `indexing_status`
   - If `"started"` or `"refreshing"`: wait before searching

2. **Generate a unique session_id** (e.g., `"session-" + timestamp` or a UUID)
   - Use this SAME session_id for ALL `context()` calls in this conversation

3. **Call `context(user_message="<first_message>", session_id="<id>")`**
   - Gets task-specific rules, lessons, and preferences
   - Check for [LESSONS_WARNING], [PREFERENCE], [RULES_NOTICE]

4. **Default behavior:** call `context(...)` first on each message. Narrow bypass is allowed only for immediate read-only ContextStream calls when previous context is still fresh and no state-changing tool has run.

5. **Instruction alignment (if tool is exposed):** call `instruct(action="get", session_id="<id>")` before `context(...)` each turn, and `instruct(action="ack", session_id="<id>", ids=[...])` after using entries.

---

## TRANSCRIPT SAVING (OPTIONAL)

Transcripts are OFF by default.

### Enable for this chat

```
context(user_message="<user's message>", save_exchange=true, session_id="<session-id>")
```

### Disable for this chat

```
context(user_message="<user's message>", save_exchange=false, session_id="<session-id>")
```

### Default policy via MCP config env

- `CONTEXTSTREAM_TRANSCRIPTS_ENABLED="true|false"`
- `CONTEXTSTREAM_HOOK_TRANSCRIPTS_ENABLED="true|false"`

### Session ID Guidelines

- Generate ONCE at the start of the conversation
- Use a unique identifier (UUID or timestamp-based)
- Keep the SAME session_id for ALL context() calls
- Different sessions = different transcript preference state

---

## FILE INDEXING (CRITICAL)

**There is NO automatic file indexing in this editor.**
You MUST manage indexing manually:

### After Creating/Editing Files

```
project(action="index")
```

If folder context is active, this resolves the current repo and uses the local ingest path automatically.

### To Target A Specific Folder Or Recover From Stale Scope

```
project(action="ingest_local", path="<project_folder>")
```

### Signs You Need to Re-index

- Search doesn't find code you just wrote
- Search returns old versions of functions
- New files don't appear in search results

---

## SEARCH-FIRST (No PreToolUse Hook)

**There is NO hook to redirect local tools.** You MUST self-enforce:

### Before ANY Search, Check Index Status

```
project(action="index_status")
```

### Search Protocol

- **IF indexed & fresh:** `search(mode="auto", query="...")` before local tools
- **IF NOT indexed or stale (>7 days):** wait up to ~20s for background refresh, retry `search(mode="auto", ...)`, then allow local tools only after the grace window elapses
- **IF search returns 0 results after retry/window:** local tools are allowed

### Choose Search Mode Intelligently

- `auto` (recommended): query-aware mode selection
- `hybrid`: mixed semantic + keyword retrieval for broad discovery
- `semantic`: conceptual questions ("how does X work?")
- `keyword`: exact text / quoted string
- `pattern`: glob or regex (`*.ts`, `foo\s+bar`)
- `refactor`: symbol usage / rename-safe lookup
- `exhaustive`: all occurrences / complete match coverage
- `team`: cross-project team search

### Output Format Hints

- Use `output_format="paths"` for file listings and rename targets
- Use `output_format="count"` for "how many" queries

### Two-Phase Search Pattern (for precision)

- Pass 1 (discovery): `search(mode="auto", query="<concept + module>", output_format="paths", limit=10)`
- Pass 2 (precision): use one of:
  - exact text/symbol: `search(mode="keyword", query="\"exact_text\"", include_content=true)`
  - symbol usage: `search(mode="refactor", query="SymbolName", output_format="paths")`
  - all occurrences: `search(mode="exhaustive", query="symbol_or_text")`
- Then use local Read/Grep only on paths returned by ContextStream.

### When Local Tools Are OK

- The stale/not-indexed grace window has elapsed (~20s default, configurable)
- ContextStream search still returns 0 results or errors after retry
- User explicitly requests local tools

---

## CONTEXT COMPACTION (No PreCompact Hook)

**There is NO automatic state saving before compaction.**
You MUST save state manually when the conversation gets long:

### When to Save State

- After completing a major task
- Before the conversation might be compacted
- If `context()` returns `context_pressure.level: "high"`

### How to Save State

```
session(action="capture", event_type="session_snapshot",
  title="Session checkpoint",
  content="{ \"summary\": \"what we did\", \"active_files\": [...], \"next_steps\": [...] }")
```

### After Compaction (if context seems lost)

```
init(folder_path="...", is_post_compact=true)
```

---

## PLANS & TASKS (CRITICAL)

**NEVER create markdown plan files** — they vanish across sessions and are not searchable.
**NEVER use built-in todo/plan tools** (e.g., `TodoWrite`, `todo_list`, `plan_mode_respond`) — use ContextStream instead.

**ALWAYS use ContextStream for planning:**

```
session(action="capture_plan", title="...", steps=[...])
memory(action="create_task", title="...", plan_id="...")
```

Plans and tasks in ContextStream persist across sessions, are searchable, and auto-surface in context.

---

## MEMORY & DOCS (CRITICAL)

**NEVER use built-in memory tools** (e.g., `create_memory`) — use ContextStream instead.
**NEVER write docs/specs/notes to local files** — use ContextStream docs instead.

**ALWAYS use ContextStream for persistence:**

```
session(action="capture", event_type="decision|insight|operation|uncategorized", title="...", content="...")
memory(action="create_node", node_type="fact|preference", title="...", content="...")
memory(action="create_doc", title="...", content="...", doc_type="spec|general")
memory(action="create_todo", title="...", todo_priority="high|medium|low")
```

ContextStream memory, docs, and todos persist across sessions, are searchable, and auto-surface in context.

---

## VERSION UPDATES

**Check for updates periodically** using `help(action="version")`.

If the response includes [VERSION_NOTICE] or [VERSION_CRITICAL], tell the user about the available update.

### Update Commands

```bash
# macOS/Linux
curl -fsSL https://contextstream.io/scripts/setup-beta.sh | bash
# npm
npm install -g @contextstream/mcp-server@latest
```

---

---

## Codex/OpenCode-Specific Rules

**CRITICAL: ContextStream search() REPLACES all built-in search tools.**
**The user is paying for ContextStream's premium search — default tools must not bypass it.**

### Search: Use ContextStream, Not Built-in Tools

- **Do NOT** use `Explore` subagents for code discovery — use `search(mode="auto", query="...")` instead
- **Do NOT** use "Searched for files" or "Searched for <pattern>" built-in operations — use `search(mode="pattern", query="...")` instead
- **Do NOT** run shell commands for search (`grep`, `find`, `rg`, `fd`, `ack`) — use `search()` instead
- **Do NOT** scan directories or list files for discovery — use `search(mode="auto", query="...")` instead
- ContextStream search handles **all** search use cases: exact text, regex, glob patterns, semantic queries, file paths
- ContextStream search results contain **real file paths, line numbers, and code content** — they ARE code results
- **NEVER** dismiss ContextStream results as "non-code" — use the returned file paths to `read_file` the relevant code
- Only fall back to local/shell tools after stale/not-indexed grace window (~20s) and retry still returns **exactly 0 results**

### Search Mode Selection (use these instead of shell commands)

- Instead of `grep "pattern"`: use `search(mode="keyword", query="pattern")`
- Instead of `find . -name "*.tsx"`: use `search(mode="pattern", query="*.tsx")`
- Instead of `grep -E "regex"`: use `search(mode="pattern", query="regex")`
- Instead of exploring directories: use `search(mode="auto", query="<what you're looking for>")`

### Memory: Use ContextStream, Not Local Files

- **Do NOT** write decisions/notes/specs to local files
- Use `session(action="capture", event_type="decision|insight|operation|uncategorized", title="...", content="...")`
- Use `memory(action="create_doc", title="...", content="...", doc_type="spec|general")`

### Planning: Use ContextStream, Not Built-in Tools

- **Do NOT** create markdown plan files — they vanish across sessions
- **Do NOT** use Codex plan mode output (`plan_mode_respond`) as the persistent plan record — save the plan to ContextStream instead
- **Do NOT** use built-in todo/plan tools (`TodoWrite`, `todo_list`, `plan_mode_respond`) for persistent plans or tasks
- **ALWAYS** save plans: `session(action="capture_plan", title="...", steps=[...])`
- **ALWAYS** create tasks: `memory(action="create_task", title="...", plan_id="...")`
</contextstream>

# MCP Apps SDK

## Project Overview

MCP Apps SDK (`@modelcontextprotocol/ext-apps`) enables MCP servers to display interactive UIs in conversational clients.

Key abstractions:

- **View** - UI running in an iframe, uses `App` class with `PostMessageTransport` to communicate with host
- **Host** - Chat client embedding the iframe, uses `AppBridge` class to proxy MCP requests
- **Server** - MCP server that registers tools/resources with UI metadata

Specification (stable): `specification/2026-01-26/apps.mdx`

## Commands

```bash
# Install dependencies
npm install

# Build the SDK only (generates schemas + bundles, does not build examples)
npm run build

# Build everything (SDK + all examples)
npm run build:all

# Type check + build a single example
npm run --workspace examples/<example-name> build

# Run all examples (starts server at http://localhost:8080)
npm start

# Run E2E tests (primary testing mechanism - starts examples server automatically)
npm run test:e2e

# Run unit tests (E2E tests have broader coverage; unit tests cover specific modules)
npm test

# Check JSDoc comment syntax and `{@link}` references
npm exec typedoc -- --treatValidationWarningsAsErrors --emit none

# Regenerate package-lock.json (especially on setups w/ custom npm registry)
rm -fR  package-lock.json node_modules && \
  docker run  --rm -it --platform linux/amd64 -v $PWD:/src:rw -w /src node:latest npm i && \
  rm -fR node_modules && \
  npm  i  --cache=~/.npm-mcp-apps --registry=https://registry.npmjs.org/
```

## Architecture

### SDK Entry Points

- `@modelcontextprotocol/ext-apps` - Main SDK for Apps (`App` class, `PostMessageTransport`)
- `@modelcontextprotocol/ext-apps/react` - React hooks (`useApp`, `useHostStyleVariables`, etc.)
- `@modelcontextprotocol/ext-apps/app-bridge` - SDK for hosts (`AppBridge` class)
- `@modelcontextprotocol/ext-apps/server` - Server helpers (`registerAppTool`, `registerAppResource`)

### Key Source Files

- `src/app.ts` - `App` class extends MCP Protocol, handles guest initialization, tool calls, messaging
- `src/app-bridge.ts` - `AppBridge` class for hosts, proxies MCP requests, sends tool input/results to guests
- `src/server/index.ts` - Helpers for MCP servers to register tools/resources with UI metadata
- `src/types.ts` - Protocol types re-exported from `spec.types.ts` and Zod schemas from `generated/schema.ts` (auto-generated during build)
- `src/message-transport.ts` - `PostMessageTransport` for iframe communication
- `src/react/` - React hooks: `useApp`, `useHostStyles`, `useAutoResize`, `useDocumentTheme`

### Protocol Flow

```
View (App) <--PostMessageTransport--> Host (AppBridge) <--MCP Client--> MCP Server
```

1. Host creates iframe with view HTML
2. View creates `App` instance and calls `connect()` with `PostMessageTransport`
3. View sends `ui/initialize` request, receives host capabilities and context
4. Host sends `sendToolInput()` with tool arguments after initialization
5. View can call server tools via `app.callServerTool()` or send messages via `app.sendMessage()`
6. Host sends `sendToolResult()` when tool execution completes
7. Host calls `teardownResource()` before unmounting iframe

## Documentation

JSDoc `@example` tags should pull type-checked code from companion `.examples.ts` files (e.g., `app.ts` → `app.examples.ts`). Use ` ```ts source="./file.examples.ts#regionName" ` fences referencing `//#region regionName` blocks; region names follow `exportedName_variant` or `ClassName_methodName_variant` pattern (e.g., `useApp_basicUsage`, `App_hostCapabilities_checkAfterConnection`). For whole-file inclusion (any file type), omit the `#regionName`. Run `npm run sync:snippets` to sync.

Standalone docs in `docs/` (listed in `typedoc.config.mjs` `projectDocuments`) can also have type-checked companion `.ts`/`.tsx` files using the same pattern.

## Full Examples

Uses npm workspaces. Full examples in `examples/` are separate packages:

- `basic-server-*` - Starter templates (vanillajs, react, vue, svelte, preact, solid). Use these as the basis for new examples.
- `basic-host` - Reference host implementation
- Other examples showcase specific features (charts, 3D, video, etc.)

## Claude Code Plugin

The `plugins/mcp-apps/` directory contains a Claude Code plugin distributed via the plugin marketplace. It provides the following Claude Code skills files:

- `plugins/mcp-apps/skills/create-mcp-app/SKILL.md` — for creating an MCP App
- `plugins/mcp-apps/skills/migrate-oai-app/SKILL.md` — for migrating an app from the OpenAI Apps SDK to the MCP Apps SDK
