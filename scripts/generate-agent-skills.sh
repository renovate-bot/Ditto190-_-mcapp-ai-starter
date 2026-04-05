#!/usr/bin/env bash
# =============================================================================
# generate-agent-skills.sh — Agent Skills Library Generator
# =============================================================================
# Bundles and compiles agent skills, workflow .md files, and validates delivery.
# Usage:
#   bash scripts/generate-agent-skills.sh              # validate + compile
#   bash scripts/generate-agent-skills.sh --new <name> # scaffold a new skill
# =============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="${REPO_ROOT}/.github/skills"
WORKFLOWS_DIR="${REPO_ROOT}/.github/workflows"
AGENTS_DIR="${REPO_ROOT}/awesome-copilot/agents"
AC_DIR="${REPO_ROOT}/awesome-copilot"
CONSOLIDATED="${REPO_ROOT}/consolidated_sources/awesome-copilot"

# Required skills (must match agent names)
REQUIRED_SKILLS=(
  "ac-feature-dev"
  "ac-github-workflows"
  "ac-qa-validation"
  "ac-ci-cd"
  "ac-debug"
  "ac-devops"
  "ac-documentation"
  "ac-maintenance"
  "ac-meta-orchestration"
)

REQUIRED_AGENTS=(
  "awesome-copilot-meta-architect.agent.md"
  "ac-feature-dev.agent.md"
  "ac-maintenance.agent.md"
  "ac-devops.agent.md"
  "ac-ci-cd.agent.md"
  "ac-debug.agent.md"
  "ac-github-workflows.agent.md"
  "ac-documentation.agent.md"
  "ac-qa.agent.md"
)

AGENTIC_WORKFLOWS=(
  "ac-skill-generator.md"
  "ac-workflow-compiler.md"
  "ac-delivery-validator.md"
)

# ─────────────────────────────────────────────────────────────────────────────
# Colors
# ─────────────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'
NC='\033[0m' # No Color
PASS="${GREEN}✅ PASS${NC}"
FAIL="${RED}❌ FAIL${NC}"
WARN="${YELLOW}⚠️  WARN${NC}"

pass=0; fail=0; warn=0

check_pass() { echo -e "  ${PASS} $1"; pass=$((pass + 1)); }
check_fail() { echo -e "  ${FAIL} $1"; fail=$((fail + 1)); }
check_warn() { echo -e "  ${WARN} $1"; warn=$((warn + 1)); }

