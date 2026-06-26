{ pkgs, ... }:

{
  programs.home-manager.enable = true;

  # Example packages to expose to the user environment
  home.packages = with pkgs; [ neovim ripgrep fzf mcp-nixos ];

  # You can enable a basic neovim configuration here or import a separate file
  programs.neovim = {
    enable = true;
    # Further neovim configuration can be added or imported
  };

  # Example of a simple shell prompt integration (oh-my-posh is installed separately)
  programs.bash.enable = true;

}
