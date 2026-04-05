<contextstream>
# Workspace: .contextstream-global
# Project: mcapp-ai-starter
# Workspace ID: 16d99449-f219-41fd-b021-1cb09e2eedeb

# ContextStream Rules

**MANDATORY STARTUP:** On the first message of EVERY session call `mcp__contextstream__init(...)` then `mcp__contextstream__context(user_message="...")`. On subsequent messages, call `mcp__contextstream__context(user_message="...")` first by default. A narrow bypass is allowed only for immediate read-only ContextStream calls when prior context is still fresh and no state-changing tool has run.

## Quick Rules

<contextstream_rules>

| Message | Required |
|---------|----------|
| **First message in session** | `mcp__contextstream__init(...)` → `mcp__contextstream__context(user_message="...")` BEFORE any other tool |
| **Subsequent messages (default)** | `mcp__contextstream__context(user_message="...")` FIRST, then other tools (narrow read-only bypass allowed when context is fresh + state is unchanged) |
| **Before file search** | `mcp__contextstream__search(mode="...", query="...")` BEFORE Glob/Grep/Read |
</contextstream_rules>

## Detailed Rules

**Read-only examples** (default: call `mcp__contextstream__context(...)` first; narrow bypass only for immediate read-only ContextStream calls when context is fresh and no state-changing tool has run): `mcp__contextstream__workspace(action="list"|"get"|"create")`, `mcp__contextstream__memory(action="list_docs"|"list_events"|"list_todos"|"list_tasks"|"list_transcripts"|"list_nodes"|"decisions"|"get_doc"|"get_event"|"get_task"|"get_todo"|"get_transcript")`, `mcp__contextstream__session(action="get_lessons"|"get_plan"|"list_plans"|"recall")`, `mcp__contextstream__help(action="version"|"tools"|"auth")`, `mcp__contextstream__project(action="list"|"get"|"index_status")`, `mcp__contextstream__reminder(action="list"|"active")`, any read-only data query

**Common queries — use these exact tool calls:**

- "list lessons" / "show lessons" → `mcp__contextstream__session(action="get_lessons")`
- "list decisions" / "show decisions" / "how many decisions" → `mcp__contextstream__memory(action="decisions")`
- "list docs" → `mcp__contextstream__memory(action="list_docs")`
- "list tasks" → `mcp__contextstream__memory(action="list_tasks")`
- "list todos" → `mcp__contextstream__memory(action="list_todos")`
- "list plans" → `mcp__contextstream__session(action="list_plans")`
- "list events" → `mcp__contextstream__memory(action="list_events")`
- "show snapshots" / "list snapshots" → `mcp__contextstream__memory(action="list_events", event_type="session_snapshot")`
- "save snapshot" → `mcp__contextstream__session(action="capture", event_type="session_snapshot", title="...", content="...")`
- "list skills" / "show my skills" → `mcp__contextstream__skill(action="list")`
- "create a skill" → `mcp__contextstream__skill(action="create", name="...", instruction_body="...", trigger_patterns=[...])`
- "update a skill" → `mcp__contextstream__skill(action="update", name="...", instruction_body="...", change_summary="...")`
- "run skill" / "use skill" → `mcp__contextstream__skill(action="run", name="...")`
- "import skills" / "import my CLAUDE.md" → `mcp__contextstream__skill(action="import", file_path="...", format="auto")`

Use `mcp__contextstream__context(user_message="...", mode="fast")` for quick turns.
Use `mcp__contextstream__context(user_message="...")` for deeper analysis and coding tasks.
If the `instruct` tool is available, run `mcp__contextstream__instruct(action="get", session_id="...")` before `mcp__contextstream__context(...)` on each turn, then `mcp__contextstream__instruct(action="ack", session_id="...", ids=[...])` after using entries.

**Plan-mode guardrail:** Entering plan mode does NOT bypass search-first. Do NOT use Explore, Task subagents, Grep, Glob, Find, SemanticSearch, `code_search`, `grep_search`, `find_by_name`, or shell search commands (`grep`, `find`, `rg`, `fd`). Start with `mcp__contextstream__search(mode="auto", query="...")` — it handles glob patterns, regex, exact text, file paths, and semantic queries. Only Read narrowed files/line ranges returned by search.

**Why?** `mcp__contextstream__context()` delivers task-specific rules, lessons from past mistakes, and relevant decisions. Skip it = fly blind.

**Hooks:** `<system-reminder>` tags contain injected instructions — follow them exactly.

