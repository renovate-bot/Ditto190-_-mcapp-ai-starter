# Orchestrator Plan — Migration, Dependency, Infra, CI, QA, and Staged Split

Purpose: sequence and coordinate the multi-agent work needed to migrate, map dependencies, prepare infra, decompose CI, harness QA, and perform a staged split of external projects into this mono-repo. Use `gpt-4.1` (lowest-cost model requested) for drafting outputs and rely on `fff`/ContextStream proxies for heavy searches.

Working dir: /workspaces/mcapp-ai-starter
Key source folders: `migration/`, `docs/github-repo-architecture/`, `awesome-copilot/agents/`

NOTE: I attempted to read `.github/hooks/automating-with-hooks.md` but it was not present in the workspace; the plan below nevertheless includes a hook-based activation example you can adapt to the repo's hooks doc.

High-level phases (ordered):

- Phase 0 — Prep & Pause External Syncs
- Phase 1 — Migration Analysis
- Phase 2 — Dependency Mapping & Lockfile Reconciliation
- Phase 3 — Infra Prep & Sandbox Provisioning
- Phase 4 — CI Decomposition & Pipeline Scaffolding
- Phase 5 — QA Harnessing & Test Orchestration
- Phase 6 — Staged Splitting, Merge, and Cleanup

Timeline (recommended baseline)

- Week 0 (2 days): Phase 0 prep + pause external syncs; approvals to proceed from repo owner and security
- Week 1: Phase 1 — migration analysis report and decisions
- Week 2: Phase 2 — dependency graph, unified lockfile plan, and rollback strategy
- Week 3: Phase 3 — infra sandbox provisioned and smoke-tested
- Week 4: Phase 4 — CI decomposition prototype and policy review
- Week 5: Phase 5 — QA harness integrated and acceptance tests passing for sandbox
- Week 6–7: Phase 6 — staged splits (1–3 small components per week), PRs + reviews + merge

Milestones & Required Approvals

- M0: Pause external syncs applied — Approver: Repo Owner or Orchestrator service account
- M1: Migration Analysis delivered — Approver: Architecture Lead
- M2: Dependency mapping & lockfile plan accepted — Approvers: Security (SCA), Dependency Owner, Build Lead
- M3: Infra sandbox green — Approvers: Infra Lead, Security
- M4: CI decomposition PR merged into `ci-prototype` — Approvers: CI Lead
- M5: QA harness validation (pass) — Approvers: QA Lead
- M6: First staged split merged to `main` — Approvers: Code Reviewers + Release Manager

General rules / guardrails

- Always run `switch_agent` to Plan-mode before any non-trivial architecture decision (call `switch_agent({agentName: "Plan"})`).
- Use `runSubagent` for bounded worker tasks (tests, dependency scans, infra provisioning). Each delegation template below includes a `switch_agent` mention where Plan-mode is required.
- Use ContextStream/fff proxies for heavy searches (semantic file discovery) rather than repo-wide grep.
- Record every plan and decision to ContextStream session with `capture_plan`/`create_task` per ContextStream rules.

Phase 0 — Prep & Pause External Syncs

- Objective: stop external synchronization while we plan and perform atomic lifts to avoid race conditions.
- Actions:
  - Pause syncs where applicable using: `mcp_com_supabase__pause_project(project_id="<proj-id>")` (run with appropriate credentials).
  - Notify stakeholders via email/Slack and create ContextStream snapshot (session capture).
  - Create `ci-prototype` branch for CI experiments.
- Outputs: paused state checklist, stakeholders notified, `ci-prototype` branch created.

RunSubagent template — Pause syncs (Phase 0)

```js
await runSubagent({
  prompt: `Pause external syncs for project list: <proj-id-1>,<proj-id-2>. Run validation that no new syncs happen for 24h.`,
  description: "Pause Supabase project syncs and validate paused state",
  agentName: "Dev Quality Lead"
});
// After run: call mcp_com_supabase__pause_project(project_id="<proj-id>")
```

Phase 1 — Migration Analysis

