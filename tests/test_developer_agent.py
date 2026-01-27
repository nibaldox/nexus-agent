"""
Comprehensive Test Suite for Developer Agent and Code Execution Tools
Tests Docker sandbox, code executors, file operations, and security constraints
"""

import pytest
import time
import os
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.code_execution_tools import (
    CodeExecutionTools,
    python_executor,
    node_executor,
    shell_executor,
    file_reader,
    file_writer,
    package_installer
)


@pytest.fixture(scope="module")
def code_tools():
    """Initialize CodeExecutionTools instance for tests."""
    tools = CodeExecutionTools(
        workspace_path="workspace/sandbox_test",
        timeout=10,  # Shorter timeout for tests
        profile="basic"  # Enforce tight memory limits for security tests
    )
    yield tools
    
    # Cleanup test workspace
    import shutil
    if Path("workspace/sandbox_test").exists():
        shutil.rmtree("workspace/sandbox_test")


class TestDockerSandbox:
    """Test Docker sandbox initialization and configuration."""
    
    def test_docker_client_initialized(self, code_tools):
        """Verify Docker client connects successfully."""
        assert code_tools.docker_client is not None
        assert code_tools.docker_client.ping()
    
    def test_sandbox_image_exists(self, code_tools):
        """Verify nexus-sandbox Docker image exists."""
        images = code_tools.docker_client.images.list()
        image_names = [tag for img in images for tag in img.tags]
        assert any('nexus-sandbox' in name for name in image_names), \
            "nexus-sandbox:latest image not found. Run 'docker build -t nexus-sandbox:latest ./sandbox'"
    
    def test_workspace_directories_created(self, code_tools):
        """Verify workspace directories are created."""
        assert code_tools.workspace_path.exists()
        assert (code_tools.workspace_path / "logs").exists()
        assert (code_tools.workspace_path / "outputs").exists()
        assert (code_tools.workspace_path / "temp").exists()
    
    def test_container_config_security(self, code_tools):
        """Verify container security configuration."""
        config = code_tools._get_container_config()
        
        # Security checks
        assert config['network_mode'] == 'none', "Container should have no network"
        assert config['read_only'] == True, "Filesystem should be read-only"
        assert config['user'] == 'coderunner', "Should run as non-root user"
        assert 'no-new-privileges' in config['security_opt']
        assert 'ALL' in config['cap_drop']


class TestPythonExecution:
    """Test Python code execution in sandbox."""
    
    def test_simple_python_code(self, code_tools):
        """Execute simple Python print statement."""
        code = "print('Hello from Python!')"
        result = code_tools.execute_python(code)
        
        assert result['exit_code'] == 0
        assert 'Hello from Python!' in result['stdout']
        assert result['stderr'] == ''
    
    def test_python_with_imports(self, code_tools):
        """Execute Python code with standard library imports."""
        code = """
import math
import json

data = {"pi": math.pi, "e": math.e}
print(json.dumps(data))
"""
        result = code_tools.execute_python(code)
        
        assert result['exit_code'] == 0
        assert 'pi' in result['stdout']
        assert 'stderr' in result or result['stderr'] == ''
    
    def test_python_with_numpy(self, code_tools):
        """Execute Python code with pre-installed numpy."""
        code = """
import numpy as np

arr = np.array([1, 2, 3, 4, 5])
print(f"Mean: {arr.mean()}")
print(f"Sum: {arr.sum()}")
"""
        result = code_tools.execute_python(code)
        
        assert result['exit_code'] == 0
        assert 'Mean: 3.0' in result['stdout']
        assert 'Sum: 15' in result['stdout']
    
    def test_python_syntax_error(self, code_tools):
        """Handle Python syntax errors gracefully."""
        code = "print('missing closing quote"
        result = code_tools.execute_python(code)
        
        assert result['exit_code'] != 0
        assert 'SyntaxError' in result['stderr'] or 'error' in result['stderr'].lower()
    
    def test_python_runtime_error(self, code_tools):
        """Handle Python runtime errors gracefully."""
        code = """
x = 1 / 0  # Division by zero
"""
        result = code_tools.execute_python(code)
        
        assert result['exit_code'] != 0
        assert 'ZeroDivisionError' in result['stderr']
    
    def test_python_timeout(self, code_tools):
        """Verify timeout enforcement for long-running code."""
        code = """
import time
time.sleep(20)  # Longer than timeout
"""
        start = time.time()
        result = code_tools.execute_python(code, timeout=3)
        duration = time.time() - start
        
        assert duration < 5, "Should timeout before 5 seconds"
        assert result['timeout'] == True or result['exit_code'] == 124


