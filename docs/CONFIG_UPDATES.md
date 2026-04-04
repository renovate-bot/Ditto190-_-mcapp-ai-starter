**Category:** config

# VS Code / Codespace Config Updates

Date: 2026-04-03
Author: automated patch (review recommended)

Summary

- Merged and expanded `.vscode/extensions.json` to include a Codespace- and Linux-safe superset of extension recommendations taken from the DRAFT workspace and `.devcontainer/devcontainer.json`.
- Rewrote `.vscode/settings.json` to use non-personal defaults (no local interpreter paths) while preserving existing Copilot/MCP server configuration and Plan/Ask agent tool lists.

Files changed

- `.vscode/extensions.json`
- `.vscode/settings.json`

Extensions added (new or consolidated)

- anthropic.claude-code
- timheuer.awesome-copilot
- digitarald.agent-memory
- ms-python.vscode-pylance
- ms-pyright.pyright
- donjayamanne.python-environment-manager
- ms-python.vscode-python-envs
- ms-toolsai.jupyter
- ms-toolsai.jupyter-keymap
- ms-toolsai.jupyter-renderers
- donjayamanne.githistory
- github.vscode-pull-request-github
- amadeusitgroup.prompt-registry
- pimzino.spec-workflow-mcp
- mongodb.mongodb-vscode
- mechatroner.rainbow-csv
- tamasfe.even-better-toml
- pkief.material-icon-theme

Notes: the repo already had a core set of extensions (Git tooling, Python, Prettier/ESLint, Docker, YAML, Markdown); the above list supplements that set where DRAFT/devcontainer suggested additional capabilities.

Settings changes (high level)

- Added Codespace/devcontainer-friendly defaults:
  - `terminal.integrated.defaultProfile.linux = "bash"`
  - `editor.formatOnSave = true` and `editor.defaultFormatter = "esbenp.prettier-vscode"`
  - `[python].editor.defaultFormatter = "ms-python.black-formatter"`
  - `python.linting.enabled = true` + `python.linting.pylintEnabled = true`
  - `files.watcherExclude` and `files.exclude` entries to ignore heavy runtime folders (`n8n-data`, `ollama_storage`, `postgres_storage`, `qdrant_storage`, `.venv`, `node_modules`)
  - `git.autofetch = true` and `git.enableSmartCommit = true`
- Preserved: Copilot plan/ask agent tool lists and the `[copilot].mcp` server entry that registers `generateagents-mcp` (unchanged, only carried through into the merged settings file).
- Removed personal/local interpreter path entries; the merged settings do not set `python.defaultInterpreterPath` to a machine-specific path.

Why these changes

- Aligns repository-level VS Code recommendations with the devcontainer's intended developer experience (notably Codespaces/Codespace-like Linux containers), while avoiding personal, machine-specific config.
- Adds Jupyter, type-checking, prompt/MCP tooling and PR UX extensions suggested by the DRAFT workspace and devcontainer.

Safety & capacity

- The Codespace was checked before applying changes: ~16GB RAM (11GB available), ~32GB disk with ~26GB free, workspace size ~374MB. Installing the recommended extensions is safe on this environment.

Next steps / actions for maintainers

1. Review the list of newly recommended extensions; remove any your team does not want to recommend centrally.
2. If you want the repo to enforce a specific Python interpreter for devcontainers, add a devcontainer `python.defaultInterpreterPath` there (not in `.vscode/settings.json`).
3. Commit these changes to a branch and open a PR for team review.
4. Optionally: install the recommended extensions into your Codespace to validate there are no extension conflicts.

How to revert

- Restore previous files from Git history, or remove entries from `.vscode/extensions.json` / `.vscode/settings.json` as needed.

Contact

- If you want, I can open a branch with these changes and create a PR; or produce a shorter “must-have” subset of extensions.
