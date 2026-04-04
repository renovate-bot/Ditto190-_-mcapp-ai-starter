---
description: >
  Quality gate agent system — code quality, testing, pre-commit validation,
  and conventional commit enforcement. Use the Dev Quality Lead as the entry
  point before any git commit or push.
applyTo: "**"
---

# Quality Gate Agent System

This project has a **multi-agent quality gate** that must be run before committing code.
All agents live in `.github/agents/`. The entry point is **`dev-quality-lead`**.

## When to Use

- Before any `git commit`
- After completing a feature or fix
- Before opening a PR
- When asked to "validate", "quality check", or "run gates"

## Agent Map

| Agent                      | Role                                                    | Invoked By                                  |
| -------------------------- | ------------------------------------------------------- | ------------------------------------------- |
| **`dev-quality-lead`**     | Orchestrator — coordinates all gates                    | User (direct entry point)                   |
| **`code-quality-checker`** | Runs lint + build for all components                    | `dev-quality-lead`                          |
| **`test-runner`**          | Runs non-e2e tests + debug scripts for all components   | `dev-quality-lead`                          |
| **`debug-evaluator`**      | Evaluates test/debug output; categorises PASS/WARN/FAIL | `dev-quality-lead` (when failures/warnings) |
| **`pre-commit-gate`**      | Evaluates GO / NO-GO for commit                         | `dev-quality-lead`                          |
| **`commit-tagger`**        | Stages + commits with conventional format + semver tag  | `dev-quality-lead` (only on GO)             |

## Gate Sequence (NEVER skip steps)

```
Code Quality → Tests → [failures?] → Debug Eval → Pre-Commit Gate → [GO] → Commit + Tag
                     → [clean]    ↗                               → [NO-GO] → STOP, report to user
```

Debug Evaluation is only invoked when `test-runner` returns failures or warnings. Skip it on clean passes.

## Subagent Rules (CRITICAL)

Subagents (`code-quality-checker`, `test-runner`, `debug-evaluator`, `pre-commit-gate`, `commit-tagger`) operate with minimal context load:

- They ONLY use `execute` (terminal commands) and `search` (grep for specific patterns).
- They do NOT read full files, explore directories, or research code.
- All context they need is passed in the delegation instruction from `dev-quality-lead`.

## Quick Start

To use the quality gate, switch to `@dev-quality-lead` and say:

```
Run quality gates and commit: <brief description of what changed>
```

Or simply:

```
Run quality checks before committing
```

## Commit Message Convention

All commits must use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>
```

**Scopes:** `sdk`, `mcp`, `agents`, `registry`, `copilot`, `n8n`, `ci`, `docker`, `config`, `docs`, `deps`

**Types:** `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `ci`, `build`, `style`, `perf`
