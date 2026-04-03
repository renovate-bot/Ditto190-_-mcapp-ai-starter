<contextstream>
# Workspace: mcpapp-monorepo
# Workspace ID: e76de4e7-5d4b-40c0-9023-10172088310c

# ContextStream Rules
**MANDATORY STARTUP:** On the first message of EVERY session call `init(...)` then `context(user_message="...")`. On subsequent messages, call `context(user_message="...")` first by default. A narrow bypass is allowed only for immediate read-only ContextStream calls when prior context is still fresh and no state-changing tool has run.

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

### Search Mode Selection:
- `auto` (recommended): query-aware mode selection
- `hybrid`: mixed semantic + keyword retrieval for broad discovery
- `semantic`: conceptual/natural-language questions ("how does auth work?")
- `keyword`: exact text or quoted string
- `pattern`: glob/regex queries (`*.sql`, `foo\s+bar`)
- `refactor`: symbol usage / rename-safe lookup (`UserService`, `snake_case`)
- `exhaustive`: all occurrences / complete match sets
- `team`: cross-project team search

### Output Format Hints:
- `output_format="paths"` for file lists and rename targets
- `output_format="count"` for "how many" queries

### Two-Phase Search Playbook (recommended):
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

### Enable for this chat:
```
context(user_message="<user's message>", save_exchange=true, session_id="<session-id>")
```

### Disable for this chat:
```
context(user_message="<user's message>", save_exchange=false, session_id="<session-id>")
```

### Default policy via MCP config env:
- `CONTEXTSTREAM_TRANSCRIPTS_ENABLED="true|false"`
- `CONTEXTSTREAM_HOOK_TRANSCRIPTS_ENABLED="true|false"`

### Session ID Guidelines:
- Generate ONCE at the start of the conversation
- Use a unique identifier (UUID or timestamp-based)
- Keep the SAME session_id for ALL context() calls
- Different sessions = different transcript preference state

---

## FILE INDEXING (CRITICAL)

**There is NO automatic file indexing in this editor.**
You MUST manage indexing manually:

### After Creating/Editing Files:
```
project(action="index")
```
If folder context is active, this resolves the current repo and uses the local ingest path automatically.

### To Target A Specific Folder Or Recover From Stale Scope:
```
project(action="ingest_local", path="<project_folder>")
```

### Signs You Need to Re-index:
- Search doesn't find code you just wrote
- Search returns old versions of functions
- New files don't appear in search results

---

## SEARCH-FIRST (No PreToolUse Hook)

**There is NO hook to redirect local tools.** You MUST self-enforce:

### Before ANY Search, Check Index Status:
```
project(action="index_status")
```

### Search Protocol:
- **IF indexed & fresh:** `search(mode="auto", query="...")` before local tools
- **IF NOT indexed or stale (>7 days):** wait up to ~20s for background refresh, retry `search(mode="auto", ...)`, then allow local tools only after the grace window elapses
- **IF search returns 0 results after retry/window:** local tools are allowed

### Choose Search Mode Intelligently:
- `auto` (recommended): query-aware mode selection
- `hybrid`: mixed semantic + keyword retrieval for broad discovery
- `semantic`: conceptual questions ("how does X work?")
- `keyword`: exact text / quoted string
- `pattern`: glob or regex (`*.ts`, `foo\s+bar`)
- `refactor`: symbol usage / rename-safe lookup
- `exhaustive`: all occurrences / complete match coverage
- `team`: cross-project team search

### Output Format Hints:
- Use `output_format="paths"` for file listings and rename targets
- Use `output_format="count"` for "how many" queries

### Two-Phase Search Pattern (for precision):
- Pass 1 (discovery): `search(mode="auto", query="<concept + module>", output_format="paths", limit=10)`
- Pass 2 (precision): use one of:
  - exact text/symbol: `search(mode="keyword", query="\"exact_text\"", include_content=true)`
  - symbol usage: `search(mode="refactor", query="SymbolName", output_format="paths")`
  - all occurrences: `search(mode="exhaustive", query="symbol_or_text")`
- Then use local Read/Grep only on paths returned by ContextStream.

### When Local Tools Are OK:
- The stale/not-indexed grace window has elapsed (~20s default, configurable)
- ContextStream search still returns 0 results or errors after retry
- User explicitly requests local tools

---

## CONTEXT COMPACTION (No PreCompact Hook)

**There is NO automatic state saving before compaction.**
You MUST save state manually when the conversation gets long:

### When to Save State:
- After completing a major task
- Before the conversation might be compacted
- If `context()` returns `context_pressure.level: "high"`

