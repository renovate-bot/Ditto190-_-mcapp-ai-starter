#!/bin/bash
# bash_profile.sh — Bootstrap developer environment for the AI Starter Kit.
#
# Registers Context Stream in PATH and configures common tool paths by appending
# idempotent entries to ~/.bashrc.  Safe to run multiple times.
#
# Usage:
#   bash scripts/bash_profile.sh            # configure and update ~/.bashrc
#   source scripts/bash_profile.sh          # configure and apply to current session
#
# To apply changes immediately after running the script:
#   source ~/.bashrc
# ============================================================================

set -euo pipefail

readonly BASHRC="$HOME/.bashrc"
# Project root — resolve relative to this script regardless of invocation path
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly PROJECT_ROOT
[[ -d "$PROJECT_ROOT" ]] || { echo "Error: Could not determine project root" >&2; exit 1; }

# ── Helpers ───────────────────────────────────────────────────────────────────

info()    { echo "  ✅  $*"; }
warn()    { echo "  ⚠️   $*" >&2; }
section() { echo ""; echo "── $* ──────────────────────────────────────────"; }

# Append a line to BASHRC only if it is not already present.
append_if_missing() {
    local line="$1"
    if ! grep -qxF "$line" "$BASHRC" 2>/dev/null; then
        echo "$line" >> "$BASHRC"
        info "Added to ~/.bashrc: $line"
    else
        info "Already in ~/.bashrc: $line"
    fi
}

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║      AI Starter Kit — Bash Profile Bootstrap             ║"
echo "╚══════════════════════════════════════════════════════════╝"

# ── 1. Context Stream PATH registration ───────────────────────────────────────
section "Context Stream"

# Determine the binary or shim to use.
_contextstream_path=""

# 1a. Already on PATH?
if command -v contextstream &>/dev/null; then
    _contextstream_path="$(command -v contextstream)"
    info "contextstream already on PATH: $_contextstream_path"
fi

# 1b. Common npm global bin locations
if [[ -z "$_contextstream_path" ]]; then
    _npm_global_bin=""
    if command -v npm &>/dev/null; then
        _npm_global_bin="$(cd "$(npm root -g 2>/dev/null)/../bin" 2>/dev/null && pwd)" || _npm_global_bin=""
    fi
    for _candidate in \
        "$HOME/.npm-global/bin" \
        "$HOME/.local/share/npm/bin" \
        "/usr/local/lib/node_modules/.bin" \
        "/usr/lib/node_modules/.bin" \
        "${_npm_global_bin:-}"
    do
        if [[ -n "$_candidate" && -x "$_candidate/contextstream" ]]; then
            _contextstream_path="$_candidate/contextstream"
            break
        fi
    done
fi

# 1c. Manual / local install
if [[ -z "$_contextstream_path" ]]; then
    for _candidate in \
        "$HOME/.local/bin/contextstream" \
        "/usr/local/bin/contextstream"
    do
        if [[ -x "$_candidate" ]]; then
            _contextstream_path="$_candidate"
            break
        fi
    done
fi

if [[ -n "$_contextstream_path" ]]; then
    _contextstream_dir="$(dirname "$_contextstream_path")"
    append_if_missing "export PATH=\"\$PATH:$_contextstream_dir\"  # Context Stream"
    info "Context Stream registered at: $_contextstream_dir"
else
    warn "contextstream binary not found."
    echo ""
    echo "     Install options:"
    echo "       npm install -g @contextstream/mcp-server"
    echo "       npx @contextstream/mcp-server@latest setup"
    echo ""
    echo "     Re-run this script after installation, or add the path manually:"
    echo "       echo 'export PATH=\"\$PATH:<path_to_contextstream>\"' >> ~/.bashrc"
fi

# ── 2. uv / Python toolchain ──────────────────────────────────────────────────
section "uv / Python"

_uv_bin="$HOME/.local/bin"
append_if_missing "export PATH=\"\$HOME/.local/bin:\$PATH\"  # uv, ruff, black, etc."

if command -v uv &>/dev/null || [[ -x "$_uv_bin/uv" ]]; then
    info "uv is available"
else
    warn "uv not found. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
fi

# ── 3. Node.js / npm global bin ───────────────────────────────────────────────
section "Node.js"

if command -v npm &>/dev/null; then
    _npm_prefix="$(npm config get prefix 2>/dev/null || true)"
    if [[ -n "$_npm_prefix" && "$_npm_prefix" != "undefined" ]]; then
        _npm_bin="$_npm_prefix/bin"
        append_if_missing "export PATH=\"\$PATH:$_npm_bin\"  # npm global binaries"
        info "npm global bin: $_npm_bin"
    fi
else
    warn "npm not found. Node.js may not be installed."
fi

# ── 4. asdf version manager ───────────────────────────────────────────────────
section "asdf"

if [[ -f "$HOME/.asdf/asdf.sh" ]]; then
    append_if_missing ". \"\$HOME/.asdf/asdf.sh\"  # asdf version manager"
    append_if_missing ". \"\$HOME/.asdf/completions/asdf.bash\"  # asdf completions"
    info "asdf sourced from ~/.asdf"
else
    info "asdf not installed (optional — see https://asdf-vm.com)"
fi

# ── 5. direnv ─────────────────────────────────────────────────────────────────
section "direnv"

if command -v direnv &>/dev/null; then
    append_if_missing "eval \"\$(direnv hook bash)\"  # per-directory environment"
    info "direnv hook registered"
else
    info "direnv not installed (optional — see https://direnv.net)"
fi

# ── 6. Project .env guard ─────────────────────────────────────────────────────
section ".env check"

if [[ -f "$PROJECT_ROOT/.env" ]]; then
    info ".env found at $PROJECT_ROOT/.env"
elif [[ -f "$PROJECT_ROOT/.env.example" ]]; then
    warn ".env not found. Run: cp $PROJECT_ROOT/.env.example $PROJECT_ROOT/.env"
    warn "Then edit .env and fill in your API keys."
fi

# ── 7. Summary ────────────────────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════════════════"
echo "  Done.  ~/.bashrc has been updated."
echo ""
echo "  Apply changes to the current session:"
echo "    source ~/.bashrc"
echo ""
echo "  Verify Context Stream:"
echo "    contextstream --version"
echo "    # or (npx shim):"
echo "    npx @contextstream/mcp-server@latest --version"
echo ""
echo "  See docs/SHELL_GUIDE.md for full environment setup docs."
echo "══════════════════════════════════════════════════════════"
