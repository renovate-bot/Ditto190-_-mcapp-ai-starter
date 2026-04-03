# Comprehensive Shell Guide

A practical reference for developers working with this project, covering terminal
tooling, environment management, task runners, session management, and
Context Stream registration in Bash.

---

## Table of Contents

1. [Context Stream Registration in Bash](#1-context-stream-registration-in-bash)
2. [Bash Profile Setup](#2-bash-profile-setup)
3. [Terminal Tooling](#3-terminal-tooling)
4. [Environment Management](#4-environment-management)
5. [Task Runners](#5-task-runners)
6. [Session Management](#6-session-management)
7. [Shell Scripting Best Practices](#7-shell-scripting-best-practices)
8. [Resources](#8-resources)

---

## 1. Context Stream Registration in Bash

Context Stream is an AI-context service that provides persistent memory, semantic
code search, and knowledge graphs across sessions. Its CLI must be resolvable by
your shell for the MCP server and helper scripts to function.

### Automatic Setup (recommended)

Run the provided profile bootstrap script once:

```bash
bash scripts/bash_profile.sh
```

This script detects where Context Stream (or its `npx` shim) is installed and
adds it to your `PATH` permanently in `~/.bashrc`.

### Manual Steps

**Step 1 – Verify installation**

```bash
contextstream --version
# or, if using npx:
npx @contextstream/mcp-server@latest --version
```

**Step 2 – Locate the binary**

```bash
which contextstream || find "$HOME/.local" /usr/local/bin -name contextstream 2>/dev/null
```

Common locations:
| Method | Default path |
|---|---|
| Global npm | `~/.npm-global/bin` or `/usr/local/lib/node_modules/.bin` |
| `npm install -g` | `$(npm root -g)/../bin` |
| `npx` (on-demand) | No permanent binary — use `npx @contextstream/mcp-server@latest` |
| Manual download | `~/.local/bin` |

**Step 3 – Add to `~/.bashrc`**

```bash
# Replace <path_to_contextstream> with the directory containing the binary
echo 'export PATH="$PATH:<path_to_contextstream>"' >> ~/.bashrc
source ~/.bashrc
```

**Step 4 – Verify**

```bash
contextstream --version
```

### VS Code / Codespace Configuration

The MCP server is already wired via `.vscode/mcp.json` to invoke Context Stream
through `npx`, so no system-wide PATH change is needed for VS Code. PATH
registration is primarily required when running helper scripts from the
integrated terminal or in CI/CD.

---

## 2. Bash Profile Setup

The `scripts/bash_profile.sh` script bootstraps a developer environment by:

- Detecting and registering Context Stream in `PATH`
- Configuring `uv`/Python, Node.js, and common CLI tool paths
- Exporting sensible defaults for this project

### Usage

```bash
# First-time setup (idempotent — safe to run multiple times)
bash scripts/bash_profile.sh

# Apply changes to the current session immediately
source ~/.bashrc
```

### What it does

| Section | Action |
|---|---|
| Context Stream | Adds binary path to `PATH` if found |
| `uv` / Python | Exports `$HOME/.local/bin` for `uv` and `ruff` |
| Node.js PATH | Adds `npm` global bin dir to `PATH` |
| `asdf` | Sources `asdf.sh` if installed |
| `direnv` | Adds `eval "$(direnv hook bash)"` if installed |
| `.env` guard | Warns if `.env` is missing in the project root |

---

## 3. Terminal Tooling

### Oh My Posh (prompt theming)

[Oh My Posh](https://ohmyposh.dev/docs/configuration/general) gives your prompt
rich contextual information such as Git status, runtime versions, and execution
time. It works with any modern shell.

```bash
# Install (Linux / macOS via Homebrew)
brew install jandedobbeleer/oh-my-posh/oh-my-posh

# Apply a theme
eval "$(oh-my-posh init bash --config ~/.config/ohmyposh/theme.json)"
```

Add the `eval` line to `~/.bashrc` for persistence.

### Neovim (editor)

If you prefer a terminal editor, the [awesome-neovim-modme](https://github.com/Ditto190/awesome-neovim-modme.git)
collection contains curated plugin configurations, including LSP, Treesitter, and
AI-assisted editing.

```bash
# Install Neovim (Debian / Ubuntu)
sudo apt install neovim

# Clone the modme configuration
git clone https://github.com/Ditto190/awesome-neovim-modme.git ~/.config/nvim
```

### Useful CLI Utilities

| Tool | Purpose | Install |
|---|---|---|
| `jq` | JSON processor | `apt install jq` / `brew install jq` |
| `yq` | YAML processor | `snap install yq` / `brew install yq` |
| `fzf` | Fuzzy finder | `apt install fzf` / `brew install fzf` |
| `ripgrep` (`rg`) | Fast regex search | `apt install ripgrep` / `brew install ripgrep` |
| `bat` | `cat` with syntax highlighting | `apt install bat` / `brew install bat` |
| `htop` | Process monitor | `apt install htop` |
| `shellcheck` | Shell script linter | `apt install shellcheck` |

---

## 4. Environment Management

### direnv — per-directory environment variables

[direnv](https://direnv.net) automatically loads and unloads `.envrc` files when
you enter or leave a directory. This keeps secrets and project-specific settings
isolated without polluting the global shell.

```bash
# Install
sudo apt install direnv   # or: brew install direnv

# Hook into Bash (add to ~/.bashrc)
eval "$(direnv hook bash)"

# Allow a project's .envrc
cd /path/to/project
direnv allow .
```

**Typical `.envrc` for this project:**

```bash
# .envrc
export N8N_API_KEY="$(grep N8N_API_KEY .env | cut -d= -f2)"
export N8N_HOST="http://localhost:5678"
layout python3
```

### asdf — multi-runtime version manager

[asdf](https://asdf-vm.com) manages multiple runtime versions (Node.js, Python,
Ruby, etc.) per project using a `.tool-versions` file.

```bash
# Install
git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.15.0

# Add to ~/.bashrc
echo '. "$HOME/.asdf/asdf.sh"' >> ~/.bashrc
echo '. "$HOME/.asdf/completions/asdf.bash"' >> ~/.bashrc
source ~/.bashrc

# Add plugins and install versions
asdf plugin add nodejs
asdf install nodejs 20.12.0
asdf global nodejs 20.12.0

asdf plugin add python
asdf install python 3.12.3
asdf global python 3.12.3
```

### uv — fast Python environment manager

[uv](https://astral.sh/uv) is the Python tool manager used throughout this
project (see `post-create.sh`).

```bash
# Install
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"   # or handled by bash_profile.sh

# Sync a project
uv sync --extra dev

# Run a tool without global install
uv run ruff check .
```

### .env Management

Sensitive configuration lives in `.env` (never committed). Use `.env.example` as
the template:

```bash
cp .env.example .env
# Edit .env with your API keys
```

Use `scripts/bash_profile.sh` or `setup-llm.sh` to populate keys interactively:

```bash
bash .devcontainer/scripts/setup-llm.sh
```

---

## 5. Task Runners

### Make

`make` is available on virtually every Unix system. It is ideal for orchestrating
common project commands.

```makefile
# Makefile example for this project
.PHONY: up down logs test

up:
	docker compose --profile cpu up -d

down:
	docker compose down

logs:
	docker compose logs -f n8n

test:
	bash scripts/test-runner.sh
```

```bash
make up
make test
```

### Task (Taskfile.yml)

[Task](https://taskfile.dev) uses a human-friendly `Taskfile.yml` format and
supports variables, dependencies, and cross-platform portability.

```bash
# Install
sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b ~/.local/bin
```

Example `Taskfile.yml`:

```yaml
version: '3'

tasks:
  up:
    desc: Start the AI stack
    cmds:
      - docker compose --profile cpu up -d

  logs:
    desc: Tail n8n logs
    cmds:
      - docker compose logs -f n8n

  test:
    desc: Run all test suites
    cmds:
      - bash scripts/test-runner.sh

  generate-agents:
    desc: Generate AGENTS.md for a repo
    vars:
      REPO: '{{.REPO | default "."}}'
    cmds:
      - cd GenerateAgents.md && uv run autogenerateagentsmd {{.REPO}} --style comprehensive
```

```bash
task up
task test
task generate-agents REPO=../my-other-repo
```

### npm scripts

Node.js projects in this repository expose common workflows through `package.json`
`scripts`. Use `npm run` to discover and execute them:

```bash
npm run          # List all available scripts
npm run build    # Build the SDK / examples
npm test         # Run unit tests
npm start        # Start the examples server (port 8080)
```

---

## 6. Session Management

### tmux — terminal multiplexer

[tmux](https://github.com/tmux/tmux/wiki) lets you run multiple terminal sessions
inside a single window, detach from running processes, and reattach later—ideal
for long-running Docker stacks and background jobs.

```bash
# Install
sudo apt install tmux   # or: brew install tmux

# Basic usage
tmux new -s ai-starter      # New named session
tmux attach -t ai-starter   # Reattach to existing session
tmux ls                     # List sessions

# Detach (inside tmux): Ctrl-b d
# Split pane horizontally: Ctrl-b "
# Split pane vertically: Ctrl-b %
# Switch pane: Ctrl-b <arrow>
```

**Suggested tmux layout for this project:**

```
┌──────────────────────┬──────────────────────┐
│  docker compose logs │  shell / editor      │
│  -f n8n              │                      │
├──────────────────────┴──────────────────────┤
│  docker compose logs -f ollama              │
└────────────────────────────────────────────-┘
```

### Sprig Terminal

The [Sprig Terminal](https://github.com/Ditto190/sprig-terminal.git) project
provides additional terminal utilities and configuration files to enhance the
development experience.

```bash
git clone https://github.com/Ditto190/sprig-terminal.git ~/.config/sprig-terminal
bash ~/.config/sprig-terminal/install.sh
```

### VS Code Integrated Terminal Profiles

For Codespace / VS Code users, you can load the project environment in every
integrated terminal by creating a small wrapper init file that sources the
standard shell files first, then the project profile:

```bash
# Create a one-time wrapper at ~/.config/ai-starter-init.sh
cat > ~/.config/ai-starter-init.sh << 'EOF'
# Source standard bash initialisation
[[ -f ~/.bashrc ]] && source ~/.bashrc
# Apply project profile (idempotent — only adds missing entries)
[[ -f "${WORKSPACE_FOLDER}/scripts/bash_profile.sh" ]] && \
    bash "${WORKSPACE_FOLDER}/scripts/bash_profile.sh" --quiet 2>/dev/null || true
EOF
```

Then reference it in `.vscode/settings.json`:

```jsonc
{
  "terminal.integrated.env.linux": {
    "WORKSPACE_FOLDER": "${workspaceFolder}"
  },
  "terminal.integrated.profiles.linux": {
    "bash (project)": {
      "path": "bash",
      "args": ["--rcfile", "${env:HOME}/.config/ai-starter-init.sh"]
    }
  },
  "terminal.integrated.defaultProfile.linux": "bash (project)"
}
```

This ensures standard bash initialisation (aliases, functions, history, etc.)
is preserved while the project environment is applied on top.

Alternatively, simply add the following line to your `~/.bashrc` (which
`bash_profile.sh` already does for most settings):

```bash
# At the bottom of ~/.bashrc
[[ -f /path/to/workspaces/scripts/bash_profile.sh ]] && \
    bash /path/to/workspaces/scripts/bash_profile.sh
```

---

## 7. Shell Scripting Best Practices

All shell scripts in this project follow the conventions described in
[`consolidated_sources/awesome-copilot/instructions/shell.instructions.md`](../consolidated_sources/awesome-copilot/instructions/shell.instructions.md).

Key rules at a glance:

- **Shebang:** `#!/bin/bash`
- **Safety flags:** `set -euo pipefail` at the top of every script
- **Cleanup:** use `trap cleanup EXIT` with a `cleanup()` function
- **Temp files:** create with `mktemp` and delete in `cleanup()`
- **Variables:** double-quote all expansions (`"$var"`); use `readonly` for constants
- **JSON/YAML:** use `jq`/`yq` — never `grep`/`awk` on structured data
- **Validation:** check required parameters before doing any work
- **Linting:** run `shellcheck` before committing

---

## 8. Resources

| Resource | URL |
|---|---|
| Awesome Sysadmin | https://github.com/Ditto190/awesome-sysadmin.git |
| Awesome Neovim Modme | https://github.com/Ditto190/awesome-neovim-modme.git |
| Sprig Terminal | https://github.com/Ditto190/sprig-terminal.git |
| Oh My Posh Docs | https://ohmyposh.dev/docs/configuration/general |
| ContextStream MCP Docs | https://contextstream.io/docs/mcp |
| asdf-vm | https://asdf-vm.com |
| direnv | https://direnv.net |
| uv (Python) | https://astral.sh/uv |
| Task runner | https://taskfile.dev |
| tmux wiki | https://github.com/tmux/tmux/wiki |

---

See also:
- [`docs/CONTEXTSTREAM_BASH_REGISTRATION.md`](CONTEXTSTREAM_BASH_REGISTRATION.md) — step-by-step Context Stream PATH registration
- [`docs/contextstream-initialization-guide.md`](contextstream-initialization-guide.md) — first-time workspace initialization
- [`scripts/bash_profile.sh`](../scripts/bash_profile.sh) — automated profile bootstrap script
