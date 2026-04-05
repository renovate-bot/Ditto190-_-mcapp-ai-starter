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
    in {
      devShells.${system}.vibe-coder = pkgs.mkShell {
        buildInputs = with pkgs; [ git neovim nodejs python3 python3Packages.pip nix-prefetch-git ];
        shellHook = ''
          echo "Entering vibe-coder devShell"
          export XDG_CONFIG_HOME=$PWD/nvim
        '';
      };

      homeConfigurations = {
        default = home-manager.lib.homeManagerConfiguration {
          pkgs = pkgs;
          modules = [ ./nix/modules/home-manager.nix ];
          configuration = {};
        };
      };
    } 
}
