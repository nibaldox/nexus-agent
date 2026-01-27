#!/usr/bin/env python3
"""
Basic Testing Script for Nexus Agent
"""

import sys
import os
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_basic_functionality():
    """Test basic Nexus functionality"""
    print("🧪 Testing Nexus Agent Basic Functionality")
    print("=" * 50)

    tests_passed = 0
    tests_failed = 0

    # Test 1: Imports
    try:
        from agents.manager import manager
        from config import settings
        print("✅ Test 1 PASSED: Critical imports successful")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 1 FAILED: Import error - {e}")
        tests_failed += 1

    # Test 2: Configuration
    try:
        assert hasattr(settings, 'workspace_dir')
        assert settings.workspace_dir.exists()
        print("✅ Test 2 PASSED: Configuration loaded correctly")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 2 FAILED: Configuration error - {e}")
        tests_failed += 1

    # Test 3: Manager initialization
    try:
        assert hasattr(manager, 'members')
        assert len(manager.members) > 0
        print(f"✅ Test 3 PASSED: Manager initialized with {len(manager.members)} members")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 3 FAILED: Manager initialization error - {e}")
        tests_failed += 1

    # Test 4: Dynamic agents
    try:
        from test_dynamic_agents import test_dynamic_agent_creation
        success = test_dynamic_agent_creation()
        if success:
            print("✅ Test 4 PASSED: Dynamic agent creation works")
            tests_passed += 1
        else:
            print("❌ Test 4 FAILED: Dynamic agent creation failed")
            tests_failed += 1
    except Exception as e:
        print(f"❌ Test 4 FAILED: Dynamic agent test error - {e}")
        tests_failed += 1

    # Test 5: API health
    try:
        from fastapi.testclient import TestClient
        from api import app

        client = TestClient(app)
        response = client.get("/api/health")

        if response.status_code == 200:
            print("✅ Test 5 PASSED: API health check successful")
            tests_passed += 1
        else:
            print(f"❌ Test 5 FAILED: API returned status {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"❌ Test 5 FAILED: API test error - {e}")
        tests_failed += 1

    # Summary
    print("\n" + "=" * 50)
    print("📊 TESTING SUMMARY")
    print("=" * 50)
    print(f"✅ Tests Passed: {tests_passed}")
    print(f"❌ Tests Failed: {tests_failed}")
    print(f"📈 Success Rate: {(tests_passed/(tests_passed+tests_failed)*100):.1f}%")

    if tests_failed == 0:
        print("🎉 ALL TESTS PASSED!")
        return True
    else:
        print("⚠️  SOME TESTS FAILED")
        return False

if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)