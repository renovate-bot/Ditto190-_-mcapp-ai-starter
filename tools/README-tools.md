# Tools helpers and quickstart

This doc explains the helper script added to inventory `tools/external/` and
how to run the new analyst agents.

Quick steps

1. Run the inventory scanner:

```bash
python3 scripts/tools_inventory.py --root tools/external --out tools/external_inventory.json
```

1. Open `tools/external_inventory.md` for a human-friendly summary.

2. Use the analyst agents in `.github/agents/` (they describe what to do).

Next steps (recommended)

- Run the inventory and review the top 3 reuse candidates.
- For Neovim plugins: consider exposing them as a curated `nvim` config in
  `home-manager` or as a `nvim` flake input.
- For Nix projects: convert repeated patterns to `flake` modules and add
  `devShell`/`package` entries for reproducible developer shells.
