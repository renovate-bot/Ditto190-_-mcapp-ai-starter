# 🚀 QUICK REFERENCE - Awesome-Copilot Multi-Project Setup

## One-Line Setup Check

```bash
cd /workspaces/mcapp-ai-starter && uv --version && npm ci --version && python3 --version
```

---

## 📦 Working on Projects

### awesome-copilot (Node.js)

```bash
cd consolidated_sources/awesome-copilot
npm ci                    # Install deps (already done ✅)
npm run build             # Build (already done ✅)
npm run skill:validate    # Validate skills
```

### generateagents-mcp (Python)

```bash
cd generateagents-mcp
uv sync                   # Install deps
uv run python verify.py   # Run script
uv run pytest            # Run tests
```

### GenerateAgents.md (Python)

```bash
cd GenerateAgents.md
uv sync --extra dev      # Install with dev tools
uv run pytest -m 'not e2e' -q
uv run autogenerateagentsmd . --style comprehensive
```

---

## 🎯 From Workspace Root (Anywhere)

```bash
# Run Python in any project context
uv --project ./generateagents-mcp run verify.py
uv --project ./GenerateAgents.md run pytest

# Add a dependency to a project
uv add -p generateagents-mcp new-package
uv add -p GenerateAgents.md new-package

# Format/lint code
uv run black .
uv run ruff check .
uv run mypy .
```

---

## 🔍 Key Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Root workspace config (UV's "package.json" for Python) |
| `UV_SETUP_GUIDE.md` | Detailed multi-project guide |
| `INSTALLATION_COMPLETE.md` | This session's full summary |
| `.envrc` | Environment setup (direnv) |
| `tools/nix/flake.nix` | Optional Nix reproducibility |

---

## ✨ Why UV (Instead of venv)?

| Benefit | Why It Matters |
|---------|----------------|
| **No per-project venv** | Work on multiple projects without activation/deactivation |
| **Global cache** | Dependencies cached once, reused everywhere (~/.cache/uv/) |
| **Fast switching** | Switch projects instantly, no "activate/deactivate" dance |
| **Nix integration** | Pairs perfectly with your flake.nix |
| **Less disk space** | Single cache instead of 100MB+ per project |

---

## 🧪 Test the Setup

```bash
# Verify everything works
cd /workspaces/mcapp-ai-starter/generateagents-mcp
uv sync
uv run python -c "import mcp; print('✓ MCP module available')"
```

---

## 📖 Documentation

- **Full Guide:** `UV_SETUP_GUIDE.md`
- **This Session:** `INSTALLATION_COMPLETE.md`
- **Setup Details:** This file (QUICK_REFERENCE.md)

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| "command not found: uv" | `export PATH="$HOME/.local/bin:$PATH"` (or source `.envrc`) |
| "uv: command not found" after installing | Restart terminal or `source ~/.bashrc` |
| "Python not found" | `uv run python3 --version` |
| "Package not found" | `uv add package-name` (not pip install) |
| Cache taking too much space | `rm -rf ~/.cache/uv/` (nuclear option) |

---

## ✅ Status Checklist

- [x] awesome-copilot: 72 npm packages, 48 plugins
- [x] Root pyproject.toml: workspace configured
- [x] UV: v0.11.3 available
- [x] Python: 3.12.13 ready
- [x] Node: 20.20.2 ready
- [x] Documentation: Complete

**You're ready to use awesome-copilot tools! 🎉**

---

*Last Updated: April 4, 2026 | Setup Method: UV-based multi-project*
