inventory: python3 scripts/tools_inventory.py --root tools/external --out tools/external_inventory.json

devshell: nix develop ./nix#vibe-coder

bootstrap-nvim: mkdir -p ~/.config
  ln -sfn $(pwd)/nvim ~/.config/nvim
  nvim --headless -c "lua require('lazy').sync()" -c qa!
