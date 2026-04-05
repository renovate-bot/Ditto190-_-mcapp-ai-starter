Neovim loader checklist (PR-ready)

What a loader needs:

- A plugin manager runtime available during startup (we use `folke/lazy.nvim` in `init.lua`).
- A Lua module `lua/loader.lua` that either:
  - returns the plugin spec table, OR
  - calls the plugin manager's setup function directly (e.g. `require('lazy').setup(plugins, opts)`).
- Each plugin entry should be declarative (string or table) and may include `config`, `build`, and `dependencies` fields.
- For reproducible builds in Nix, ensure `XDG_CONFIG_HOME` is set to the repo path in `devShell` shellHook and that the bootstrap step clones `lazy.nvim` into `stdpath('data')`.

Example loader entry (in `lua/loader.lua`):

```lua
local plugins = {
  { 'neovim/nvim-lspconfig', config = function() require('lspconfig').pyright.setup{} end },
}
require('lazy').setup(plugins)
```
