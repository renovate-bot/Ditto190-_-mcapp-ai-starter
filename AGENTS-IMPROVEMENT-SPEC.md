# AGENTS Improvement Spec

**Date:** 2026-04-09  
**Scope:** Root `AGENTS.md`, `.github/agents/*.agent.md`, folder-scoped `AGENTS.md` files  
**Author:** Audit pass — Ona

---

## 1. Audit Findings

### 1.1 What's Good

| Item | Location | Why it works |
|------|----------|--------------|
| Specialist subagent pattern | `.github/agents/` | Clear separation of concerns: each agent has one job, defined inputs/outputs, and explicit "NOT for direct user invocation" guards |
| Structured output formats | All `.agent.md` files | Every agent specifies an exact output block (e.g. `CODE QUALITY REPORT`, `PRE-COMMIT GATE REPORT`). Orchestrators can parse these reliably |
| Gate sequence enforcement | `dev-quality-lead.agent.md` | Ordered pipeline (quality → tests → debug → gate → commit) with explicit STOP-on-FAIL logic |
| Conventional commits + scopes | `commit-tagger.agent.md` | Scope taxonomy is project-specific and complete; semver tagging logic is sound |
| Folder-scoped AGENTS.md | `n8n/AGENTS.md`, `generateagents-mcp/AGENTS.md` | Correct pattern — each subfolder documents its own conventions, quick commands, and pitfalls |
| Security posture in pre-commit gate | `pre-commit-gate.agent.md` | Scans for secrets, blocks `.env` staging, validates docker compose config |
| Cloud reviewer depth tiers | `cloud-reviewer.agent.md` | `full / standard / lightweight` depth model is practical and well-defined |
| `AGENTS-revised.md` intent | Root | Contains the clearest statement of project identity, PR authoring requirements, and cross-provider rules — better than the current `AGENTS.md` |

---

### 1.2 What's Missing

| Gap | Impact |
|-----|--------|
| **Root `AGENTS.md` has no project identity section** | Agents have no authoritative description of what this repo is, what stack it runs, or what the primary goal is. Every agent must infer this from README or other files |
| **No agent index / registry** | Nine agents exist in `.github/agents/` but `AGENTS.md` only documents one (`cloud-reviewer`). An agent reading `AGENTS.md` cannot discover the others |
| **No invocation trigger table** | `dev-quality-lead` and `cloud-reviewer` have `argument-hint` / trigger phrases in frontmatter, but there is no single place listing all agents and when to call them |
| **No environment / toolchain contract** | Agents hardcode paths like `/workspaces/mcapp-ai-starter` and assume `uv`, `npm`, `docker`, `gh` are available. No file documents these prerequisites |
| **No error escalation policy** | What happens when an agent fails and the user is not present? No fallback or notification path is defined |
| **No agent versioning or changelog** | Agents evolve but there is no version field or change history. Breaking changes to output formats will silently break orchestrators |
| **`migration-analyst` has no trigger definition** | Unlike other agents, it has no `description` frontmatter trigger phrases and no integration into `dev-quality-lead` |
| **`multi-agent-orchestrator` references non-existent script** | References `.github/scripts/orchestrator.js` which does not exist in the repo |
| **No folder-scoped AGENTS.md for `src/`, `prompt-registry/`, `awesome-copilot/`** | These are active code directories with no agent guidance |
| **`agentskills/` directory is undocumented** | Contains skills (`add-feature`, `expert-advice`, `start-dev-server`, etc.) with no index or usage instructions in any AGENTS file |
| **No human-in-the-loop policy** | `commit-tagger` blocks push but there is no documented policy for when human approval is required before any agent action |

---

### 1.3 What's Wrong

