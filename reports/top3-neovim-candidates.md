# Top-3 Neovim Candidates — mcapp-ai-starter

**Generated from research synthesis + repo analysis (mason.nvim, devcontainer.vim, tree-sitter-vimdoc, tree-sitter-vimdoc-vim)**

## Codebase Profile

| Signal | Finding |
|--------|---------|
| Primary language | **TypeScript / JavaScript** (`n8n ^2.10.3`, `axios`, MCP Apps SDK `src/*.ts`) |
| Secondary languages | **Python** (`GenerateAgents.md/`, `generateagents-mcp/`), **Nix** (`flake.nix`, `home-manager.nix`), **Lua** (Neovim config) |
| Dev environment | **GitHub Codespaces** (devcontainer), Docker Compose stack |
| API schemas | Many YAML files (n8n workflows, GH Actions, OAS specs) |
| Documentation type | Vim-style help (`AGENTS.md`, `SKILL.md`, `.agent.md`) which align with vimdoc/markdown parsers |

---

## Candidate 1 — mason.nvim + mason-lspconfig + nvim-lspconfig

**Verdict: ESSENTIAL**

| Attribute | Value |
|-----------|-------|
| Repos | `mason-org/mason.nvim`, `mason-org/mason-lspconfig.nvim`, `neovim/nvim-lspconfig` |
| Role | Automatic LSP server installation and wiring |
| Why this codebase | TypeScript is the primary language → `ts_ls` must be available; Python → `pyright`; Nix → `nil_ls`; Lua → `lua_ls` |
| Integration model | mason installs binaries to `~/.local/share/nvim/mason/bin/`; mason-lspconfig.setup_handlers wires each installed server through lspconfig |

### Lazy.nvim spec (as implemented in `nvim/lua/loader.lua`)

```lua
{ "mason-org/mason.nvim",            build = ":MasonUpdate", opts = { ui = { border = "rounded" } } },
{ "mason-org/mason-lspconfig.nvim",
  dependencies = { "mason-org/mason.nvim", "neovim/nvim-lspconfig" },
  opts = { ensure_installed = { "ts_ls", "pyright", "lua_ls", "nil_ls" }, automatic_installation = true }
},
{ "neovim/nvim-lspconfig" },
```

### Nix complement (devShell extraPackages)

```nix
nodePackages.typescript-language-server  # fallback when mason not yet run
nodePackages.pyright
lua-language-server
nil
```

---

## Candidate 2 — nvim-treesitter (with vimdoc + typescript + nix parsers)

**Verdict: ESSENTIAL**

| Attribute | Value |
|-----------|-------|
| Repo | `nvim-treesitter/nvim-treesitter` |
| tree-sitter-vimdoc | **Built in** — `ensure_installed = { "vimdoc" }` pulls the official `neovim/tree-sitter-vimdoc` grammar (v4.1.0 / Apache-2.0) |
| Key parsers for this repo | `vimdoc`, `typescript`, `tsx`, `javascript`, `python`, `nix`, `yaml`, `json`, `markdown` |
| Why vimdoc matters | AGENTS.md, SKILL.md, and .agent.md files follow vimdoc heading patterns; the parser enables structured navigation, textobjects, and injection queries without a separate plugin |

### tree-sitter-vimdoc node types used by vimdoc parser

```
@markup.heading.1/2/3/4  — h1 (======), h2 (------), h3 (uppercase), h4 (~)
@label                    — tag *foo* (cross-reference anchors)
@markup.link              — taglink |foo|, optionlink 'opt'
@markup.raw               — codespan `code`, codeblock starting with >
```

### tree-sitter-vimdoc-vim (tools/external/tree-sitter-vimdoc-vim)

A vendored local copy (`Ditto190/tree-sitter-vimdoc-vim`), identical to `neovim/tree-sitter-vimdoc` at v4.1.0.  
**Recommendation**: Use the upstream nvim-treesitter bundled version — no separate plugin needed.

---

## Candidate 3 — devcontainer.vim (Go binary)

**Verdict: HIGH VALUE for Codespaces workflow**

| Attribute | Value |
|-----------|-------|
| Repo | `mikoto2000/devcontainer.vim` |
| Type | **Go binary** (not a Neovim Lua plugin) |
| Role | Launch Neovim *inside* a running devcontainer from the host, with clipboard passthrough |
| Why this codebase | The repo lives in Codespaces with an active `.devcontainer/` and `docker-compose.yml`; devcontainer.vim enables a Vim-first workflow without abandoning the devcontainer runtime |
| lazy.nvim | Loaded conditionally: `cond = function() return vim.fn.executable("devcontainer.vim") == 1 end` |

### Usage

```bash
# Build from tools/external
make build-devcontainer-vim      # → bin/devcontainer.vim

# Launch Neovim inside the running devcontainer (--nvim flag)
devcontainer.vim --nvim start .
```

### Integration files

- `.devcontainer/devcontainer.vim.json` — mount nvim config, clipboard port 49200
- `loader.lua` — conditional plugin spec sets `vim.g.devcontainer_vim_nvim = 1`
- `flake.nix` devShell — `go` in buildInputs + shellHook builds binary on first entry

---

## Honorable Mentions

| Plugin | Reason not Top-3 | When to add |
|--------|-----------------|-------------|
| `nvim-telescope/telescope.nvim` | Quality-of-life, not core toolchain | Already added to loader.lua |
| `hrsh7th/nvim-cmp` | Completion UX, depends on LSP being working first | Already added to loader.lua |
| `nvimtools/none-ls.nvim` | null-ls replacement for Spectral/ESLint linting inside Neovim | Add if in-editor OpenAPI lint is needed |
| `folke/trouble.nvim` | LSP diagnostic list UI | Add after LSPs are stable |

---

## Delivery Checklist

| Item | File | Status |
|------|------|--------|
| LSP devShell (ts_ls, pyright, nil, lua-ls, spectral) | `nix/flake.nix` | ✅ |
| home-manager LSP extraPackages + mason autocmd | `nix/modules/home-manager.nix` | ✅ |
| mason + treesitter + devcontainer plugin specs | `nvim/lua/loader.lua` | ✅ |
| Spectral ruleset | `.spectral.yaml` | ✅ |
| devcontainer.vim config | `.devcontainer/devcontainer.vim.json` | ✅ |
| Plenary test suite | `nvim/tests/plugins_spec.lua` | ✅ |
| `make test-nvim` target | `Makefile` | ✅ |
| `make lint-api` target | `Makefile` | ✅ |
| `make build-devcontainer-vim` target | `Makefile` | ✅ |
