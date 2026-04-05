{ config, pkgs, lib, ... }:

let
  username = if builtins.getEnv "USER" != "" then builtins.getEnv "USER" else "user";
in {
  programs.neovim = {
    enable = true;
    package = pkgs.neovim;
    viAlias = true;

    # LSP binaries made available to Neovim (mason.nvim can augment these at runtime)
    extraPackages = with pkgs; [
      # TypeScript / JavaScript  (primary — this is a TS/Node.js codebase)
      nodePackages.typescript-language-server
      # Python  (GenerateAgents.md, generateagents-mcp)
      nodePackages.pyright
      # Lua  (Neovim config files)
      lua-language-server
      # Nix  (flake.nix, home-manager modules)
      nil
      # OpenAPI / AsyncAPI linting via Spectral
      nodePackages."@stoplight/spectral-cli"
    ];

    extraLuaConfig = ''
      -- ── Mason auto-install bootstrap ──────────────────────────────────────
      -- mason.nvim is loaded via lazy.nvim (loader.lua).
      -- This block fires after plugins are ready and ensures LSPs are installed.
      vim.api.nvim_create_autocmd("User", {
        pattern = "LazyDone",
        once    = true,
        callback = function()
          -- Verify mason-lspconfig is available before calling
          local ok_mason, mason = pcall(require, "mason")
          local ok_mlsp, mlsp   = pcall(require, "mason-lspconfig")
          if ok_mason and ok_mlsp then
            mason.setup({ ui = { border = "rounded" } })
            mlsp.setup({
              ensure_installed = {
                "ts_ls",     -- TypeScript / JavaScript
                "pyright",   -- Python
                "lua_ls",    -- Lua / Neovim configs
                "nil_ls",    -- Nix flakes
              },
              automatic_installation = true,
            })
          end
        end,
      })
    '';
  };

  home.packages = with pkgs; [
    git
    fff-mcp
    # Spectral CLI also on home PATH for use outside Neovim
    nodePackages."@stoplight/spectral-cli"
  ];

  services = {
    # placeholder for future service modules
  };
}
