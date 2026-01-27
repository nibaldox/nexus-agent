#!/usr/bin/env python3
"""
Automated Testing Script for Nexus Agent
Ejecuta pruebas automatizadas de funcionalidades críticas
"""

import sys
import os
import time
from pathlib import Path
from typing import Dict, List, Any
import json

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import test utilities
from test_dynamic_agents import test_dynamic_agent_creation

class NexusTester:
    """Automated testing suite for Nexus Agent"""

    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0

    def log_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.results.append({
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": time.strftime("%H:%M:%S")
        })

        if passed:
            self.passed += 1
        else:
            self.failed += 1

        print(f"{status}: {test_name}")
        if details:
            print(f"   {details}")

    def test_imports(self):
        """Test that all critical imports work"""
        try:
            # Test basic imports
            from agents.manager import manager
            from agents.provider import get_openrouter_model
            from config import settings
            from api import app

            # Test dynamic agent functionality
            from agents.manager import DynamicAgentFactory, create_dynamic_agent

            self.log_result("Critical Imports", True, "All core modules imported successfully")
            return True
        except Exception as e:
            self.log_result("Critical Imports", False, f"Import failed: {e}")
            return False

    def test_dynamic_agents(self):
        """Test dynamic agent creation functionality"""
        try:
            success = test_dynamic_agent_creation()
            self.log_result("Dynamic Agent Creation", success, "Factory and creation functions work")
            return success
        except Exception as e:
            self.log_result("Dynamic Agent Creation", False, f"Dynamic agents test failed: {e}")
            return False

    def test_configuration(self):
        """Test configuration loading"""
        try:
            from config import settings

            # Check required settings exist
            required_attrs = ['workspace_dir', 'agent_db_path', 'cors_origins']
            for attr in required_attrs:
                if not hasattr(settings, attr):
                    raise AttributeError(f"Missing setting: {attr}")

            # Check workspace directory exists
            if not settings.workspace_dir.exists():
                raise FileNotFoundError(f"Workspace directory not found: {settings.workspace_dir}")

            self.log_result("Configuration", True, "All settings loaded correctly")
            return True
        except Exception as e:
            self.log_result("Configuration", False, f"Configuration error: {e}")
            return False

    def test_database_connection(self):
        """Test SQLite database connectivity"""
        try:
            import sqlite3
            from config import settings

            # Test connection
            conn = sqlite3.connect(settings.agent_db_path)
            cursor = conn.cursor()

            # Test basic query
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()

            conn.close()

            self.log_result("Database Connection", True, f"Connected successfully, {len(tables)} tables found")
            return True
        except Exception as e:
            self.log_result("Database Connection", False, f"Database error: {e}")
            return False

    def test_workspace_structure(self):
        """Test workspace directory structure"""
        try:
            from config import settings

            workspace = settings.workspace_dir

            # Check required directories
            required_dirs = [
                workspace / "assets",
                workspace / "conversations",
                workspace / "knowledge",
                workspace / "mission_plans"
            ]

            missing_dirs = []
            for dir_path in required_dirs:
                if not dir_path.exists():
                    missing_dirs.append(str(dir_path))

            if missing_dirs:
                self.log_result("Workspace Structure", False, f"Missing directories: {missing_dirs}")
                return False

            self.log_result("Workspace Structure", True, "All required directories exist")
            return True
        except Exception as e:
            self.log_result("Workspace Structure", False, f"Workspace check failed: {e}")
            return False

    def test_agent_initialization(self):
        """Test that agents can be initialized"""
        try:
            from agents.manager import manager
            from agents.squads.data_intelligence.squad_leader import data_intelligence_squad

            # Check manager has members
            if not hasattr(manager, 'members') or len(manager.members) == 0:
                raise ValueError("Manager has no members")

            # Check at least one squad is loaded
            squad_names = [getattr(member, 'name', str(member)) for member in manager.members]
            if not squad_names:
                raise ValueError("No squads found in manager")

            self.log_result("Agent Initialization", True, f"Manager initialized with {len(manager.members)} members: {squad_names}")
            return True
        except Exception as e:
            self.log_result("Agent Initialization", False, f"Agent initialization failed: {e}")
            return False

    def test_api_endpoints(self):
        """Test basic API endpoints"""
        try:
            from fastapi.testclient import TestClient
            from api import app

            client = TestClient(app)

            # Test health endpoint
            response = client.get("/api/health")
            if response.status_code != 200:
                raise ValueError(f"Health endpoint returned {response.status_code}")

            health_data = response.json()
            if "status" not in health_data:
                raise ValueError("Health endpoint missing status field")

            self.log_result("API Endpoints", True, f"Health check: {health_data.get('status', 'Unknown')}")
            return True
        except Exception as e:
            self.log_result("API Endpoints", False, f"API test failed: {e}")
            return False

    def run_all_tests(self):
        """Run all automated tests"""
        print("🚀 Iniciando Suite de Testing Automatizado - Nexus Agent")
        print("=" * 60)

        # Run tests
        self.test_imports()
        self.test_configuration()
        self.test_database_connection()
        self.test_workspace_structure()
        self.test_agent_initialization()
        self.test_dynamic_agents()
        self.test_api_endpoints()

        # Summary
        print("\n" + "=" * 60)
        print("📊 RESULTADOS DEL TESTING")
        print("=" * 60)
        print(f"✅ Tests Pasados: {self.passed}")
        print(f"❌ Tests Fallados: {self.failed}")
        print(f"📈 Total Tests: {self.passed + self.failed}")

        if self.failed == 0:
            print("🎉 ¡Todos los tests pasaron exitosamente!")
            return True
        else:
            print("⚠️  Algunos tests fallaron. Revisa los detalles arriba.")
            return False

    def save_report(self, filename: str = "test_report.json"):
        """Save test results to file"""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "passed": self.passed,
                "failed": self.failed,
                "total": self.passed + self.failed
            },
            "results": self.results
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"📄 Reporte guardado en: {filename}")

if __name__ == "__main__":
    tester = NexusTester()
    success = tester.run_all_tests()
    tester.save_report()

    # Exit with appropriate code
    sys.exit(0 if success else 1)</content>
<parameter name="filePath">d:\12_WindSurf\42-Agents\10-Agent-Agno\02-general001\test_nexus_automated.py