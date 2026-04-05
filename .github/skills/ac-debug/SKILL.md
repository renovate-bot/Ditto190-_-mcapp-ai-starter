---
name: ac-debug
description: >
  Debug and diagnose issues in awesome-copilot agents, skills, and workflows. Use when
  asked to debug a failure, investigate an error, read logs, troubleshoot a skill not loading,
  diagnose why an agent is not working, analyze gh aw run output, or trace a build failure.
  Triggers: 'debug', 'diagnose', 'why is it failing', 'investigate error', 'skill not loading',
  'workflow failure', 'gh aw logs', 'trace bug', 'fix error'.
---

# AC Debug Skill

Diagnose failures and investigate issues in agents, skills, and agentic workflows.

## When to Use This Skill

- A skill is not being loaded by Copilot despite being present
- An agentic workflow fails during `gh aw run`
- `npm run skill:validate` or `plugin:validate` reports errors
- An agent `.agent.md` file is not triggering expected behavior
- Build pipeline fails

## Diagnosis Framework

### Phase 1 — Assess

Gather quick signal before deep investigation:

```bash
# Check gh aw status
gh aw compile 2>&1 | head -20

# Check skill validation
cd /workspaces/mcapp-ai-starter/awesome-copilot
npm run skill:validate 2>&1

# Check agent files
ls /workspaces/mcapp-ai-starter/awesome-copilot/agents/
ls /workspaces/mcapp-ai-starter/.github/skills/
```

### Phase 2 — Investigate

```bash
# View workflow run logs
gh aw logs <workflow-name> 2>&1

# Audit specific run
gh aw audit <run-id>

# Check skill frontmatter validity
python3 -c "
import yaml, sys
with open('SKILL.md') as f:
    content = f.read()
if content.startswith('---'):
    parts = content.split('---', 2)
    meta = yaml.safe_load(parts[1])
    print('name:', meta.get('name'))
    print('description:', meta.get('description', '')[:80])
"
```

### Phase 3 — Fix & Verify

- For skill not loading: ensure `description` has "Use when asked to..." triggers
- For compile error: check frontmatter YAML syntax
- For missing agent behavior: verify `.agent.md` frontmatter is valid

## Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Skill never activates | Vague description | Add "Use when asked to..." |
| `gh aw compile` fails | Bad YAML frontmatter | Fix `---` blocks |
| Agent not found | Wrong file location | Move to `agents/` dir |
| `skill:validate` fails | name > 64 chars or missing | Fix frontmatter |
| Workflow not triggered | Wrong `on:` format | Check `schedule` or `slash_command` |
