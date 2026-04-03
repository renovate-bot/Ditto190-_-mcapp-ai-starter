# ContextStream + Awesome Copilot Knowledge Pack

This document captures the relevant command/rule guidance requested for:

- critical thinking and reflection loops
- technical write-ups
- memory, context, and knowledge management

It is derived from loaded instruction assets and generated ContextStream rule output in this project.

## Commands And Rules Loaded

### ContextStream help and rules discovery

Actions run:

- `mcp_contextstream_help(action="tools")`
- `mcp_contextstream_help(action="version")`
- `mcp_contextstream_help(action="editor_rules", folder_path="/workspaces/mcapp-ai-starter", mode="full", include_post_write=true, include_pre_compact=true)`

Result:

- ContextStream editor rules were generated and written to the project.
- Server version reported by help: `0.2.12`.

Primary generated artifact:

- `.github/contextstream-rules.md`

### Awesome Copilot instructions and skills loaded

Loaded with `mcp_awesome-copil_load_instruction`:

- Agent: `dotnet-self-learning-architect.agent.md`
- Agent: `voidbeast-gpt41enhanced.agent.md`
- Instruction: `context-engineering.instructions.md`
- Instruction: `github-actions-ci-cd-best-practices.instructions.md`
- Skill: `memory-merger/SKILL.md`
- Skill: `remember/SKILL.md`
- Skill: `agentic-eval/SKILL.md`
- Skill: `copilot-spaces/SKILL.md`

## Practical Rule Set To Apply In This Repo

### 1. Critical-thinking execution loop

Use a repeatable loop for non-trivial tasks:

1. Define goal and constraints.
2. Discover context (search-first, then scoped reads).
3. Plan steps with explicit verification points.
4. Execute smallest safe change set.
5. Evaluate outputs with a reflection pass.
6. Capture lessons and decisions.

### 2. Reflection and quality checks

Use an evaluator pass for quality-critical work:

- generate -> evaluate -> critique -> refine
- enforce iteration caps
- require structured acceptance criteria

This aligns with `agentic-eval` and the loaded architect agent's lessons-first approach.

### 3. Memory and knowledge management

Apply memory patterns from `remember` and `memory-merger`:

- capture reusable lessons as concise instruction content
- keep domain-specific memory grouped by topic
- merge mature lessons from memory files into stable instruction files
- keep instructions scannable, concrete, and action-oriented

### 4. Context engineering rules

Apply context-engineering guidance:

- keep file names and paths semantic
- maintain explicit interfaces and contracts
- keep relevant files open when requesting multi-file work
- provide concrete examples and references for pattern reuse

### 5. CI/CD review hygiene

Apply loaded CI/CD instruction guidance:

- least-privilege workflow permissions by default
- explicit triggers and path filters
- concurrency cancellation for stale runs
- clear artifact uploads for async review

## `mcp_contextstream_context` Option Reference

Use these options deliberately when available:

- Required: `user_message`
- Common control options:
  - `mode`: `standard | pack | fast`
  - `format`: `minified | readable | structured`
  - `max_tokens`
  - `distill`
- Session/transcript options:
  - `session_id`
  - `save_exchange`
  - `session_tokens`
- Project/workspace options:
  - `folder_path`
  - `project_id`
  - `workspace_id`

Recommended usage:

- new session: bootstrap context first, then proceed
- routine turns: `mode="fast"` for quick responses, `mode="standard"` for deeper coding tasks
- capture important milestones to memory to reduce context-loss risk

## Saved Project Assets

This learning bundle is now saved into project files:

- `.github/contextstream-rules.md` (generated rules)
- `.github/instructions/contextstream-knowledge-management.instructions.md` (operational instruction)
- `docs/CONTEXTSTREAM_AWESOME_COPILOT_KNOWLEDGE_PACK.md` (this file)
