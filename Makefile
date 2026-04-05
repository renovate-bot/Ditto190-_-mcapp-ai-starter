.PHONY: inventory devshell bootstrap-nvim

inventory:
	python3 scripts/tools_inventory.py --root tools/external --out tools/external_inventory.json

devshell:
	nix develop ./nix#vibe-coder

bootstrap-nvim:
	# symlink repo nvim as XDG config and install plugins headless
	mkdir -p $(HOME)/.config
	ln -sfn $(CURDIR)/nvim $(HOME)/.config/nvim
	# headless plugin sync for lazy.nvim
	nvim --headless -c "lua require('lazy').sync()" -c qa!
