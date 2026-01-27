"""Test resource profiles with different workloads"""
import sys
sys.path.insert(0, '.')

from tools.code_execution_tools import CodeExecutionTools
from tools.resource_profiles import PROFILES, get_hardware_summary

print("=" * 70)
print("RESOURCE PROFILES TEST")
print("=" * 70)

# Show hardware
print("\n📊 Hardware Summary:")
hw = get_hardware_summary()
for key, value in hw.items():
    print(f"  {key}: {value}")

# Test each profile
profiles_to_test = ["basic", "standard", "ml"]

for profile_name in profiles_to_test:
    prof = PROFILES[profile_name]
    print(f"\n{'=' * 70}")
    print(f"Testing Profile: {profile_name.upper()}")
    print(f"  RAM: {prof.memory_limit}, CPUs: {prof.cpu_count}, Timeout: {prof.timeout}s")
    print("=" * 70)
    
    tools = CodeExecutionTools(profile=profile_name)
    
    if profile_name == "basic":
        # Simple test
        code = """
import sys
print(f"Python {sys.version}")
print("Basic profile test passed!")
"""
    elif profile_name == "standard":
        # Moderate test with pandas
        code = """
import numpy as np
import pandas as pd

# Create moderate dataset
data = np.random.randn(10000, 10)
df = pd.DataFrame(data)

print(f"DataFrame shape: {df.shape}")
print(f"Memory usage: {df.memory_usage().sum() / 1024**2:.2f} MB")
print("Standard profile test passed!")
"""
    else:  # ml
        # ML-like test
        code = """
import numpy as np
import time

# Simulate ML workload
print("Simulating ML workload...")
start = time.time()

# Large matrix operations (simulates training)
X = np.random.randn(5000, 1000)
y = np.random.randn(5000)

# Matrix multiplication (CPU intensive)
for i in range(5):
    result = X.T @ X
    print(f'  Iteration {i+1}/5 completed')

duration = time.time() - start
print(f'Completed in {duration:.2f}s')
print(f'Matrix size: {result.shape}, Memory: ~{result.nbytes / 1024**2:.1f} MB')
print('ML profile test passed!')
"""
    
    result = tools.execute_python(code)
    
    print(f"\n📝 Results:")
    print(f"  Exit Code: {result['exit_code']}")
    print(f"  Duration: {result['execution_time_ms']}ms")
    print(f"  Memory Used: {result['memory_mb']:.1f} MB")
    
    if result['exit_code'] == 0:
        print(f"  ✅ SUCCESS")
        print(f"\n  Output:")
        for line in result['stdout'].strip().split('\n'):
            print(f"    {line}")
    else:
        print(f"  ❌ FAILED")
        print(f"  Error: {result['stderr'][:500]}")

print("\n" + "=" * 70)
print("All profile tests completed!")
print("=" * 70)
