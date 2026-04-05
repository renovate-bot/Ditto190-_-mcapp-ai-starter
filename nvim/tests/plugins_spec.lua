-- nvim/tests/plugins_spec.lua
-- Headless Neovim tests using plenary.nvim
-- Run: make test-nvim
--
-- These run after lazy.nvim has synced plugins once (make bootstrap-nvim).
-- They validate that the Top-3 plugin integration points are reachable.

local assert = require("luassert")

describe("mason.nvim integration", function()
  it("mason module is loadable", function()
    local ok, mason = pcall(require, "mason")
    assert.is_true(ok, "mason module should load without errors")
    assert.is_not_nil(mason)
  end)

  it("mason has a setup function", function()
    local mason = require("mason")
    assert.is_function(mason.setup)
  end)

  it("mason-lspconfig module is loadable", function()
    local ok, mlsp = pcall(require, "mason-lspconfig")
    assert.is_true(ok, "mason-lspconfig module should load without errors")
    assert.is_not_nil(mlsp)
  end)
end)

describe("nvim-treesitter integration", function()
  it("nvim-treesitter parsers module is loadable", function()
    local ok, parsers = pcall(require, "nvim-treesitter.parsers")
    assert.is_true(ok, "nvim-treesitter.parsers should load without errors")
  end)

  it("vimdoc parser is registered", function()
    local parsers = require("nvim-treesitter.parsers")
    assert.is_not_nil(parsers.get_parser_configs()["vimdoc"],
      "vimdoc parser should be registered in nvim-treesitter")
  end)

  it("typescript parser is registered", function()
    local parsers = require("nvim-treesitter.parsers")
    assert.is_not_nil(parsers.get_parser_configs()["typescript"],
      "typescript parser should be registered")
  end)
end)

describe("devcontainer.vim conditional load", function()
  it("binary detection does not crash when binary absent", function()
    -- When devcontainer.vim binary is not on PATH, plugin.cond returns false
    -- and the plugin is not loaded. This test asserts safe fallback.
    local has_binary = vim.fn.executable("devcontainer.vim") == 1
    -- Either it loads (binary present) or not (absent) — no error either way
    if has_binary then
      local ok, dv = pcall(require, "devcontainer.vim")
      assert.is_true(ok, "devcontainer.vim plugin should load when binary is present")
    else
      -- Binary absent → plugin not loaded.  vim.g.devcontainer_vim is nil.
      assert.is_nil(vim.g.devcontainer_vim,
        "devcontainer_vim global should not be set when binary is absent")
    end
  end)
end)

describe("nvim-lspconfig integration", function()
  it("lspconfig module is loadable", function()
    local ok, lspconfig = pcall(require, "lspconfig")
    assert.is_true(ok, "nvim-lspconfig should load without errors")
  end)

  it("ts_ls server config exists", function()
    local lspconfig = require("lspconfig")
    assert.is_not_nil(lspconfig.ts_ls,
      "ts_ls (TypeScript Language Server) config should be available")
  end)

  it("pyright server config exists", function()
    local lspconfig = require("lspconfig")
    assert.is_not_nil(lspconfig.pyright,
      "pyright (Python Language Server) config should be available")
  end)
end)
