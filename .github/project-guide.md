<contextstream>

<!-- BEGIN ContextStream -->
## ContextStream MCP Integration

This project uses [ContextStream](https://contextstream.io) for persistent AI memory across sessions. Use the `contextstream-workflow` skill for detailed examples and reference material.

## 🚨 MANDATORY STARTUP: CONTEXT-FIRST FLOW 🚨

<contextstream_rules>
| Message | What to Call |
|---------|--------------|
| **First message in session** | `init()` → `context(user_message="<msg>")` BEFORE any other tool |
| **Subsequent messages (default)** | `context(user_message="<msg>")` FIRST, then other tools |
| **Narrow bypass** | Immediate read-only ContextStream calls are allowed only when prior context is fresh and no state-changing tool has run |
| **Before Glob/Grep/Read/Search/Explore/Task/EnterPlanMode** | `search(mode="auto", query="...")` FIRST |
</contextstream_rules>

Use `context()` by default to get task-specific rules, lessons from past mistakes, and relevant decisions.

---

## Why Default Context-First

❌ **Wrong:** "I already called init, so I can skip context for everything"
✅ **Correct:** `context()` is the default first call for subsequent messages, with a narrow read-only bypass when context is still fresh and state is unchanged

**What you lose without `context()`:**
- Dynamic rules matched to your current task
- Lessons from past mistakes (you WILL repeat them)
- Semantically relevant decisions and context
- Warnings about risky operations

**`init()` returns recent items by time. `context()` finds items semantically relevant to this message.**

---

## Handle Notices from context()

- **[LESSONS_WARNING]** → Tell user about past mistakes BEFORE proceeding
- **[PREFERENCE]** → Follow user preferences (high-priority user memories)
- **[RULES_NOTICE]** → Run `generate_rules()` to update
- **[VERSION_NOTICE]** → Tell user to update MCP

---

## 🚨 HOOKS - AUTOMATIC RULE ENFORCEMENT 🚨

**ContextStream installs hooks that automatically enforce rules.** You MUST follow hook output.

### Installed Hooks

| Hook | What It Does | Output |
|------|--------------|--------|
| **UserPromptSubmit** | Injects rules reminder on EVERY message | `<system-reminder>` with rules block |
| **PreToolUse** | Blocks Glob/Grep/Search/Explore when ContextStream is available | Error message redirecting to `search()` |
| **PostToolUse** | Auto-indexes files after Edit/Write operations | Background indexing |
| **PreCompact** | Saves session state before context compaction | Snapshot creation |

### How Hooks Work

1. **`<system-reminder>` tags** - Injected by UserPromptSubmit hook on every message
   - These tags contain the current rules
   - **FOLLOW THE INSTRUCTIONS INSIDE** - they ARE the rules
   - Example: `[CONTEXTSTREAM RULES] 1. BEFORE Glob/Grep... [END RULES]`

2. **PreToolUse blocking** - If you try to use Glob/Grep/Search/Explore:
   - Hook returns error: `STOP: Use mcp__contextstream__search(mode="auto") instead`
   - **You MUST use the suggested ContextStream tool instead**
   - Local tools are only allowed if project is not indexed or ContextStream returns 0 results

3. **PostToolUse indexing** - After Edit/Write operations:
   - Changed files are automatically re-indexed
   - No action required from you

4. **PreCompact snapshots** - Before context compaction:
   - Hook reminds you to save important state
   - Call `session(action="capture", event_type="session_snapshot", ...)` when warned

### Disabling Hooks

Set environment variable: `CONTEXTSTREAM_HOOK_ENABLED=false`

**Note:** Disabling hooks removes rule enforcement. Only disable for debugging.

---

## 🚨 CRITICAL RULE #1 - CONTEXTSTREAM SEARCH FIRST 🚨

**BEFORE using Glob, Grep, Search, Read (for discovery), Explore, Task(Explore), EnterPlanMode, or ANY local file scanning:**
```
STOP → Call search(mode="auto", query="...") FIRST
```

**Note:** PreToolUse hooks block these tools when ContextStream is available.
**Claude Code users:** Your tool names are `mcp__contextstream__search`, `mcp__contextstream__init`, etc.

❌ **NEVER DO THIS:**
- `Glob("**/*.ts")` → Use `search(mode="pattern", query="*.ts")` instead
- `Grep("functionName")` → Use `search(mode="keyword", query="functionName")` instead
- `Read(file)` for discovery → Use `search(mode="auto", query="...")` instead
- `Explore` or `Task(subagent_type="Explore")` → Use `search(mode="auto")` instead
- `EnterPlanMode` for discovery → Use `search(mode="auto", output_format="paths")` instead

✅ **ALWAYS DO THIS:**
1. `search(mode="auto", query="what you're looking for")`
2. Only use local tools (Glob/Grep/Read) if ContextStream returns **0 results**
3. Use Read ONLY for exact file edits after you know the file path

This applies to **EVERY search** throughout the **ENTIRE conversation**, not just the first message.

---

## 🚨 CRITICAL RULE #2 - AUTO-INDEXING 🚨

**ContextStream auto-indexes your project on `init`.** You do NOT need to:
- Ask the user to index
- Manually trigger ingestion
- Check index_status before every search

**When `init` returns `indexing_status: "started"` or `"refreshing"`:**
- Background indexing is running automatically
- Search results will be available within seconds to minutes
- **DO NOT fall back to local tools** - wait for ContextStream search to work
- If search returns 0 results initially, try again after a moment

**Only manually trigger indexing if:**
- `init` returned `ingest_recommendation.recommended: true` (rare edge case)
- User explicitly asks to re-index

---

## 🚨 CRITICAL RULE #3 - LESSONS (PAST MISTAKES) 🚨

**Lessons are past mistakes that MUST inform your work.** Ignoring lessons leads to repeated failures.

### On `init`:
- Check for `lessons` and `lessons_warning` in the response
- If present, **READ THEM IMMEDIATELY** before doing any work
- These are high-priority lessons (critical/high severity) relevant to your context
- **Apply the prevention steps** from each lesson to avoid repeating mistakes

### On `context`:
- Check for `[LESSONS_WARNING]` tag in the response
- If present, you **MUST** tell the user about the lessons before proceeding
- Lessons are proactively fetched when risky actions are detected (refactor, migrate, deploy, etc.)
- **Do not skip or bury this warning** - lessons represent real past mistakes

### Before ANY Non-Trivial Work:
**ALWAYS call `session(action="get_lessons", query="<topic>")`** where `<topic>` matches what you're about to do:
- Before refactoring → `session(action="get_lessons", query="refactoring")`
- Before API changes → `session(action="get_lessons", query="API changes")`
- Before database work → `session(action="get_lessons", query="database migrations")`
- Before deployments → `session(action="get_lessons", query="deployment")`

### When Lessons Are Found:
1. **Summarize the lessons** to the user before proceeding
2. **Explicitly state how you will avoid the past mistakes**
3. If a lesson conflicts with the current approach, **warn the user**

**Failing to check lessons before risky work is a critical error.**

---

## ContextStream v0.4.x Integration (Enhanced)

You have access to ContextStream MCP tools for persistent memory and context.
v0.4.x uses **~11 consolidated domain tools** for ~75% token reduction vs previous versions.
Rules Version: 0.4.68

## TL;DR - CONTEXT EVERY MESSAGE

| Message | Required |
|---------|----------|
| **1st message** | `init()` → `context(user_message="<msg>")` |
| **EVERY message after** | `context(user_message="<msg>")` **FIRST** |
| **Before file search** | `search(mode="auto")` FIRST |
| **After significant work** | `session(action="capture", event_type="decision", ...)` |
| **User correction** | `session(action="capture_lesson", ...)` |

### Why EVERY Message?

`context()` delivers:
- **Dynamic rules** matched to your current task
- **Lessons** from past mistakes (prevents repeating errors)
- **Relevant decisions** and context (semantic search)
- **Warnings** about risky operations

**Without `context()`, you are blind to relevant context and will repeat past mistakes.**

### Protocol

| Step | What to Call |
|------|--------------|
| **1st message** | `init(folder_path="...", context_hint="<msg>")`, then `context(...)` |
| **2nd+ messages** | `context(user_message="<msg>", format="minified", max_tokens=400)` |
| **Code search** | `search(mode="auto", query="...")` — BEFORE Glob/Grep/Read |
| **After significant work** | `session(action="capture", event_type="decision", ...)` |
| **User correction** | `session(action="capture_lesson", ...)` |
| **⚠️ When warnings received** | **STOP**, acknowledge, explain mitigation, then proceed |

**First message rule:** After `init`:
1. Check for `lessons` in response - if present, READ and SUMMARIZE them to user
2. Then call `context` before any other tool or response

**Context Pack (Pro+):** If enabled, use `context(..., mode="pack", distill=true)` for code/file queries. If unavailable or disabled, omit `mode` and proceed with standard `context` (the API will fall back).

**Tool naming:** Use the exact tool names exposed by your MCP client. Claude Code typically uses `mcp__<server>__<tool>` where `<server>` matches your MCP config (often `contextstream`). If a tool call fails with "No such tool available", refresh rules and match the tool list.

---

## Consolidated Domain Tools Architecture

v0.4.x consolidates ~58 individual tools into ~11 domain tools with action/mode dispatch:

### Standalone Tools
- **`init`** - Initialize session with workspace detection + context (skip for simple utility operations)
- **`context`** - Semantic search for relevant context (skip for simple utility operations)

### Domain Tools (Use action/mode parameter)

| Domain | Actions/Modes | Example |
|--------|---------------|---------|
| **`search`** | mode: auto (recommended), semantic, hybrid (legacy alias), keyword, pattern | `search(mode="auto", query="auth implementation", limit=3)` |
| **`session`** | action: capture, capture_lesson, get_lessons, recall, remember, user_context, summary, compress, delta, smart_search, decision_trace | `session(action="capture", event_type="decision", title="Use JWT", content="...")` |
| **`memory`** | action: create_event, get_event, update_event, delete_event, list_events, distill_event, create_node, get_node, update_node, delete_node, list_nodes, supersede_node, search, decisions, timeline, summary | `memory(action="list_events", limit=10)` |
| **`graph`** | action: dependencies, impact, call_path, related, path, decisions, ingest, circular_dependencies, unused_code, contradictions | `graph(action="impact", symbol_name="AuthService")` |
| **`project`** | action: list, get, create, update, index, overview, statistics, files, index_status, ingest_local | `project(action="statistics")` |
| **`workspace`** | action: list, get, associate, bootstrap | `workspace(action="list")` |
| **`reminder`** | action: list, active, create, snooze, complete, dismiss | `reminder(action="active")` |
| **`integration`** | provider: slack/github/all; action: status, search, stats, activity, contributors, knowledge, summary, channels, discussions, sync_users, repos, issues | `integration(provider="github", action="search", query="...")` |
| **`help`** | action: tools, auth, version, editor_rules, enable_bundle | `help(action="tools")` |

---

### Why context is Required (Even After init)

**Common mistake:** "init already gave me context, I don't need context"

**This is WRONG. Here's why:**
- `init` returns the last ~10 items **BY TIME** (chronological)
- `context` **SEARCHES** for items **RELEVANT to THIS message** (semantic)

**Example failure:**
- User asks: "how should I implement authentication?"
- Auth decisions were made 20 conversations ago
- `init` won't have it (too old, not in recent 10)
- `context` FINDS it via semantic search

**Without context, you WILL miss relevant older context.**

---

### Recommended Token Budgets

- For trivial/local edits: `context(..., max_tokens=200)`
- Default: `context(..., max_tokens=400)`
- Deep debugging/architecture: `context(..., max_tokens=800)`
- Keep `format="minified"` (default) unless debugging

If context still feels missing, use `session(action="recall", query="...")` for focused deep lookup.

---

### Rules, Version & Lessons Notices

**[RULES_NOTICE]** - Update rules via `generate_rules()` (or rerun setup).

**[VERSION_NOTICE]** or **[VERSION_CRITICAL]** - You **MUST** tell the user (be helpful, not annoying):
  1. A new MCP server version is available with improvements
  2. Provide update commands (user chooses preferred method):
     - macOS/Linux: `curl -fsSL https://contextstream.io/scripts/setup.sh | bash`
     - Windows: `irm https://contextstream.io/scripts/setup.ps1 | iex`
     - npm: `npm install -g @contextstream/mcp-server@latest`
  3. Restart AI tool after updating
  **Mention once** - don't nag. Users often miss stderr warnings so this helps.

**[LESSONS_WARNING]** - You **MUST** before proceeding:
  1. Read all lessons listed
  2. Tell the user about relevant lessons
  3. Explain how you will avoid each past mistake
  **This is critical** - ignoring lessons leads to repeated failures.

---

### Preferences & Lessons (Use Early)

**Preferences ([PREFERENCE] in context response):**
- High-priority user memories that should guide your behavior
- Surfaced automatically via `context()` warnings field
- To save: `session(action="remember", content="...")`
- To retrieve explicitly: `session(action="user_context")`

**Lessons ([LESSONS_WARNING] in context response):**
- Past mistakes to avoid - apply prevention steps
- Surfaced automatically via `context()` warnings field
- Before risky changes: `session(action="get_lessons", query="<topic>")`
- On mistakes: `session(action="capture_lesson", title="...", trigger="...", impact="...", prevention="...")`

---

### Context Pressure & Compaction Awareness

ContextStream tracks context pressure to help you stay ahead of conversation compaction:

**Automatic tracking:** Token usage is tracked automatically. `context` returns `context_pressure` when usage is high.

**When `context` returns `context_pressure` with high/critical level:**
1. Review the `suggested_action` field:
   - `prepare_save`: Start thinking about saving important state
   - `save_now`: Immediately call `session(action="capture", event_type="session_snapshot")` to preserve state

**PreCompact Hook:** Automatically saves session state before context compaction.
Installed by default. Disable with: `CONTEXTSTREAM_HOOK_ENABLED=false`

**Before compaction happens (when warned):**
```
session(action="capture", event_type="session_snapshot", title="Pre-compaction snapshot", content="{
  \"conversation_summary\": \"<summarize what we've been doing>\",
  \"current_goal\": \"<the main task>\",
  \"active_files\": [\"file1.ts\", \"file2.ts\"],
  \"recent_decisions\": [{title: \"...\", rationale: \"...\"}],
  \"unfinished_work\": [{task: \"...\", status: \"...\", next_steps: \"...\"}]
}")
```

**After compaction (when context seems lost):**
1. Call `init(folder_path="...", is_post_compact=true)` - this auto-restores the most recent snapshot
2. Or call `session_restore_context()` directly to get the saved state
3. Review the `restored_context` to understand prior work
4. Acknowledge to the user what was restored and continue

---

### Index Status (Auto-Managed)

**Indexing is automatic.** After `init`, the project is auto-indexed in the background.

**You do NOT need to manually check index_status before every search.** Just use `search()`.

**If search returns 0 results and you expected matches:**
1. Check if `init` returned `indexing_status: "started"` - indexing may still be in progress
2. Wait a moment and retry `search()`
3. Only as a last resort: `project(action="index_status")` to check

**Graph data:** If graph queries (`dependencies`, `impact`) return empty, run `graph(action="ingest")` once.

**NEVER fall back to local tools (Glob/Grep/Read) just because search returned 0 results on first try.** Retry first.

### Enhanced Context (Server-Side Warnings)

`context` now includes **intelligent server-side filtering** that proactively surfaces relevant warnings:

**Response fields:**
- `warnings`: Array of warning strings (displayed with ⚠️ prefix)

**What triggers warnings:**
- **Lessons**: Past mistakes relevant to the current query (via semantic matching)
- **Risky actions**: Detected high-risk operations (deployments, migrations, destructive commands)
- **Breaking changes**: When modifications may impact other parts of the codebase

**When you receive warnings:**
1. **STOP** and read each warning carefully
2. **Acknowledge** the warning to the user
3. **Explain** how you will avoid the issue
4. Only proceed after addressing the warnings

### Search & Code Intelligence (ContextStream-first)

⚠️ **STOP: Before using Search/Glob/Grep/Read/Explore** → Call `search(mode="auto")` FIRST. Use local tools ONLY if ContextStream returns 0 results.

**❌ WRONG workflow (wastes tokens, slow):**
```
Grep "function" → Read file1.ts → Read file2.ts → Read file3.ts → finally understand
```

**✅ CORRECT workflow (fast, complete):**
```
search(mode="auto", query="function implementation") → done (results include context)
```

**Why?** ContextStream search returns semantic matches + context + file locations in ONE call. Local tools require multiple round-trips.

**Search order:**
1. `session(action="smart_search", query="...")` - context-enriched
2. `search(mode="auto", query="...", limit=3)` or `search(mode="keyword", query="<filename>", limit=3)`
3. `project(action="files")` - file tree/list (only when needed)
4. `graph(action="dependencies", ...)` - code structure
5. Local repo scans (rg/ls/find) - ONLY if ContextStream returns no results, errors, or the user explicitly asks

**Search Mode Selection:**

| Need | Mode | Example |
|------|------|---------|
| Find code by meaning | `auto` | "authentication logic", "error handling" |
| Exact string/symbol | `keyword` | "UserAuthService", "API_KEY" |
| File patterns | `pattern` | "*.sql", "test_*.py" |
| ALL matches (grep-like) | `exhaustive` | "TODO", "FIXME" (find all occurrences) |
| Symbol renaming | `refactor` | "oldFunctionName" (word-boundary matching) |
| Conceptual search | `semantic` | "how does caching work" |

**Token Efficiency:** Use `output_format` to reduce response size:
- `full` (default): Full content for understanding code
- `paths`: File paths only (80% token savings) - use for file listings
- `minimal`: Compact format (60% savings) - use for refactoring
- `count`: Match counts only (90% savings) - use for quick checks

**When to use `output_format=count`:**
- User asks "how many X" or "count of X" → `search(..., output_format="count")`
- Checking if something exists → count > 0 is sufficient
- Large exhaustive searches → get count first, then fetch if needed

**Auto-suggested formats:** Search responses include `query_interpretation.suggested_output_format` when the API detects an optimal format:
- Symbol queries (e.g., "authOptions") → suggests `minimal` (path + line + snippet)
- Count queries (e.g., "how many") → suggests `count`
**USE the suggested format** on subsequent searches for best token efficiency.

**Search defaults:** `search` returns the top 3 results with compact snippets. Use `limit` + `offset` for pagination, and `content_max_chars` to expand snippets when needed.

If ContextStream returns results, stop and use them. NEVER use local Search/Explore/Read unless you need exact code edits or ContextStream returned 0 results.

**Code Analysis:**
- Dependencies: `graph(action="dependencies", file_path="...")`
- Change impact: `graph(action="impact", symbol_name="...")`
- Call path: `graph(action="call_path", from_symbol="...", to_symbol="...")`
- Build graph: `graph(action="ingest")` - async, can take a few minutes

---

### Distillation & Memory Hygiene

- Quick context: `session(action="summary")`
- Long chat: `session(action="compress", content="...")`
- Memory summary: `memory(action="summary")`
- Condense noisy entries: `memory(action="distill_event", event_id="...")`

---

### When to Capture

| When | Call | Example |
|------|------|---------|
| User makes decision | `session(action="capture", event_type="decision", ...)` | "Let's use PostgreSQL" |
| User states preference | `session(action="capture", event_type="preference", ...)` | "I prefer TypeScript" |
| Complete significant task | `session(action="capture", event_type="task", ...)` | Capture what was done |
| Need past context | `session(action="recall", query="...")` | "What did we decide about X?" |

**DO NOT capture utility operations:**
- ❌ "Listed workspaces" - not meaningful context
- ❌ "Showed version" - not a decision
- ❌ "Listed projects" - just data retrieval

**DO capture meaningful work:**
- ✅ Decisions, preferences, completed features
- ✅ Lessons from mistakes
- ✅ Insights about architecture or patterns

---

### 🚨 Plans & Tasks - USE CONTEXTSTREAM, NOT FILE-BASED PLANS 🚨

**CRITICAL: When the user requests planning, implementation plans, roadmaps, task breakdowns, or step-by-step approaches:**

❌ **DO NOT** use built-in plan mode (EnterPlanMode tool)
❌ **DO NOT** write plans to markdown files or plan documents
❌ **DO NOT** ask "should I create a plan file?"
❌ **DO NOT** use `Explore` / `Task(subagent_type="Explore")` to read files one-by-one while planning

✅ **ALWAYS** use ContextStream's plan/task system instead
✅ **ALWAYS** use `search(mode="auto", output_format="paths")` for planning discovery before targeted reads

**Trigger phrases to detect (use ContextStream immediately):**
- "create a plan", "make a plan", "plan this", "plan for"
- "implementation plan", "roadmap", "milestones"
- "break down", "breakdown", "break this into steps"
- "what are the steps", "step by step", "outline the approach"
- "task list", "todo list", "action items"
- "how should we approach", "implementation strategy"

**When detected, immediately:**

1. **Create the plan in ContextStream:**
```
session(action="capture_plan", title="<descriptive title>", description="<what this plan accomplishes>", goals=["goal1", "goal2"], steps=[{id: "1", title: "Step 1", order: 1, description: "..."}, ...])
```

2. **Create tasks for each step:**
```
memory(action="create_task", title="<task title>", plan_id="<plan_id from step 1>", priority="high|medium|low", description="<detailed task description>")
```

**Why ContextStream plans are better:**
- Plans persist across sessions and are searchable
- Tasks track status (pending/in_progress/completed/blocked)
- Context is preserved with workspace/project association
- Can be retrieved with `session(action="get_plan", plan_id="...", include_tasks=true)`
- Future sessions can continue from where you left off

**Managing plans/tasks:**
- List plans: `session(action="list_plans")`
- Get plan with tasks: `session(action="get_plan", plan_id="<uuid>", include_tasks=true)`
- List tasks: `memory(action="list_tasks", plan_id="<uuid>")` or `memory(action="list_tasks")` for all
- Update task status: `memory(action="update_task", task_id="<uuid>", task_status="pending|in_progress|completed|blocked")`
- Link task to plan: `memory(action="update_task", task_id="<uuid>", plan_id="<plan_uuid>")`
- Unlink task from plan: `memory(action="update_task", task_id="<uuid>", plan_id=null)`
- Delete: `memory(action="delete_task", task_id="<uuid>")` or `memory(action="delete_event", event_id="<plan_uuid>")`

---

### Complete Action Reference

**session actions:**
- `capture` - Save decision/insight/task (requires: event_type, title, content)
- `capture_lesson` - Save lesson from mistake (requires: title, category, trigger, impact, prevention)
- `get_lessons` - Retrieve relevant lessons (optional: query, category, severity)
- `recall` - Natural language memory recall (requires: query)
- `remember` - Quick save to memory (requires: content)
- `user_context` - Get user preferences/style
- `summary` - Workspace summary
- `compress` - Compress long conversation
- `delta` - Changes since timestamp
- `smart_search` - Context-enriched search
- `decision_trace` - Trace decision provenance

**memory actions:**
- Event CRUD: `create_event`, `get_event`, `update_event`, `delete_event`, `list_events`, `distill_event`
- Node CRUD: `create_node`, `get_node`, `update_node`, `delete_node`, `list_nodes`, `supersede_node`
- Query: `search`, `decisions`, `timeline`, `summary`

**graph actions:**
- Analysis: `dependencies`, `impact`, `call_path`, `related`, `path`
- Quality: `circular_dependencies`, `unused_code`, `contradictions`
- Management: `ingest`, `decisions`

See full documentation: https://contextstream.io/docs/mcp/tools

### VS Code Copilot Notes

- Keep this file concise; put detailed workflows in `.github/skills/contextstream-workflow/SKILL.md`
- Use ContextStream plans/tasks as the persistent record of work
- Before code discovery, use `search(mode="auto", query="...")`

Full docs: https://contextstream.io/docs/mcp/tools


---
## ⚠️ IMPORTANT: No Hooks Available ⚠️

**This editor does NOT have hooks to enforce ContextStream behavior.**
You MUST follow these rules manually - there is no automatic enforcement.

---

## 🚀 SESSION START PROTOCOL

**On EVERY new session, you MUST:**

1. **Call `init(folder_path="<project_path>")`** FIRST
   - This triggers project indexing
   - Check response for `indexing_status`
   - If `"started"` or `"refreshing"`: wait before searching

2. **Generate a unique session_id** (e.g., `"session-" + timestamp` or a UUID)
   - Use this SAME session_id for ALL context() calls in this conversation
   - This groups all turns together in the transcript

3. **Call `context(user_message="<first_message>", save_exchange=true, session_id="<your-session-id>")`**
   - Gets task-specific rules, lessons, and preferences
   - Check for [LESSONS_WARNING] - past mistakes to avoid
   - Check for [PREFERENCE] - user preferences to follow
   - Check for [RULES_NOTICE] - update rules if needed
   - **save_exchange=true** saves each conversation turn for later retrieval

4. **Default behavior:** call `context(...)` first on each message. Narrow bypass is allowed only for immediate read-only ContextStream calls when previous context is still fresh and no state-changing tool has run.

---

## 💾 AUTOMATIC TRANSCRIPT SAVING (CRITICAL)

**This editor does NOT have hooks to auto-save transcripts.**
You MUST save each conversation turn manually:

### On MOST messages (including the first):
```
context(user_message="<user's message>", save_exchange=true, session_id="<session-id>")
```

### Why save_exchange matters:
- Transcripts enable searching past conversations
- Allows context restoration after compaction
- Provides conversation history for debugging
- Required for the Transcripts page in the dashboard

### Session ID Guidelines:
- Generate ONCE at the start of the conversation
- Use a unique identifier: `"session-" + Date.now()` or a UUID
- Keep the SAME session_id for ALL context() calls in this session
- Different sessions = different transcripts

---

## 📁 FILE INDEXING (CRITICAL)

**There is NO automatic file indexing in this editor.**
You MUST manage indexing manually:

### After Creating/Editing Files:
```
project(action="index")  # Re-index entire project
```

### For Single File Updates:
```
project(action="ingest_local", path="<file_path>")
```

### Signs You Need to Re-index:
- Search doesn't find code you just wrote
- Search returns old versions of functions
- New files don't appear in search results

### Best Practice:
After completing a feature or making multiple file changes, ALWAYS run:
```
project(action="index")
```

---

## 🔍 SEARCH-FIRST (No PreToolUse Hook)

**There is NO hook to block local tools (Glob/Grep/Read/Explore/Task/EnterPlanMode).** You MUST self-enforce:

### Before ANY Search, Check Index Status:
```
project(action="index_status")
```

This tells you:
- `indexed`: true/false - is project indexed?
- `last_indexed_at`: timestamp - when was it last indexed?
- `file_count`: number - how many files indexed?

### Search Protocol:

**IF project is indexed and fresh:**
```
search(mode="auto", query="what you're looking for")
```
→ Use this instead of Explore/Task/EnterPlanMode for file discovery.

**IF project is NOT indexed or very stale (>7 days):**
→ Use local tools (Glob/Grep/Read) directly
→ OR run `project(action="index")` first, then search

**IF ContextStream search returns 0 results or errors:**
→ Use local tools (Glob/Grep/Read) as fallback

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
✅ Project is not indexed
✅ Index is stale/outdated (>7 days old)
✅ ContextStream search returns 0 results
✅ ContextStream returns errors
✅ User explicitly requests local tools

### When to Use ContextStream Search:
✅ Project is indexed and fresh
✅ Looking for code by meaning/concept
✅ Need semantic understanding

---

## 💾 CONTEXT COMPACTION (No PreCompact Hook)

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
This restores the most recent snapshot.

---

## 📋 PLANS & TASKS (No EnterPlanMode)

**Always use ContextStream for planning:**

```
session(action="capture_plan", title="...", steps=[...])
memory(action="create_task", title="...", plan_id="...")
```

❌ DO NOT use built-in plan mode (`EnterPlanMode`) or `Task(subagent_type="Explore")` for file-by-file scans.
✅ For planning discovery, use `search(mode="auto", query="...", output_format="paths")` then read only narrowed files.

---

## 🔄 VERSION UPDATES (Check Periodically)

**This editor does NOT have hooks to check for updates automatically.**
You should check for updates using `help(action="version")` periodically (e.g., at session start).

### If the response includes [VERSION_NOTICE] or [VERSION_CRITICAL]:

**Tell the user** about the available update in a helpful, non-annoying way:
- Frame it as "new features and improvements available"
- Provide the update commands (user can choose their preferred method)
- Don't nag repeatedly - mention once, then only if user asks

### Update Commands (provide all options):

**macOS/Linux:**
```bash
curl -fsSL https://contextstream.io/scripts/setup.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://contextstream.io/scripts/setup.ps1 | iex
```

**npm (requires Node.js 18+):**
```bash
npm install -g @contextstream/mcp-server@latest
```

After updating, user should restart their AI tool.

---
<!-- END ContextStream -->

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
