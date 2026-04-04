Tools and Nix dev environment
-------------------------------

This folder contains helper scripts and a minimal Nix flake to bootstrap a reproducible development environment.

Files of interest:

- `scripts/install-oh-my-posh.sh` — installs the oh-my-posh binary into `~/.local/bin` and creates a default config at `~/.config/oh-my-posh/theme.omp.json`.
- `nix/flake.nix` — minimal flake template for a `home-manager` configuration (neovim, ripgrep, fzf). Edit and extend as needed.

External repos should be cloned into `tools/external/`.

Usage examples
--------------

Install oh-my-posh locally (user):

```bash
bash tools/scripts/install-oh-my-posh.sh
```

Apply Nix home-manager config (if Nix is installed and flakes enabled):

```bash
cd tools/nix
# modify flake.nix to your taste, then:
nix build ".#homeConfigurations.default.activationPackage"
./result/activate
```
