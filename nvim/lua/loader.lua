-- Loader: returns plugin specs and runs lazy setup
-- Top-3 Neovim integration for mcapp-ai-starter (TS/Python/Nix Codespaces stack)
--   1. mason.nvim + mason-lspconfig     — LSP auto-install (ts_ls, pyright, nil_ls, lua_ls)
--   2. nvim-treesitter (vimdoc parser)  — AST syntax for TS, Python, Nix, YAML, vimdoc
--   3. devcontainer.vim (binary)        — loaded conditionally when binary is on PATH

local plugins = {
  -- ── 1. LSP: mason.nvim + mason-lspconfig + nvim-lspconfig ─────────────────
  {
    "mason-org/mason.nvim",
    build = ":MasonUpdate",
    opts  = { ui = { border = "rounded" } },
  },
  {
    "mason-org/mason-lspconfig.nvim",
    dependencies = { "mason-org/mason.nvim", "neovim/nvim-lspconfig" },
    opts = {
      -- Auto-install LSPs required by this codebase
      ensure_installed = {
        "ts_ls",    -- TypeScript / JavaScript  ← primary language
        "pyright",  -- Python  (GenerateAgents.md, generateagents-mcp)
        "lua_ls",   -- Lua  (Neovim config authoring)
        "nil_ls",   -- Nix  (flake.nix, home-manager modules)
      },
      automatic_installation = true,
    },
    config = function(_, opts)
      require("mason-lspconfig").setup(opts)
      -- Wire every installed server through nvim-lspconfig defaults
      require("mason-lspconfig").setup_handlers({
        function(server_name)
          require("lspconfig")[server_name].setup({})
        end,
        -- ts_ls: enable inlay hints for TS/JS files
        ["ts_ls"] = function()
          require("lspconfig").ts_ls.setup({
            settings = {
              typescript = { inlayHints = { includeInlayParameterNameHints = "all" } },
              javascript = { inlayHints = { includeInlayParameterNameHints = "all" } },
            },
          })
        end,
      })
    end,
  },
  { "neovim/nvim-lspconfig" },

  -- ── 2. nvim-treesitter with vimdoc + TS / Nix / YAML parsers ─────────────
  {
    "nvim-treesitter/nvim-treesitter",
    build = ":TSUpdate",
    opts  = {
      highlight = { enable = true },
      indent    = { enable = true },
      ensure_installed = {
        "lua",
        "vim",
        "vimdoc",       -- vim help files, SKILL.md, AGENTS.md authoring
        "typescript",
        "javascript",
        "tsx",
        "python",
        "nix",
        "json",
        "yaml",
        "markdown",
        "markdown_inline",
        "bash",
      },
    },
    config = function(_, opts)
      require("nvim-treesitter.configs").setup(opts)
    end,
  },

  -- ── 3. devcontainer.vim — loaded only when the Go binary is on PATH ────────
  --  The binary is built by the Nix devShell shellHook (bin/devcontainer.vim).
  --  When present, this plugin exposes :DevcontainerUp / :DevcontainerExec.
  {
    "mikoto2000/devcontainer.vim",
    cond = function()
      return vim.fn.executable("devcontainer.vim") == 1
    end,
    config = function()
      -- Variables recognised by devcontainer.vim Vim runtime
      vim.g.devcontainer_vim_nvim        = 1   -- use nvim flag
      vim.g.devcontainer_vim_config_file = ".devcontainer/devcontainer.vim.json"
    end,
  },

  -- ── fff.nvim: frecency-aware file finder (existing) ───────────────────────
  {
    "dmtrKovalenko/fff.nvim",
    build = function()
      require("fff.download").download_or_build_binary()
    end,
    lazy  = false,
    opts  = {
      debug = { enabled = false, show_scores = false },
    },
    keys  = {
      { "ff", function() require("fff").find_files() end,  desc = "FFFind files" },
      { "fg", function() require("fff").live_grep() end,   desc = "LiFFFe grep"  },
    },
  },

  -- ── Fuzzy finder + completion (quality-of-life) ────────────────────────────
  {
    "nvim-telescope/telescope.nvim",
    dependencies = { "nvim-lua/plenary.nvim" },
    opts = { defaults = { layout_strategy = "horizontal" } },
    keys = {
      { "<leader>ff", "<cmd>Telescope find_files<cr>",  desc = "Find files"  },
      { "<leader>fg", "<cmd>Telescope live_grep<cr>",   desc = "Live grep"   },
      { "<leader>fb", "<cmd>Telescope buffers<cr>",     desc = "Buffers"     },
    },
  },
  { "nvim-lua/plenary.nvim", lazy = true },

  -- ── Completion engine ──────────────────────────────────────────────────────
  {
    "hrsh7th/nvim-cmp",
    dependencies = {
      "hrsh7th/cmp-nvim-lsp",
      "hrsh7th/cmp-buffer",
      "hrsh7th/cmp-path",
    },
    config = function()
      local cmp = require("cmp")
      cmp.setup({
        mapping = cmp.mapping.preset.insert({
          ["<C-Space>"] = cmp.mapping.complete(),
          ["<CR>"]      = cmp.mapping.confirm({ select = true }),
        }),
        sources = cmp.config.sources({
          { name = "nvim_lsp" },
          { name = "buffer"   },
          { name = "path"     },
        }),
      })
    end,
  },
}

local opts = {
  performance = { rtp = { disabled_plugins = { "netrw", "gzip" } } },
}

require("lazy").setup(plugins, opts)

-- Export plugin list for tooling / tests
return plugins

