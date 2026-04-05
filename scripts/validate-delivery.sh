#!/usr/bin/env bash
# =============================================================================
# validate-delivery.sh — Validate Skills/Agents/Workflows Delivery
# =============================================================================
# Quick validation: are all required files in place?
# Returns 0 (success) or 1 (failure) for CI integration.
# =============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Full validation delegates to generate-agent-skills.sh
exec bash "${REPO_ROOT}/scripts/generate-agent-skills.sh" "$@"
