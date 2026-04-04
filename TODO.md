# TODO - Direnv + Nix Foundation + Devcontainer Nix Preinstall

- [x] Create foundation config files (`.envrc`, `flake.nix`) with non-breaking defaults
- [x] Create implementation planning document with in-depth analysis and source links
- [x] Add AGENTS.md planned-feature note + symlink-style reference entry
- [x] Update TODO statuses after each completed step

## Nix Preinstall on Rebuild (Current Pass)

- [ ] Update `.devcontainer/post-create.sh` to install Nix (Determinate installer) if missing
- [ ] Update `.devcontainer/devcontainer.json` with Nix flakes config in `remoteEnv`
- [ ] Pin `flake.nix` nixpkgs input to `9576c24a0ca1746d83d84bb40eaa0839f38d440b`
- [ ] Run syntax/validation checks for changed files
