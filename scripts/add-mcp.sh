#!/usr/bin/env sh
# Helper: add ContextStream MCP to VS Code and optionally create a gh alias
# Usage: ./scripts/add-mcp.sh [--gh-alias]

set -eu

JSON='{"name":"contextstream","type":"http","url":"https://mcp.contextstream.io/mcp?default_context_mode=fast"}'

if command -v code >/dev/null 2>&1; then
  echo "Registering MCP with VS Code..."
  if code --add-mcp "$JSON"; then
    echo "✅ MCP added to VS Code (contextstream)."
  else
    echo "⚠️ code --add-mcp returned non-zero exit status"
  fi
else
  echo "❌ VS Code 'code' CLI not found in PATH."
  echo "   In VS Code: open Command Palette -> 'Shell Command: Install 'code' command in PATH'"
  exit 1
fi

if [ "${1-}" = "--gh-alias" ]; then
  if command -v gh >/dev/null 2>&1; then
    # Create a gh alias that runs the 'code --add-mcp' command. The alias runs the shell command.
    ALIAS_CMD="!code --add-mcp '$JSON'"
    if gh alias set add-mcp "$ALIAS_CMD"; then
      echo "✅ gh alias 'add-mcp' created. Use: gh add-mcp"
    else
      echo "⚠️ Failed to create gh alias"
    fi
  else
    echo "❌ GitHub CLI 'gh' not found in PATH; skipping gh alias creation."
  fi
fi
