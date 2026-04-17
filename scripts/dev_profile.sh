#!/usr/bin/env bash
# Dev profile for mcapp-ai-starter
# Loads project .env, adjusts PATH for local tools, and provides helper commands
# Source this file from your shell (e.g., add to ~/.bashrc or your terminal profile):
#   source /path/to/mcapp-ai-starter/scripts/dev_profile.sh

_mcapp_project_root() {
  # Determine repo root (git) or fallback to current dir
  git rev-parse --show-toplevel 2>/dev/null || pwd
}

_mcapp_load_dotenv() {
  local root file line key val
  root=$(_mcapp_project_root)
  file="$root/.env"
  if [ ! -f "$file" ]; then
    return 0
  fi
  echo "[dev_profile] Loading environment from $file"
  # Read .env line-by-line and export assignments (ignore comments and blanks)
  while IFS= read -r line || [ -n "$line" ]; do
    # Trim leading/trailing whitespace
    line="$(echo "$line" | sed -e 's/^\s*//' -e 's/\s*$//')"
    # Skip empty and comment lines
    [[ -z "$line" || "$line" == \#* ]] && continue
    # Skip lines without =
    [[ "$line" != *=* ]] && continue
    key="${line%%=*}"
    val="${line#*=}"
    # Remove surrounding quotes if present
    val="${val%\"}"
    val="${val#\"}"
    val="${val%\'}"
    val="${val#\'}"
    export "$key=$val"
  done < "$file"
}

_mcapp_add_paths() {
  local root
  root=$(_mcapp_project_root)
  # Add node_modules/.bin from repo root
  if [ -d "$root/node_modules/.bin" ]; then
    PATH="$root/node_modules/.bin:$PATH"
  fi
  # Common local binary locations
  PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
  export PATH
}

_mcapp_activate_venv() {
  local root venv
  root=$(_mcapp_project_root)
  venv="$root/.venv"
  if [ -f "$venv/bin/activate" ]; then
    # Avoid re-activating if already active
    if [ -z "$VIRTUAL_ENV" ]; then
      # shellcheck source=/dev/null
      source "$venv/bin/activate"
      echo "[dev_profile] Activated virtualenv: $venv"
    fi
  fi
}

_mcapp_contextstream_helpers() {
  # Provide convenient wrappers/aliases for ContextStream if CLI is installed
  if command -v contextstream-mcp >/dev/null 2>&1; then
    alias cs_init='contextstream-mcp init --folder-path="$(_mcapp_project_root)"'
    alias cs_context='contextstream-mcp context --session_id="session-$(date +%F-%H%M%S)"'
    alias cs_search='contextstream-mcp search'
  else
    cs_init() { echo "[dev_profile] contextstream-mcp not found; install or add to PATH"; }
    cs_context() { echo "[dev_profile] contextstream-mcp not found; install or add to PATH"; }
  fi
}

_mcapp_prompt() {
  # Append a short prompt indicator when inside the repo
  local root cwd
  root=$(_mcapp_project_root)
  cwd=$(pwd)
  if [ "${cwd#"$root"}" != "$cwd" ]; then
    PS1="[mcapp] $PS1"
  fi
}

# Public entrypoint: call to initialize the dev profile in the current shell
mcapp_dev_setup() {
  _mcapp_load_dotenv
  _mcapp_add_paths
  _mcapp_activate_venv
  _mcapp_contextstream_helpers
  _mcapp_prompt
  # Quick status
  echo "[dev_profile] setup complete"
  echo "[dev_profile] PATH: $PATH"
  if [ -n "$CONTEXTSTREAM_API_KEY" ]; then
    echo "[dev_profile] CONTEXTSTREAM_API_KEY is set"
  else
    echo "[dev_profile] CONTEXTSTREAM_API_KEY not set — set it to enable ContextStream CLI/tools"
  fi
}

# Auto-run setup when this file is sourced
mcapp_dev_setup

export MCAPP_DEV_PROFILE_LOADED=1

# Helpful hints
_mcapp_dev_help() {
  cat <<'EOF'
mcapp_dev_profile helpers:
  mcapp_dev_setup     # reload profile in current shell
  cs_init             # initialize ContextStream session (if CLI available)
  cs_context          # open context command wrapper (if CLI available)

To enable for all new terminals, add to your ~/.bashrc or your terminal profile:
  source /path/to/mcapp-ai-starter/scripts/dev_profile.sh

EOF
}

alias mcapp_dev_help=_mcapp_dev_help
