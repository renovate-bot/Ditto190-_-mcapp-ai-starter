#!/usr/bin/env bash
set -euo pipefail

echo "This script installs Nix (single-user, no-daemon) and appends a guarded oh-my-posh init to your ~/.bashrc."

if command -v nix >/dev/null 2>&1; then
  echo "Nix already installed: $(nix --version)"
  exit 0
fi

# Install prerequisites when apt and sudo are available
if command -v apt-get >/dev/null 2>&1 && command -v sudo >/dev/null 2>&1; then
  echo "Installing prerequisites via apt..."
  sudo apt-get update -y
  sudo apt-get install -y curl ca-certificates gnupg
fi

echo "Running Nix single-user installer..."
curl -L https://nixos.org/nix/install | sh -s -- --no-daemon

echo "Sourcing nix profile (for the current session) if available..."
if [ -f "$HOME/.nix-profile/etc/profile.d/nix.sh" ]; then
  # shellcheck disable=SC1090
  . "$HOME/.nix-profile/etc/profile.d/nix.sh"
  echo "Sourced nix profile"
fi

if ! command -v nix >/dev/null 2>&1; then
  echo "ERROR: nix still not found after install" >&2
  exit 2
fi

echo "Appending guarded oh-my-posh init to ~/.bashrc if not present..."
BASHRC="$HOME/.bashrc"
OMP_MARKER="# --- oh-my-posh guarded init ---"
if ! grep -Fq "$OMP_MARKER" "$BASHRC" 2>/dev/null; then
  cat >> "$BASHRC" <<'BASH_APPEND'

# --- oh-my-posh guarded init ---
OMP_CONF="$HOME/.config/oh-my-posh/theme.omp.json"
if command -v oh-my-posh >/dev/null 2>&1 && [ -f "$OMP_CONF" ]; then
  eval "$(oh-my-posh init bash --config \"$OMP_CONF\")"
else
  unset OMP_CONFIG 2>/dev/null || true
fi
# --- end oh-my-posh guarded init ---
BASH_APPEND
  echo "Appended guarded oh-my-posh init to $BASHRC"
else
  echo "oh-my-posh guard already present in $BASHRC"
fi

echo "Done. Open a new terminal (or run: source \"$HOME/.nix-profile/etc/profile.d/nix.sh\") to use nix."
