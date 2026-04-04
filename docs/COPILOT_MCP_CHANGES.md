Copilot MCP Integration — Technical & Change Log

Date: 2026-04-03
Author: Automation

Summary
- Merged VS Code MCP config into a repo-local Copilot CLI config at `.copilot/mcp.json`.
- Sanitized inline API key in `.vscode/mcp.json` to use `${CONTEXTSTREAM_API_KEY}` and documented secret handling.
- Created `.github/copilot-instructions.md` describing how the Copilot CLI uses MCP configs and how to run local stdio servers.
- Started and verified `n8n-mcp` locally for testing, then stopped it (process management logged).

Files changed/created
- .copilot/mcp.json (created) — contains merged servers from .vscode/mcp.json, uses `${CONTEXTSTREAM_API_KEY}`.
- .vscode/mcp.json (edited) — API key replaced with `${CONTEXTSTREAM_API_KEY}` placeholder.
- .github/copilot-instructions.md (created) — guidance for devs and Copilot CLI usage.
- .github/copilot-instructions.md (created)
- docs/COPILOT_MCP_CHANGES.md (this file)
- docs/CI-SECRETS.md (created) — CI guidance for storing CONTEXTSTREAM_API_KEY.

Technical details & rationale
- Copilot CLI config discovery (confirmed): precedence is command-line > repo/project-local (.copilot/mcp-config.json, .mcp.json, .vscode/mcp.json) > user-level (~/.copilot/mcp-config.json or $XDG_CONFIG_HOME) > built-in defaults. Use `.copilot/mcp-config.json` for a canonical repo-shared configuration.
- Security: Do not commit API keys. Use environment variables and CI secret stores. The repo already contains `.env` (local dev); `.gitignore` contains `.env` so keys are not committed.

How to reproduce
1. Verify `.copilot/mcp.json` exists in repo root.
2. Populate `.env` with CONTEXTSTREAM_API_KEY for local dev.
3. Start n8n-mcp for stdio server: `set -o allexport && source .env && set +o allexport && npx --yes n8n-mcp`.

Notes
- If any secret was committed prior to this sanitization, rotate it and purge from git history.
- For CI, create a repo secret named `CONTEXTSTREAM_API_KEY` and map into your workflow's environment.
