{
  description = "AI Starter Kit reproducible development shell (foundation)";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/9576c24a0ca1746d83d84bb40eaa0839f38d440b";
  };

  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" "aarch64-darwin" "x86_64-darwin" ];
      forAllSystems = f:
        nixpkgs.lib.genAttrs systems (system:
          f {
            pkgs = import nixpkgs { inherit system; };
          });
    in
    {
      devShells = forAllSystems ({ pkgs }: {
        default = pkgs.mkShell {
          packages = with pkgs; [
            bash
            coreutils
            curl
            git
            gnugrep
            jq
            nodejs_20
            python312
            shellcheck
            uv
            yq-go
          ];

          shellHook = ''
            export UV_SYSTEM_PYTHON=1
            export COMPOSE_DOCKER_CLI_BUILD=1
            export DOCKER_BUILDKIT=1
            echo "Entering Nix dev shell: Node $(node --version 2>/dev/null || true), Python $(python3 --version 2>/dev/null || true)"
          '';
        };
      });
    };
}
