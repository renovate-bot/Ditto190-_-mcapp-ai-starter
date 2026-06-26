# UV Multi-Project Dependency Management Guide

#

# This workspace uses UV (<https://docs.astral.sh/uv/>) instead of per-project venvs

# for flexible, cross-project dependency management

## Quick Start

### For awesome-copilot (Node.js)

```bash
cd /workspaces/mcapp-ai-starter/consolidated_sources/awesome-copilot
npm ci              # Install from lock file
npm run build       # Generate marketplace.json + README updates
npm run skill:validate    # Validate skills
npm run plugin:validate   # Validate plugins
```

### For Python Projects (generateagents-mcp, GenerateAgents.md, etc.)

```bash
# Use UV to run scripts without activating a venv per project
cd /workspaces/mcapp-ai-starter/generateagents-mcp
uv sync                    # Install dependencies (global cache)
uv run verify.py           # Run verification script
uv python --version        # Check Python version used

# Or from root, use project-specific commands:
cd /workspaces/mcapp-ai-starter
uv --project ./generateagents-mcp run pytest
uv --project ./GenerateAgents.md run pytest -m 'not e2e'
```

## Why UV instead of venv?

1. **No Project Pollution**: Dependencies cached globally in ~/.cache/uv/
2. **Project Switching**: Easy switching between multiple projects without reactivating
3. **Faster Reinstalls**: Reuses cached packages across projects
4. **Cross-Language**: Works with Python, Node.js, Rust, etc. seamlessly
5. **Nix Compatible**: Pairs well with the flake.nix in tools/nix/ for reproducibility

## Project Structure with UV

```
/workspaces/mcapp-ai-starter/
├── pyproject.toml                    # Root UV config (declares managed projects)
├── package.json                      # Root Node.js (not a workspace)
├── awesome-copilot/
│   ├── package.json                  # Node project (use npm)
│   ├── npm ci && npm run build
│   └── .github/plugin/marketplace.json  # Build output
├── generateagents-mcp/
│   ├── pyproject.toml                # Python project (use uv sync)
│   ├── uv sync
│   └── uv run verify.py
├── GenerateAgents.md/
│   ├── pyproject.toml                # Python project (use uv sync)
│   ├── uv sync --extra dev
│   └── uv run pytest -m 'not e2e'
└── tools/
    └── nix/
        ├── flake.nix                 # Optional: Full reproducibility
        └── home.nix                  # Optional: Home Manager config
```

## Commands by Use Case

### Working on awesome-copilot

```bash
cd consolidated_sources/awesome-copilot
npm ci
npm run build
npm run skill:validate
npm run plugin:validate
```

### Working on generateagents-mcp

```bash
cd generateagents-mcp
uv sync                               # Install deps (no venv created)
uv run python verify.py               # Run script
uv run pytest -xvs tests/             # Run tests
```

### Working on GenerateAgents.md

```bash
cd GenerateAgents.md
uv sync --extra dev                   # Install with dev deps
uv run pytest -m 'not e2e' -q         # Run non-e2e tests
uv run autogenerateagentsmd . --style comprehensive
```

### Running Python tools from anywhere

```bash
# From workspace root, target specific project
uv --project ./generateagents-mcp run verify.py
uv --project ./GenerateAgents.md run pytest

# Or use uv tool run for ad-hoc script execution
uv run python -c "import yaml; print(yaml.safe_load('...'))"
```

## Optional: Nix Integration

For full reproducibility across systems, use the Nix flake:

```bash
# Activate Nix dev environment (includes Node 20, Python 3.12, UV, etc.)
nix develop

# Or with direnv (install: https://direnv.net/)
direnv allow
# Your shell automatically loads the Nix dev environment when entering this directory
```

## Switching Projects Without Venv Overhead

**Before (with venv):**

```bash
cd project-a
source .venv/bin/activate
# ... work ...
deactivate
cd ../project-b
source .venv/bin/activate
# Lots of context switching overhead
```

**After (with UV):**

```bash
cd project-a
uv sync
# ... work ...

cd ../project-b
uv sync
# UV reuses cached deps, much faster!
# No venv activation needed
```

## Global Tool Installation via UV

For tools you want available everywhere:

```bash
# Install globally (adds to ~/.local/bin)
uv tool install black
uv tool install ruff
uv tool install mypy

# List installed tools
uv tool list

# Run without installation
uv run --python 3.12 my-script.py
```

## Directory Structure for UV

UV looks for project configuration in this order:

1. `pyproject.toml` (root level) with `[tool.uv.workspace]`
2. `pyproject.toml` in subdirectories (individual project configs)
3. Environment variables (UV_PROJECT_ENVIRONMENT, etc.)

The root `pyproject.toml` we created defines the workspace strategy.

## Troubleshooting

**Q: How do I know UV is using the global cache?**

```bash
du -sh ~/.cache/uv/
# Should show a reasonable size, not multiple GBs per project
```

**Q: How do I force a fresh install?**

```bash
uv sync --refresh  # Refreshes all dependencies
rm ~/.cache/uv/*/  # Nuclear option (clear cache)
```

**Q: Can I use both npm and uv in the same workspace?**
Yes! Use npm for Node.js projects (awesome-copilot) and uv for Python projects. They work independently.

**Q: How do I add a dependency to a Python project?**

```bash
cd project-name
uv add package-name              # Add to main dependencies
uv add --dev package-name        # Add to dev dependencies
# This updates pyproject.toml and uv.lock
```

## Next Steps

1. ✅ awesome-copilot installed and built
2. Set up generateagents-mcp: `cd generateagents-mcp && uv sync`
3. Set up GenerateAgents.md: `cd GenerateAgents.md && uv sync --extra dev`
4. Optional: `nix develop` to activate full reproducible environment
5. Start using MCP tools in VS Code Copilot and Claude

## References

- [UV Documentation](https://docs.astral.sh/uv/)
- [UV Workspace Configuration](https://docs.astral.sh/uv/concepts/projects/)
- [Nix Flakes Documentation](https://nixos.wiki/wiki/Flakes)
- awesome-copilot Build Status: ✅ marketplace.json (15 KB) 48 plugins
