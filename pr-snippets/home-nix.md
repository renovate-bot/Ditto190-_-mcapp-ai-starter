Home Manager snippet (home.nix)

```nix
{ config, pkgs, lib, ... }:

{
  imports = [ ./modules/home-manager.nix ];
  programs.neovim.enable = true;
  home.packages = with pkgs; [ git neovim ];
}
```

Notes: Place loader.lua under `$XDG_CONFIG_HOME/nvim/lua/loader.lua` and ensure `init.lua` bootstraps the plugin manager.
