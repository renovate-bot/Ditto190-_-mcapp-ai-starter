# Dev Environment Migration Plan: Direnv + Nix (+ asdf-direnv Compatibility)

## Status

**Type:** Foundation + Implementation Plan  
**Scope in this pass:** Non-breaking setup files and migration blueprint  
**Execution mode:** Incremental, reversible, and devcontainer-compatible

---

## 1) Objective

Establish a reproducible, low-friction developer environment strategy that:

- reduces shell/path drift,
- improves onboarding consistency across local/devcontainer usage,
- preserves existing Docker Compose workflow,
- supports gradual adoption without breaking current scripts.

This document analyzes Direnv, Nix ecosystem components, and asdf-direnv; then defines a phased implementation plan tailored to this repository.

---

## 2) Source Links (Requested)

1. Direnv  
   - https://direnv.net/

2. Nix / NixOS ecosystem  
   - nixpkgs repo: https://github.com/NixOS/nixpkgs.git  
   - NixOS tree path (specific revision): https://github.com/NixOS/nixpkgs/tree/9576c24a0ca1746d83d84bb40eaa0839f38d440b/nixos  
   - Determinate Nix installer docs: https://docs.determinate.systems/determinate-nix/  
   - Nix package catalogue fork: https://github.com/Ditto190/nixpkgs-pkgOS.git  
   - Nix repo: https://github.com/NixOS/nix.git

3. asdf-direnv plugin  
   - https://github.com/asdf-community/asdf-direnv

---

## 3) Current Repository Baseline (Observed)

- Environment provisioning is currently script-driven:
  - `.devcontainer/devcontainer.json` installs Node/Python via devcontainer features
  - `.devcontainer/post-create.sh` performs additional setup (uv, pip install, scripts, background setup)
- Docker Compose and `.env` workflow are central to runtime operations.
- Node and Python coexist; tooling is mixed across npm/pip/uv/shell scripts.
- Existing workflows are functional, but can drift across host/container contexts over time.

---

## 4) Technology Analysis

## 4.1 Direnv

### What it contributes
- Automatic directory-scoped environment activation.
- Trust gate (`direnv allow`) prevents accidental execution.
- Smooth orchestration point for loading either Nix shells or conventional vars.

### Why it fits here
- This repo has many scripts and environment assumptions; direnv can centralize activation behavior.
- Minimal disruption to current Docker/Devcontainer process.

### Caveats
- Not a package manager.
- Should not blindly auto-load secrets from `.env` by default.

---

## 4.2 Nix ecosystem (nix + nixpkgs + flake model)

### What it contributes
- Reproducible, declarative dev shell with pinned inputs.
- Consistent cross-machine tool versions.
- Better determinism than ad hoc install scripts.

### Why it fits here
- Current setup mixes installation layers (devcontainer features + post-create script installs).
- Nix can become the single source of truth for core CLI tools.

### Caveats
- Team learning curve.
- Requires careful overlap management with devcontainer setup.

### Determinate Nix installer relevance
- Provides smoother bootstrap for contributors adopting Nix.
- Good entry path for mixed-experience teams.

---

## 4.3 asdf-direnv

### What it contributes
- Bridges asdf version management with direnv auto-activation.
- Useful compatibility lane where Nix adoption is deferred.

### Why it fits here
- Enables phased migration and optional contributor path.
- Can coexist during transition.

### Caveats
- Less hermetic than Nix.
- Plugin-based toolchains can still drift.

---

## 5) Recommended Target Architecture

Primary path:
- **Direnv + Nix flake dev shell** for reproducible toolchain.

Compatibility path:
- **asdf-direnv + `.tool-versions`** for contributors not ready for Nix.

Runtime path:
- Keep Docker Compose as service runtime backbone.
- Keep devcontainer, but gradually align provisioning with flake-defined shell.

---

## 6) Phased Implementation Plan

## Phase 0 (completed in this pass: foundation)

- Add `.envrc` with non-breaking defaults and optional Nix loading.
- Add initial `flake.nix` devShell for core tooling.
- Keep all existing scripts/workflows intact.
- Document migration blueprint and sources (this file).

Deliverables:
- `.envrc`
- `flake.nix`
- `docs/dev-environment-migration-plan-direnv-nix-asdf.md`
- AGENTS.md planned-feature entry (to be linked)

---

## Phase 1 (pilot: optional usage)

1. Team trial with direnv + flake in local environments.
2. Add concise setup instructions:
   - install direnv,
   - install Nix via Determinate docs,
   - run `direnv allow`.
3. Collect pain points for shell startup speed, command availability, and interoperability.

Success metrics:
- New contributor can run baseline tool commands in <10 minutes.
- Reduced “missing tool/version mismatch” reports.

---

## Phase 2 (alignment)

1. De-duplicate installs between `.devcontainer/post-create.sh` and flake shell.
2. Keep post-create focused on runtime bootstrap and project-specific initialization.
3. Add explicit environment checks to scripts/CI docs.

---

## Phase 3 (CI parity)

1. Add optional Nix-based CI jobs for lint/tests in parallel to existing jobs.
2. Compare outcomes and flake-lock update cadence.
3. Promote Nix-based jobs gradually after stability period.

---

## Phase 4 (compatibility lane)

1. Add `.tool-versions` for asdf users.
2. Add asdf-direnv setup notes.
3. Keep as non-default fallback.

---

## 7) Security and Governance Considerations

- Require review of `.envrc` changes (treat as executable policy).
- Keep `.env` loading opt-in to reduce accidental secret exposure.
- Pin Nix inputs and review lock updates in PRs.
- During migration, keep dual-path workflow until reliability is verified.

---

## 8) Risk Register + Mitigations

1. **Nix onboarding friction**  
   - Mitigation: Determinate installer docs, optional rollout, compatibility lane.

2. **Devcontainer/Nix overlap confusion**  
   - Mitigation: clear ownership split (devcontainer = runtime shell/container; flake = toolchain).

3. **CI migration regressions**  
   - Mitigation: run in parallel first; keep baseline jobs unchanged initially.

4. **Script breakage risk**  
   - Mitigation: no destructive changes in foundation phase; incremental edits only.

---

## 9) Rollback Strategy

- Remove/ignore `.envrc` and flake usage docs as default path.
- Continue using existing devcontainer + post-create + Docker Compose workflow.
- Disable Nix CI jobs independently without touching baseline pipeline.

---

## 10) Planned Next Implementation PR (post-container rebuild)

1. Add contributor quickstart section for direnv + Determinate Nix.
2. Add `flake.lock` and lock maintenance guidance.
3. Add optional CI validation job using `nix develop`.
4. Add compatibility docs for asdf-direnv and `.tool-versions`.
5. Propose devcontainer alignment patch to reduce duplicate installs.

---

## 11) Notes for AGENTS.md linkage

This migration is a **planned feature** and should be linked from `AGENTS.md` with a short “planned infrastructure feature” note, pointing to:

- `docs/dev-environment-migration-plan-direnv-nix-asdf.md`

Suggested tag:
- `#planned-feature`
- `#environment`
- `#direnv`
- `#nix`
