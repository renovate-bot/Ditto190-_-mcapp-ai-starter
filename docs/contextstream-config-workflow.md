# ContextStream Configuration & Workflow Setup

## Environment Configuration

Based on `contextstream-mcp --help` and lessons learned from PATH debugging.

### Recommended .env or MCP Client Configuration

```bash
# ─ API & Auth ─────────────────────────────────
export CONTEXTSTREAM_API_URL="https://api.contextstream.io"
export CONTEXTSTREAM_API_KEY="<your-key-here>"  # Get from https://contextstream.io/settings

# ─ Workspace & Project ────────────────────────
export CONTEXTSTREAM_WORKSPACE_ID="<your-workspace-id>"  # Optional
export CONTEXTSTREAM_PROJECT_ID="<your-project-id>"      # Optional

# ─ Tool Configuration (Performance) ───────────
# Lesson: Need diverse tools for multi-agent analysis
export CONTEXTSTREAM_TOOLSET="standard"         # balanced set
export CONTEXTSTREAM_AUTO_TOOLSET="true"        # auto-detect client needs
export CONTEXTSTREAM_SCHEMA_MODE="compact"      # reduce tokens
export CONTEXTSTREAM_OUTPUT_FORMAT="compact"    # minimize verbosity
export CONTEXTSTREAM_PROGRESSIVE_MODE="false"   # Don't start minimal

# ─ Search & Context ───────────────────────────
# Lesson: Lessons are text-heavy, need good search recall
export CONTEXTSTREAM_SEARCH_LIMIT="5"           # Good balance
export CONTEXTSTREAM_SEARCH_MAX_CHARS="600"     # Include full context
export CONTEXTSTREAM_CONTEXT_PACK="true"        # Enable Context Pack

# ─ HTTP Gateway (Optional) ─────────────────────
export MCP_HTTP_HOST="0.0.0.0"
export MCP_HTTP_PORT="8787"
export MCP_HTTP_REQUIRE_AUTH="true"

# ─ Integration (Upstash Context7) ──────────────
export UPSTASH_CONTEXT_URL="<your-upstash-context-url>"
export UPSTASH_CONTEXT_TOKEN="<your-token>"
```

### VS Code / Cursor / Cline Configuration

Add to `.vscode/settings.json` (to register MCP server):

```json
{
  "copilot.advanced": {
    "debug.testingEnabled": true
  },
  "[copilot].mcp": {
    "servers": [
      {
        "name": "contextstream-mcp",
        "description": "ContextStream MCP with lesson-learning integration",
        "command": "bash",
        "args": ["-lc", "export $(cat .env | xargs) && contextstream-mcp"],
        "env": {
          "CONTEXTSTREAM_TOOLSET": "standard",
          "CONTEXTSTREAM_SCHEMA_MODE": "compact",
          "CONTEXTSTREAM_OUTPUT_FORMAT": "compact"
        },
        "disabled": false
      }
    ]
  }
}
```

---

## ContextStream Session Lifecycle

### Phase 1: Session Initialization

```javascript
// First message of session
mcp_contextstream_init(
  folder_path="/workspaces/mcapp-ai-starter",
  context_hint="User is testing ContextStream workflow with lesson-learning"
)

// Then immediately call context
mcp_contextstream_context(
  user_message="<current task>",
  save_exchange=true,
  session_id="vim-contextstream-design-2026-04-04"
)
```

**Result**: Gets task-specific rules, relevant lessons from past mistakes, preferences

### Phase 2: Capture Initial Context

```javascript
// Document the problem or task
session(
  action="capture",
  event_type="note",
  title="Starting ContextStream workflow test",
  content="Goal: Validate lesson-learning framework with multi-agent feedback",
  importance="high"
)
```

### Phase 3: Design & Analysis Phase

```javascript
// Capture design decisions
session(
  action="capture",
  event_type="decision",
  title="Use 3-agent validation (prompt-eng, self-critic, reflection-learner)",
  content="Multi-perspective feedback ensures lessons are complete and generalizable"
)

// Create task for tracking work
memory(
  action="create_task",
  title="Test ContextStream lesson-learning with PATH issue",
  description="Validate that the 5-checkpoint lesson-learning model works",
  priority="high"
)
```

### Phase 4: Execute Work

```javascript
// Mark task in progress
memory(
  action="update_task",
  task_id="<task_id>",
  status="in_progress"
)

// Make changes, run tests, etc...
```

### Phase 5: Capture Lesson from Work

```javascript
// When a lesson is learned, capture it
session(
  action="capture_lesson",
  title="npm globals require NVM sourcing in shell startup",
  trigger="contextstream-mcp: command not found",
  impact="Global CLIs inaccessible; automation blocked",
  prevention="Verify .bashrc/.zshrc sources NVM. Test: bash -l -c 'tool --version'",
  severity="high",
  keywords=["shell", "NVM", "PATH", "startup", "interactive-shell"],
  category="environment"
)
```

### Phase 6: Multi-Agent Validation

```javascript
// Request feedback from specialized agents
// (Use runSubagent for each agent - don't ask them to read files)

// Agent 1: Prompt Engineer - Validate phrasing
// Agent 2: Self-Critic - Identify gaps  
// Agent 3: Reflection-Learner - Extract patterns

// After feedback, update lesson with improvements
```

### Phase 7: Store in Persistent Context

```javascript
// Save lesson to Upstash Context7 for cross-session retrieval
context7_api.put({
  key: "lesson-nvm-shell-initialization",
  type: "lesson",
  content: {
    title: "npm/contextstream-mcp: command not found — NVM not sourced",
    trigger: "Tool not found despite global install",
    prevention: "...",
    pattern: "runtime-manager-initialization-gap"
  },
  ttl: 2592000,  // 30 days
  tags: ["shell", "NVM", "PATH", "startup"]
})
```

