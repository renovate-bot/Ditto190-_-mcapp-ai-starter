Flake inputs (PR-ready snippet)

Add these inputs to your flake.nix under `inputs`:

```
nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
home-manager.url = "github:nix-community/home-manager";
home-manager.inputs.nixpkgs.follows = "nixpkgs";
```

Usage: this provides `pkgs`, `home-manager` modules and lets you expose a `devShells` and `homeConfigurations` outputs.