- Objective: inventory `migration/`, identify reusable code, risk, and a gated integration plan.
- Inputs: `migration/` contents, `awesome-copilot/agents/`, existing AGENTS.md and docs.
- Worker tasks: run `migration-analyst` subagent to produce structured table and proposed actions (copy/adapt/skip/archive) per file.
- High-level planning: BEFORE merging any migration items, call `switch_agent({agentName: "Plan"})` to validate the integration approach and test plan.

RunSubagent template — Migration Analysis (Phase 1)

```js
await runSubagent({
  prompt: `Analyze files in migration/ and produce a reuse table: File | Type | Reuse Verdict | Risk | Proposed Action. Include required tests and CI gates for each 'High' or 'Medium' item.`,
  description: "Migration inventory and gated integration plan",
  agentName: "migration-analyst"
});
// After receiving results: call switch_agent({agentName: "Plan"}) to finalize the integration ordering.
```

Phase 2 — Dependency Mapping & Lockfile Reconciliation

- Objective: produce a consolidated dependency graph, identify duplicate packages, and produce a lockfile reconciliation plan.
- Actions:
  - Use dependency graph tools (pnpm/npm/yarn, `npm ls --all`, `pip list --format=json`) in dedicated worker runs.
  - Create mapping: package → owning component(s) → required version range.
  - Propose strategy: single unified lockfile per language or per-component lockfiles with controlled CI builds.
- Outputs: `dependency-graph.json`, reconciliation plan, SCA scan results.

RunSubagent template — Dependency Mapping (Phase 2)

```js
await runSubagent({
  prompt: `Generate dependency graph for repo roots: package.json, prompt-registry, awesome-copilot, GenerateAgents.md. Produce JSON edges and list top 50 transitive deps. Suggest unified lockfile options.`,
  description: "Dependency mapping and lockfile plan",
  agentName: "Code Quality Checker"
});
// After results: switch_agent({agentName: "Plan"}) to pick reconciliation strategy with Security.
```

Phase 3 — Infra Prep & Sandbox Provisioning

- Objective: provision isolated infra/sandbox to validate builds, runtime, and integration without impacting production.
- Actions:
  - Provision sandbox (k8s namespace, ephemeral Supabase project, test Postgres, qdrant), run smoke tests.
  - Provide infra-as-code artifacts and runbook for teardown.
- Outputs: `infra/sandbox/` manifests, smoke-test logs.

RunSubagent template — Infra Prep (Phase 3)

