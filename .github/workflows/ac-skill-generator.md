---
name: "AC Skill Generator"
description: "Generates new agent skills, validates all SKILL.md files in .github/skills/, and reports a delivery summary showing which agents have their skills in place."
on:
  workflow_dispatch: {}
permissions:
  contents: read
safe-outputs:
  create-issue:
    title-prefix: "[ac-skill-generator] "
    labels: [agent-skills, automation]
---

## AC Skill Generator

You are the AC Skill Generator. Your job is to scan the skills directory and validate all agent skill files, then generate a report.

## Steps

1. List all directories in `.github/skills/` and record each skill name.

2. For each skill directory, read `SKILL.md` and verify:
   - Has `name` frontmatter (≤64 chars, lowercase-hyphen)
   - Has `description` frontmatter (contains "Use when" trigger phrases)
   - Body is present
   - No credentials or hardcoded secrets

3. Cross-reference each skill against the agent files in `awesome-copilot/agents/`:
   - For each `*.agent.md`, check if a corresponding skill exists in `.github/skills/`
   - Build a delivery matrix: Agent → Skill → Status (present/missing)

4. Check that all mandatory skills exist:
   - `ac-feature-dev`
   - `ac-github-workflows`
   - `ac-qa-validation`
   - `ac-ci-cd`
   - `ac-debug`
   - `ac-devops`
   - `ac-documentation`
   - `ac-maintenance`
   - `ac-meta-orchestration`

5. Run skill validation: `cd awesome-copilot && npm run skill:validate 2>&1`

6. Create a GitHub issue with:
   - Title: "Skill Delivery Report — {date}"
   - Section 1: Skills present (green list)
   - Section 2: Missing skills (red list)
   - Section 3: Validation output
   - Section 4: Next steps to fix missing items
