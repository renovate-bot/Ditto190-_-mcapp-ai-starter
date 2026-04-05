#!/usr/bin/env bash
# Wrapper to run mcp-nixos safely from VS Code MCP config.
# Exits with a friendly message if `nix` is not installed.

set -euo pipefail

# Resolve workspace root
WORKDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." >/dev/null 2>&1 && pwd)"
cd "$WORKDIR" || true

if ! command -v nix >/dev/null 2>&1; then
  cat <<'MSG' >&2

ERROR: the 'nix' command was not found in PATH.
The MCP server entry for 'nixos' requires Nix to be installed.

Options to resolve:
  1) Install Nix in this environment: https://nixos.org/download.html
  2) Use the declarative flake/home-manager in tools/nix (see tools/README.md)
  3) If you don't want a local nix-based MCP, remove or disable the 'nixos' server in .vscode/mcp.json

For now the wrapper will exit so VS Code doesn't repeatedly spawn a missing binary.

MSG
  exit 2
fi

# If nix exists, run the mcp-nixos package
exec nix run github:utensils/mcp-nixos -- "$@"