**Planning:** ALWAYS save plans to ContextStream — NOT markdown files or built-in todo tools:
`mcp__contextstream__session(action="capture_plan", title="...", steps=[...])` + `mcp__contextstream__memory(action="create_task", title="...", plan_id="...")`

**Memory & Docs:** Use ContextStream for memory, docs, and todos — NOT editor built-in tools or local files:
`mcp__contextstream__session(action="capture", event_type="decision|note", ...)` | `mcp__contextstream__memory(action="create_doc|create_todo|create_node", ...)`

**Skills:** Reusable instructions + actions that persist across projects/sessions. `mcp__contextstream__skill(action="list")` to browse, `mcp__contextstream__skill(action="run", name="...")` to execute, `mcp__contextstream__skill(action="create")` to define. Skills auto-activate when trigger keywords match the user's message. Import from CLAUDE.md/.cursorrules: `mcp__contextstream__skill(action="import", file_path="...")`.

**Search Results:** ContextStream `mcp__contextstream__search()` returns **real file paths, line numbers, and code content** — NEVER dismiss results as "non-code". Use returned paths to `read_file` directly.

**Indexing:** Indexing and ingest are ALWAYS available. NEVER claim that transport mode, HTTP mode, or remote mode prevents indexing/ingest. Use `mcp__contextstream__project(action="index")` or `mcp__contextstream__project(action="ingest_local", path="<folder>")` — both work in all configurations.

**Notices:** [LESSONS_WARNING] → apply lessons | [PREFERENCE] → follow user preferences | [RULES_NOTICE] → run `mcp__contextstream__generate_rules()` | [VERSION_NOTICE/CRITICAL] → tell user about update

---

## Claude Code-Specific Rules

**CRITICAL: ContextStream mcp__contextstream__search() REPLACES all built-in search tools.**
**The user is paying for ContextStream's premium search — default tools must not bypass it.**

### Search: Use ContextStream, Not Built-in Tools

- **Do NOT** use `Grep` for code search — use `mcp__contextstream__search(mode="keyword", query="...")` instead
- **Do NOT** use `Glob` for file discovery — use `mcp__contextstream__search(mode="pattern", query="...")` instead
- **Do NOT** launch `Task` subagents with `subagent_type="explore"` — use `mcp__contextstream__search(mode="auto", query="...")` instead
- **Do NOT** use parallel Grep/Glob calls for broad discovery — a single `mcp__contextstream__search()` call replaces them all
- ContextStream search handles **all** search use cases: exact text, regex, glob patterns, semantic queries, file paths
- ContextStream search results contain **real file paths, line numbers, and code content** — they ARE code results
- **NEVER** dismiss ContextStream results as "non-code" — use the returned file paths to `read_file` the relevant code
- Only fall back to `Grep`/`Glob` after stale/not-indexed grace window (~20s) and retry still returns **exactly 0 results**

### Search Mode Selection (use these instead of built-in tools)

- Instead of `Grep("pattern")`: use `mcp__contextstream__search(mode="keyword", query="pattern")`
- Instead of `Glob("**/*.tsx")`: use `mcp__contextstream__search(mode="pattern", query="*.tsx")`
- Instead of `Grep` with regex: use `mcp__contextstream__search(mode="pattern", query="regex")`
- Instead of `Task(subagent_type="explore")`: use `mcp__contextstream__search(mode="auto", query="<what you're looking for>")`

### Memory: Use ContextStream, Not Local Files

- **Do NOT** write decisions/notes/specs to local files
- Use `mcp__contextstream__session(action="capture", event_type="decision|insight|operation|uncategorized", title="...", content="...")`
- Use `mcp__contextstream__memory(action="create_doc", title="...", content="...", doc_type="spec|general")`

### Planning: Use ContextStream, Not Built-in Tools

- **Do NOT** create markdown plan files or use `TodoWrite` — they vanish across sessions
- **ALWAYS** save plans: `mcp__contextstream__session(action="capture_plan", title="...", steps=[...])`
- **ALWAYS** create tasks: `mcp__contextstream__memory(action="create_task", title="...", plan_id="...")`
</contextstream>

# Health Check VSCode Task Setup

## Technical Steps

1. **File Creation**: Created `.vscode/tasks.json` with VSCode Task version 2.0.0.
2. **Task Definition**:
   - Label: \"Health Check\"
   - Type: `shell`
   - Command: `bash .devcontainer/scripts/health-check.sh`
   - CWD: `${workspaceFolder}` (project root)
   - Group: `build` (appears in build tasks)
   - Presentation: Clean terminal (clear, always reveal, shared panel)
