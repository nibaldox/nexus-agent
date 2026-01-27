"""
Simple helper for manual cost logging in API endpoints
Use this to log costs after agent execution
"""

from costs.logger import log_llm_request


def log_agent_execution(
    agent_name: str,
    response,
    session_id: str = None
):
    """
    Log cost for an agent execution.
    
    Works with Agno/Phidata agent responses that have metrics.
    
    Usage in api.py:
        from costs.helpers import log_agent_execution
        
        response = manager.print_response(message, stream=False)
        log_agent_execution("Manager", response, session_id)
    
    Args:
        agent_name: Name of the agent
        response: Agent response with metrics
        session_id: Optional session ID
    """
    try:
        #Check if response has metrics (Agno format)
        if hasattr(response, 'metrics'):
            metrics = response.metrics
            
            # Extract usage data
            usage = {
                'prompt_tokens': metrics.get('input_tokens', 0),
                'completion_tokens': metrics.get('output_tokens', 0),
                'total_tokens': metrics.get('total_tokens', 0)
            }
            
            # Extract model
            model = metrics.get('model', 'unknown')
            
            # Extract duration if available
            duration_ms = None
            if 'time' in metrics:
                duration_ms = int(metrics['time'] * 1000)
            
            # Log to database
            cost_info = log_llm_request(
                agent_name=agent_name,
                model=model,
                usage=usage,
                session_id=session_id,
                duration_ms=duration_ms,
                purpose=f"{agent_name} execution"
            )
            
            return cost_info
        
        return None
        
    except Exception as e:
        print(f"Warning: Could not log cost for {agent_name}: {e}")
        return None
