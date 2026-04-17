# ContextStream MCP Setup & Usage Guide

Category: config

This guide documents how this repository integrates with ContextStream's MCP toolset, the local Codespace checks performed, and operational guidance for agents and maintainers.

1) Quick status (automated checks)

- `contextstream-mcp` present in Codespace: yes (v0.2.10)
- Codespace capacity checked: ~16GB RAM (11GB available), 32GB disk (~26GB free), workspace size ~374MB

1) Recommended installation (one-liner)

- Run the setup wizard (recommended):

```bash
# macOS / Linux (Codespace)
curl -fsSL https://contextstream.io/scripts/mcp.sh | bash
# Or use the local binary if present
contextstream-mcp setup --dry-run
```

1) Project-level MCP config (recommended)

- For VS Code/Copilot project-scope, create `.mcp.json` (or update `.vscode/mcp.json`) with this minimal HTTP entry:

```json
{
  "servers": {
    "contextstream": {
      "type": "http",
      "url": "https://mcp.contextstream.io/mcp?default_context_mode=fast"
    }
  }
}
```

1) Editor Rules (required best practice)

- Add a `CLAUDE.md` or `AGENTS.md` file in the project root to document the required pre-tool-use rules for AI-assisted responses. See `CLAUDE.md` in repo root (created by automation).

1) Lessons capture (what we did)

- We merged `.vscode/extensions.json` and `.vscode/settings.json` to align with devcontainer and DRAFT workspace recommendations. This change is documented in `docs/CONFIG_UPDATES.md`.
- To persist the lesson into ContextStream programmatically, use the included `scripts/save_lesson.js` script with environment variables:

```bash
# DRY RUN (safe):
DRY_RUN=true node scripts/save_lesson.js

# To POST the lesson (requires API key + project ID):
export CONTEXTSTREAM_API_KEY="sk-..."
export CONTEXTSTREAM_PROJECT_ID="<project-id>"
# OR set CONTEXTSTREAM_API_URL if using a private instance
DRY_RUN=false node scripts/save_lesson.js
```

1) Quick agent reference (Search-first rules)

- ALWAYS call ContextStream search first for code/doc discovery:
  - `mcp__contextstream__search(mode="hybrid", query="<term>")` (Claude Code namespaced)
  - `search(mode="hybrid", query="<term>")` (Codex/OpenCode raw names)
- On session start: include lessons and context via `session_init` / `context_smart` as described in the docs.

1) How to push this repo-level lesson now (manual alternative)

- If the automated `capture_lesson` call failed due to permissions, run `scripts/save_lesson.js` with the environment variables set (see above). The script prints the payload on DRY_RUN.

1) Next steps & plan

- Team review: confirm recommended extension list in `.vscode/extensions.json`.
- Decide which extensions to centrally recommend vs optional.
- Optionally: commit `.mcp.json` with project-scoped server config for team use (requires secret approval on first use).
- Optionally: enable the setup wizard for maintainers to auto-configure the Codespace.
