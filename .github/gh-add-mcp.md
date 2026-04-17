Add ContextStream MCP to VS Code and create a gh alias

This repository helper explains how to register the ContextStream MCP endpoint with VS Code (Cursor) and optionally create a gh CLI alias that runs the same command.

Commands

1. Run the helper script (recommended):

   # Make executable (once)

   chmod +x ./scripts/add-mcp.sh

   # Register MCP with VS Code

   ./scripts/add-mcp.sh

   # Register MCP with VS Code and create a gh alias (if gh is installed)

   ./scripts/add-mcp.sh --gh-alias

2. Manual commands

- Bash / macOS / Linux (recommended):

  code --add-mcp '{"name":"contextstream","type":"http","url":"<https://mcp.contextstream.io/mcp?default_context_mode=fast"}>'

- Create a gh alias (bash):

  gh alias set add-mcp '!code --add-mcp '\''{"name":"contextstream","type":"http","url":"<https://mcp.contextstream.io/mcp?default_context_mode=fast"}'\>'''

  # Now run

  gh add-mcp

- PowerShell (Windows):

  code --add-mcp "{\"name\":\"contextstream\",\"type\":\"http\",\"url\":\"<https://mcp.contextstream.io/mcp?default_context_mode=fast\"}>"

  # gh alias for PowerShell (use double quotes for the alias command)

  gh alias set add-mcp "!code --add-mcp \"{\\\"name\\\":\\\"contextstream\\\",\\\"type\\\":\\\"http\\\",\\\"url\\\":\\\"<https://mcp.contextstream.io/mcp?default_context_mode=fast\\\"}\>""

Notes

- The 'code' command comes from VS Code. If it's not available, open the Command Palette in VS Code and run "Shell Command: Install 'code' command in PATH".
- The Cursor/ContextStream extension must be installed/active in VS Code to accept MCP registrations.
- gh aliases are stored in your user gh config (~/.config/gh/aliases.yml) and are local to the user who runs the command.

Troubleshooting

- If code --add-mcp fails, run it directly in an interactive shell to see errors. Common issues are: 'code' not in PATH, or the Cursor extension not supporting the --add-mcp flag in older versions.
- If gh alias fails, ensure gh is authenticated (gh auth login) and up-to-date.
