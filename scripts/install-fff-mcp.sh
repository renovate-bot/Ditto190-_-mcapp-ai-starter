#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="${FFF_MCP_INSTALL_DIR:-${HOME}/.local/bin}"

if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
  cat <<'EOF'
Usage: install-fff-mcp.sh [--dir <install-dir>]

Installs the FFF MCP binary for local use.
By default it runs the upstream installer from dmtrkovalenko.dev.
EOF
  exit 0
fi

while [ $# -gt 0 ]; do
  case "$1" in
    --dir)
      shift
      INSTALL_DIR="$1"
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
  shift
done

mkdir -p "$INSTALL_DIR"

if command -v curl >/dev/null 2>&1; then
  echo "Installing fff-mcp to $INSTALL_DIR using upstream installer..."
  curl -L https://dmtrkovalenko.dev/install-fff-mcp.sh | bash
else
  echo "curl is required to download the installer." >&2
  echo "Install curl or use Nix to add fff-mcp to the dev shell." >&2
  exit 1
fi

echo "To use fff-mcp in new shells, ensure $INSTALL_DIR is on your PATH."