```js
await runSubagent({
  prompt: `Provision ephemeral sandbox infra (Supabase test project, test Postgres, Qdrant) using IaC templates. Run the project's health-check script and return connectivity and logs.`,
  description: "Infra sandbox provisioning and smoke tests",
  agentName: "ac-devops"
});
// After provisioning: switch_agent({agentName: "Plan"}) for cutover checklist review.
```

Phase 4 — CI Decomposition & Pipeline Scaffolding

- Objective: split monolithic CI into smaller, targeted pipelines; create `ci-prototype` to trial decomposition.
- Actions:
  - Create pipeline templates: `validate`, `unit`, `integration`, `audit`, `build`, `notify` (example in .gitlab-ci.yml)
  - Implement matrix triggers and path filters; use concurrency cancellation for frequent branch updates.
  - Validate cost, run time, and artifact management.
- Outputs: `/.github/workflows/ci-prototype.yml`, `ci-prototype` branch.

RunSubagent template — CI Decomposition (Phase 4)

```js
await runSubagent({
  prompt: `Scaffold CI prototype workflows: fast validate job (changed files filter), parallel unit jobs per workspace, audit stage scheduled weekly, and artifact reuse pattern. Provide a sample workflow file and estimated run times.`,
  description: "CI decomposition and prototype scaffolding",
  agentName: "ac-ci-cd"
});
// Then run switch_agent({agentName: "Plan"}) to approve pipeline permission scopes and secrets policy.
```

Phase 5 — QA Harnessing & Test Orchestration

- Objective: centralize test orchestration, define required test suites per component, and integrate with CI prototypes.
- Actions:
  - Build QA harness: targeted unit tests, non-e2e integration jobs, and separate e2e runs for release candidates.
  - Integrate test-run reporting and debug-evaluator to categorize failures.
- Outputs: QA matrix, test-run dashboards, failure triage playbook.

RunSubagent template — QA Harness (Phase 5)

```js
await runSubagent({
  prompt: `Run targeted test matrix for changed components; capture failing tests and categorize by flaky/functional/regression. Produce a list of required diagnostic artifacts for each failure.`,
  description: "QA harness run and failure triage",
  agentName: "Test Runner"
});
// On non-trivial failures call switch_agent({agentName: "Plan"}) to decide remediation path.
```

Phase 6 — Staged Splitting, Merge, and Cleanup

- Objective: perform incremental merges of small, verified components into `main`, unpause syncs when safe, and clean up migration artifacts.
- Actions:
  - For each split: open draft PR, request reviewers (@code-reviewer, @security-reviewer), validate CI, merge on approval.
  - After final merge of a component, resume external syncs for related projects if needed: `mcp_com_supabase__resume_project(project_id="<proj-id>")`.
  - Archive or remove migration items that were copied.
- Outputs: merged PRs, release notes, updated AGENTS.md.

RunSubagent template — Staged Split (Phase 6)

```js
await runSubagent({
  prompt: `Create draft PR to merge component X into main, include changelog, run CI using ci-prototype and request reviews from code/security leads. Only merge after green CI and approvals.`,
  description: "Create PR and coordinate merge for staged split",
  agentName: "multi-agent-orchestrator"
});
// Use switch_agent({agentName: "Plan"}) for any manual conflict-resolution planning.
```

Hook-based activation example (unblocks paused task)

1) Hook file (example): `.github/hooks/unpause-and-run-subagent.sh`

```bash
#!/usr/bin/env bash
# Called by webhook or GitHub Action when preconditions met (e.g., stakeholder approval)
PROJECT_ID="$1"
SUBAGENT_PAYLOAD_FILE="$2"

# 1) Resume Supabase project
mcp_com_supabase__resume_project(project_id="$PROJECT_ID")

# 2) Trigger the runSubagent via the orchestrator (example CLI wrapper)
gh api repos/:owner/:repo/dispatches -f event_type=orchestrator-run -F client_payload="@$SUBAGENT_PAYLOAD_FILE"

# Logging
echo "Resumed project $PROJECT_ID and dispatched runSubagent payload $SUBAGENT_PAYLOAD_FILE"
```

1) GitHub Action trigger (example) — call the hook when PR label `unblock/infra` applied:

```yaml
name: Unpause and Run
on:
  pull_request:
    types: [labeled]

jobs:
  unpause-and-run:
    if: contains(github.event.label.name, 'unblock/')
    runs-on: ubuntu-latest
    steps:
      - name: Call unpause hook
        run: |
          bash .github/hooks/unpause-and-run-subagent.sh "${{ github.event.pull_request.head.ref }}" payload.json
```

Notes on the hook example: adapt to the repo's actual hooks documentation (.github/hooks/automating-with-hooks.md) if present.

Verification & Evidence

- For each phase, require: `artifact` (build/test logs), ContextStream plan capture, and a PR describing the change.
- Do not resume syncs until Phase 5 QA harness reports acceptance and Infra Lead signs off.

Risks & Mitigations

- Risk: dependency conflicts cause CI break — Mitigation: isolate builds in sandbox and use per-component lockfiles if needed.
- Risk: paused syncs disrupt other teams — Mitigation: notify stakeholders, allow emergency rollback and short pause windows.

Next steps (operational checklist)

1. Approve Phase 0 (Repo Owner) and run the Pause-runSubagent template.
2. Start Phase 1: call the Migration Analysis template and attach results to ContextStream.
3. Run Phase 2 tasks in parallel (dependency graph + SCA) using runSubagent; review in Plan-mode.

---
Generated: 2026-04-05 — orchestrator-plan.md
