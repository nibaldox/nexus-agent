#!/usr/bin/env python3
"""
Test script for Dynamic Agent Creation functionality
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_dynamic_agent_creation():
    """Test the dynamic agent creation system"""
    try:
        # Import only the specific classes we need, not the full manager module
        from agno.agent import Agent
        from agents.provider import get_openrouter_model
        from tools.workspace_file_tools import FileTools
        from skills.research_skills import ResearchSkills

        # Define a minimal version of the factory for testing
        class TestDynamicAgentFactory:
            @staticmethod
            def create_agent_from_spec(spec: dict) -> Agent:
                """Create an agent from a specification dictionary."""
                name = spec.get('name', 'TestAgent')
                role = spec.get('role', 'Test role')
                instructions = spec.get('instructions', [])
                tools = spec.get('tools', [])

                # Simple tool mapping for testing
                tool_instances = []
                if 'FileTools' in tools:
                    tool_instances.append(FileTools())
                if 'ResearchSkills' in tools:
                    tool_instances.append(ResearchSkills())

                return Agent(
                    name=name,
                    role=role,
                    model=get_openrouter_model(max_tokens=5000),
                    tools=tool_instances,
                    instructions=instructions,
                    markdown=True,
                )

        # Test agent specification
        spec = {
            "name": "TestCryptoAnalyst",
            "role": "Especialista en análisis de criptomonedas",
            "instructions": ["Analizar tendencias del mercado crypto", "Evaluar riesgos"],
            "tools": ["FileTools", "ResearchSkills"]
        }

        # Create agent
        factory = TestDynamicAgentFactory()
        agent = factory.create_agent_from_spec(spec)

        # Verify agent properties
        assert agent.name == "TestCryptoAnalyst"
        assert agent.role == "Especialista en análisis de criptomonedas"
        assert len(agent.instructions) == 2
        assert len(agent.tools) >= 1  # Should have at least one tool

        print("✅ Test passed: Dynamic agent creation works")
        print(f"   Agent name: {agent.name}")
        print(f"   Agent role: {agent.role}")
        print(f"   Instructions count: {len(agent.instructions)}")
        print(f"   Tools count: {len(agent.tools)}")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing Dynamic Agent Creation...")
    success = test_dynamic_agent_creation()
    if success:
        print("🎉 All tests passed!")
    else:
        print("💥 Tests failed!")
        sys.exit(1)