| Problem | Location | Severity |
|---------|----------|----------|
| **Root `AGENTS.md` is a session log, not agent guidance** | `AGENTS.md` | ❌ Critical — the file documents a past VSCode task setup session. It is not useful to any agent reading it for project context |
| **`AGENTS.md` and `CLAUDE.md` are identical** | Both files | ❌ Critical — both contain the same session log content. `CLAUDE.md` should contain Claude-specific instructions; instead it duplicates a stale artifact |
| **`AGENTS-revised.md` is the real AGENTS.md but is not named correctly** | `AGENTS-revised.md` | ❌ Critical — the authoritative agent instructions live in a file that agents will not read by convention |
| **`dev-quality-lead.agent.md` has corrupted content** | `.github/agents/dev-quality-lead.agent.md` | ❌ Critical — the file contains duplicated and interleaved text blocks (Step 3 and Step 4 appear twice, Step 2 is truncated mid-sentence: `"Run lint aDebug Evaluation..."`) |
| **Hardcoded absolute workspace path** | `pre-commit-gate.agent.md`, `test-runner.agent.md`, `commit-tagger.agent.md` | ⚠️ High — `/workspaces/mcapp-ai-starter` is hardcoded in every command. If the workspace path changes (Codespaces, local clone), all commands break |
| **`multi-agent-orchestrator` workflow file does not exist** | `multi-agent-orchestrator.agent.md` | ⚠️ High — references `.github/workflows/multi-agent-orchestrator.yml` which is absent; the agent cannot be activated |
| **`pre-commit-gate` tool list is too broad** | `pre-commit-gate.agent.md` | ⚠️ Medium — `tools: [execute, search]` is vague; other agents specify exact tool names. Inconsistent tool declarations reduce predictability |
| **`cloud-reviewer` references non-existent sub-agents** | `cloud-reviewer.agent.md` | ⚠️ Medium — references `se-security-reviewer`, `terraform-iac-reviewer`, `se-system-architecture-reviewer`, `agent-governance-reviewer` as sources, but none of these agents exist in `.github/agents/` |
| **`awesome-copilot` vendor index is referenced but absent** | `AGENTS-revised.md` §2 | ⚠️ Medium — mandates `vendor/awesome-copilot-index/` as canonical cache; directory does not exist |
| **Date in root `AGENTS.md` is wrong** | `AGENTS.md` | 🟢 Low — states "Updated: 2024" but was generated in 2025/2026 |
| **`TODO.md` is tracked in git** | Root | 🟢 Low — session-specific task tracking file committed to the repo; not useful to agents or contributors |

---

## 2. Improvement Spec

### Priority 1 — Fix broken/misleading files (do first)

#### SPEC-01: Replace root `AGENTS.md` with authoritative content

**Problem:** Current `AGENTS.md` is a session log. `AGENTS-revised.md` contains the real instructions but is not read by convention.

**Action:**
1. Replace `AGENTS.md` content with the content of `AGENTS-revised.md`, extended with the additions below.
2. Delete `AGENTS-revised.md` (it becomes redundant).
3. `CLAUDE.md` should be reset to Claude-specific instructions (model preferences, tool permissions, response style) — not a copy of `AGENTS.md`.

**Required sections in the new `AGENTS.md`:**

```
# AGENTS.md

## 0. Project Identity
## 1. Must-Read Order
## 2. Agent Registry (index of all agents)
## 3. Environment Contract (tools, paths, env vars)
## 4. Invocation Triggers (when to call which agent)
## 5. PR Authoring Requirements
## 6. Review Requirements
## 7. Cross-Provider Rules
## 8. Human-in-the-Loop Policy
## 9. Error Escalation Policy
```

---

#### SPEC-02: Fix `dev-quality-lead.agent.md` corruption

**Problem:** File has duplicated and interleaved content. Step 2 is truncated. The file is the primary orchestrator — corruption here breaks the entire gate pipeline.

**Action:** Rewrite the file with clean, non-duplicated content. The correct structure is:

```
Step 1 — Code Quality    → code-quality-checker
Step 2 — Test Suite      → test-runner
Step 3 — Debug Eval      → debug-evaluator (conditional)
Step 4 — Pre-Commit Gate → pre-commit-gate
Step 5 — Commit & Tag    → commit-tagger
```

Each step section must appear exactly once.

---

#### SPEC-03: Replace hardcoded workspace paths with a variable

**Problem:** `/workspaces/mcapp-ai-starter` is hardcoded in `pre-commit-gate`, `test-runner`, and `commit-tagger`. Breaks on path change.

**Action:** Add to `AGENTS.md` §3 (Environment Contract):

```markdown
## 3. Environment Contract

**Workspace root:** Agents MUST resolve the workspace root dynamically:
- Shell: `REPO_ROOT=$(git rev-parse --show-toplevel)`
- All agent commands must use `$REPO_ROOT` or `$(git rev-parse --show-toplevel)` instead of hardcoded paths.
```

Update all three agent files to use `$(git rev-parse --show-toplevel)` in their command blocks.

---

### Priority 2 — Fill structural gaps

