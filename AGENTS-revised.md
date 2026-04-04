# AGENTS.md — Copilot & Agent Instructions (Ditto190 Fork)

## 0) Identity & Goal

- **User:** Ditto190 (Researcher)
- **Primary goal:** Build a rigorous, reproducible, automation-first “agent OS” for coding + research.
- **Tone:** Formal, professional, actionable.
- **Priority:** Traceability, correctness, reproducibility, and reusability.

---

## 1) MUST‑READ Order (all agents)

1. **AGENTS.md** (this file)
2. `README.md`
3. `CONTRIBUTING.md`
4. `.github/pull_request_template.md`
5. `.github/CODEOWNERS` (if present)

If any are missing, propose adding them immediately.

---

## 2) Canonical Agent Source & Indexing (NON‑NEGOTIABLE)

- **Canonical source of reusable assets:** `Ditto190/awesome-copilot`
- **Local cache/index location:** `vendor/awesome-copilot-index/`
- **Update method:** event‑driven on push to `awesome-copilot` (with fallback schedule)
- **Agents MUST use the cached index** during PR creation and review.
- If index is stale, note in PR:  
  `Index stale vs upstream; request refresh.`

---

## 3) Local vs Upstream Assets

- **Use upstream (`awesome-copilot`)** for reusable prompts, skills, checklists.
- **Use local assets** only for repo‑specific logic under:
  - `agents/`
    - `agents/prompts/`
    - `agents/review/`
    - `agents/skills/`
    - `agents/subagents/`
- If a new asset is reusable, propose upstreaming to `awesome-copilot`.

---

## 4) PR Authoring Requirements (ALL PRs)

Every PR MUST include:

- **Intent & scope**
- **Changes summary**
- **Validation steps**
- **Risks / tradeoffs**
- **awesome‑copilot reuse note**  
  (what prompt/skill/checklist was used, or “none”)

---

## 5) Review Requirements (ALL reviews)

Reviewers MUST check:

- correctness
- scope discipline
- maintainability
- automation readiness
- alignment with AGENTS.md

Comments must be actionable and include severity:  
**blocker / non‑blocker / suggestion**

---

## 6) Cross‑Provider Rules

- This repo supports **Copilot, Claude, Cursor, etc.**
- All providers MUST follow **AGENTS.md** first.
- No provider‑specific syntax allowed.
- If a provider cannot access upstream, it must:
  - disclose limitation in PR, and
  - use local assets under `agents/`.

---

## 7) Safety & Integrity

- Never commit secrets.
- Respect licensing.
- Prompt assets are treated as code: versioned, reviewed, attributed.

---

## 8) Operating Procedure (Step‑by‑Step)

1. Read required docs (Section 1).
2. Classify task type (feature/bug/docs/ci/security/research).
3. Search cached index in `vendor/awesome-copilot-index/`.
4. Use relevant prompt/skill/checklist.
5. Implement minimal, testable changes.
6. Validate locally + CI.
7. Fill PR template fully.
8. Propose upstreaming reusable assets when applicable.

---

## 9) Language & Tooling

- Primary languages: **TypeScript, Python, JavaScript, Go**
- Automation preferred via **TypeScript + esbuild** (if bundling needed)

---

## 10) If Anything Conflicts

**AGENTS.md overrides all other instructions.**
