---
name: troubleshoot-generateagents
description: "Diagnose and suggest fixes for common issues running `GenerateAgents.md` CLI and `generateagents-mcp` server."
argument-hint: Optionally supply an error message or log snippet
agent: agent
---

When invoked, do the following:

1. Ask whether the issue is with the local CLI (`GenerateAgents.md`) or the MCP server (`generateagents-mcp`).
2. For CLI issues, list these checks in order: Python v3.12+, virtualenv activated, `uv sync` completed, `.env` present (do not request secrets), and exact failing command.
3. For MCP issues, check server logs, `python setup.py all` registration, and whether the MCP server can locate `GenerateAgents.md` sibling folder.
4. Suggest exact diagnostic commands (e.g., `python -V`, `uv run pytest -m 'not e2e' -q`, `python server.py 2>&1 | tee debug.log`) and what to look for in their output.
5. Provide a safe, minimal remediation plan for the top 3 causes with commands to run.

Keep answers focused and include copy-pasteable commands. Never echo API keys or secrets.
