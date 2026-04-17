# ContextStream Integration Plan

Goals:

- Ensure ContextStream MCP tools are available and configured for repo/team
- Persist lesson about `.vscode` changes into ContextStream memory
- Create editor rules (CLAUDE.md / AGENTS.md) to enforce "search-first" and lesson surfacing
- Provide onboarding steps for maintainers to run the setup wizard and approve MCP access

Steps:

1. Team review of `docs/CONFIG_UPDATES.md` and `.vscode/extensions.json` (decide must-have vs optional)
2. (Optional) Commit `.mcp.json` with project-scoped server config and include instructions to approve the server in VS Code/Claude on first use
3. Persist lesson: run `scripts/save_lesson.js` with `CONTEXTSTREAM_API_KEY` + `CONTEXTSTREAM_PROJECT_ID` (or ask admin to post)
4. Add `CLAUDE.md`/`AGENTS.md` project rules (already drafted in docs) and adjust as team agrees
5. Validate environment: maintainers run `contextstream-mcp --version` and `contextstream-mcp setup --dry-run`
6. Monitor usage and adjust recommended extensions after 1-week trial