#### SPEC-04: Add Agent Registry to `AGENTS.md`

**Problem:** No single place lists all agents and their invocation triggers.

**Action:** Add this table to `AGENTS.md` §2:

```markdown
## 2. Agent Registry

| Agent | File | Invoked by | Trigger |
|-------|------|------------|---------|
| Dev Quality Lead | `.github/agents/dev-quality-lead.agent.md` | User directly | "run quality checks", "pre-commit", "validate and commit" |
| Code Quality Checker | `.github/agents/code-quality-checker.agent.md` | dev-quality-lead | Internal only |
| Test Runner | `.github/agents/test-runner.agent.md` | dev-quality-lead | Internal only |
| Debug Evaluator | `.github/agents/debug-evaluator.agent.md` | dev-quality-lead | Internal only |
| Pre-Commit Gate | `.github/agents/pre-commit-gate.agent.md` | dev-quality-lead | Internal only |
| Commit Tagger | `.github/agents/commit-tagger.agent.md` | dev-quality-lead | Internal only |
| Cloud Reviewer | `.github/agents/cloud-reviewer.agent.md` | User directly | "review for cloud", "cloud readiness", "pre-deployment check" |
| Migration Analyst | `.github/agents/migration-analyst.agent.md` | User directly | "analyze migration/", "what's in migration/" |
| Multi-Agent Orchestrator | `.github/agents/multi-agent-orchestrator.agent.md` | Scheduler / User | "orchestrate worktrees", "sync agents" |
```

---

#### SPEC-05: Add `agentskills/` documentation

**Problem:** `agentskills/` contains 5 skills (`add-feature`, `expert-advice`, `start-dev-server`, `review`, `wasp-plugin-*`) with no documentation in any AGENTS file.

**Action:** Add a section to `AGENTS.md`:

```markdown
## Agent Skills (`agentskills/`)

Reusable skill definitions for common tasks. Load with your agent runtime's skill loader.

| Skill | Purpose |
|-------|---------|
| `add-feature` | Scaffold a new feature following project conventions |
| `expert-advice` | Request architectural or design guidance |
| `start-dev-server` | Start the local development stack |
| `review` | Run a code review pass on staged changes |
| `wasp-plugin-help` | Get help with Wasp plugin integration |
| `wasp-plugin-init` | Initialize a new Wasp plugin |
```

---

#### SPEC-06: Add folder-scoped `AGENTS.md` to missing directories

**Problem:** `src/`, `prompt-registry/`, and `awesome-copilot/` are active code directories with no agent guidance.

**Action:** Create minimal `AGENTS.md` in each:

**`src/AGENTS.md`** — document: TypeScript SDK entry points, build command (`npm run build`), test command (`npm test`), key exports.

**`prompt-registry/AGENTS.md`** — document: VS Code extension structure, compile (`npm run compile`), lint (`npm run lint`), test (`npm run test:unit`), how prompts are registered.

**`awesome-copilot/AGENTS.md`** — document: skill/prompt file conventions, validation command (`npm run skill:validate`), upstream sync policy.

---

#### SPEC-07: Add Human-in-the-Loop and Error Escalation policies

**Problem:** No documented policy for when agents must pause for human approval, or what to do on unrecoverable failure.

**Action:** Add to `AGENTS.md`:

```markdown
## 8. Human-in-the-Loop Policy

Agents MUST pause and request explicit user approval before:
- Any `git push` or remote operation
- Creating or merging a PR
- Deleting files outside `migration/` or `tmp/`
- Any operation that modifies `.env`, secrets, or credentials

## 9. Error Escalation Policy

If an agent reaches an unrecoverable state (3 consecutive failures, missing dependency, gate NO-GO):
1. Stop all further actions immediately.
2. Output a structured failure report with: agent name, step that failed, error excerpt, suggested remediation.
3. Do NOT attempt workarounds or retries beyond 3 attempts.
4. Do NOT proceed to downstream agents.
```

---

### Priority 3 — Fix inconsistencies and stale references

#### SPEC-08: Fix `cloud-reviewer` phantom sub-agent references

**Problem:** References `se-security-reviewer`, `terraform-iac-reviewer`, etc. as "Sources" — these agents do not exist.

**Action:** Either:
- (a) Remove the "Sources" column from the step table and treat the cloud-reviewer as self-contained, OR
- (b) Create stub agent files for the referenced agents with a `status: planned` frontmatter field.

