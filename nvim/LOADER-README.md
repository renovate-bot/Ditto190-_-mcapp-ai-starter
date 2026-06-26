Neovim loader requirements

What a loader needs:

- A plugin manager runtime (this project uses 'folke/lazy.nvim'). The init.lua bootstraps lazy.nvim into runtimepath.
- A Lua module (e.g. lua/loader.lua) that returns or calls the plugin manager with a table of plugin specs.
- Plugin specs: each entry can be a string or a table with fields (config, build, dependencies, opts).
- An entrypoint in init.lua that requires the loader module after plugin manager is available.

Why a loader:

- Keeps plugin list declarative and testable.
- Enables programmatic re-use in Nix devShells and dotfile templates.