# ─────────────────────────────────────────────────────────────────────────────
# Scaffold a new skill from template
# ─────────────────────────────────────────────────────────────────────────────
scaffold_skill() {
  local skill_name="$1"
  # Validate name: lowercase, hyphens only, ≤64 chars
  if [[ ! "$skill_name" =~ ^[a-z][a-z0-9-]{1,62}$ ]]; then
    echo -e "${RED}Error: skill name must be lowercase-hyphen, 2-63 chars${NC}"
    exit 1
  fi

  local skill_dir="${SKILLS_DIR}/${skill_name}"
  local skill_file="${skill_dir}/SKILL.md"

  if [[ -d "$skill_dir" ]]; then
    echo -e "${YELLOW}Skill '${skill_name}' already exists at ${skill_file}${NC}"
    exit 0
  fi

  mkdir -p "$skill_dir"
  cat > "$skill_file" <<TEMPLATE
---
name: ${skill_name}
description: >
  TODO: Describe what this skill does, when to use it, and trigger keywords.
  Use when asked to ...; triggers on: 'keyword1', 'keyword2'.
---

# ${skill_name^} Skill

TODO: Write the skill body here.

## When to Use This Skill

- Use case 1
- Use case 2

## Step-by-Step Workflows

### Workflow Name

\`\`\`bash
# commands here
\`\`\`

## References

- See \`consolidated_sources/awesome-copilot/instructions/\` for examples
TEMPLATE

  echo -e "${GREEN}✅ Scaffolded new skill: ${skill_file}${NC}"
  echo "Edit it, then run: bash scripts/generate-agent-skills.sh"
}

# ─────────────────────────────────────────────────────────────────────────────
# Handle --new flag
# ─────────────────────────────────────────────────────────────────────────────
if [[ "${1:-}" == "--new" ]]; then
  if [[ -z "${2:-}" ]]; then
    echo "Usage: $0 --new <skill-name>"
    exit 1
  fi
  scaffold_skill "$2"
  exit 0
fi

# ─────────────────────────────────────────────────────────────────────────────
# Main: validate + compile
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Agent Skills Library Generator & Validator   ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"

# 1. Check skills directory
echo ""
echo -e "${BLUE}── 1. Skill Files Check ──${NC}"
for skill in "${REQUIRED_SKILLS[@]}"; do
  skill_file="${SKILLS_DIR}/${skill}/SKILL.md"
  if [[ -f "$skill_file" ]]; then
    # Check frontmatter has name and description
    if grep -q "^name:" "$skill_file" && grep -q "description:" "$skill_file"; then
      check_pass "${skill}/SKILL.md (name + description present)"
    else
      check_fail "${skill}/SKILL.md (missing frontmatter fields)"
    fi
  else
    check_fail "${skill}/SKILL.md (FILE MISSING)"
  fi
done

# 2. Check agent files
echo ""
echo -e "${BLUE}── 2. Agent Files Check ──${NC}"
for agent in "${REQUIRED_AGENTS[@]}"; do
  if [[ -f "${AGENTS_DIR}/${agent}" ]]; then
    check_pass "${agent}"
  else
    check_fail "${agent} (MISSING from awesome-copilot/agents/)"
  fi
done

# 3. Check agentic workflow .md files
echo ""
echo -e "${BLUE}── 3. Agentic Workflow Files Check ──${NC}"
for workflow in "${AGENTIC_WORKFLOWS[@]}"; do
  if [[ -f "${WORKFLOWS_DIR}/${workflow}" ]]; then
    check_pass "${workflow}"
  else
    check_fail "${workflow} (MISSING from .github/workflows/)"
  fi
done

# 4. gh aw compile check
echo ""
echo -e "${BLUE}── 4. gh aw Compile ──${NC}"
if command -v gh &>/dev/null && gh extension list 2>/dev/null | grep -q "gh-aw"; then
  for workflow in "${AGENTIC_WORKFLOWS[@]}"; do
    workflow_path="${WORKFLOWS_DIR}/${workflow}"
    if [[ -f "$workflow_path" ]]; then
      if gh aw compile "$workflow_path" 2>&1 | grep -q "error(s).*0"; then
        check_pass "Compiled: ${workflow}"
      else
        check_warn "Compile issues: ${workflow}"
      fi
    fi
  done
else
  check_warn "gh aw not installed (run: gh extension install github/gh-aw)"
fi

# 5. awesome-copilot npm validation (if available)
echo ""
echo -e "${BLUE}── 5. awesome-copilot npm skill:validate ──${NC}"
if [[ -f "${CONSOLIDATED}/package.json" ]]; then
  cd "${CONSOLIDATED}"
  if npm run skill:validate 2>&1 | tail -5 | grep -qi "error\|fail"; then
    check_fail "npm run skill:validate failed in consolidated_sources"
  else
    check_pass "npm run skill:validate passed in consolidated_sources"
  fi
  cd "${REPO_ROOT}"
else
  check_warn "consolidated_sources/awesome-copilot not found — skipping npm validation"
fi

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "  Results: ${GREEN}${pass} passed${NC}  ${RED}${fail} failed${NC}  ${YELLOW}${warn} warnings${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"

if [[ $fail -gt 0 ]]; then
  echo ""
  echo -e "${RED}Pipeline has ${fail} failure(s). Fix and re-run.${NC}"
  exit 1
fi
echo -e "${GREEN}All checks passed!${NC}"
