"""Integration test for MVP AgentSpec tools in MCP server.

Tests:
1. Server imports MVP module successfully
2. generate_agentspec tool works with real awesome-copilot data
3. validate_agentspec tool validates generated spec
4. Round-trip: generate -> validate with MCP tools
"""

import json
import sys
from pathlib import Path

import pytest

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import server
from agentspec_mvp import generate_agentspec_from_awesome_copilot


def test_server_imports_mvp_module():
    """Test that server successfully imports MVP module."""
    # Server should have imported the MVP functions
    assert hasattr(server, 'generate_agentspec_from_awesome_copilot')
    assert hasattr(server, 'validate_agentspec_file')
    
    print("✓ Server imports MVP module successfully")


def test_generate_agentspec_tool_works(tmp_path: Path):
    """Test generate_agentspec MCP tool with real data."""
    awesome_path = Path(__file__).resolve().parents[2] / "awesome-copilot"
    
    if not awesome_path.exists():
        pytest.skip(f"awesome-copilot not found at {awesome_path}")
    
    output_file = tmp_path / "test-agentspec.json"
    
    # Call MVP function that tool uses
    result = generate_agentspec_from_awesome_copilot(
        str(awesome_path),
        output_path=str(output_file),
    )
    
    assert result["success"] is True, "Should generate successfully"
    assert result["agent_count"] > 0, "Should have agents"
    assert result["skill_count"] > 0, "Should have skills"
    assert output_file.exists(), "Output file should exist"
    
    # Verify it's valid JSON
    spec = json.loads(output_file.read_text(encoding="utf-8"))
    assert spec["version"] == "1.0.0"
    assert "agents" in spec
    assert "tools" in spec
    
    print(f"✓ generate_agentspec tool works: {result['agent_count']} agents, {result['skill_count']} skills")


def test_validate_agentspec_tool_works(tmp_path: Path):
    """Test validate_agentspec MCP tool."""
    awesome_path = Path(__file__).resolve().parents[2] / "awesome-copilot"
    
    if not awesome_path.exists():
        pytest.skip(f"awesome-copilot not found at {awesome_path}")
    
    # Generate a spec
    output_file = tmp_path / "test-agentspec.json"
    generate_result = generate_agentspec_from_awesome_copilot(
        str(awesome_path),
        output_path=str(output_file),
    )
    
    assert generate_result["success"] is True
    
    # Now validate it (via MVP function that tool uses)
    from agentspec_mvp import validate_agentspec_file
    validation = validate_agentspec_file(str(output_file))
    
    assert validation["success"] is True, "Should load successfully"
    assert validation["is_valid"] is True, f"Should be valid. Errors: {validation.get('errors')}"
    assert validation["error_count"] == 0, "Should have no errors"
    
    print("✓ validate_agentspec tool works: validation passed")


def test_mvp_e2e_workflow_via_tools(tmp_path: Path):
    """Test end-to-end: generate -> validate using MVP."""
    awesome_path = Path(__file__).resolve().parents[2] / "awesome-copilot"
    
    if not awesome_path.exists():
        pytest.skip(f"awesome-copilot not found at {awesome_path}")
    
    output_file = tmp_path / "e2e-agentspec.json"
    
    # Step 1: Generate
    from agentspec_mvp import generate_agentspec_from_awesome_copilot
    gen_result = generate_agentspec_from_awesome_copilot(
        str(awesome_path),
        output_path=str(output_file),
    )
    
    assert gen_result["success"] is True
    assert gen_result["agent_count"] > 100, "Should have many agents"
    assert gen_result["skill_count"] > 100, "Should have many skills"
    
    # Step 2: Validate
    from agentspec_mvp import validate_agentspec_file
    val_result = validate_agentspec_file(str(output_file))
    
    assert val_result["success"] is True
    assert val_result["is_valid"] is True
    
    # Step 3: Verify schema structure
    spec = json.loads(output_file.read_text(encoding="utf-8"))
    
    # Check all agents have required fields
    for agent_id, agent in spec["agents"].items():
        assert "name" in agent, f"Agent {agent_id} missing name"
        assert "description" in agent, f"Agent {agent_id} missing description"
        assert "type" in agent, f"Agent {agent_id} missing type"
        assert "source_file" in agent, f"Agent {agent_id} missing source_file"
    
    # Check all tools have required fields
    for tool_id, tool in spec["tools"].items():
        assert "name" in tool, f"Tool {tool_id} missing name"
        assert "description" in tool, f"Tool {tool_id} missing description"
        assert "type" in tool, f"Tool {tool_id} missing type"
        assert "source_file" in tool, f"Tool {tool_id} missing source_file"
    
    print(f"✓ E2E workflow complete: {gen_result['agent_count']} agents, {gen_result['skill_count']} skills validated")


if __name__ == "__main__":
    print("Running MVP integration tests...\n")
    
    tmp_dir = Path("/tmp/mvp_integration_test")
    tmp_dir.mkdir(exist_ok=True)
    
    try:
        test_server_imports_mvp_module()
        test_generate_agentspec_tool_works(tmp_dir)
        test_validate_agentspec_tool_works(tmp_dir)
        test_mvp_e2e_workflow_via_tools(tmp_dir)
        
        print("\n✓ All MVP integration tests passed!")
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)
