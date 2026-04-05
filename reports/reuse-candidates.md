Top-3 Neovim reuse candidates

1) Plugin loader using folke/lazy.nvim
   - Why: centralizes plugin management, fast startup, supports declarative plugin specs.
   - Integration pattern: put `init.lua` that bootstraps `lazy.nvim` and `lua/loader.lua` for specs. In Nix devShell set `XDG_CONFIG_HOME` to repo `nvim/` and bootstrap `lazy.nvim` in `init.lua` (see `nvim/init.lua` and `nvim/lua/loader.lua`).

2) LSP + lspconfig setup (pyright + rust_analyzer)
   - Why: language support commonly reused across projects.
   - Integration: add `nvim-lspconfig` to loader and configure in-line or via separate `lua/lsp/*.lua` modules. In home-manager, ensure `programs.neovim.enable = true` and include required packages in `home.packages` or `environment.systemPackages` in a flake.

3) Treesitter + Telescope user workflows
   - Why: code navigation & parsing are high-value reuses.
   - Integration: include `nvim-treesitter` (with `build=':TSUpdate'`) and `telescope.nvim` in loader; ensure `tree-sitter` parsers are kept up-to-date in devShell via `nvim --headless -c ':TSUpdate' -c qa!` on bootstrap.

Top-3 Nix reuse candidates

1) Home Manager module for Neovim configuration
   - Pattern: provide a reusable `nix/modules/home-manager.nix` that enables `programs.neovim` and references the repo loader. Our flake exposes `homeConfigurations.default` that imports `./nix/modules/home-manager.nix`.

2) devShell for vibe-coder
   - Pattern: a `devShells.x86_64-linux.vibe-coder` in `flake.nix` that provisions `neovim`, `nodejs`, `python3`, and sets `$XDG_CONFIG_HOME` to workspace `nvim/`. See `nix/flake.nix`.

3) Flake + inputs standardization
   - Pattern: standardize `inputs` (nixpkgs, home-manager) and expose `devShells` + `homeConfigurations` so repo consumers can `nix develop` or `home-manager switch` from the flake.

Files added

- `nix/flake.nix` — flake with `devShells.vibe-coder` and `homeConfigurations`.
- `nix/modules/home-manager.nix` — home-manager module enabling neovim.
- `nvim/init.lua`, `nvim/lua/loader.lua` — loader-based Neovim config.
- `Makefile` and `justfile` — helper targets (inventory, devshell, bootstrap-nvim).
- `pr-snippets/*` — PR-ready snippets for flake inputs, home.nix, nvim loader checklist.
