"""
Integration utilities for cost tracking in agents
Provides decorators and helper functions to automatically track LLM costs
"""

import time
from functools import wraps
from typing import Any, Callable, Dict
import inspect

from .logger import get_logger


def track_agent_cost(agent_name: str = None):
    """
    Decorator to automatically track costs for agent LLM calls.
    
    Usage:
        @track_agent_cost("Researcher")
        def my_agent_function(prompt, model="claude-3.5-sonnet"):
            response = llm.complete(prompt)
            return response
    
    Args:
        agent_name: Name of agent (auto-detected if not provided)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Auto-detect agent name from function or class
            nonlocal agent_name
            if agent_name is None:
               # Try to get from function name
                agent_name = func.__name__.replace('_', ' ').title()
            
            start_time = time.time()
            
            # Call original function
            result = func(*args, **kwargs)
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Extract usage from result if available
            if hasattr(result, 'usage'):
                usage = result.usage
            elif isinstance(result, dict) and 'usage' in result:
                usage = result['usage']
            else:
                # Can't track without usage data
                return result
            
            # Extract model from kwargs or result
            model = kwargs.get('model', 'unknown')
            if isinstance(result, dict) and 'model' in result:
                model = result['model']
            
            # Get session ID if available
            session_id = kwargs.get('session_id')
            
            # Log the cost
            logger = get_logger()
            logger.log_request(
                agent_name=agent_name,
                model=model,
                usage=usage,
                session_id=session_id,
                duration_ms=duration_ms,
                purpose=f"{agent_name} execution"
            )
            
            return result
        
        return wrapper
    return decorator


def log_phidata_agent_cost(
    agent_name: str,
    response: Any,
    session_id: str = None
):
    """
    Manually log cost for a Phidata agent response.
    
    This is a helper for manual integration when decorators can't be used.
    
    Usage:
        response = agent.run(prompt)
        log_phidata_agent_cost("Researcher", response, session_id="abc123")
    
    Args:
        agent_name: Name of the agent
        response: Response object from agent.run()
        session_id: Optional session identifier
    """
    logger = get_logger()
    
    # Extract metrics from response
    if hasattr(response, 'metrics'):
        metrics = response.metrics
        
        # Extract usage
        usage = {
            'prompt_tokens': metrics.get('input_tokens', 0),
            'completion_tokens': metrics.get('output_tokens', 0),
            'total_tokens': metrics.get('total_tokens', 0)
        }
        
        # Extract model
        model = metrics.get('model', 'unknown')
        
        # Extract duration
        duration_ms = metrics.get('time_to_first_token', 0) * 1000 if 'time_to_first_token' in metrics else None
        
        # Log
        cost_info = logger.log_request(
            agent_name=agent_name,
            model=model,
            usage=usage,
            session_id=session_id,
            duration_ms=duration_ms,
            purpose=f"{agent_name} phidata execution"
        )
        
        return cost_info
    
    return None


def create_cost_wrapper_for_agent(agent: Any, agent_name: str):
    """
    Wrap an agent's run/complete method to automatically track costs.
    
    Usage:
        from phidata import Agent
        researcher = Agent(...)
        create_cost_wrapper_for_agent(researcher, "Researcher")
        
        # Now all calls to researcher.run() will be tracked
        researcher.run("What is AI?")
    
    Args:
        agent: Agent instance to wrap
        agent_name: Name for cost tracking
    """
    original_run = agent.run
    
    def wrapped_run(*args, **kwargs):
        # Get session ID from kwargs if provided
        session_id = kwargs.get('session_id')
        
        # Call original
        response = original_run(*args, **kwargs)
        
        # Log cost
        log_phidata_agent_cost(agent_name, response, session_id)
        
        return response
    
    # Replace method
    agent.run = wrapped_run
    
    return agent
