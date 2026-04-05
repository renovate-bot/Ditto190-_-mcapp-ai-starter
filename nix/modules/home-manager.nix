{ config, pkgs, lib, ... }:

let
  username = lib.getEnv "USER" or "user";
in {
  programs.neovim = {
    enable = true;
    package = pkgs.neovim;
    viAlias = true;
    extraConfig = ''
      -- use XDG_CONFIG_HOME/nvim/init.lua which should call the loader
      -- keep this minimal; loader handles plugin setup
    '';
    # Optionally ensure the loader is present under $HOME/.config/nvim/lua/loader.lua
  };

  home.packages = with pkgs; [ git ];

  services = {
    # placeholder for future modules
  };
}
