"""AgentSpec MVP: Parse real agents/skills from awesome-copilot, generate schema, validate.

MVP Scope:
- Parse .agent.md files from awesome-copilot/agents/
- Parse SKILL.md files from awesome-copilot/skills/*/
- Generate AgentSpec schema matching real data
- Validate schema compliance (required fields, types)
- Test with actual data

NO complex patterns - just parse, validate, test.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def _parse_frontmatter(content: str) -> dict[str, Any]:
    """Parse YAML frontmatter from markdown file.
    
    Returns:
        Dict with frontmatter fields or empty dict if none found
    """
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return {}
    
    frontmatter_text = match.group(1)
    result: dict[str, Any] = {}
    
    for line in frontmatter_text.split('\n'):
        line = line.strip()
        if not line or ':' not in line:
            continue
        
        key, _, value = line.partition(':')
        key = key.strip()
        value = value.strip().strip("'\"")
        result[key] = value
    
    return result


def parse_agents_from_awesome_copilot(awesome_copilot_path: str) -> list[dict[str, Any]]:
    """Parse all .agent.md files from awesome-copilot/agents/.
    
    Returns:
        List of agent dicts with: name, description, file_path
    """
    agents_dir = Path(awesome_copilot_path) / "agents"
    if not agents_dir.exists():
        return []
    
    agents: list[dict[str, Any]] = []
    
    for agent_file in agents_dir.glob("*.agent.md"):
        try:
            content = agent_file.read_text(encoding="utf-8")
            frontmatter = _parse_frontmatter(content)
            
            agent_id = agent_file.stem  # filename without extension
            agents.append({
                "id": agent_id,
                "name": frontmatter.get("name", agent_id),
                "description": frontmatter.get("description", ""),
                "file_path": str(agent_file),
            })
        except Exception as e:
            print(f"Warning: Failed to parse {agent_file}: {e}")
    
    return agents


def parse_skills_from_awesome_copilot(awesome_copilot_path: str) -> list[dict[str, Any]]:
    """Parse all SKILL.md files from awesome-copilot/skills/*/.
    
    Returns:
        List of skill dicts with: name, description, file_path
    """
    skills_dir = Path(awesome_copilot_path) / "skills"
    if not skills_dir.exists():
        return []
    
    skills: list[dict[str, Any]] = []
    
    for skill_file in skills_dir.glob("*/SKILL.md"):
        try:
            content = skill_file.read_text(encoding="utf-8")
            frontmatter = _parse_frontmatter(content)
            
            skill_id = skill_file.parent.name
            skills.append({
                "id": skill_id,
                "name": frontmatter.get("name", skill_id),
                "description": frontmatter.get("description", ""),
                "file_path": str(skill_file),
            })
        except Exception as e:
            print(f"Warning: Failed to parse {skill_file}: {e}")
    
    return skills


def generate_agentspec_from_awesome_copilot(
    awesome_copilot_path: str,
    output_path: str | None = None,
) -> dict[str, Any]:
    """Generate AgentSpec from real awesome-copilot agents and skills.
    
    Args:
        awesome_copilot_path: Path to awesome-copilot directory
        output_path: Optional path to save AgentSpec JSON
    
    Returns:
        Dict with:
        - success (bool)
        - agentspec (dict): Generated schema
        - agent_count (int)
        - skill_count (int)
        - output_path (str): Where it was saved (if provided)
    """
    awesome_path = Path(awesome_copilot_path).resolve()
    if not awesome_path.exists():
        return {
            "success": False,
            "error": f"awesome-copilot path not found: {awesome_copilot_path}",
        }
    
    # Parse real agents and skills
    agents = parse_agents_from_awesome_copilot(str(awesome_path))
    skills = parse_skills_from_awesome_copilot(str(awesome_path))
    
    # Build AgentSpec schema
    agentspec = {
        "version": "1.0.0",
        "name": "awesome-copilot-agentspec",
        "description": "AgentSpec generated from awesome-copilot agents and skills",
        "source": str(awesome_path),
        "agents": {
            agent["id"]: {
                "name": agent["name"],
                "description": agent["description"],
                "type": "agent",
                "source_file": agent["file_path"],
            }
            for agent in agents
        },
        "tools": {
            skill["id"]: {
                "name": skill["name"],
                "description": skill["description"],
                "type": "skill",
                "source_file": skill["file_path"],
            }
            for skill in skills
        },
    }
    
    result = {
        "success": True,
        "agentspec": agentspec,
        "agent_count": len(agents),
        "skill_count": len(skills),
    }
    
    # Save if output path provided
    if output_path:
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(json.dumps(agentspec, indent=2) + "\n", encoding="utf-8")
        result["output_path"] = str(out_file)
    
    return result


def validate_agentspec(agentspec: dict[str, Any]) -> dict[str, Any]:
    """Validate AgentSpec schema - MVP validation (required fields only).
    
    Args:
        agentspec: AgentSpec dict to validate
    
    Returns:
        Dict with:
        - is_valid (bool)
        - errors (list): List of error strings
    """
    errors: list[str] = []
    
    # Check required top-level fields
    required_fields = ["version", "name", "agents", "tools"]
    for field in required_fields:
        if field not in agentspec:
            errors.append(f"Missing required field: {field}")
    
    # Check agents is dict
    if "agents" in agentspec:
        if not isinstance(agentspec["agents"], dict):
            errors.append("Field 'agents' must be an object")
        else:
            # Check each agent has required fields
            for agent_id, agent in agentspec["agents"].items():
                if not isinstance(agent, dict):
                    errors.append(f"Agent '{agent_id}' must be an object")
                    continue
                
                for field in ["name", "description", "type"]:
                    if field not in agent:
                        errors.append(f"Agent '{agent_id}' missing field: {field}")
    
    # Check tools is dict
    if "tools" in agentspec:
        if not isinstance(agentspec["tools"], dict):
            errors.append("Field 'tools' must be an object")
        else:
            # Check each tool has required fields
            for tool_id, tool in agentspec["tools"].items():
                if not isinstance(tool, dict):
                    errors.append(f"Tool '{tool_id}' missing must be an object")
                    continue
                
                for field in ["name", "description", "type"]:
                    if field not in tool:
                        errors.append(f"Tool '{tool_id}' missing field: {field}")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "error_count": len(errors),
    }


def validate_agentspec_file(agentspec_path: str) -> dict[str, Any]:
    """Load and validate AgentSpec JSON file.
    
    Args:
        agentspec_path: Path to AgentSpec JSON file
    
    Returns:
        Dict with:
        - success (bool)
        - is_valid (bool)
        - errors (list)
        - agentspec_path (str)
    """
    path = Path(agentspec_path).resolve()
    if not path.exists():
        return {
            "success": False,
            "error": f"AgentSpec file not found: {agentspec_path}",
        }
    
    try:
        spec = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Invalid JSON: {e}",
        }
    
    validation = validate_agentspec(spec)
    
    return {
        "success": True,
        "agentspec_path": str(path),
        "is_valid": validation["is_valid"],
        "errors": validation["errors"],
        "error_count": validation["error_count"],
    }