### Phase 8: Complete Task & Plan

```javascript
// Mark work complete
memory(
  action="update_task",
  task_id="<task_id>",
  status="completed"
)

// Optionally update plan 
session(
  action="update_plan",
  plan_id="<original-plan-id>",
  status="completed"
)

// Capture final summary
session(
  action="capture",
  event_type="session_snapshot",
  title="ContextStream workflow test completed",
  content={
    "lessons_learned": 1,
    "agents_validated": 3,
    "pattern_extracted": true,
    "all_checkpoints_passed": true
  }
)
```

---

## Lesson-Learning Validation Checkpoints

### 5-Point Validation Model

| Checkpoint | What to Check | How to Verify | Pass/Fail |
|---|---|---|---|
| **1. Problem Identified** | Error/issue is clear and reproducible | Can describe the error exactly | ✅ |
| **2. Root Cause Diagnosed** | Traced to underlying cause | Root cause is specific, not "configuration issue" | ✅ |
| **3. Fix Implemented & Tested** | Solution works and is verified | Tests pass; before/after diff shows fix | ✅ |
| **4. Prevention Captured** | Rule to prevent recurrence | Prevention rule is actionable and specific | ✅ |
| **5. Pattern Generalized** | Lesson applies beyond specific issue | Can name similar problems pattern solves | ✅ |

### Checkpoints in ContextStream

```javascript
// Track checkpoints as task subtasks or events
memory(
  action="create_task",
  title="Validate checkpoint 1: Problem Identified",
  description="Error is 'contextstream-mcp: command not found'",
  plan_step_id="validation-1",
  priority="high"
)

// After each checkpoint passes
memory(
  action="update_task",
  task_id="checkpoint-1",
  status="completed"
)
```

---

## Multi-Agent Workflow Pattern

### Request Structure (No Heavy File Reads)

```markdown
## Prompt for Prompt-Engineer Agent

**Task**: Validate lesson clarity and search-ability

**Lesson to Review**:
- Title: "npm/contextstream-mcp: command not found — NVM not sourced"
- Trigger: "Tool not found despite global install"
- Keywords: [npm, NVM, shell, PATH, startup, .bashrc]

**Questions** (analytical, no file reads):
1. Is title specific enough to search for?
2. Are keywords sufficient for future retrieval?
3. Would agent naturally find this lesson when encountering "command not found"?
4. Suggest improvements.

**Format**: 1-2 sentences per question.
```

### Response Integration

```javascript
// After agent feedback, update lesson
session(
  action="capture",
  event_type="note",
  title="Prompt-Engineer feedback on lesson phrasing",
  content="Improved title to include exact error message. Added keywords: command-not-found, global-install. Test command now uses -l flag for login shell."
)

// Capture improved lesson
session(
  action="capture_lesson",
  title="npm/contextstream-mcp: command not found — NVM not sourced in shell startup",  // UPDATED
  trigger="contextstream-mcp: command not found (exact error from agent feedback)",       // UPDATED
  // ... rest of lesson
)
```

---

## Quick Reference: Common ContextStream Operations

### Start Session
```javascript
init(folder_path="/workspaces/mcapp-ai-starter")
context(user_message="<task>", session_id="<id>", save_exchange=true)
```

### Capture Work
```javascript
session(action="capture", event_type="decision|note|insight", title="...", content="...")
session(action="capture_lesson", title="...", trigger="...", impact="...", prevention="...")
memory(action="create_task", title="...", priority="high|medium|low")
memory(action="update_task", task_id="...", status="in_progress|completed")
```

### Query Context
```javascript
session(action="get_lessons", query="shell-initialization")
memory(action="list_tasks")
memory(action="list_docs")
session(action="list_plans")
```

### Store Persistent Context
```javascript
context7_api.put({
  key: "lesson-key",
  type: "lesson",
  content: {...},
  ttl: 2592000,  // 30 days
  tags: ["tag1", "tag2"]
})

context7_api.get("type:lesson AND tags:shell") // Retrieve
```

---

## Testing the Workflow

### Test Scenario 1: Known Issue (NVM/Shell)
- **Start**: Describe "contextstream-mcp not found" error
- **Process**: Retrieve lesson from Context7, apply prevention, verify
- **Result**: Should recognize as known lesson and apply prevention

### Test Scenario 2: New Issue (Similar Pattern)
- **Start**: Describe "python: command not found" error
- **Process**: Context7 returns "runtime-manager-initialization" pattern
- **Result**: Should recognize pattern and suggest similar prevention

### Test Scenario 3: Multi-Agent Validation
- **Start**: New lesson captured
- **Process**: Request feedback from 3 agents
- **Result**: Should improve lesson phrasing, detect gaps, extract patterns

---

## Files Reference

- **Workflow Framework**: [contextstream-workflow-framework.md](./contextstream-workflow-framework.md)
- **Lessons Learned (Detailed)**: [contextstream-lessons-learned.md](./contextstream-lessons-learned.md)
- **Configuration Template**: This file
- **Upstash Context7 API**: https://docs.upstash.com/redis (Context7 is built on Redis)

---

## Next Steps

1. ✅ Configure environment with CONTEXTSTREAM_* env vars
2. ✅ Register MCP server in `.vscode/settings.json`
3. ✅ Initialize session: `init()` → `context()`
4. ✅ Test lesson capture: `capture_lesson()`  
5. ✅ Load agents for validation: `runSubagent()`
6. ✅ Store in Context7: `context7_api.put()`
7. Test retrieval: `context7_api.get()` on new session
8. Validate cross-session persistence

**Current Status**: ✅ Workflow designed, agents tested, lessons captured, ready for deployment.
