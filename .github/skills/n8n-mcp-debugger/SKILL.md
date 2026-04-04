---
name: 'n8n-mcp-debugger'
description: 'Debug and validate the n8n demo stack and n8n MCP integration from VS Code, using logs, MCP config, and registered tools.'
---

# n8n MCP Debugger Skill

Use this skill when:
- n8n MCP tools are not responding or appear misconfigured in GitHub Copilot or other MCP clients.
- The n8n demo stack does not start, or APIs are unreachable.
- You need a structured workflow to diagnose and fix n8n + MCP issues, then verify with a real workflow run.

This is a **workspace-scoped** skill intended for the `self-hosted-ai-starter-kit` project.

---

## Phase 1: Problem Assessment (n8n + MCP)

1. **Gather context**
   - Read recent error messages, stack traces, or MCP connection errors from the client UI.
   - Inspect logs:
     - n8n MCP log (for example: `/tmp/n8n-mcp.log`).
     - Docker logs for the n8n stack (via `docker compose logs -f n8n` when applicable).
   - Compare expected vs actual behavior:
     - Expected: n8n MCP server stays running on stdio, tools are discoverable.
     - Actual: timeouts, SIGHUP shutdowns, or missing tools.

2. **Review configuration and docs**
   - Open and skim the key docs in this repo:
     - `N8N_AI_ASSISTANT_SETUP.md`
     - `N8N_AUTONOMOUS_AGENT_GUIDE.md`
     - `docs/mcp-debugging-guide.md` (if present) for MCP-specific advice.
   - Inspect MCP configuration files:
     - `.vscode/mcp.json` — shared workspace MCP servers.
     - `.vscode/mcp.local.json` — local overrides (e.g., `awesome-copilot`).
   - Note any use of `bash -lc`, unusual wrappers, or missing `env` settings.

3. **Reproduce the issue**
   - If possible, trigger the failing MCP tool again from Copilot chat.
   - Capture:
     - The command or tool name invoked.
     - Any visible error text.
     - The approximate time to correlate with logs.

---

## Phase 2: Environment & Stack Verification

4. **Verify the n8n demo stack**
   - Use the `start-n8n-workflow` prompt (see `.github/prompts/start-n8n-workflow.prompt.md`) as a reference for commands.
   - Ensure the stack is running:
     - Start services with `docker compose up` (or the appropriate profile).
     - Confirm n8n is reachable via the health-check URL using `N8N_HOST` from `.env`.
   - If n8n is not reachable, check and fix quickly:
     - Containers not running.
     - Wrong `N8N_HOST` URL (especially in Codespaces).
     - Missing or incorrect `N8N_API_KEY`.

5. **Check local n8n-dev environment (if relevant)**
   - Inspect `n8n-dev/package.json` to confirm local dependencies:
     - Verify `@n8n/n8n-nodes-langchain` (and other node packages) are installed.
   - If nodes are missing, run the appropriate package manager commands (e.g., `npm install`).

---

## Phase 3: MCP Server Configuration Debugging

6. **Validate MCP process configuration**
   - For `n8n-mcp` in `.vscode/mcp.json`:
     - Prefer a direct command like `"command": "npx", "args": ["n8n-mcp"]` over `bash -lc` wrappers.
     - Confirm environment variables:
       - `MCP_MODE=stdio`
       - `N8N_MODE=true`
       - Use `LOG_LEVEL=info` and `DISABLE_CONSOLE_OUTPUT=false` during debugging.
   - For other MCP servers (e.g., `awesome-copilot` in `.vscode/mcp.local.json`):
     - Use `bash -c` with `set -e` for fail-fast behavior and `exec` to replace the shell.
     - Ensure any git clone + `dotnet run` or similar scripts log progress and fail clearly.

7. **Correlate with logs**
   - Look for patterns such as:
     - `Server startup completed` followed by `Shutdown initiated by: SIGHUP`.
     - Repeated restart loops or permission errors.
   - Use these to refine hypotheses:
     - Wrapper shells exiting early.
     - Missing binaries (`npx`, `dotnet`, `node`).
     - Misconfigured environment (`PATH`, `PYTHONPATH`, etc.).

---

## Phase 4: Tool & Node Registry Cross-Check

8. **Use the registered tools index**
   - Open `.vscode/n8n-registered-tools.json` to see available node types and display names.
   - When the user asks for a capability (e.g., "Qdrant", "OpenAI", "Supabase"), check whether a corresponding node exists.
   - If a node appears missing:
     - Verify the installed packages in the n8n environment.
     - Suggest installing or enabling the relevant community package, or using a generic `HTTP Request` node as a fallback.

9. **Validate MCP-exposed tools**
   - If an MCP client lists fewer tools than expected, compare against:
     - The `n8n-registered-tools.json` catalogue.
     - The n8n MCP server log, which should list how many tools were registered on startup.
   - Use this comparison to decide whether the issue is:
     - In the MCP server (tool discovery/registration).
     - In the client (filtering, configuration, or permissions).

---

## Phase 5: Fix Implementation & Verification

10. **Apply targeted fixes**
    - Adjust only the configuration that directly addresses the hypothesized root cause:
      - Simplify `command`/`args` for MCP servers.
      - Correct environment variables or paths.
      - Update `.env` entries for n8n access.
    - Keep changes small and easy to revert.

11. **Verify behavior**
    - Reload MCP configuration in the client (e.g., reload VS Code window if needed).
    - Re-run the failing MCP tool call and confirm:
      - The server stays running (no immediate SIGHUP or crash).
      - Tools are discoverable and respond as expected.
    - Use the `start-n8n-workflow` prompt to:
      - Create or import a simple demo workflow via n8n API.
      - Execute it and check that results are returned successfully.

12. **Quality checks & regression guardrails**
    - Ensure logging levels are set back to normal (e.g., `LOG_LEVEL=error`, `DISABLE_CONSOLE_OUTPUT=true`) once debugging is complete, if appropriate.
    - Optionally document the fix:
      - Update `docs/mcp-debugging-guide.md` or relevant README.
      - Note common pitfalls (e.g., `bash -lc` wrappers, missing `exec`).

---

## Usage Examples

Use natural language prompts like:
- "Use the **n8n-mcp-debugger** skill to figure out why my n8n MCP tools stopped working after a few minutes and guide me through fixing it."
- "Run the n8n MCP debugging workflow to verify that the demo stack is up, n8n is reachable, and the MCP server is correctly configured in `.vscode/mcp.json`."
- "Cross-check this desired integration against `n8n-registered-tools.json` and suggest which n8n nodes I should use, then help me test the workflow end-to-end."

When this skill is active, follow the phases in order, keep changes minimal, and always confirm fixes with a real workflow execution.
