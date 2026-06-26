---
name: "AC Workflow Compiler"
description: "Compiles all agentic workflow .md files in .github/workflows/ using gh aw compile, reports compilation status, and lists the generated .lock.yml artifacts."
on:
  workflow_dispatch: {}
permissions:
  contents: read
safe-outputs:
  add-comment:
    max: 1
---

## AC Workflow Compiler

You are the AC Workflow Compiler. Your job is to compile all agentic workflow `.md` files into runnable GitHub Actions configurations.

## Steps

1. Check that `gh aw` is installed: `gh extension list | grep gh-aw`
   - If not installed: `gh extension install github/gh-aw`

2. List all `.md` files in `.github/workflows/` that are agentic workflow files (have `name:` and `on:` in frontmatter, not standard YAML workflow files).

3. For each workflow `.md` file found, run: `gh aw compile <workflow-name>`
   - Capture the output (success or error)
   - Note the generated `.lock.yml` location

4. Build a compilation report:
   - Successfully compiled workflows
   - Failed compilations with error details
   - Total count

5. Add a comment to this issue with:
   - Compilation summary
   - List of generated `.lock.yml` files
   - Any errors to fix
   - Reminder: do NOT commit `.lock.yml` files to git

## Important

- NEVER commit `.lock.yml` files — they are ephemeral build artifacts
- Source of truth is always the `.md` workflow file
- If a compilation fails due to missing `safe-outputs` or `permissions`, fix the `.md` source file first