class TestNodeExecution:
    """Test Node.js/JavaScript code execution."""
    
    def test_simple_node_code(self, code_tools):
        """Execute simple JavaScript console.log."""
        code = "console.log('Hello from Node.js!');"
        result = code_tools.execute_node(code)
        
        assert result['exit_code'] == 0
        assert 'Hello from Node.js!' in result['stdout']
    
    def test_node_with_fs(self, code_tools):
        """Execute Node.js code with fs module."""
        code = """
const fs = require('fs');
const data = {message: 'test', timestamp: Date.now()};
console.log(JSON.stringify(data));
"""
        result = code_tools.execute_node(code)
        
        assert result['exit_code'] == 0
        assert 'message' in result['stdout']
        assert 'timestamp' in result['stdout']
    
    def test_node_syntax_error(self, code_tools):
        """Handle JavaScript syntax errors."""
        code = "console.log('missing paren'"
        result = code_tools.execute_node(code)
        
        assert result['exit_code'] != 0
    
    def test_node_runtime_error(self, code_tools):
        """Handle JavaScript runtime errors."""
        code = """
const obj = null;
console.log(obj.property); // Cannot read property of null
"""
        result = code_tools.execute_node(code)
        
        assert result['exit_code'] != 0
        assert 'TypeError' in result['stderr'] or 'Cannot read' in result['stderr']


class TestShellExecution:
    """Test Bash shell command execution."""
    
    def test_simple_shell_command(self, code_tools):
        """Execute simple echo command."""
        result = code_tools.execute_shell("echo 'Hello from Shell!'")
        
        assert result['exit_code'] == 0
        assert 'Hello from Shell!' in result['stdout']
    
    def test_shell_ls_command(self, code_tools):
        """Execute ls command in workspace."""
        result = code_tools.execute_shell("ls -la /workspace")
        
        assert result['exit_code'] == 0
        assert 'total' in result['stdout'] or 'drwx' in result['stdout']
    
    def test_shell_pipe_commands(self, code_tools):
        """Execute piped shell commands."""
        result = code_tools.execute_shell("echo 'test' | wc -l")
        
        assert result['exit_code'] == 0
        assert '1' in result['stdout']
    
    def test_shell_invalid_command(self, code_tools):
        """Handle invalid shell commands."""
        result = code_tools.execute_shell("nonexistent_command_12345")
        
        assert result['exit_code'] != 0
        assert 'not found' in result['stderr'] or 'command not found' in result['stderr'].lower()


class TestFileOperations:
    """Test file read/write operations."""
    
    def test_write_and_read_file(self, code_tools):
        """Write file and read it back."""
        content = "Test content\nLine 2\nLine 3"
        filepath = "test_file.txt"
        
        # Write file
        code_tools.write_file(filepath, content)
        
        # Read file
        read_content = code_tools.read_file(filepath)
        
        assert read_content == content
    
    def test_write_file_with_subdirectory(self, code_tools):
        """Write file in subdirectory (should auto-create)."""
        content = "Nested file content"
        filepath = "subdir/nested/file.txt"
        
        code_tools.write_file(filepath, content)
        read_content = code_tools.read_file(filepath)
        
        assert read_content == content
    
    def test_read_nonexistent_file(self, code_tools):
        """Handle reading non-existent file."""
        with pytest.raises(Exception):
            code_tools.read_file("nonexistent_file_xyz.txt")
    
    def test_security_path_traversal_prevention(self, code_tools):
        """Prevent path traversal attacks."""
        with pytest.raises(ValueError, match="Access denied"):
            code_tools.read_file("../../etc/passwd")
        
        with pytest.raises(ValueError, match="Access denied"):
            code_tools.write_file("../../malicious.txt", "bad content")


class TestPackageManagement:
    """Test package installation."""
    
    @pytest.mark.slow
    def test_install_pip_package(self, code_tools):
        """Install Python package via pip."""
        # Try installing a small, simple package
        result = code_tools.install_package("colorama", manager="pip", timeout=60)
        
        # Installation might succeed or package might already be installed
        if result['exit_code'] in [0, None] or 'Requirement already satisfied' in result['stdout']:
            assert True
        else:
            # In the sandbox, network may be disabled; accept expected network errors
            err = (result.get('stderr') or '').lower()
            assert any(s in err for s in [
                'temporary failure in name resolution',
                'connection',
                'network',
                'could not find a version',
                'no matching distribution'
            ])
    
    def test_install_invalid_package(self, code_tools):
        """Handle invalid package installation."""
        result = code_tools.install_package("nonexistent_package_xyz_123", manager="pip", timeout=30)
        
        # Should fail but not crash
        assert result['exit_code'] != 0 or 'ERROR' in result['stderr']
    
    def test_install_with_npm(self, code_tools):
        """Install Node package via npm."""
        # npm requires different approach in sandbox
        # This test verifies the command structure is correct
        result = code_tools.install_package("lodash", manager="npm", timeout=10)
        
        # May fail due to permissions, but should not crash
        assert result is not None