### How to Save State:
```
session(action="capture", event_type="session_snapshot",
  title="Session checkpoint",
  content="{ \"summary\": \"what we did\", \"active_files\": [...], \"next_steps\": [...] }")
```

### After Compaction (if context seems lost):
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

### Update Commands:
```bash
# macOS/Linux
curl -fsSL https://contextstream.io/scripts/setup-beta.sh | bash
# npm
npm install -g @contextstream/mcp-server@latest
```

---


---
## VS Code Copilot Notes

- Keep this file concise; put detailed workflows in `.github/skills/contextstream-workflow/SKILL.md`
- Use ContextStream plans/tasks as the persistent record of work
- Before code discovery, use `search(mode="auto", query="...")`

</contextstream>


# Copilot Agent Guide — mcapp-ai-starter

> Trust these instructions first. Only read the codebase when something here is incomplete or appears out of date.
> Before modifying any component subdirectory, read its `AGENTS.md` file — each component has one.

---

## Project at a Glance

Multi-component AI toolkit. Stack: **Python 3.12+** (`uv`), **Node 20+** (`npm`), **Docker Compose**, TypeScript, FastMCP.

| Directory             | Purpose                                                              | Entry file                 |
| --------------------- | -------------------------------------------------------------------- | -------------------------- |
| `src/`                | MCP Apps SDK — TypeScript (App, AppBridge, PostMessageTransport)     | `app.ts`                   |
| `generateagents-mcp/` | FastMCP server exposing GenerateAgents tools to Copilot/Claude       | `server.py`                |
| `examples/`           | SDK example servers — npm workspaces                                 | per-example `package.json` |
| `n8n/`                | Demo workflows + demo data for the Docker stack                      | `demo-data/`               |
| `awesome-copilot/`    | Agent/skill/plugin library                                           | `README.md`                |
| `prompt-registry/`    | VS Code extension for prompt bundle management (TypeScript)          | `package.json`             |
| `GenerateAgents.md/`  | CLI to auto-generate AGENTS.md files (DSPy + LiteLLM)               | `pyproject.toml`           |
| `migration/`          | Scratch space for content from external projects — analysis only     | —                          |

---

## Build & Validate

```bash
# Root SDK (MCP Apps SDK — TypeScript)
npm install
npm run build           # generates schemas + bundles (not examples)
npm run build:all       # SDK + all examples
npm test                # unit tests
npm run test:e2e        # E2E tests (primary coverage; starts examples server automatically)

# Build / type-check a single example
npm run --workspace examples/<example-name> build

# generateagents-mcp (Python)
cd generateagents-mcp && uv sync && uv run python verify.py

# Docker stack (n8n + Ollama + Qdrant + Postgres)
cp .env.example .env    # required — never commit .env
docker compose config -q
docker compose up                      # CPU mode
docker compose up --profile gpu-nvidia # with NVIDIA GPU

# Component checks (CI mirrors)
docker compose config -q                                           # 1. root stack
cd GenerateAgents.md && uv sync --extra dev && uv run pytest -m 'not e2e' -q  # 2. GenerateAgents
cd ../generateagents-mcp && uv sync && uv run python verify.py    # 3. mcp server
cd ../prompt-registry && npm ci && npm run compile && npm run lint # 4. VS Code ext
cd ../awesome-copilot && npm ci && npm run build                   # 5. content library
```

**Caveats:**
- `npm run compile` is the fast smoke test for `prompt-registry`; `npm test` may trigger a VS Code download.
- Use `uv run ...` — `python` may not be on PATH in all environments.
- `npm run test:e2e` has broader coverage than `npm test`; run both before merging SDK changes.

---

## Architecture — MCP Apps SDK (`src/`)

TypeScript SDK enabling MCP servers to display interactive UIs in conversational clients.

**Protocol flow:**
```
View (App) <--PostMessageTransport--> Host (AppBridge) <--MCP Client--> MCP Server
```

1. Host creates iframe; View calls `app.connect()` with `PostMessageTransport`
2. View sends `ui/initialize`; host sends `sendToolInput()` with tool arguments
3. View calls server tools via `app.callServerTool()` or sends messages via `app.sendMessage()`
4. Host calls `teardownResource()` before unmounting

**SDK entry points:**

| Package path                                    | Export                              |
| ----------------------------------------------- | ----------------------------------- |
| `@modelcontextprotocol/ext-apps`                | `App`, `PostMessageTransport`       |
| `@modelcontextprotocol/ext-apps/react`          | `useApp`, `useHostStyles`, etc.     |
| `@modelcontextprotocol/ext-apps/app-bridge`     | `AppBridge`                         |
| `@modelcontextprotocol/ext-apps/server`         | `registerAppTool`, `registerAppResource` |