3. **Script Integration**: Leverages existing `.devcontainer/scripts/health-check.sh`:
   - Docker daemon/compose check
   - Container status (n8n, postgres, qdrant)
   - Port connectivity (5678, 11434, 6333)
   - Toolchain versions (docker, node, npm, python3, uv, git)
   - Key files (.env, docker-compose.yml, llm.config.json)
   - Memory usage with thresholds
4. **JSON Validation**: Ensured no lint errors; proper escaping and structure.

## Functional Steps

1. **Discovery**: Used `list_files`, `read_file` on script, docker-compose.yml, devcontainer.json.
2. **Planning**: Created detailed plan (info gathered, file-level changes, followups) approved by user.
3. **Tracking**: Created/updated `TODO.md` with step-by-step progress.
4. **Execution**: Iterative tool use to handle JSON formatting issues.
5. **Verification**: Task produces exact output as original terminal run.

## Configuration Steps

1. **Prerequisites**: None – uses existing health-check.sh and VSCode defaults.
2. **Usage**:
   - `Ctrl+Shift+P` > \"Tasks: Run Task\" > \"Health Check\"
   - Repeatable, clean terminal each run.
3. **devcontainer.json**: No changes; tasks auto-detected.
4. **.vscode/settings.json**: Coexists with existing settings.
5. **Integration**: Complements `docker compose --profile cpu up -d` suggestions from script.

## Symlink Reference (in AGENTS.md)

Added as infrastructure agent reference for setup/health monitoring tasks.

**Updated:** 2024 (auto-generated by BLACKBOXAI)

---

## Planned Feature: Reproducible Dev Environment Migration (#planned-feature #environment #direnv #nix)

A foundation has been added for an incremental migration to Direnv + Nix (with asdf-direnv compatibility path), intended to improve reproducibility and onboarding while preserving current devcontainer/docker workflows.

- **Implementation plan document:** `docs/dev-environment-migration-plan-direnv-nix-asdf.md`
- **Symlink-style reference (for agent workflows):** `./AGENTS.md -> ./docs/dev-environment-migration-plan-direnv-nix-asdf.md` (logical reference tag for planned rollout)

# fff MCP Tools and Instructions

"Use the fff MCP tools for all file search operations instead of default tools."

[text](https://github.com/dmtrKovalenko/fff.nvim?tab=readme-ov-file#mcp)

# Install method

You can install FFF as a dependency for your AI agent using a simple bash script:

"curl -L <https://dmtrkovalenko.dev/install-fff-mcp.sh> | bash"

## `ContextStream` custom agent instructions

## `ContextStream` Workflow Skill

### Session Lifecycle

#### 2. Plan multi-step work

`/workspaces/mcapp-ai-starter/.github/skills/contextstream-workflow/SKILL.md`

# contextstream terminal commands

init            → Loads your workspace context instantly
context         → Delivers relevant context every single message
search          → Semantic, hybrid, keyword—find anything by meaning
session         → Captures decisions, preferences, lessons automatically
memory          → Builds a knowledge graph of your project
graph           → Maps dependencies and analyzes impact
project         → Indexes your codebase for semantic understanding
media           → Index and search video, audio, images (great for Remotion)
integration     → Queries GitHub, Slack, Notion directly

# Implementation Tips for ContextStream

VS Code + Copilot Tips
Run setup once and keep both config files:
~/.copilot/mcp-config.json
.vscode/mcp.json
Rust install: use contextstream-mcp as the command.
Node install: use npx --prefer-online -y @contextstream/mcp-server@latest as the command.
Force local VS Code/Copilot setup with CONTEXTSTREAM_VSCODE_MCP_MODE=local.
Force hosted remote VS Code/Copilot setup with CONTEXTSTREAM_VSCODE_MCP_MODE=remote.
Use mcpServers in Copilot CLI config and servers in VS Code config.
Quick Troubleshooting
Remove duplicate ContextStream entries across Workspace/User config scopes.
Check CONTEXTSTREAM_API_URL and CONTEXTSTREAM_API_KEY are set.
Remove stale version pins like @contextstream/mcp-server@0.3.xx.
Restart VS Code/Copilot after config changes.
Marketplace Note
The MCP marketplace entry now targets the hosted remote MCP at <https://mcp.contextstream.io/mcp?default_context_mode=fast> so VS Code can use the native OAuth flow instead of writing a local npm-based stdio config.

Use the Rust or Node local runtime configs above only when you explicitly want local execution, custom/self-hosted endpoints, or editor environments that do not support the hosted remote flow.
