# Lesson: Merge .vscode config and extension recommendations

- Title: Merge .vscode config and extensions from DRAFT/devcontainer
- Severity: medium
- Category: workflow
- Trigger: Merged `.vscode/extensions.json` and `.vscode/settings.json` to align Codespace/devcontainer and project recommendations
- Impact: Ensures consistent developer experience across Codespaces; risk of recommending unwanted extensions centrally if not reviewed
- Prevention: Review recommended extension list with team; keep personal interpreter paths out of repo settings; prefer devcontainer to enforce machine-specific interpreter
- Keywords: vscode, codespace, devcontainer, extensions, config, mcp

Payload (for ContextStream):

{
  "title": "Merge .vscode config and extensions from DRAFT/devcontainer",
  "severity": "medium",
  "category": "workflow",
  "trigger": "Merged .vscode/extensions.json and .vscode/settings.json to align Codespace/devcontainer and project recommendations",
  "impact": "Ensures consistent developer experience across Codespaces; risk of recommending unwanted extensions centrally if not reviewed",
  "prevention": "Review recommended extension list with team; keep personal interpreter paths out of repo settings; prefer devcontainer to enforce machine-specific interpreter",
  "keywords": ["vscode","codespace","devcontainer","extensions","config","mcp"]
}

To post this lesson to ContextStream, run (set API key & project id first):

```bash
export CONTEXTSTREAM_API_KEY="sk-..."
export CONTEXTSTREAM_PROJECT_ID="<project-id>"
DRY_RUN=false node scripts/save_lesson.js
```
