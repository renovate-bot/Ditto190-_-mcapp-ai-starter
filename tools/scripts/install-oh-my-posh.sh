#!/usr/bin/env bash
set -euo pipefail

# Installs oh-my-posh Linux binary into ~/.local/bin and creates a default config
DEST_DIR="${HOME}/.local/bin"
CONFIG_DIR="${HOME}/.config/oh-my-posh"

mkdir -p "$DEST_DIR" "$CONFIG_DIR"

echo "Installing oh-my-posh to $DEST_DIR"
curl -sSL https://ohmyposh.dev/install.sh | bash -s -- -d "$DEST_DIR"

OMP_BIN="$DEST_DIR/oh-my-posh"
if [ ! -x "$OMP_BIN" ]; then
    echo "oh-my-posh binary not found after install" >&2
    exit 1
fi

CONFIG_FILE="$CONFIG_DIR/theme.omp.json"
if [ ! -f "$CONFIG_FILE" ]; then
    cat > "$CONFIG_FILE" <<'JSON'
{
  "$schema": "https://raw.githubusercontent.com/JanDeDobbeleer/oh-my-posh/main/schemas/config.schema.json",
  "blocks": [
    {
      "type": "prompt",
      "style": "powerline",
      "powerline_symbol": "",
      "segments": [
        { "type": "path", "style": "plain" },
        { "type": "git", "style": "plain" }
      ]
    }
  ]
}
JSON
    echo "Created default oh-my-posh config at $CONFIG_FILE"
fi

echo "oh-my-posh installed and configured (binary: $OMP_BIN, config: $CONFIG_FILE)"
