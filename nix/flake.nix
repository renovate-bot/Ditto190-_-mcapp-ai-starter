{
  description = "Flake providing devShell and Home Manager configuration for mcapp-ai-starter";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    home-manager = {
      url = "github:nix-community/home-manager";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, home-manager, ... }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
    packages = {
      fff-mcp = import ./packages/fff-mcp.nix {
        inherit lib rustPlatform;
        fetchFromGitHub = pkgs.fetchFromGitHub;
        pkg-config = pkgs.pkg-config;
        openssl = pkgs.openssl;
        zlib = pkgs.zlib;
      };
    };

    in {
      devShells.${system}.vibe-coder = pkgs.mkShell {
        buildInputs = with pkgs; [
          # Core tools
          git neovim nodejs python3 python3Packages.pip nix-prefetch-git
          # fff MCP file finder
          fff-mcp
          # --- LSPs (TypeScript/JS primary, then Python, Nix, Lua) ---
          nodePackages.typescript-language-server  # ts_ls — primary for this TS/Node.js codebase
          nodePackages.pyright                     # Python — GenerateAgents.md, generateagents-mcp
          lua-language-server                      # lua_ls — Neovim config authoring
          nil                                      # nil_ls — Nix flake/module files
          # --- OpenAPI / AsyncAPI linting ---
          nodePackages."@stoplight/spectral-cli"  # spectral lint *.yaml
          # --- devcontainer.vim Go binary (Vim-in-Codespaces workflow) ---
          go                                       # needed to build devcontainer.vim from tools/external
        ];
        shellHook = ''
          echo "Entering vibe-coder devShell"
          export XDG_CONFIG_HOME=$PWD/nvim

          # Build devcontainer.vim binary on first entry if not in PATH
          if ! command -v devcontainer.vim &>/dev/null; then
            if [ -d "$PWD/tools/external/devcontainer.vim" ]; then
              echo "Building devcontainer.vim binary…"
              (cd "$PWD/tools/external/devcontainer.vim" && go build -o "$PWD/bin/devcontainer.vim" . 2>/dev/null) \
                && echo "  → $PWD/bin/devcontainer.vim" \
                || echo "  ⚠  devcontainer.vim build failed (Go not available?)"
            fi
          fi
          # Add local bin to PATH
          export PATH="$PWD/bin:$PATH"
        '';
      };

      homeConfigurations = {
        default = home-manager.lib.homeManagerConfiguration {
          pkgs = pkgs;
          modules = [ ./nix/modules/home-manager.nix ];
          configuration = {};
        };
      };
    }; 
}
