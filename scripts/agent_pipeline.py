#!/usr/bin/env python3
"""
Dynamic Agent Generation Pipeline
Connects: awesome-copilot → agentspec → skills-ref validation → marketplace catalogue

Usage:
    uv run python scripts/agent_pipeline.py            # full pipeline
    uv run python scripts/agent_pipeline.py --validate-only
    uv run python scripts/agent_pipeline.py --emit agents-md
    uv run python scripts/agent_pipeline.py --compose "security-best-practices,code-quality-checker"
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AWESOME_COPILOT = ROOT / "consolidated_sources" / "awesome-copilot"
SKILLS_REF = ROOT / "consolidated_sources" / "agentskills" / "skills-ref"
MCP_DIR = ROOT / "generateagents-mcp"
AGENTSPEC_GENERATED = MCP_DIR / "agentspec" / "generated"
AGENTSPEC_JSON = AGENTSPEC_GENERATED / "awesome-copilot.agentspec.json"
MARKETPLACE_CATALOGUE = AGENTSPEC_GENERATED / "marketplace-catalogue.json"

sys.path.insert(0, str(MCP_DIR))


def step_generate_agentspec(ac_path: Path = AWESOME_COPILOT) -> dict:
    """Step 1: Parse awesome-copilot and generate agentspec JSON."""
    print("\n[1/4] Generating AgentSpec from awesome-copilot...")
    from agentspec_mvp import generate_agentspec_from_awesome_copilot

    AGENTSPEC_GENERATED.mkdir(parents=True, exist_ok=True)
    result = generate_agentspec_from_awesome_copilot(
        awesome_copilot_path=str(ac_path),
        output_path=str(AGENTSPEC_JSON),
    )

    if result.get("success"):
        print(f"  ✅ {result['agent_count']} agents, {result['skill_count']} skills")
        print(f"     → {AGENTSPEC_JSON}")
    else:
        print(f"  ❌ {result.get('error_message', 'unknown error')}")

    return result


def step_validate_with_skills_ref(skills_dir: Path = AWESOME_COPILOT / "skills") -> dict:
    """Step 2: Validate skills using the agentskills skills-ref CLI."""
    print("\n[2/4] Validating skills with skills-ref...")
    errors = []
    validated = 0
    skipped = 0

    for skill_dir in skills_dir.iterdir():
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            skipped += 1
            continue

        result = subprocess.run(
            ["uv", "run", "--project", str(SKILLS_REF), "skills-ref", "validate", str(skill_dir)],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        if result.returncode != 0:
            errors.append(
                {"skill": skill_dir.name, "error": result.stderr.strip() or result.stdout.strip()}
            )
        else:
            validated += 1

    status = "clean" if not errors else "warnings"
    print(
        f"  {'✅' if not errors else '⚠️ '} {validated} valid, {skipped} skipped, {len(errors)} errors"
    )
    if errors:
        for e in errors[:3]:
            print(f"     ⚠️  {e['skill']}: {e['error'][:80]}")
        if len(errors) > 3:
            print(f"     ... and {len(errors) - 3} more")

    return {"success": not bool(errors), "status": status, "validated": validated, "errors": errors}


def step_emit_artifacts(
    targets: list[str] | None = None,
    output_dir: Path = AGENTSPEC_GENERATED,
) -> dict:
    """Step 3: Emit AGENTS.md and/or n8n workflow from the agentspec."""
    print("\n[3/4] Emitting artifacts...")
    from agentspec_integration import emit_agentspec_artifacts

    target_list = targets or ["agents-md", "n8n-workflow"]
    result = emit_agentspec_artifacts(str(AGENTSPEC_JSON), target_list, str(output_dir))

    if result.get("success"):
        for target, path in result.get("emitted", {}).items():
            print(f"  ✅ {target}: {path}")
    else:
        print(f"  ❌ {result.get('error_message', 'emission failed')}")

    return result


def step_build_marketplace_catalogue() -> dict:
    """Step 4: Build a growing marketplace catalogue JSON from the agentspec."""
    print("\n[4/4] Building marketplace catalogue...")
    import datetime

    if not AGENTSPEC_JSON.exists():
        return {"success": False, "error_message": "agentspec JSON not found — run step 1 first"}

    spec = json.loads(AGENTSPEC_JSON.read_text(encoding="utf-8"))
    agents = spec.get("agents", {})
    tools = spec.get("tools", {})

    # Merge with existing catalogue if it exists (catalogue grows over time)
    existing: dict = {}
    if MARKETPLACE_CATALOGUE.exists():
        try:
            existing = json.loads(MARKETPLACE_CATALOGUE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass

    # Index existing entries for dedup
    existing_agent_ids = {a["id"] for a in existing.get("agents", [])}
    existing_skill_ids = {s["id"] for s in existing.get("skills", [])}

    new_agents = [
        {
            "id": k,
            "name": v.get("name", k),
            "description": v.get("description", ""),
            "type": "agent",
            "source_file": v.get("source_file", ""),
        }
        for k, v in agents.items()
        if k not in existing_agent_ids
    ]
    new_skills = [
        {
            "id": k,
            "name": v.get("name", k),
            "description": v.get("description", ""),
            "type": "skill",
            "source_file": v.get("source_file", ""),
        }
        for k, v in tools.items()
        if k not in existing_skill_ids
    ]

    merged_agents = existing.get("agents", []) + new_agents
    merged_skills = existing.get("skills", []) + new_skills

    catalogue = {
        "version": "1.0.0",
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "source": str(AWESOME_COPILOT),
        "stats": {"agent_count": len(merged_agents), "skill_count": len(merged_skills)},
        "agents": merged_agents,
        "skills": merged_skills,
    }

    MARKETPLACE_CATALOGUE.write_text(json.dumps(catalogue, indent=2), encoding="utf-8")
    print(f"  ✅ {len(merged_agents)} agents, {len(merged_skills)} skills")
    print(f"     → {MARKETPLACE_CATALOGUE}")
    if new_agents or new_skills:
        print(f"     ➕ Added {len(new_agents)} new agents, {len(new_skills)} new skills")

    return {
        "success": True,
        "agent_count": len(merged_agents),
        "skill_count": len(merged_skills),
        "new_agents": len(new_agents),
        "new_skills": len(new_skills),
        "output_path": str(MARKETPLACE_CATALOGUE),
    }


def compose_agent(agent_ids: list[str]) -> dict:
    """Compose a bespoke agent spec from named agents in the catalogue."""
    print(f"\n🔧 Composing agent from: {', '.join(agent_ids)}")
    if not MARKETPLACE_CATALOGUE.exists():
        return {"success": False, "error": "Catalogue not found — run pipeline first"}

    catalogue = json.loads(MARKETPLACE_CATALOGUE.read_text(encoding="utf-8"))
    agent_index = {a["id"]: a for a in catalogue.get("agents", [])}
    skill_index = {s["id"]: s for s in catalogue.get("skills", [])}

    selected = []
    missing = []
    for aid in agent_ids:
        if aid in agent_index:
            selected.append(agent_index[aid])
        elif aid in skill_index:
            selected.append(skill_index[aid])
        else:
            missing.append(aid)

    composed = {
        "version": "1.0.0",
        "name": "composed-agent",
        "description": f"Dynamically composed from: {', '.join(agent_ids)}",
        "components": selected,
        "missing": missing,
    }

    out = AGENTSPEC_GENERATED / "composed-agent.json"
    out.write_text(json.dumps(composed, indent=2), encoding="utf-8")
    print(f"  ✅ {len(selected)} components selected, {len(missing)} not found")
    if missing:
        print(f"  ⚠️  Missing: {missing}")
    print(f"     → {out}")
    return {"success": True, "selected": len(selected), "missing": missing, "output": str(out)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Dynamic Agent Generation Pipeline")
    parser.add_argument(
        "--validate-only", action="store_true", help="Only run skills-ref validation"
    )
    parser.add_argument("--emit", help="Emit targets (comma-separated: agents-md,n8n-workflow)")
    parser.add_argument("--compose", help="Compose agent from IDs (comma-separated)")
    parser.add_argument("--ac-path", default=str(AWESOME_COPILOT), help="Path to awesome-copilot")
    args = parser.parse_args()

    print("╔══════════════════════════════════════════════════╗")
    print("║       Dynamic Agent Generation Pipeline          ║")
    print("║  awesome-copilot → agentspec → skills-ref →      ║")
    print("║  emit → marketplace catalogue                    ║")
    print("╚══════════════════════════════════════════════════╝")

    if args.compose:
        compose_agent([s.strip() for s in args.compose.split(",")])
        return

    if args.validate_only:
        step_validate_with_skills_ref()
        return

    if args.emit:
        targets = [t.strip() for t in args.emit.split(",")]
        step_emit_artifacts(targets)
        return

    # Full pipeline
    r1 = step_generate_agentspec(Path(args.ac_path))
    if not r1.get("success"):
        sys.exit(1)

    step_validate_with_skills_ref()
    step_emit_artifacts()
    step_build_marketplace_catalogue()

    print("\n✅ Pipeline complete!")


if __name__ == "__main__":
    main()
