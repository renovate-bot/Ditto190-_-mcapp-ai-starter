# Codespace Session-End Plan And Best Practices

This guide defines a repeatable end-of-session workflow for this repository.

It is designed around three constraints:

1. A stopped Codespace preserves saved files in `/workspaces`, but it does not auto-commit or auto-push anything.
2. A deleted Codespace can take unpushed work with it.
3. Personal tooling, extensions, and local settings are safer when encoded as devcontainer config, dotfiles, Settings Sync, or exported inventories instead of being left implicit in the running container.

## What Persists And What Does Not

From GitHub Codespaces guidance gathered through Context7-backed GitHub Docs:

- Saved files under `/workspaces` persist across stop/start.
- Unsaved editor buffers can still be lost, especially outside web auto-save behavior.
- `/tmp` is cleared when the Codespace stops.
- Rebuilds preserve the mounted workspace, but local container state outside the workspace is not something to trust as a long-term backup.
- Deleted Codespaces delete unpushed work unless that work was committed, pushed, or copied elsewhere.

## Structured Session-End Plan

### Phase 1: Save And Snapshot

Best-practice pattern borrowed from the local `contextstream-workflow` skill and the repo’s operational skills:

- capture state first
- keep the workflow phased and explicit
- make verification part of the process
- prefer small, reversible actions over broad implicit automation

Run the snapshot script:

```bash
npm run session:pre-end -- --label my-session
```

This creates a gitignored snapshot under `.session-state/snapshots/<label>/` with:

- raw Git status and patch files
- sanitized copies of workspace config files
- inventories of optional tools and extensions
- restore helper scripts
- a generated `changelog.md` that marks newly added optional items where possible

### Phase 2: Review What Changed

Review these files in the snapshot:

- `changelog.md`
- `summary.md`
- `raw/git-working-tree.patch`

The changelog is intended to answer two questions quickly:

- what code and config changed in the repo
- what optional local tools or extensions are newly present compared to the previous snapshot

### Phase 3: Decide How Durable The Work Must Be

Use this decision tree:

- If the change only needs to survive a temporary disconnect or timeout, the snapshot plus saved files may be enough.
- If the change must survive Codespace deletion, branch cleanup, or machine loss, commit and push it.
- If the change is a personal preference, move it into dotfiles or Settings Sync instead of relying on this single Codespace.

## Tool-Guided Best Practices

### `mcp_gitkraken_git_add_or_commit` And Related Git Tools

Use Git-oriented tools to curate and explain a commit after reviewing the diff, not as a blind backup substitute.

Recommended behavior:

- snapshot first
- inspect staged and unstaged changes
- exclude secrets and machine-local artifacts from tracked commits
- prefer a focused WIP commit over an oversized end-of-day dump

If you want a repository-backed checkpoint after reviewing the snapshot:

```bash
npm run session:end -- --label my-session --commit --message "chore: save codespace session state"
git push
```

### GitHub Review And PR Tools

PR comment tools such as `mcp_github2_add_comment_to_pending_review` are follow-up tools, not backup tools.

Use them after push when you want to:

- leave a note that a session-end checkpoint was pushed
- document why a WIP commit exists
- explain why a config or workflow change was made

### Agent And Skill Expertise Applied Here

The local skill and agent patterns in this repo emphasize:

- phased workflows instead of one-shot automation
- explicit validation
- minimal, targeted changes
- documentation of risks before integration

Those patterns are reflected here:

- `session-pre-end.sh` captures state without changing Git history
- `session-end.sh` only commits or pushes when explicitly requested
- raw snapshots are gitignored to avoid accidental secret commits
- sanitized config copies are separated from raw patches

## CI/CD Best Practices Applied Here

From GitHub Actions guidance gathered through Context7 and from this repo’s existing workflows:

- default workflow permissions should stay at `contents: read`
- elevate permissions per job only when needed
- never cache secrets
- use artifacts for debug and recovery output when appropriate
- keep automation easy to run manually with `workflow_dispatch`

This repo already follows the least-privilege pattern in key workflows. The session-end automation follows the same rule.

## New Automation Added For This Workflow

### Local Scripts

- `scripts/session-pre-end.sh`
- `scripts/session-end.sh`
- `scripts/session-checkpoint.sh`
- `scripts/checkpoint-fast-review.sh`

### Package Entry Points

- `npm run session:pre-end`
- `npm run session:end`
- `npm run session:bundle`
- `npm run session:checkpoint`
- `npm run ci:checkpoint-fast-review`

### CI Validation

The new workflow runs the snapshot script in a dry-run style and uploads the generated snapshot as an artifact for inspection.

### Async Checkpoint Review Trigger

The new workflow `.github/workflows/checkpoint-fast-review.yml` is designed for quick, asynchronous review:

- Runs on pushes to non-main branches.
- Runs on PR updates.
- Supports a slash command trigger (`/checkpoint-review`) via `issue_comment` on PRs.
- Uses concurrency cancellation so stale in-progress runs are replaced by newer pushes.

This lets you checkpoint and push while continuing work, instead of batching all review waits at the end.

## Recommended End-Session Commands

Minimal local snapshot:

```bash
npm run session:pre-end -- --label daily-checkpoint
```

Snapshot plus archive:

```bash
npm run session:bundle -- --label daily-checkpoint
```

Snapshot, stop services, and then review before leaving:

```bash
npm run session:end -- --label daily-checkpoint --stop-services
```

Snapshot and explicit commit:

```bash
npm run session:end -- --label daily-checkpoint --commit --message "chore: save codespace session state"
git push
```

Checkpoint commit + push + optional PR creation:

```bash
npm run session:checkpoint -- --message "checkpoint: mid-session review" --open-pr
```

Trigger checkpoint review manually from a PR comment:

```text
/checkpoint-review
```

## Tool Mapping (Requested)

How these scripts and workflows align with your requested MCP tools:

- `mcp_gitkraken_git_add_or_commit`: Equivalent role to `session-checkpoint.sh` when staging and committing checkpoint changes.
- `mcp_github2_add_comment_to_pending_review`: Equivalent follow-up role to annotate review context after checkpoint pushes.
- `mcp_github2` PR and issue-comment capabilities: Mirrored operationally by `issue_comment` trigger + PR comment posting in `checkpoint-fast-review.yml`.

Recommended operating pattern:

1. Use checkpoint script for local savepoint + push.
2. Let fast review pipeline run asynchronously.
3. Add review-context comments only when needed (not for every tiny checkpoint).

## What To Put Somewhere More Permanent

Do not rely on session snapshots alone for these categories:

- important code changes
- shared devcontainer changes
- reusable VS Code settings that belong in the repo
- personal shell aliases and editor defaults that belong in dotfiles or Settings Sync

Use the snapshot as a safety net, not as the final source of truth.