**Key source files:**
- `src/app.ts` — `App` class (View SDK)
- `src/app-bridge.ts` — `AppBridge` class (Host SDK)
- `src/server/index.ts` — server helpers
- `src/types.ts` — protocol types; `generated/schema.ts` is auto-generated during build (do not edit)
- `src/react/` — React hooks

---

## Architecture — Docker Stack

Services in `docker-compose.yml`: **n8n** (workflow automation), **PostgreSQL 16** (n8n persistence), **Ollama** (local LLM inference, pulls `phi:latest` on startup), **Qdrant** (vector DB, port 6333).

n8n API: use `X-N8N-API-KEY: <key>` header — **not** `Authorization: Bearer`.

```bash
# n8n API examples
curl -H "X-N8N-API-KEY: $N8N_API_KEY" $N8N_HOST/api/v1/workflows
```

---

## CI/CD

| Workflow                            | File                                      | What runs                                               |
| ----------------------------------- | ----------------------------------------- | ------------------------------------------------------- |
| Primary CI                          | `.github/workflows/ci.yml`                | prettier, build, unit tests, Playwright e2e             |
| Component CI                        | `.github/workflows/repo-ci.yml`           | compose-validate, pytest, compile, awesome-copilot build |
| Dependency health                   | `.github/workflows/dependency-health.yml` | npm audit, pip-audit                                    |

PRs must pass `ci.yml` and `repo-ci.yml` before merge. Workflow permissions default to `contents: read` at workflow scope; elevate per-job only when required.

---

## Agent/Prompt File Layout

```
.github/
  agents/       ← *.agent.md — custom agent modes
  instructions/ ← *.instructions.md — file-scoped coding standards
  prompts/      ← *.prompt.md — slash-command prompts
  skills/       ← <name>/SKILL.md — on-demand workflow bundles
  workflows/    ← GitHub Actions CI/CD
```

Naming: **lowercase-hyphen** for all agent/skill/prompt files. Always single-quote `description:` frontmatter values that contain colons.

---

## Conventions

**Secrets:**
- Copy `.env.example` → `.env`, populate locally. Never commit `.env`.
- Generate `N8N_ENCRYPTION_KEY` and `N8N_USER_MANAGEMENT_JWT_SECRET` with `openssl rand -base64 32`.

**TypeScript (SDK / prompt-registry):**
- Strict mode enabled (`tsconfig.json`). Target: ES2020.
- JSDoc `@example` blocks pull from companion `.examples.ts` files (e.g., `app.ts` → `app.examples.ts`).
- Use ` ```ts source="./file.examples.ts#regionName" ` fences for type-checked examples.
- Run `npm run sync:snippets` after updating example regions.
- `basic-server-*` examples are canonical starter templates for new examples.

**Python (generateagents-mcp / GenerateAgents.md):**
- Type hints required on all function signatures. `snake_case` functions, `PascalCase` classes.
- Sanitize all MCP tool responses — never expose API keys.
- Subprocess timeouts for CLI execution: 600–900 s.
- Tests: `@pytest.mark.e2e` for tests that require LLM API keys; CI skips these by default.

**Awesome Copilot content:**
- Lowercase-hyphen filenames; single-quoted YAML frontmatter strings.
- Skill folder name must match the `name` field in `SKILL.md`.

---

## Migration Folder Rules

`migration/` is a **controlled scratch space** for content from external projects.

1. Files here are for analysis only — never import directly into source without an integration plan.
2. Use the `migration-analyst` agent (`.github/agents/migration-analyst.agent.md`) to inventory files.
3. Scan migration files for credentials, workspace IDs, or API keys before referencing them.
4. Integration steps must include passing tests (`npm test` / `uv run pytest`) before moving code to source.

---

## Key References

- [DEVELOPER-QUICKSTART.md](../DEVELOPER-QUICKSTART.md) — one-liner per component
- [QUICKSTART.md](../QUICKSTART.md) — 5-minute setup
- [generateagents-mcp/README.md](../generateagents-mcp/README.md) — MCP tool contracts
- [n8n/AGENTS.md](../n8n/AGENTS.md) — n8n demo data and workflow conventions
- [CLAUDE.md](../CLAUDE.md) / [AGENTS.md](../AGENTS.md) — full architecture reference
- [specification/2026-01-26/apps.mdx](../specification/2026-01-26/apps.mdx) — MCP Apps protocol spec

---

#