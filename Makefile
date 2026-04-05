.PHONY: inventory devshell bootstrap-nvim test-nvim lint-api build-devcontainer-vim

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

# ── Tests ──────────────────────────────────────────────────────────────────────
test-nvim:
	@echo "Running headless Neovim tests via plenary.nvim…"
	@nvim --headless \
	  -u nvim/init.lua \
	  -c "lua require('plenary.test_harness').test_directory('nvim/tests', { sequential = true })" \
	  -c "qa!" 2>&1

# ── Linting ────────────────────────────────────────────────────────────────────
lint-api:
	@echo "Linting OpenAPI / AsyncAPI files with Spectral…"
	@if ! command -v spectral &>/dev/null; then \
	  echo "  spectral not found. Install: npm install -g @stoplight/spectral-cli"; \
	  exit 1; \
	fi
	@find . -name "*.yaml" -o -name "*.yml" \
	  | grep -v node_modules | grep -v .git \
	  | xargs -r spectral lint --ruleset .spectral.yaml --format stylish

# ── devcontainer.vim binary ────────────────────────────────────────────────────
build-devcontainer-vim:
	@echo "Building devcontainer.vim Go binary…"
	@mkdir -p bin
	(cd tools/external/devcontainer.vim && go build -o $(CURDIR)/bin/devcontainer.vim .)
	@echo "  → bin/devcontainer.vim (add to PATH)"

# ── Inventory (re-run after cloning new repos) ─────────────────────────────────
