# Context Stream Bash Registration Guide

## Overview

This guide provides instructions on how to register the Context Stream command
in your Bash environment, ensuring that it is accessible from the terminal.

> **Quick path:** Run `bash scripts/bash_profile.sh` to auto-detect the
> installation and register it in `~/.bashrc` in one step.  
> See [`docs/SHELL_GUIDE.md`](SHELL_GUIDE.md) for the full environment
> reference covering terminal tooling, environment management, task runners,
> and session management.

---

## Automated Registration (recommended)

```bash
bash scripts/bash_profile.sh
source ~/.bashrc
```

The script detects where Context Stream is installed, appends the correct
`export PATH=…` entry to `~/.bashrc` (idempotent — safe to run multiple times),
and prints a summary of every change it makes.

---

## Manual Steps

### Step 1: Verify Installation

Ensure that Context Stream is installed correctly:

```bash
contextstream --version
# or, using npx (no global install required):
npx @contextstream/mcp-server@latest --version
```

If you receive a `command not found` error, proceed to the next step.

### Step 2: Install Context Stream

```bash
# Option A — global npm install
npm install -g @contextstream/mcp-server

# Option B — interactive setup wizard (recommended for first-time users)
npx @contextstream/mcp-server@latest setup
```

### Step 3: Locate the Installation Path

Find out where Context Stream was installed:

```bash
which contextstream
# Common locations:
#   ~/.npm-global/bin/contextstream
#   /usr/local/lib/node_modules/.bin/contextstream
#   ~/.local/bin/contextstream
```

### Step 4: Update Your Bash Profile

Open `~/.bashrc` in an editor and add the path found above:

```bash
nano ~/.bashrc
```

Append (replacing `<path_to_contextstream>` with the actual directory):

```bash
export PATH="$PATH:<path_to_contextstream>"
```

### Step 5: Apply Changes

```bash
source ~/.bashrc
```

### Step 6: Verify

```bash
contextstream --version
```

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| `command not found: contextstream` | Not installed, or not on PATH | Install via `npm install -g @contextstream/mcp-server`, then run `bash scripts/bash_profile.sh` |
| Works in VS Code terminal but not SSH | SSH opens a login shell that sources `~/.bash_profile` (not `~/.bashrc`) | Add `[[ -f ~/.bashrc ]] && source ~/.bashrc` to `~/.bash_profile` so both files share the same PATH entries |
| `npx` works but the binary does not | Only on-demand install | Use `npm install -g …` for a permanent binary |
| Changes lost after reboot | Added to wrong file | Keep PATH exports in `~/.bashrc` and ensure `~/.bash_profile` sources it (login shells read only `~/.bash_profile`) |

---

## Additional Tools

See [`docs/SHELL_GUIDE.md`](SHELL_GUIDE.md) for full details. Quick reference:

| Tool | Purpose |
|---|---|
| **Make** | Task runner for build automation |
| **Task** | Human-friendly task runner (`Taskfile.yml`) |
| **Direnv + asdf** | Per-project environment variables and tool versions |
| **Tmux** | Terminal multiplexer — keep sessions alive after disconnect |
| **Oh My Posh** | Rich, configurable shell prompt |

---

## Resources

- [Awesome Sysadmin](https://github.com/Ditto190/awesome-sysadmin.git)
- [Awesome Neovim Modme](https://github.com/Ditto190/awesome-neovim-modme.git)
- [Sprig Terminal](https://github.com/Ditto190/sprig-terminal.git)
- [Oh My Posh Documentation](https://ohmyposh.dev/docs/configuration/general)
- [ContextStream MCP Docs](https://contextstream.io/docs/mcp)
- [Full Shell Guide](SHELL_GUIDE.md) — terminal tooling, environment management, task runners, session management