Recommended: option (a) for now. Remove the column, add a note: `"This agent performs all review steps internally. Sub-agent delegation is planned."`

---

#### SPEC-09: Fix or stub `multi-agent-orchestrator` missing workflow

**Problem:** References `.github/workflows/multi-agent-orchestrator.yml` and `.github/scripts/orchestrator.js` — neither exists.

**Action:** Either:
- (a) Create the workflow file and a stub `orchestrator.js`, OR
- (b) Add `status: planned` to the agent frontmatter and note the missing files explicitly.

Recommended: option (b) until the orchestrator is actually implemented. Add to frontmatter:

```yaml
status: planned
missing-artifacts:
  - .github/workflows/multi-agent-orchestrator.yml
  - .github/scripts/orchestrator.js
```

---

#### SPEC-10: Add `migration-analyst` trigger phrases to frontmatter

**Problem:** `migration-analyst.agent.md` has no `description` frontmatter with trigger phrases, making it undiscoverable by agent runtimes that use frontmatter for routing.

**Action:** Add frontmatter:

```yaml
---
name: "Migration Analyst"
description: >
  Analyzes content in migration/ to identify reusable patterns and integration risks.
  USE WHEN: 'analyze migration', 'what can we reuse', 'review migration folder',
  'migration assessment', 'integrate from migration'.
tools: [read_file, grep_search, semantic_search, file_search, run_in_terminal]
user-invocable: true
---
```

---

#### SPEC-11: Standardize tool declarations across all agents

**Problem:** Tool lists are inconsistent — some use exact tool names (`execute/runInTerminal`), others use generic categories (`execute, search`).

**Action:** Adopt a two-tier convention documented in `AGENTS.md`:

```markdown
Tool declaration format:
- User-facing agents: list specific tool names (enables runtime permission scoping)
- Internal subagents: may use category shorthand (`execute`, `search`, `read`) if the
  runtime does not support fine-grained tool scoping
```

Update `pre-commit-gate`, `test-runner`, `code-quality-checker`, `commit-tagger`, and `debug-evaluator` to use consistent category shorthand or specific names — pick one and apply uniformly.

---

## 3. Implementation Order

| # | Spec | Effort | Blocks |
|---|------|--------|--------|
| 1 | SPEC-01: Replace root AGENTS.md | Medium | Everything |
| 2 | SPEC-02: Fix dev-quality-lead corruption | Low | Gate pipeline |
| 3 | SPEC-03: Remove hardcoded paths | Low | All agent commands |
| 4 | SPEC-04: Add Agent Registry | Low | Discoverability |
| 5 | SPEC-07: Add HITL + escalation policy | Low | Safety |
| 6 | SPEC-05: Document agentskills/ | Low | Skill usage |
| 7 | SPEC-06: Add missing folder AGENTS.md | Medium | Subfolder guidance |
| 8 | SPEC-08: Fix cloud-reviewer phantom refs | Low | Accuracy |
| 9 | SPEC-09: Stub orchestrator artifacts | Low | Accuracy |
| 10 | SPEC-10: Add migration-analyst triggers | Low | Discoverability |
| 11 | SPEC-11: Standardize tool declarations | Low | Consistency |

---

## 4. Files to Change

| File | Action |
|------|--------|
| `AGENTS.md` | **Replace** — rewrite from `AGENTS-revised.md` + new sections |
| `AGENTS-revised.md` | **Delete** — content merged into AGENTS.md |
| `CLAUDE.md` | **Replace** — reset to Claude-specific instructions only |
| `.github/agents/dev-quality-lead.agent.md` | **Rewrite** — fix corruption |
| `.github/agents/pre-commit-gate.agent.md` | **Edit** — replace hardcoded paths |
| `.github/agents/test-runner.agent.md` | **Edit** — replace hardcoded paths |
| `.github/agents/commit-tagger.agent.md` | **Edit** — replace hardcoded paths |
| `.github/agents/cloud-reviewer.agent.md` | **Edit** — remove phantom sub-agent refs |
| `.github/agents/multi-agent-orchestrator.agent.md` | **Edit** — add `status: planned` |
| `.github/agents/migration-analyst.agent.md` | **Edit** — add frontmatter triggers |
| `src/AGENTS.md` | **Create** |
| `prompt-registry/AGENTS.md` | **Create** |
| `awesome-copilot/AGENTS.md` | **Create** |
