"""Test AgentSpec MVP with real awesome-copilot data.

Tests:
1. Parse real agents from awesome-copilot/agents/
2. Parse real skills from awesome-copilot/skills/
3. Generate AgentSpec from real data
4. Validate generated AgentSpec
5. Round-trip test (generate -> save -> load -> validate)
"""

import json
import sys
from pathlib import Path

import pytest

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agentspec_mvp import (
    generate_agentspec_from_awesome_copilot,
    parse_agents_from_awesome_copilot,
    parse_skills_from_awesome_copilot,
    validate_agentspec,
    validate_agentspec_file,
)


# Path to awesome-copilot in the workspace
AWESOME_COPILOT_PATH = Path(__file__).resolve().parents[2] / "awesome-copilot"
# If the canonical dataset isn't present at the repository root, try the
# consolidated_sources location as a non-invasive fallback so CI/tests can
# run without moving large datasets.
if not AWESOME_COPILOT_PATH.exists():
    _fallback = Path(__file__).resolve().parents[2] / "consolidated_sources" / "awesome-copilot"
    if _fallback.exists():
        AWESOME_COPILOT_PATH = _fallback


def test_parse_agents_from_awesome_copilot():
    """Test parsing real .agent.md files."""
    if not AWESOME_COPILOT_PATH.exists():
        pytest.skip(f"awesome-copilot not found at {AWESOME_COPILOT_PATH}")
    
    agents = parse_agents_from_awesome_copilot(str(AWESOME_COPILOT_PATH))
    
    # Should find agents
    assert len(agents) > 0, "Should parse at least one agent"
    
    # Check agent structure
    agent = agents[0]
    assert "id" in agent, "Agent should have 'id'"
    assert "name" in agent, "Agent should have 'name'"
    assert "description" in agent, "Agent should have 'description'"
    assert "file_path" in agent, "Agent should have 'file_path'"
    
    # Check file path exists
    assert Path(agent["file_path"]).exists(), f"Agent file should exist: {agent['file_path']}"
    
    print(f"✓ Parsed {len(agents)} agents from awesome-copilot")


def test_parse_skills_from_awesome_copilot():
    """Test parsing real SKILL.md files."""
    if not AWESOME_COPILOT_PATH.exists():
        pytest.skip(f"awesome-copilot not found at {AWESOME_COPILOT_PATH}")
    
    skills = parse_skills_from_awesome_copilot(str(AWESOME_COPILOT_PATH))
    
    # Should find skills
    assert len(skills) > 0, "Should parse at least one skill"
    
    # Check skill structure
    skill = skills[0]
    assert "id" in skill, "Skill should have 'id'"
    assert "name" in skill, "Skill should have 'name'"
    assert "description" in skill, "Skill should have 'description'"
    assert "file_path" in skill, "Skill should have 'file_path'"
    
    # Check file path exists
    assert Path(skill["file_path"]).exists(), f"Skill file should exist: {skill['file_path']}"
    
    print(f"✓ Parsed {len(skills)} skills from awesome-copilot")


def test_generate_agentspec_from_real_data():
    """Test generating AgentSpec from real awesome-copilot data."""
    if not AWESOME_COPILOT_PATH.exists():
        pytest.skip(f"awesome-copilot not found at {AWESOME_COPILOT_PATH}")
    
    result = generate_agentspec_from_awesome_copilot(str(AWESOME_COPILOT_PATH))
    
    assert result["success"] is True, "Should successfully generate AgentSpec"
    assert "agentspec" in result, "Should return AgentSpec"
    assert result["agent_count"] > 0, "Should include agents"
    assert result["skill_count"] > 0, "Should include skills"
    
    spec = result["agentspec"]
    
    # Check structure
    assert "version" in spec, "Should have version"
    assert "name" in spec, "Should have name"
    assert "agents" in spec, "Should have agents"
    assert "tools" in spec, "Should have tools"
    
    # Check agents
    assert len(spec["agents"]) > 0, "Should have at least one agent"
    first_agent_id = list(spec["agents"].keys())[0]
    first_agent = spec["agents"][first_agent_id]
    assert "name" in first_agent, "Agent should have name"
    assert "description" in first_agent, "Agent should have description"
    assert "type" in first_agent, "Agent should have type"
    assert "source_file" in first_agent, "Agent should have source_file"
    
    # Check tools
    assert len(spec["tools"]) > 0, "Should have at least one tool"
    first_tool_id = list(spec["tools"].keys())[0]
    first_tool = spec["tools"][first_tool_id]
    assert "name" in first_tool, "Tool should have name"
    assert "description" in first_tool, "Tool should have description"
    assert "type" in first_tool, "Tool should have type"
    assert "source_file" in first_tool, "Tool should have source_file"
    
    print(f"✓ Generated AgentSpec with {result['agent_count']} agents and {result['skill_count']} skills")


