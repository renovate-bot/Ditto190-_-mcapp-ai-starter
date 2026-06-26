# Skills Tree

This file provides an AST-style overview of where SKILL.md files live in the repository (counts approximated from index generation).

Total SKILL entries (indexed): 224

```mermaid
graph TD
  R[repo root]
  R --> A[consolidated_sources/awesome-copilot\n(≈210 SKILLs)]
  R --> B[.github/skills\n(≈11 SKILLs)]
  R --> C[.agents/skills\n(≈8 SKILLs)]
  R --> D[plugins/mcp-apps/skills\n(≈4 SKILLs)]
  R --> E[examples/pdf-server/plugin/skills\n(≈1 SKILL)]
  R --> F[migration & vendor paths\n(e.g., migration dumps, .venv, site-packages)\n(remaining SKILLs)]
  A --> A1[consolidated_sources/awesome-copilot/skills/*]
  B --> B1[.github/skills/*]
  C --> C1[.agents/skills/*]
  D --> D1[plugins/mcp-apps/skills/*]
  F --> F1[migration/repodumps/*, .venv, site-packages]
```

Quick usage:
- Use `.github/skills-index.md` and `.github/skills-index.json` (generated) to navigate to specific skill files.
- Update `scripts/generate_skills_index.js` to regenerate the index/tree as needed.

