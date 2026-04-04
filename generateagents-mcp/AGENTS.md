# generateagents-mcp — AGENTS.md (folder guidance)

Purpose
-------
This file documents conventions and quick pointers for working inside the `generateagents-mcp/` folder. The MCP server wraps the `GenerateAgents.md` CLI and exposes tools to MCP-compatible clients (VS Code Copilot, Claude Desktop, etc.).

What to read first
------------------
- `README.md` — server overview and deployment guidance
- `server.py` — entrypoint and tool registration
- `setup.py` — installation and client registration hooks

Common commands
---------------
Install & dev:

```bash
cd generateagents-mcp
uv sync
python setup.py all
```

Run server (dev):

```bash
python server.py
# or: uv run server.py
```

Tests & validation
------------------
- `uv run python verify.py` — runs the repository sanity checks and test harness

Conventions & patterns
----------------------
- Use `pydantic` dataclasses for tool input/output validation.
- Keep tools idempotent and sanitize outputs to avoid leaking secrets.
- Timeouts for CLI execution are typically long (600–900s) — ensure subprocess calls are robust and kill hung processes.

Where agents expect outputs
--------------------------
- Generated `AGENTS.md` files are saved under `GenerateAgents.md/projects/<repo_name>/AGENTS.md` by the core CLI; the MCP server returns a preview (first 1000 chars) in responses.

Tips & pitfalls
--------------
- Do not expose API keys in tool responses — sanitize or redact before returning.
- When adding new tools, include unit tests and update `README.md` describing the tool contract and expected inputs.
