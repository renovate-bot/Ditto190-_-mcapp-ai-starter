{
  description = "Minimal flake for home-manager / dev environment (neovim, oh-my-posh, treefmt)";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    home-manager.url = "github:nix-community/home-manager/release-24.05";
  };

  outputs = { self, nixpkgs, home-manager, ... }@inputs:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
    in {
      homeConfigurations = {
        default = home-manager.lib.homeManagerConfiguration {
          inherit pkgs;
          home.username = "root";
          home.homeDirectory = "/root";
          programs.home-manager.enable = true;
          programs.neovim.enable = true;
          # Add mcp-nixos to the user's packages for a declarative MCP server
          home.packages = with pkgs; [ neovim ripgrep fzf mcp-nixos ];
          # Additional configuration should be added by the user
        };
      };
    };
