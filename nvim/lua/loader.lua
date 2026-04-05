-- Loader: returns plugin specs and runs lazy setup
local plugins = {
  -- Plugin manager is external (lazy.nvim). Plugins here are prioritized for a vibe-coder setup
  { 'neovim/nvim-lspconfig', config = function() require('lspconfig').pyright.setup{} end },
  { 'nvim-treesitter/nvim-treesitter', build = ':TSUpdate' },
  { 'nvim-telescope/telescope.nvim', dependencies = { 'nvim-lua/plenary.nvim' } },
}

local opts = {
  performance = { rtp = { disabled_plugins = { 'netrw', 'gzip' } } },
}

require('lazy').setup(plugins, opts)

-- Export plugin list for potential tooling
return plugins