def test_validate_valid_agentspec():
    """Test validation of valid AgentSpec."""
    if not AWESOME_COPILOT_PATH.exists():
        pytest.skip(f"awesome-copilot not found at {AWESOME_COPILOT_PATH}")
    
    result = generate_agentspec_from_awesome_copilot(str(AWESOME_COPILOT_PATH))
    spec = result["agentspec"]
    
    validation = validate_agentspec(spec)
    
    assert validation["is_valid"] is True, f"Should be valid. Errors: {validation['errors']}"
    assert validation["error_count"] == 0, "Should have no errors"
    assert len(validation["errors"]) == 0, "Errors list should be empty"
    
    print("✓ Generated AgentSpec passes validation")


def test_validate_invalid_agentspec():
    """Test validation catches missing fields."""
    invalid_spec = {
        "version": "1.0.0",
        # Missing 'name', 'agents', 'tools'
    }
    
    validation = validate_agentspec(invalid_spec)
    
    assert validation["is_valid"] is False, "Should be invalid"
    assert validation["error_count"] > 0, "Should have errors"
    
    error_text = " ".join(validation["errors"])
    assert "name" in error_text, "Should report missing 'name'"
    assert "agents" in error_text, "Should report missing 'agents'"
    assert "tools" in error_text, "Should report missing 'tools'"
    
    print(f"✓ Validation catches {validation['error_count']} errors")


def test_roundtrip_generate_save_load_validate(tmp_path: Path):
    """Test complete workflow: generate -> save -> load -> validate."""
    if not AWESOME_COPILOT_PATH.exists():
        pytest.skip(f"awesome-copilot not found at {AWESOME_COPILOT_PATH}")
    
    output_file = tmp_path / "awesome-copilot.agentspec.json"
    
    # Generate and save
    result = generate_agentspec_from_awesome_copilot(
        str(AWESOME_COPILOT_PATH),
        output_path=str(output_file),
    )
    
    assert result["success"] is True, "Should generate successfully"
    assert "output_path" in result, "Should have output_path"
    assert Path(result["output_path"]).exists(), "Output file should exist"
    
    # Load and validate
    validation = validate_agentspec_file(str(output_file))
    
    assert validation["success"] is True, "Should load successfully"
    assert validation["is_valid"] is True, f"Should be valid. Errors: {validation['errors']}"
    assert validation["error_count"] == 0, "Should have no errors"
    
    # Check file content
    spec = json.loads(output_file.read_text(encoding="utf-8"))
    assert spec["version"] == "1.0.0", "Should have correct version"
    assert len(spec["agents"]) > 0, "Should have agents"
    assert len(spec["tools"]) > 0, "Should have tools"
    
    print(f"✓ Round-trip complete: {result['agent_count']} agents, {result['skill_count']} skills")


def test_agentspec_schema_compliance():
    """Test that generated AgentSpec matches expected schema."""
    if not AWESOME_COPILOT_PATH.exists():
        pytest.skip(f"awesome-copilot not found at {AWESOME_COPILOT_PATH}")
    
    result = generate_agentspec_from_awesome_copilot(str(AWESOME_COPILOT_PATH))
    spec = result["agentspec"]
    
    # Top-level required fields
    assert spec["version"] == "1.0.0", "Version should be 1.0.0"
    assert spec["name"] == "awesome-copilot-agentspec", "Should have correct name"
    assert "description" in spec, "Should have description"
    assert "source" in spec, "Should have source"
    
    # Agents compliance
    for agent_id, agent in spec["agents"].items():
        assert isinstance(agent_id, str), "Agent ID should be string"
        assert isinstance(agent, dict), "Agent should be dict"
        assert agent["name"], "Agent name should not be empty"
        assert agent["type"] == "agent", "Agent type should be 'agent'"
        assert "source_file" in agent, "Agent should have source_file"
        assert Path(agent["source_file"]).exists(), f"Agent source file should exist: {agent['source_file']}"
    
    # Tools compliance
    for tool_id, tool in spec["tools"].items():
        assert isinstance(tool_id, str), "Tool ID should be string"
        assert isinstance(tool, dict), "Tool should be dict"
        assert tool["name"], "Tool name should not be empty"
        assert tool["type"] == "skill", "Tool type should be 'skill'"
        assert "source_file" in tool, "Tool should have source_file"
        assert Path(tool["source_file"]).exists(), f"Tool source file should exist: {tool['source_file']}"
    
    print(f"✓ Schema compliance verified for {len(spec['agents'])} agents and {len(spec['tools'])} tools")


if __name__ == "__main__":
    # Run tests manually for quick validation
    print("Running AgentSpec MVP tests...\n")
    
    try:
        test_parse_agents_from_awesome_copilot()
        test_parse_skills_from_awesome_copilot()
        test_generate_agentspec_from_real_data()
        test_validate_valid_agentspec()
        test_validate_invalid_agentspec()
        test_roundtrip_generate_save_load_validate(Path("/tmp/agentspec_mvp_test"))
        test_agentspec_schema_compliance()
        
        print("\n✓ All MVP tests passed!")
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)
