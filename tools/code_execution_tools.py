"""
Code Execution Tools for Nexus Developer Agent
Provides secure code execution in Docker sandbox with support for:
- Python 3.11
- Node.js / JavaScript
- Bash / Shell commands
- File operations (read/write)
- Package management (pip, npm)
- Flexible resource profiles (basic, standard, ml, heavy)
"""

import docker
import json
import hashlib
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Union
import logging

from tools.resource_profiles import ResourceProfile, get_profile, PROFILES

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeExecutionTools:
    """
    Manages code execution in isolated Docker sandbox environment.
    
    Security features:
    - Non-root user execution
    - Resource limits (CPU, memory, timeout)
    - Network isolation
    - Read-only filesystem (except workspace)
    - Comprehensive logging
    """
    
    def __init__(
        self,
        workspace_path: str = "workspace/sandbox",
        image_name: str = "nexus-sandbox:latest",
        profile: Union[str, ResourceProfile] = "standard",  # Changed default to 'standard'
        timeout: Optional[int] = None,
        memory_limit: Optional[str] = None,
        cpu_quota: Optional[int] = None
    ):
        """
        Initialize code execution environment.
        
        Args:
            workspace_path: Path to workspace directory (mounted in container)
            image_name: Docker image to use for sandbox
            profile: Resource profile name ('basic', 'standard', 'ml', 'heavy') or ResourceProfile instance
            timeout: Override timeout (uses profile default if None)
            memory_limit: Override memory limit (uses profile default if None)
            cpu_quota: Override CPU quota (uses profile default if None)
        """
        self.workspace_path = Path(workspace_path).absolute()
        self.image_name = image_name
        
        # Load resource profile
        if isinstance(profile, str):
            self.profile = get_profile(profile)
        elif isinstance(profile, ResourceProfile):
            self.profile = profile
        else:
            raise ValueError(f"profile must be str or ResourceProfile, got {type(profile)}")
        
        # Allow overrides
        self.timeout = timeout or self.profile.timeout
        self.memory_limit = memory_limit or self.profile.memory_limit
        self.cpu_quota = cpu_quota or self.profile.cpu_quota
        
        logger.info(f"Initialized with profile: {self.profile.name} "
                   f"(RAM: {self.profile.memory_limit}, CPUs: {self.profile.cpu_count}, "
                   f"Timeout: {self.timeout}s, GPU: {self.profile.gpu_enabled})")
        
        # Ensure workspace exists
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        (self.workspace_path / "logs").mkdir(exist_ok=True)
        (self.workspace_path / "outputs").mkdir(exist_ok=True)
        (self.workspace_path / "temp").mkdir(exist_ok=True)
        
        # Initialize Docker client
        try:
            self.docker_client = docker.from_env()
            logger.info("Docker client initialized successfully")
            try:
                self.docker_client.images.get(self.image_name)
            except docker.errors.ImageNotFound:
                raise RuntimeError(
                    f"Docker image '{self.image_name}' not found. "
                    "Build it with: docker build -t nexus-sandbox:latest ./sandbox"
                )
        except Exception as e:
            logger.error(f"Failed to initialize Docker client or image: {e}")
            raise
    
    def _get_container_config(self) -> Dict:
        """Generate secure container configuration."""
        return {
            "image": self.image_name,
            "detach": True,
            "network_mode": "none",  # No network access
            "mem_limit": self.memory_limit,
            "cpu_quota": self.cpu_quota,
            "pids_limit": 100,  # Max 100 processes
            "security_opt": ["no-new-privileges"],
            "cap_drop": ["ALL"],  # Drop all capabilities
            "cap_add": ["CHOWN", "DAC_OVERRIDE"],  # Minimal required
            "read_only": True,  # Filesystem is read-only
            "tmpfs": {"/tmp": "rw,noexec,nosuid,size=100m"},
            "volumes": {
                str(self.workspace_path): {"bind": "/workspace", "mode": "rw"}
            },
            "working_dir": "/workspace",
            "user": "coderunner"  # Non-root user
        }
    
    def _execute_in_container(
        self,
        command: str,
        timeout: Optional[int] = None
    ) -> Dict[str, any]:
        """
        Execute command in Docker container.
        
        Args:
            command: Command to execute
            timeout: Execution timeout (uses default if None)
            
        Returns:
            Dict with stdout, stderr, exit_code, and execution metrics
        """
        timeout = timeout or self.timeout
        container = None
        start_time = time.time()
        
        try:
            # Create container
            config = self._get_container_config()
            config["command"] = ["bash", "-c", command]
            
            container = self.docker_client.containers.create(**config)
            logger.info(f"Container created: {container.id[:12]}")
            
            # Start container
            container.start()
            
            # Wait for completion with timeout
            try:
                result = container.wait(timeout=timeout)
                exit_code = result.get("StatusCode", -1)
            except Exception as e:
                logger.warning(f"Container timeout after {timeout}s")
                container.kill()
                exit_code = 124  # Timeout exit code
            
            # Get logs
            stdout = container.logs(stdout=True, stderr=False).decode('utf-8', errors='replace')
            stderr = container.logs(stdout=False, stderr=True).decode('utf-8', errors='replace')
            
            execution_time = time.time() - start_time
            
            # Get resource stats
            stats = container.stats(stream=False)
            memory_usage = stats['memory_stats'].get('usage', 0) / (1024 * 1024)  # MB
            
            result = {
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": exit_code,
                "execution_time_ms": int(execution_time * 1000),
                "memory_mb": round(memory_usage, 2),
                "timeout": exit_code == 124
            }
            
            # Log execution
            self._log_execution(command, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return {
                "stdout": "",
                "stderr": str(e),
                "exit_code": -1,
                "execution_time_ms": int((time.time() - start_time) * 1000),
                "memory_mb": 0,
                "timeout": False
            }
        finally:
            # Cleanup container
            if container:
                try:
                    container.remove(force=True)
                    logger.info(f"Container removed: {container.id[:12]}")
                except Exception as e:
                    logger.warning(f"Failed to remove container: {e}")
    
    def _log_execution(self, command: str, result: Dict):
        """Log execution details to file."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "command_hash": hashlib.sha256(command.encode()).hexdigest()[:16],
            "exit_code": result.get("exit_code"),
            "execution_time_ms": result.get("execution_time_ms"),
            "memory_mb": result.get("memory_mb"),
            "timeout": result.get("timeout"),
            "stdout_preview": result.get("stdout", "")[:200],
            "stderr_preview": result.get("stderr", "")[:200]
        }
        
        log_file = self.workspace_path / "logs" / f"execution_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def _execute_in_container_streaming(
        self,
        command: str,
        callback: callable = None,
        timeout: Optional[int] = None
    ) -> Dict[str, any]:
        """
        Execute command in Docker container with real-time streaming output.
        
        Args:
            command: Command to execute
            callback: Function called for each line of output: callback(line, stream_type)
                     where stream_type is 'stdout' or 'stderr'
            timeout: Execution timeout (uses default if None)
            
        Returns:
            Dict with stdout, stderr, exit_code, and execution metrics
        """
        import threading
        import queue
        
        timeout = timeout or self.timeout
        container = None
        start_time = time.time()
        stdout_lines = []
        stderr_lines = []
        output_queue = queue.Queue()
        
        try:
            # Create container
            config = self._get_container_config()
            config["command"] = ["bash", "-c", command]
            # Remove detach for streaming
            config["detach"] = False
            config["stdout"] = True
            config["stderr"] = True
            config["stream"] = True
            
            container = self.docker_client.containers.create(**config)
            logger.info(f"Streaming container created: {container.id[:12]}")
            
            # Start container and get streaming socket
            container.start()
            
            # Get streaming logs
            log_stream = container.attach(stream=True, logs=True, stdout=True, stderr=True, demux=True)
            
            # Thread to read output streams
            def read_streams():
                try:
                    for stdout_chunk, stderr_chunk in log_stream:
                        current_time = time.time() - start_time
                        
                        if stdout_chunk:
                            lines = stdout_chunk.decode('utf-8', errors='replace').splitlines()
                            for line in lines:
                                if line.strip():
                                    stdout_lines.append(line)
                                    if callback:
                                        callback(line, 'stdout', current_time)
                        
                        if stderr_chunk:
                            lines = stderr_chunk.decode('utf-8', errors='replace').splitlines()
                            for line in lines:
                                if line.strip():
                                    stderr_lines.append(line)
                                    if callback:
                                        callback(line, 'stderr', current_time)
                except Exception as e:
                    logger.warning(f"Stream reading error: {e}")
            
            # Start reading thread
            reader_thread = threading.Thread(target=read_streams, daemon=True)
            reader_thread.start()
            
            # Wait for completion with timeout
            try:
                result = container.wait(timeout=timeout)
                exit_code = result.get("StatusCode", -1)
            except Exception as e:
                logger.warning(f"Container timeout after {timeout}s")
                container.kill()
                exit_code = 124  # Timeout exit code
            
            # Wait for reader thread to finish (with timeout)
            reader_thread.join(timeout=2.0)
            
            execution_time = time.time() - start_time
            
            # Get resource stats
            try:
                stats = container.stats(stream=False)
                memory_usage = stats['memory_stats'].get('usage', 0) / (1024 * 1024)  # MB
            except:
                memory_usage = 0
            
            stdout_text = '\n'.join(stdout_lines)
            stderr_text = '\n'.join(stderr_lines)
            
            result = {
                "stdout": stdout_text,
                "stderr": stderr_text,
                "exit_code": exit_code,
                "execution_time_ms": int(execution_time * 1000),
                "memory_mb": round(memory_usage, 2),
                "timeout": exit_code == 124,
                "streamed": True  # Mark as streamed execution
            }
            
            # Notify completion via callback
            if callback:
                callback(None, 'complete', execution_time, exit_code)
            
            # Log execution
            self._log_execution(command, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Streaming execution error: {e}")
            error_result = {
                "stdout": '\n'.join(stdout_lines),
                "stderr": '\n'.join(stderr_lines) + f"\n{str(e)}",
                "exit_code": -1,
                "execution_time_ms": int((time.time() - start_time) * 1000),
                "memory_mb": 0,
                "timeout": False,
                "streamed": True
            }
            if callback:
                callback(None, 'error', time.time() - start_time, -1)
            return error_result
        finally:
            # Cleanup container
            if container:
                try:
                    container.remove(force=True)
                    logger.info(f"Streaming container removed: {container.id[:12]}")
                except Exception as e:
                    logger.warning(f"Failed to remove container: {e}")
    
    def execute_python(self, code: str, timeout: Optional[int] = None) -> Dict:
        """
        Execute Python 3.11 code in sandbox.
        
        Args:
            code: Python code to execute
            timeout: Execution timeout in seconds
            
        Returns:
            Dict with execution results
        """
        # Save code to temp file
        temp_file = self.workspace_path / "temp" / f"script_{int(time.time())}.py"
        temp_file.write_text(code, encoding='utf-8')
        
        command = f"python3 /workspace/temp/{temp_file.name}"
        result = self._execute_in_container(command, timeout)
        
        # Cleanup temp file
        try:
            temp_file.unlink()
        except:
            pass
        
        return result
    
    def execute_node(self, code: str, timeout: Optional[int] = None) -> Dict:
        """
        Execute JavaScript/Node.js code in sandbox.
        
        Args:
            code: JavaScript code to execute
            timeout: Execution timeout in seconds
            
        Returns:
            Dict with execution results
        """
        # Save code to temp file
        temp_file = self.workspace_path / "temp" / f"script_{int(time.time())}.js"
        temp_file.write_text(code, encoding='utf-8')
        
        command = f"node /workspace/temp/{temp_file.name}"
        result = self._execute_in_container(command, timeout)
        
        # Cleanup temp file
        try:
            temp_file.unlink()
        except:
            pass
        
        return result
    
    def execute_shell(self, command: str, timeout: Optional[int] = None) -> Dict:
        """
        Execute Bash shell command in sandbox.
        
        Args:
            command: Shell command to execute
            timeout: Execution timeout in seconds
            
        Returns:
            Dict with execution results
        """
        return self._execute_in_container(command, timeout)
    
    # ========== STREAMING METHODS (Real-time output) ==========
    
    def execute_python_streaming(
        self, 
        code: str, 
        callback: callable = None,
        timeout: Optional[int] = None
    ) -> Dict:
        """
        Execute Python code with real-time streaming output.
        
        Args:
            code: Python code to execute
            callback: Function called for each output line: callback(line, stream_type, elapsed_time)
            timeout: Execution timeout in seconds
            
        Returns:
            Dict with execution results
        """
        # Save code to temp file
        temp_file = self.workspace_path / "temp" / f"script_{int(time.time())}.py"
        temp_file.write_text(code, encoding='utf-8')
        
        command = f"python3 -u /workspace/temp/{temp_file.name}"  # -u for unbuffered output
        result = self._execute_in_container_streaming(command, callback, timeout)
        
        # Cleanup temp file
        try:
            temp_file.unlink()
        except:
            pass
        
        return result
    
    def execute_node_streaming(
        self,
        code: str,
        callback: callable = None,
        timeout: Optional[int] = None
    ) -> Dict:
        """
        Execute Node.js code with real-time streaming output.
        
        Args:
            code: JavaScript code to execute
            callback: Function called for each output line: callback(line, stream_type, elapsed_time)
            timeout: Execution timeout in seconds
            
        Returns:
            Dict with execution results
        """
        # Save code to temp file
        temp_file = self.workspace_path / "temp" / f"script_{int(time.time())}.js"
        temp_file.write_text(code, encoding='utf-8')
        
        command = f"node /workspace/temp/{temp_file.name}"
        result = self._execute_in_container_streaming(command, callback, timeout)
        
        # Cleanup temp file
        try:
            temp_file.unlink()
        except:
            pass
        
        return result
    
    def execute_shell_streaming(
        self,
        command: str,
        callback: callable = None,
        timeout: Optional[int] = None
    ) -> Dict:
        """
        Execute shell command with real-time streaming output.
        
        Args:
            command: Shell command to execute
            callback: Function called for each output line: callback(line, stream_type, elapsed_time)
            timeout: Execution timeout in seconds
            
        Returns:
            Dict with execution results
        """
        return self._execute_in_container_streaming(command, callback, timeout)
    
    def read_file(self, filepath: str) -> str:
        """
        Read file from workspace.
        
        Args:
            filepath: Relative path within workspace
            
        Returns:
            File contents as string
        """
        if not filepath:
            raise ValueError("Invalid filepath")
        normalized = filepath.replace("\\", "/").lstrip()
        if normalized.startswith("/workspace/"):
            normalized = normalized[len("/workspace/"):]
        if normalized.startswith("workspace/"):
            normalized = normalized[len("workspace/"):]
        if normalized in ("workspace", "/workspace"):
            normalized = ""
        if normalized in (".", "./"):
            normalized = ""
        full_path = (self.workspace_path / normalized).resolve()
        
        # Security check: ensure file is within workspace
        if not str(full_path.resolve()).startswith(str(self.workspace_path)):
            raise ValueError("Access denied: file outside workspace")
        
        try:
            if full_path.is_dir():
                return "\n".join(sorted(p.name for p in full_path.iterdir()))
            return full_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"Failed to read file {filepath}: {e}")
            raise
    
    def write_file(self, filepath: str, content: str):
        """
        Write file to workspace.
        
        Args:
            filepath: Relative path within workspace
            content: Content to write
        """
        if not filepath:
            raise ValueError("Invalid filepath")
        normalized = filepath.replace("\\", "/").lstrip()
        if normalized.startswith("/workspace/"):
            normalized = normalized[len("/workspace/"):]
        if normalized.startswith("workspace/"):
            normalized = normalized[len("workspace/"):]
        if normalized in ("workspace", "/workspace"):
            normalized = ""
        full_path = (self.workspace_path / normalized).resolve()
        
        # Security check: ensure file is within workspace
        if not str(full_path.resolve()).startswith(str(self.workspace_path)):
            raise ValueError("Access denied: file outside workspace")
        
        try:
            # Create parent directories if needed
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding='utf-8')
            logger.info(f"File written: {filepath}")
        except Exception as e:
            logger.error(f"Failed to write file {filepath}: {e}")
            raise
    
    def install_package(
        self,
        package: str,
        manager: str = "pip",
        timeout: Optional[int] = None
    ) -> Dict:
        """
        Install package in sandbox environment.
        
        Args:
            package: Package name to install
            manager: Package manager ("pip", "npm", or "apt")
            timeout: Installation timeout
            
        Returns:
            Dict with installation results
        """
        # Use workspace-scoped installs to avoid read-only filesystem issues
        pip_target = "/workspace/.pip"
        npm_prefix = "/workspace/.npm-global"

        commands = {
            "pip": (
                f"mkdir -p {pip_target} /workspace/.pip-cache && "
                f"PIP_DISABLE_PIP_VERSION_CHECK=1 "
                f"PIP_CACHE_DIR=/workspace/.pip-cache "
                f"pip3 install --no-cache-dir --target {pip_target} {package}"
            ),
            "npm": (
                f"mkdir -p {npm_prefix} && "
                f"npm install -g --prefix {npm_prefix} {package}"
            ),
            "apt": f"apt-get install -y {package}"  # Requires root, will fail
        }
        
        if manager not in commands:
            raise ValueError(f"Unsupported package manager: {manager}")
        
        command = commands[manager]
        return self._execute_in_container(command, timeout or 60)
    
    def cleanup_old_logs(self, days: int = 7):
        """
        Remove log files older than specified days.
        
        Args:
            days: Remove logs older than this many days
        """
        log_dir = self.workspace_path / "logs"
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        for log_file in log_dir.glob("execution_*.jsonl"):
            if log_file.stat().st_mtime < cutoff_time:
                log_file.unlink()
                logger.info(f"Removed old log: {log_file.name}")


# Agno tool wrappers
def python_executor(code: str, profile: str = "ml") -> str:
    """
    Execute Python code and return formatted result.
    
    Args:
        code: Python code to execute
        profile: Resource profile ('basic', 'standard', 'ml', 'heavy')
    """
    tools = CodeExecutionTools(profile=profile)
    result = tools.execute_python(code)
    
    output = f"[STDOUT]\n{result['stdout']}\n"
    if result['stderr']:
        output += f"\n[STDERR]\n{result['stderr']}\n"
    output += f"\n[EXIT_CODE] {result['exit_code']}"
    output += f"\n[DURATION] {result['execution_time_ms']}ms"
    output += f"\n[MEMORY] {result['memory_mb']}MB"
    output += f"\n[PROFILE] {profile}"
    
    return output


# Alias for compatibility with LLM hallucinations
def execute_python_code(code: str) -> str:
    """Alias for python_executor - used when LLM hallucinations call this name."""
    return python_executor(code, profile="standard")


def node_executor(code: str) -> str:
    """Execute Node.js code and return formatted result."""
    tools = CodeExecutionTools()
    result = tools.execute_node(code)
    
    output = f"[STDOUT]\n{result['stdout']}\n"
    if result['stderr']:
        output += f"\n[STDERR]\n{result['stderr']}\n"
    output += f"\n[EXIT_CODE] {result['exit_code']}"
    output += f"\n[DURATION] {result['execution_time_ms']}ms"
    
    return output


def shell_executor(command: str) -> str:
    """Execute shell command and return formatted result."""
    tools = CodeExecutionTools()
    result = tools.execute_shell(command)
    
    output = f"[STDOUT]\n{result['stdout']}\n"
    if result['stderr']:
        output += f"\n[STDERR]\n{result['stderr']}\n"
    output += f"\n[EXIT_CODE] {result['exit_code']}"
    output += f"\n[DURATION] {result['execution_time_ms']}ms"
    
    return output


def file_reader(filepath: str) -> str:
    """Read file from workspace."""
    tools = CodeExecutionTools()
    return tools.read_file(filepath)


def file_writer(filepath: str, content: str) -> str:
    """Write file to workspace."""
    tools = CodeExecutionTools()
    tools.write_file(filepath, content)
    return f"File written successfully: {filepath}"


def package_installer(package: str, manager: str = "pip") -> str:
    """Install package in sandbox."""
    tools = CodeExecutionTools()
    result = tools.install_package(package, manager)
    
    if result['exit_code'] == 0:
        return f"Package '{package}' installed successfully via {manager}"
    else:
        return f"Failed to install '{package}': {result['stderr']}"