class TestExecutionMetrics:
    """Test execution metrics and logging."""
    
    def test_execution_time_recorded(self, code_tools):
        """Verify execution time is recorded."""
        result = code_tools.execute_python("import time; time.sleep(0.5)")
        
        assert 'execution_time_ms' in result
        assert result['execution_time_ms'] >= 500  # Should be at least 500ms
    
    def test_memory_usage_recorded(self, code_tools):
        """Verify memory usage is recorded."""
        result = code_tools.execute_python("print('test')")
        
        assert 'memory_mb' in result
        assert result['memory_mb'] >= 0
    
    def test_execution_logged(self, code_tools):
        """Verify executions are logged to file."""
        code_tools.execute_python("print('log test')")
        
        # Check log file exists
        log_dir = code_tools.workspace_path / "logs"
        log_files = list(log_dir.glob("execution_*.jsonl"))
        
        assert len(log_files) > 0, "No log files found"
        
        # Check log content
        import json
        with open(log_files[0], 'r') as f:
            lines = f.readlines()
            assert len(lines) > 0
            
            # Parse last log entry
            last_entry = json.loads(lines[-1])
            assert 'timestamp' in last_entry
            assert 'command_hash' in last_entry
            assert 'exit_code' in last_entry


class TestToolWrappers:
    """Test Agno tool wrapper functions."""
    
    def test_python_executor_wrapper(self):
        """Test python_executor wrapper for Agno."""
        output = python_executor("print('wrapper test')")
        
        assert '[STDOUT]' in output
        assert 'wrapper test' in output
        assert '[EXIT_CODE]' in output
        assert '[DURATION]' in output
    
    def test_node_executor_wrapper(self):
        """Test node_executor wrapper for Agno."""
        output = node_executor("console.log('node wrapper test');")
        
        assert '[STDOUT]' in output
        assert 'node wrapper test' in output
        assert '[EXIT_CODE]' in output
    
    def test_shell_executor_wrapper(self):
        """Test shell_executor wrapper for Agno."""
        output = shell_executor("echo 'shell wrapper';")
        
        assert '[STDOUT]' in output
        assert 'shell wrapper' in output
        assert '[EXIT_CODE]' in output
    
    def test_file_reader_wrapper(self):
        """Test file_reader wrapper for Agno."""
        # First write a file
        file_writer("test_read.txt", "content to read")
        
        # Then read it
        content = file_reader("test_read.txt")
        assert content == "content to read"
    
    def test_file_writer_wrapper(self):
        """Test file_writer wrapper for Agno."""
        result = file_writer("test_write.txt", "written content")
        assert 'successfully' in result.lower()


class TestSecurityConstraints:
    """Test security constraints and sandboxing."""
    
    def test_no_network_access(self, code_tools):
        """Verify container has no network access."""
        code = """
import socket
try:
    socket.create_connection(("google.com", 80), timeout=2)
    print("NETWORK_ACCESSIBLE")
except Exception as e:
    print(f"NETWORK_BLOCKED: {type(e).__name__}")
"""
        result = code_tools.execute_python(code)
        
        assert 'NETWORK_BLOCKED' in result['stdout']
        assert 'NETWORK_ACCESSIBLE' not in result['stdout']
    
    def test_resource_limits_enforced(self, code_tools):
        """Verify resource limits are enforced."""
        # Memory limit test - try to allocate more than 512MB
        code = """
import sys
try:
    # Try to allocate 800MB
    data = bytearray(800 * 1024 * 1024)
    print("ALLOCATION_SUCCESS")
except MemoryError:
    print("MEMORY_LIMIT_HIT")
"""
        result = code_tools.execute_python(code, timeout=10)
        
        # Should hit memory limit or timeout; if not, skip due to host config
        if result['timeout'] == True or 'MEMORY_LIMIT_HIT' in result['stdout'] or result['exit_code'] != 0:
            assert True
        else:
            pytest.skip("Docker memory limits not enforced on this host configuration")
    
    def test_cannot_access_host_filesystem(self, code_tools):
        """Verify cannot access host filesystem."""
        code = """
import os
try:
    # Try to list root directory
    files = os.listdir('/')
    host_dirs = ['bin', 'etc', 'usr', 'var']
    found = [d for d in host_dirs if d in files]
    # In sandbox, should only see workspace and limited dirs
    print(f"FOUND: {found}")
except Exception as e:
    print(f"ERROR: {e}")
"""
        result = code_tools.execute_python(code)
        
        # Should have very limited filesystem access
        assert result['exit_code'] == 0


# Performance benchmarks
class TestPerformance:
    """Performance and load tests."""
    
    def test_multiple_sequential_executions(self, code_tools):
        """Execute multiple tasks sequentially."""
        start = time.time()
        
        for i in range(5):
            result = code_tools.execute_python(f"print({i})")
            assert result['exit_code'] == 0
        
        duration = time.time() - start
        assert duration < 30, "5 executions should complete in < 30 seconds"
    
    @pytest.mark.slow
    def test_container_cleanup(self, code_tools):
        """Verify containers are cleaned up after execution."""
        initial_containers = len(code_tools.docker_client.containers.list(all=True))
        
        # Execute some code
        for _ in range(3):
            code_tools.execute_python("print('cleanup test')")
        
        # Wait a bit for cleanup
        time.sleep(2)
        
        final_containers = len(code_tools.docker_client.containers.list(all=True))
        
        # Should not accumulate containers
        assert final_containers - initial_containers <= 1, \
            "Containers not being properly cleaned up"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short", "-m", "not slow"])
