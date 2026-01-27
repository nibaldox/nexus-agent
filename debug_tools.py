"""Quick debug script to test CodeExecutionTools"""
import sys
sys.path.insert(0, '.')

from tools.code_execution_tools import CodeExecutionTools

# Initialize tools
tools = CodeExecutionTools(workspace_path="workspace/sandbox_debug")

print("=" * 60)
print("Testing Code Execution Tools")
print("=" * 60)

# Test 1: Simple Python
print("\n1. Testing Python execution...")
result = tools.execute_python("print('Hello from Python')")
print(f"  Exit Code: {result['exit_code']}")
print(f"  Stdout: {result['stdout']}")
print(f"  Stderr: {result['stderr']}")

# Test 2: Simple Node
print("\n2. Testing Node execution...")
result = tools.execute_node("console.log('Hello from Node');")
print(f"  Exit Code: {result['exit_code']}")
print(f"  Stdout: {result['stdout']}")
print(f"  Stderr: {result['stderr']}")

# Test 3: Shell
print("\n3. Testing Shell execution...")
result = tools.execute_shell("echo 'Hello from Shell'")
print(f"  Exit Code: {result['exit_code']}")
print(f"  Stdout: {result['stdout']}")
print(f"  Stderr: {result['stderr']}")

print("\n" + "=" * 60)
print("Debug complete!")
