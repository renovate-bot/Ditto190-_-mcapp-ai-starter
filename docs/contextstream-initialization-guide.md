# ContextStream Setup & Initialization Guide

## What is ContextStream?

ContextStream provides:
- **Persistent memory** across AI sessions
- **Semantic code search** (find by meaning, not keywords)
- **Knowledge graphs** of decisions, code, and docs
- **Team context** from GitHub, Slack, Notion
- **Lessons learned** system (never repeat mistakes)

## MCP Configuration

✅ **Already configured** in `.vscode/mcp.json`:
- Server: `contextstream` 
- Command: `npx -y @contextstream/mcp-server@latest`
- API URL: `https://api.contextstream.io`
- API Key: Prompted on first use (secure input)

## Getting Your API Key

1. Visit [contextstream.io](https://contextstream.io)
2. Sign up or log in
3. Generate an API key from your dashboard
4. When VS Code prompts for `CONTEXTSTREAM_API_KEY`, paste it

**Or use the setup wizard:**
```bash
npx @contextstream/mcp-server@latest setup
```

## First-Time Workspace Initialization

Once the MCP server is running, initialize your workspace:

### Step 1: Initialize Session
Ask your AI assistant (or invoke tool directly):
```
"Initialize ContextStream for this workspace"
```

**Tool:** `mcp_io_github_con_session_init`
- `folder_path`: `/workspaces/self-hosted-ai-starter-kit`
- `context_hint`: "n8n self-hosted AI starter kit for automation workflows"

### Step 2: Index Project (Enable Semantic Search)
Ask your AI:
```
"Index this project for ContextStream semantic search"
```

**Tool:** `mcp_io_github_con_project`
- `action`: `"ingest_local"`
- `path`: `/workspaces/self-hosted-ai-starter-kit`

Indexing runs in background (30-60 seconds for typical repos).

### Step 3: Test It
Try these queries:
```
"What services are in docker-compose.yml?"
"Show me n8n configuration"
"What decisions have we made about authentication?"
```

## Tools Available

Once initialized, your AI can use:

| Tool | Purpose | Example |
|------|---------|---------|
| `context_smart` | Get relevant context for any query | Auto-called every message |
| `search` | Semantic code search | `search(mode="hybrid", query="auth")` |
| `session` | Capture decisions/lessons | `session(action="capture", ...)` |
| `memory` | Store/retrieve memories | `memory(action="list_events")` |
| `graph` | Dependency/impact analysis | `graph(action="dependencies")` |
| `integration` | Query GitHub/Slack/Notion | `integration(provider="github")` |

## Search Modes

| Mode | Use Case |
|------|----------|
| `hybrid` | General code search (default) |
| `semantic` | Conceptual questions |
| `keyword` | Exact symbol/string match |
| `exhaustive` | Find ALL matches (grep-like) |

## Agent Mode Integration

ContextStream is already exposed to Agent mode via:
```jsonc
"github.copilot.chat.askAgent.additionalTools": [
    "mcp_io_github_con_context"  // ✅ Already configured
]
```

Agent mode can autonomously:
- Search your codebase semantically
- Retrieve past decisions and lessons
- Understand project architecture
- Build knowledge graphs

## Lessons Learned System

ContextStream automatically captures lessons when you:
- Express frustration ("NO! Don't do that!")
- Correct mistakes ("That's wrong, use X instead")
- State preferences ("I prefer TypeScript strict mode")
- Experience failures ("This broke production")

Lessons are auto-surfaced in future sessions to prevent repeated mistakes.

## Best Practices

### ✅ DO:
- Let AI call `context_smart` at start of each response
- Use `search(mode="hybrid")` BEFORE local file reads
- Capture important decisions with `session(action="capture")`
- Initialize workspace once per project

### ❌ DON'T:
- Skip initialization (tools won't work without setup)
- Use local grep/search when ContextStream is available
- Forget to index large repos (semantic search needs it)
- Commit your API key (already handled via VS Code inputs)

## Troubleshooting

### "ContextStream could not resolve a workspace"
**Solution:** Run `session_init` with your workspace folder path first.

### "Project index not found"
**Solution:** Run `project(action="ingest_local")` to build the index.

### API Key Prompt
**Solution:** Get key from [contextstream.io/dashboard](https://contextstream.io/dashboard), paste when prompted.

### Tools Not Appearing
**Solution:** Restart VS Code after editing `mcp.json`.

## Documentation

- **Full MCP Docs:** https://contextstream.io/docs/mcp
- **Tool Reference:** https://contextstream.io/docs/mcp/tools
- **GitHub Repository:** https://github.com/contextstream/mcp-server
- **Pricing:** https://contextstream.io/pricing

## Token Efficiency (v0.4.x)

ContextStream v0.4.x uses ~11 consolidated domain tools with action dispatch:
- **~75% token reduction** vs previous versions
- **Progressive mode available:** Add `"CONTEXTSTREAM_PROGRESSIVE_MODE": "true"` to env for ~2 meta-tools (most compact)

## Quick Start Commands

```bash
# Get API key and auto-configure (recommended)
npx @contextstream/mcp-server@latest setup

# Verify installation
npx @contextstream/mcp-server@latest --version

# Check workspace MCP config
cat .vscode/mcp.json
```

---

**Status:** 
- ✅ MCP server configured in workspace
- ⏳ Needs: API key + workspace initialization
- ⏳ Needs: Project indexing for semantic search

**Next:** Restart VS Code → Get API key → Initialize workspace → Start coding!
