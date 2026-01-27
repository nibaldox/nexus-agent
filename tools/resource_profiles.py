"""
Resource Profiles for Code Execution Sandbox
Defines resource allocation based on workload type and available hardware
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ResourceProfile:
    """Resource allocation profile for Docker containers."""
    name: str
    memory_limit: str
    cpu_quota: int  # 100000 = 1 CPU
    timeout: int  # seconds
    gpu_enabled: bool = False
    description: str = ""
    
    @property
    def cpu_count(self) -> float:
        """Get CPU count from quota."""
        return self.cpu_quota / 100000
    
    @property
    def memory_mb(self) -> int:
        """Get memory in MB."""
        if self.memory_limit.endswith('g'):
            return int(float(self.memory_limit[:-1]) * 1024)
        elif self.memory_limit.endswith('m'):
            return int(self.memory_limit[:-1])
        return 512  # default


# Pre-defined resource profiles based on workload type
PROFILES = {
    "basic": ResourceProfile(
        name="basic",
        memory_limit="512m",
        cpu_quota=100000,  # 1 CPU
        timeout=30,
        description="Minimal resources for simple scripts"
    ),
    
    "standard": ResourceProfile(
        name="standard",
        memory_limit="2g",
        cpu_quota=400000,  # 4 CPUs
        timeout=60,
        description="Standard resources for general development"
    ),
    
    "ml": ResourceProfile(
        name="ml",
        memory_limit="8g",
        cpu_quota=800000,  # 8 CPUs
        timeout=300,  # 5 minutes
        gpu_enabled=True,
        description="Machine Learning workloads with GPU access"
    ),
    
    "heavy": ResourceProfile(
        name="heavy",
        memory_limit="16g",
        cpu_quota=1200000,  # 12 CPUs
        timeout=600,  # 10 minutes
        gpu_enabled=True,
        description="Heavy computational workloads (large datasets, complex ML)"
    ),
}


def get_profile(name: str = "standard") -> ResourceProfile:
    """
    Get resource profile by name.
    
    Args:
        name: Profile name (basic, standard, ml, heavy)
        
    Returns:
        ResourceProfile instance
    """
    if name not in PROFILES:
        raise ValueError(f"Unknown profile: {name}. Available: {list(PROFILES.keys())}")
    return PROFILES[name]


def create_custom_profile(
    memory_limit: str,
    cpu_count: int,
    timeout: int = 60,
    gpu_enabled: bool = False,
    name: str = "custom"
) -> ResourceProfile:
    """
    Create custom resource profile.
    
    Args:
        memory_limit: Memory limit (e.g., "2g", "512m")
        cpu_count: Number of CPUs to allocate
        timeout: Execution timeout in seconds
        gpu_enabled: Whether to enable GPU access
        name: Profile name
        
    Returns:
        ResourceProfile instance
    """
    return ResourceProfile(
        name=name,
        memory_limit=memory_limit,
        cpu_quota=cpu_count * 100000,
        timeout=timeout,
        gpu_enabled=gpu_enabled,
        description=f"Custom profile: {memory_limit} RAM, {cpu_count} CPUs"
    )


# Auto-detect optimal profile based on system resources
def detect_optimal_profile() -> ResourceProfile:
    """
    Auto-detect optimal resource profile based on available system resources.
    
    Returns:
        Recommended ResourceProfile
    """
    try:
        import psutil
        
        total_ram_gb = psutil.virtual_memory().total / (1024**3)
        cpu_count = psutil.cpu_count(logical=True)
        
        # Allocate based on available resources
        if total_ram_gb >= 32 and cpu_count >= 12:
            return PROFILES["ml"]  # Use ML profile for powerful systems
        elif total_ram_gb >= 16 and cpu_count >= 8:
            return PROFILES["standard"]
        else:
            return PROFILES["basic"]
            
    except ImportError:
        # Fallback if psutil not available
        return PROFILES["standard"]


# Hardware detection summary
def get_hardware_summary() -> dict:
    """
    Get summary of available hardware resources.
    
    Returns:
        Dict with hardware info
    """
    try:
        import psutil
        
        return {
            "total_ram_gb": round(psutil.virtual_memory().total / (1024**3), 1),
            "available_ram_gb": round(psutil.virtual_memory().available / (1024**3), 1),
            "cpu_count": psutil.cpu_count(logical=True),
            "cpu_physical": psutil.cpu_count(logical=False),
        }
    except ImportError:
        return {"error": "psutil not installed"}
