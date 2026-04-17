# Comprehensive Shell Environment Guide

> A complete reference for setting up a productive, reproducible shell environment  
> in Codespaces / dev containers. Covers dotfiles, prompts, task runners, version  
> managers, and the ContextStream MCP PATH fix.

---

## Table of Contents

1. [ContextStream MCP PATH Fix](#1-contextstream-mcp-path-fix)
2. [Bash Profile Structure and Sourcing Order](#2-bash-profile-structure-and-sourcing-order)
3. [Devcontainer Prebuilds and Lifecycle Hooks](#3-devcontainer-prebuilds-and-lifecycle-hooks)
4. [Dotfiles Repo Pattern](#4-dotfiles-repo-pattern)
5. [Oh My Posh Prompt Configuration](#5-oh-my-posh-prompt-configuration)
6. [tmux and tmuxp Session Management](#6-tmux-and-tmuxp-session-management)
7. [Task Runners: just, task, make](#7-task-runners-just-task-make)
8. [Version Management: direnv and asdf](#8-version-management-direnv-and-asdf)
9. [Shell Scripting Best Practices](#9-shell-scripting-best-practices)
10. [VS Code MCP Registration](#10-vs-code-mcp-registration)

---

## 1. ContextStream MCP PATH Fix

### Problem

The binary installed by the ContextStream npm package is named **`contextstream-mcp`**,  
not `contextstream`. Running `contextstream` in a new shell returns "not found" even  
though the binary is installed.

### Diagnosis

```bash
# binary is at:
/usr/local/bin/contextstream-mcp   # ← correct name

# /usr/local/bin IS on PATH already (check):
echo "$PATH" | tr ':' '\n' | grep local/bin
# → /usr/local/bin

# version check:
contextstream-mcp --version
# → contextstream-mcp 0.2.10
```

### Fix 1 — Alias in `~/.bashrc` (recommended)

```bash
# Append once:
echo "" >> ~/.bashrc
echo "# ContextStream MCP alias" >> ~/.bashrc
echo "alias contextstream='contextstream-mcp'" >> ~/.bashrc

# Reload current session:
source ~/.bashrc

# Verify:
contextstream --version
```

### Fix 2 — Symlink (system-wide)

```bash
ln -sf /usr/local/bin/contextstream-mcp /usr/local/bin/contextstream
contextstream --version
```

### Fix 3 — Devcontainer `postCreateCommand`

```jsonc
// .devcontainer/devcontainer.json
{
  "postCreateCommand": "ln -sf /usr/local/bin/contextstream-mcp /usr/local/bin/contextstream || true"
}
```

---

## 2. Bash Profile Structure and Sourcing Order

### Sourcing Order (interactive login shell)

```text
/etc/profile
└── /etc/profile.d/*.sh
~/.bash_profile  (or ~/.profile if .bash_profile absent)
└── sources → ~/.bashrc
              └── ~/.bashrc.d/*.sh  (optional pattern)
```

### Recommended `~/.bashrc` Layout

```bash
#!/usr/bin/env bash
# ~/.bashrc — Interactive non-login shell config

# 1. Guard: skip if not interactive
[[ $- != *i* ]] && return

# 2. Safety (set for shell sessions, not just scripts)
# (scripts use set -euo pipefail; interactive shells keep going on errors)

# 3. PATH extensions — add unique paths only
_add_to_path() {
  [[ -d "$1" && ":$PATH:" != *":$1:"* ]] && export PATH="$1:$PATH"
}
_add_to_path "$HOME/.local/bin"
_add_to_path "$HOME/.cargo/bin"       # Rust / just
_add_to_path "$HOME/.asdf/bin"        # asdf
_add_to_path "$HOME/.asdf/shims"      # asdf shims

# 4. Shell options
HISTSIZE=50000
HISTFILESIZE=100000
HISTCONTROL=ignoreboth
shopt -s histappend
shopt -s checkwinsize
shopt -s globstar 2>/dev/null

# 5. Tool initializations (order matters)
# asdf (version manager)
[[ -f "$HOME/.asdf/asdf.sh" ]] && source "$HOME/.asdf/asdf.sh"
[[ -f "$HOME/.asdf/completions/asdf.bash" ]] && source "$HOME/.asdf/completions/asdf.bash"

# direnv (per-directory env, must come after asdf)
command -v direnv >/dev/null && eval "$(direnv hook bash)"

# Oh My Posh (prompt, must be last prompt setup)
if command -v oh-my-posh >/dev/null; then
  if [[ -f "$HOME/.config/ohmyposh/theme.omp.json" ]]; then
    eval "$(oh-my-posh init bash --config "$HOME/.config/ohmyposh/theme.omp.json")"
  else
    eval "$(oh-my-posh init bash)"
  fi
fi

# 6. Aliases
alias contextstream='contextstream-mcp'   # ← ContextStream fix
alias ll='ls -lah --color=auto'
alias gs='git status'
alias gc='git commit'
alias gp='git push'
alias ..='cd ..'
alias ...='cd ../..'

# 7. Functions
mkdcd() { mkdir -p "$1" && cd "$1"; }

# 8. Source local overrides last (machine-specific)
[[ -f "$HOME/.bashrc.local" ]] && source "$HOME/.bashrc.local"
```

---

## 3. Devcontainer Prebuilds and Lifecycle Hooks

### Lifecycle Hook Order

```text
Container image build (Dockerfile/image)
        ↓
initializeCommand          ← runs on HOST before container starts
        ↓
postCreateCommand          ← runs once after container created
        ↓
postStartCommand           ← runs on every container start
        ↓
postAttachCommand          ← runs when VS Code attaches
```

### Minimal `devcontainer.json`

```jsonc
{
  "name": "my-project",
  "image": "mcr.microsoft.com/devcontainers/base:ubuntu",

  // Run once after creation
  "postCreateCommand": "bash .devcontainer/scripts/setup.sh",

  // Run on every start (fast ops only)
  "postStartCommand": "bash .devcontainer/scripts/start.sh",

  // Mount dotfiles from your personal repo
  "dotfiles.repository": "https://github.com/YOUR_USER/dotfiles",
  "dotfiles.targetPath": "~/dotfiles",
  "dotfiles.installCommand": "~/dotfiles/install.sh",

  "features": {
    // Includes asdf
    "ghcr.io/devcontainers/features/common-utils:2": {},
    // Node via nvm
    "ghcr.io/devcontainers/features/node:1": { "version": "20" },
    // Oh My Posh
    "ghcr.io/devcontainers-extra/features/oh-my-posh:1": {}
  },

  "customizations": {
    "vscode": {
      "settings": {
        "terminal.integrated.defaultProfile.linux": "bash"
      },
      "extensions": [
        "ms-vscode.live-server"
      ]
    }
  }
}
```

### Prebuild Strategy for Codespaces

```bash
# .github/workflows/codespace-prebuild.yml
name: Codespaces Prebuild
on:
  push:
    branches: [main]
  schedule:
    - cron: '0 3 * * 0'   # Weekly Sunday 3am

jobs:
  prebuild:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v4
      - name: Trigger Codespaces prebuild
        uses: github/codespaces-prebuild-action@v1
        with:
          repo-token: ${{ secrets.GITHUB_TOKEN }}
```

### `setup.sh` Pattern (postCreateCommand)

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "=== Devcontainer Setup ==="

# Install Oh My Posh if not present
if ! command -v oh-my-posh >/dev/null; then
  curl -s https://ohmyposh.dev/install.sh | bash -s -- -d ~/.local/bin
fi

# Install contextstream-mcp
if ! command -v contextstream-mcp >/dev/null; then
  npm install -g @contextstream/mcp-server
fi

# Symlink contextstream → contextstream-mcp
ln -sf "$(which contextstream-mcp 2>/dev/null || echo /usr/local/bin/contextstream-mcp)" \
       "$HOME/.local/bin/contextstream" 2>/dev/null || true

# Install go-task
if ! command -v task >/dev/null; then
  sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b ~/.local/bin
fi

# Install just
if ! command -v just >/dev/null; then
  curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to ~/.local/bin
fi

echo "=== Setup Complete ==="
```

---

## 4. Dotfiles Repo Pattern

### Repository Layout

```text
dotfiles/
├── install.sh         ← entry point (Codespaces calls this)
├── bash/
│   ├── .bashrc
│   ├── .bash_profile  → sources .bashrc
│   └── .bashrc.local.example
├── git/
│   ├── .gitconfig
│   └── .gitmessage
├── tmux/
│   ├── .tmux.conf
│   └── sessions/      ← tmuxp YAML files
│       └── dev.yaml
├── ohmyposh/
│   └── theme.omp.json
├── tools/
│   ├── .tool-versions ← asdf global versions
│   └── .envrc.example ← direnv template
└── vscode/
    └── settings.json
```

### `install.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

symlink() {
  local src="$DOTFILES_DIR/$1"
  local dst="$HOME/$2"
  mkdir -p "$(dirname "$dst")"
  ln -sfv "$src" "$dst"
}

echo "Installing dotfiles from $DOTFILES_DIR"

# Bash
symlink "bash/.bashrc"       ".bashrc"
symlink "bash/.bash_profile" ".bash_profile"

# Git
symlink "git/.gitconfig"   ".gitconfig"
symlink "git/.gitmessage"  ".gitmessage"

# tmux
symlink "tmux/.tmux.conf"  ".tmux.conf"

# Oh My Posh
mkdir -p "$HOME/.config/ohmyposh"
symlink "ohmyposh/theme.omp.json" ".config/ohmyposh/theme.omp.json"

# asdf
symlink "tools/.tool-versions" ".tool-versions"

echo "Done. Run: source ~/.bashrc"
```

---

## 5. Oh My Posh Prompt Configuration

### Install (Linux / Codespaces)

```bash
# Recommended: install to ~/.local/bin
curl -s https://ohmyposh.dev/install.sh | bash -s -- -d ~/.local/bin

# Or via npm
npm install -g oh-my-posh

# Or via Homebrew
brew install jandedobbeleer/oh-my-posh/oh-my-posh
```

### Initialize in Bash

```bash
# ~/.bashrc — basic (uses built-in default theme)
eval "$(oh-my-posh init bash)"

# With a specific local theme file (recommended for performance):
eval "$(oh-my-posh init bash --config ~/.config/ohmyposh/theme.omp.json)"

# Reload the shell to see the new prompt:
exec bash
```

### Theme File Formats

Oh My Posh supports `.omp.json`, `.omp.yaml`, and `.omp.toml`. JSON is most common:

```json
{
  "$schema": "https://raw.githubusercontent.com/JanDeDobbeleer/oh-my-posh/main/themes/schema.json",
  "version": 2,
  "final_space": true,
  "console_title_template": "{{ .Shell }} in {{ .Folder }}",
  "blocks": [
    {
      "type": "prompt",
      "alignment": "left",
      "segments": [
        {
          "type": "path",
          "style": "powerline",
          "powerline_symbol": "\ue0b0",
          "foreground": "#ffffff",
          "background": "#61afef",
          "properties": {
            "style": "folder"
          }
        },
        {
          "type": "git",
          "style": "powerline",
          "powerline_symbol": "\ue0b0",
          "foreground": "#011627",
          "background": "#ECBE76",
          "properties": {
            "branch_icon": "\ue0a0 ",
            "fetch_status": true
          }
        }
      ]
    }
  ]
}
```

### Export Your Current Theme

```bash
# Export to JSON (modify and re-use)
oh-my-posh config export --output ~/.config/ohmyposh/my-export.omp.json

# Export to PNG image (for sharing)
oh-my-posh config export image

# Get current shell
oh-my-posh get shell
```

### Performance Tip

Use a **local file** (not a theme name or remote URL) — theme names and URLs  
are downloaded on each shell start; local files are read instantly.

```bash
# Slow (downloads on startup):
eval "$(oh-my-posh init bash --config jandedobbeleer)"

# Fast (reads local file):
eval "$(oh-my-posh init bash --config ~/.config/ohmyposh/theme.omp.json)"
```

### Useful Themes to Start From

```bash
# Browse installed themes:
ls "$(brew --prefix oh-my-posh)/themes/"   # homebrew
ls /usr/local/share/oh-my-posh/themes/     # system install

# Recommended starting themes: jandedobbeleer, agnoster, atomic, tokyo
```

---

## 6. tmux and tmuxp Session Management

### Install

```bash
# tmux
sudo apt-get install -y tmux       # Debian/Ubuntu
brew install tmux                  # macOS

# tmuxp (Python-based session manager)
pip install tmuxp
# or
pipx install tmuxp
```

### `~/.tmux.conf` Essentials

```bash
# Change prefix from C-b to C-a (screen-like)
unbind C-b
set-option -g prefix C-a
bind-key C-a send-prefix

# Enable mouse support
set -g mouse on

# Start windows and panes at index 1
set -g base-index 1
setw -g pane-base-index 1

# Sane splitting shortcuts
bind | split-window -h -c "#{pane_current_path}"
bind - split-window -v -c "#{pane_current_path}"

# Vim-style pane navigation
bind -r h select-pane -L
bind -r j select-pane -D
bind -r k select-pane -U
bind -r l select-pane -R

# Resize panes
bind -r H resize-pane -L 5
bind -r J resize-pane -D 5
bind -r K resize-pane -U 5
bind -r L resize-pane -R 5

# Increase scrollback buffer
set -g history-limit 50000

# 256 colors + true color
set -g default-terminal "tmux-256color"
set -ag terminal-overrides ",xterm-256color:RGB"

# Status bar
set -g status-interval 5
set -g status-left "#[fg=green][#S] "
set -g status-right "#[fg=cyan]%H:%M %d-%b-%y"

# Reload config
bind r source-file ~/.tmux.conf \; display-message "Config reloaded!"
```

### tmuxp Session Files

Create `~/dotfiles/tmux/sessions/dev.yaml`:

```yaml
# ~/dotfiles/tmux/sessions/dev.yaml
session_name: dev
start_directory: ~/projects/my-project

windows:
  - window_name: editor
    layout: main-vertical
    panes:
      - shell_command: nvim
      - shell_command: bash

  - window_name: server
    panes:
      - shell_command: docker compose up

  - window_name: tools
    layout: even-horizontal
    panes:
      - shell_command: bash
      - shell_command: bash
```

```bash
# Start a session from a config file:
tmuxp load ~/dotfiles/tmux/sessions/dev.yaml

# Or using a project-local file:
tmuxp load .tmuxp.yaml

# List running sessions:
tmux ls

# Attach to a named session:
tmux attach-session -t dev

# Kill a session:
tmux kill-session -t dev
```

### `start.sh` Integration (postStartCommand)

```bash
# Auto-attach to dev session on Codespace start
if command -v tmuxp >/dev/null && [[ -f "$HOME/dotfiles/tmux/sessions/dev.yaml" ]]; then
  tmuxp load -d ~/dotfiles/tmux/sessions/dev.yaml 2>/dev/null || true
fi
```

---

## 7. Task Runners: just, task, make

### Quick Comparison

| Feature               | `make`           | `task` (go-task)       | `just`               |
|-----------------------|------------------|------------------------|----------------------|
| Language              | Make DSL         | YAML                   | justfile DSL         |
| Variables             | `VAR ?= val`     | `vars: VAR: val`       | `VAR := "val"`       |
| Dependency resolution | Yes (file-based) | Yes (task-based)       | Yes (explicit)       |
| Shell integration     | Full             | Full (sh/bash/cmd)     | Full                 |
| Cross-platform        | Partial          | ✅ (Go binary)         | ✅ (Rust binary)     |
| `.env` support        | Manual           | Built-in (`dotenv:`)   | Built-in             |
| Includes              | `include`        | `includes:`            | `import`             |
| Learn curve           | High (gotchas)   | Low (YAML)             | Very low             |
| Install size          | OS built-in      | ~10MB                  | ~5MB                 |

### `just` — Justfile

```makefile
# justfile
set dotenv-load  # auto-load .env

# Default recipe
default:
  @just --list

# Variables
BINARY := "myapp"
VERSION := `git describe --tags --abbrev=0`

# Build
build:
  cargo build --release

# Test with coverage
test:
  cargo test -- --nocapture
  cargo tarpaulin --out Html

# Docker build
docker-build tag=VERSION:
  docker build -t {{BINARY}}:{{tag}} .

# Aliases
alias b := build
alias t := test
```

```bash
# Run a recipe:
just build
just docker-build v1.2.3

# List all recipes:
just --list

# List with docs:
just --list --unsorted
```

### `task` (go-task) — Taskfile.yml

```yaml
# Taskfile.yml
version: '3'

# Global variables
vars:
  APP_NAME: myapp
  VERSION:
    sh: git describe --tags --abbrev=0
  BUILD_TIME:
    sh: date -u +"%Y-%m-%dT%H:%M:%SZ"

# Global environment
env:
  NODE_ENV: development
  DATABASE_URL:
    sh: echo $DATABASE_URL

# Load .env file
dotenv: ['.env', '.env.local']

# Task definitions
tasks:
  default:
    desc: List all tasks
    cmds:
      - task --list

  build:
    desc: Build the application
    cmds:
      - go build -ldflags "-X main.version={{.VERSION}}" -o dist/{{.APP_NAME}} ./cmd/...
    sources:
      - "**/*.go"
    generates:
      - dist/{{.APP_NAME}}

  test:
    desc: Run tests
    cmds:
      - go test ./... -v

  docker-build:
    desc: Build Docker image
    vars:
      TAG: '{{.TAG | default .VERSION}}'
    cmds:
      - docker build -t {{.APP_NAME}}:{{.TAG}} .

  ci:
    desc: Full CI pipeline
    deps: [build, test]
    cmds:
      - echo "CI passed for {{.APP_NAME}} {{.VERSION}}"
```

```bash
# Install
sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b ~/.local/bin

# Run a task:
task build
task docker-build TAG=v1.2.3

# Auto-complete:
task --list
```

### Include External Taskfiles

```yaml
# Taskfile.yml
includes:
  docker:
    taskfile: ./taskfiles/Docker.yml
    dir: .

  ci:
    taskfile: ./taskfiles/CI.yml
    vars:
      REGISTRY: ghcr.io
```

---

## 8. Version Management: direnv and asdf

### direnv — Per-Directory Environment

```bash
# Install
sudo apt-get install direnv      # Debian/Ubuntu
brew install direnv              # macOS

# Hook into bash (in ~/.bashrc, AFTER asdf):
eval "$(direnv hook bash)"
```

#### `.envrc` Patterns

```bash
# .envrc — project root

# Load .env file (gitignored secrets)
dotenv_if_exists .env
dotenv_if_exists .env.local

# Pin Node version (works with asdf)
use asdf nodejs 20.10.0

# Pin Python (works with asdf)  
use asdf python 3.12.2

# Add local bin to PATH
PATH_add bin
PATH_add .venv/bin

# Set project-specific vars
export APP_ENV=development
export LOG_LEVEL=debug
export DATABASE_URL="postgresql://localhost:5432/myapp_dev"

# Create venv automatically
layout python3

# Activate conda env
# layout anaconda myenv
```

```bash
# Allow a new/changed .envrc:
direnv allow .

# Revoke:
direnv deny .

# Check status:
direnv status

# Edit (auto-allows after):
direnv edit .
```

### asdf — Multi-Language Version Manager

```bash
# Install
git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.14.0

# Source in ~/.bashrc:
source "$HOME/.asdf/asdf.sh"
source "$HOME/.asdf/completions/asdf.bash"

# Add plugins:
asdf plugin add nodejs https://github.com/asdf-vm/asdf-nodejs.git
asdf plugin add python https://github.com/danhper/asdf-python.git
asdf plugin add golang https://github.com/asdf-community/asdf-golang.git
asdf plugin add rust https://github.com/code-lever/asdf-rust.git
asdf plugin add direnv https://github.com/asdf-community/asdf-direnv.git

# Install versions:
asdf install nodejs 20.10.0
asdf install python 3.12.2
asdf install golang 1.22.0

# Pin globally (writes to ~/.tool-versions):
asdf global nodejs 20.10.0
asdf global python 3.12.2

# Pin locally in a project (writes to .tool-versions):
asdf local nodejs 18.20.0
```

#### `~/.tool-versions` (global defaults)

```text
nodejs 20.10.0
python 3.12.2
golang 1.22.0
rust 1.76.0
```

### direnv + asdf Together

```bash
# In .envrc — use specific version just for this project:
use asdf nodejs 18.20.0
use asdf python 3.11.8

# asdf's PATH shim ensures tools from the specified version are used
# when you cd into the directory
```

---

## 9. Shell Scripting Best Practices

*Based on conventions from `awesome-copilot/instructions/shell.instructions.md`*

### Canonical Script Template

```bash
#!/usr/bin/env bash

# ============================================================================
# Script: script-name.sh
# Purpose: Brief description of what this script does
# Usage:   ./script-name.sh [OPTIONS]
# ============================================================================

set -euo pipefail

# ── Cleanup handler ──────────────────────────────────────────────────────────
TEMP_DIR=""

cleanup() {
  if [[ -n "${TEMP_DIR:-}" && -d "$TEMP_DIR" ]]; then
    rm -rf "$TEMP_DIR"
  fi
}
trap cleanup EXIT

# ── Constants ────────────────────────────────────────────────────────────────
readonly SCRIPT_NAME="$(basename "$0")"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Defaults ─────────────────────────────────────────────────────────────────
RESOURCE_GROUP=""
REQUIRED_PARAM=""
OPTIONAL_PARAM="default-value"

# ── Functions ─────────────────────────────────────────────────────────────────
usage() {
  cat <<EOF
Usage: $SCRIPT_NAME [OPTIONS]

Options:
  -g, --resource-group   Resource group (required)
  -n, --name             Name parameter (required)
  -o, --optional         Optional value (default: $OPTIONAL_PARAM)
  -h, --help             Show this help

Examples:
  $SCRIPT_NAME -g my-group -n my-name
EOF
  exit 0
}

log()   { echo "[$(date '+%H:%M:%S')] $*" >&2; }
error() { echo "ERROR: $*" >&2; exit 1; }

validate_requirements() {
  command -v jq  >/dev/null || error "'jq' is required but not installed"
  [[ -n "${RESOURCE_GROUP:-}" ]] || error "--resource-group is required"
  [[ -n "${REQUIRED_PARAM:-}" ]] || error "--name is required"
}

# ── Main ─────────────────────────────────────────────────────────────────────
main() {
  validate_requirements

  TEMP_DIR="$(mktemp -d)"
  log "Working directory: $TEMP_DIR"

  # Main logic here
  local result
  result=$(some_command | jq -r '.field // empty')
  [[ -n "$result" ]] || error "Empty result from some_command"

  log "SUCCESS: $result"
}

# ── Argument Parsing ──────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case $1 in
    -g|--resource-group) RESOURCE_GROUP="$2"; shift 2 ;;
    -n|--name)           REQUIRED_PARAM="$2";  shift 2 ;;
    -o|--optional)       OPTIONAL_PARAM="$2";  shift 2 ;;
    -h|--help)           usage ;;
    *) error "Unknown option: $1" ;;
  esac
done

main "$@"
```

### Key Rules

```bash
# 1. Always — fail-fast settings
set -euo pipefail
#     -e  exit on error
#     -u  treat unset vars as error
#     -o pipefail  propagate pipe failures

# 2. Double-quote ALL variable expansions
echo "$var"         # ✅
echo "${var}"       # ✅
echo $var           # ⛔ (word splitting, glob expansion)

# 3. Use [[ ]] not [ ]
[[ -f "$file" ]]    # ✅ (bash built-in, no word-splitting)
[ -f "$file" ]      # ⚠️  (POSIX sh, more error-prone)

# 4. Declare constants
readonly MAX_RETRIES=3
declare -r CONFIG_FILE="$HOME/.config/myapp/config.json"

# 5. Parse JSON with jq, YAML with yq — not grep/awk
value=$(jq -r '.key // empty' config.json)
[[ -n "$value" ]] || { echo "ERROR: key missing" >&2; exit 1; }

# 6. Use mktemp for temp files
tmpfile=$(mktemp)
tmpdir=$(mktemp -d)
trap 'rm -f "$tmpfile"; rm -rf "$tmpdir"' EXIT

# 7. Capture return codes explicitly
if ! output=$(some_command 2>&1); then
  echo "Command failed: $output" >&2
  exit 1
fi
```

### ShellCheck Integration

```bash
# Install
sudo apt-get install shellcheck
# or
brew install shellcheck

# Run on a script
shellcheck myscript.sh

# Run on all scripts in a repo
find . -name "*.sh" -exec shellcheck {} +

# VS Code: install timonwong.shellcheck extension
# Settings: "shellcheck.executablePath": "shellcheck"
```

---

## 10. VS Code MCP Registration

### Register ContextStream via `code --add-mcp`

```bash
# Register contextstream as an MCP server in VS Code:
code --add-mcp '{"name":"contextstream","type":"http","url":"https://mcp.contextstream.io/mcp?default_context_mode=fast"}'

# Or create a gh alias for convenience:
gh alias set add-mcp '!code --add-mcp "{\"name\":\"contextstream\",\"type\":\"http\",\"url\":\"https://mcp.contextstream.io/mcp?default_context_mode=fast\"}"'

# Then run:
gh add-mcp
```

### Register ContextStream as stdio MCP (alternative)

```bash
# Using the local binary directly:
code --add-mcp '{"name":"contextstream-stdio","type":"stdio","command":"contextstream-mcp","args":["run"]}'
```

### `mcp.json` (workspace-level MCP config)

```jsonc
// .vscode/mcp.json
{
  "servers": {
    "contextstream": {
      "type": "http",
      "url": "https://mcp.contextstream.io/mcp?default_context_mode=fast"
    },
    "context7": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    },
    "serena": {
      "type": "stdio",
      "command": "uvx",
      "args": ["--from", "serena", "serena", "--context", "ide-assistant"]
    }
  }
}
```

### Devcontainer MCP Auto-Registration

```bash
# .devcontainer/scripts/setup.sh
# Auto-register contextstream on container creation:

if command -v code >/dev/null; then
  code --add-mcp '{"name":"contextstream","type":"http","url":"https://mcp.contextstream.io/mcp?default_context_mode=fast"}' 2>/dev/null || true
  echo "✅ ContextStream MCP registered"
fi
```

---

## Quick Reference Card

| Task | Command |
| ---- | ------- |
| ContextStream version | `contextstream-mcp --version` |
| ContextStream alias | `alias contextstream='contextstream-mcp'` (in `~/.bashrc`) |
| Oh My Posh init | `eval "$(oh-my-posh init bash --config ~/theme.omp.json)"` |
| Oh My Posh export theme | `oh-my-posh config export --output ~/theme.omp.json` |
| Task run | `task build` / `task --list` |
| Just run | `just build` / `just --list` |
| direnv allow | `direnv allow .` |
| asdf install | `asdf install nodejs 20.10.0` |
| asdf global pin | `asdf global nodejs 20.10.0` |
| tmuxp load session | `tmuxp load sessions/dev.yaml` |
| Source bash config | `source ~/.bashrc` |
| MCP register | `code --add-mcp '{"name":"...","type":"http","url":"..."}'` |

---

Generated from: awesome-copilot shell.instructions.md, Oh My Posh docs (context7), go-task docs (context7), Codespaces devcontainer spec
