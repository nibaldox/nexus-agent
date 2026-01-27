"""
Cost Logger - Main interface for tracking LLM costs
"""

import time
from typing import Optional, Dict, Any
from datetime import datetime

from .pricing import calculate_cost
from .database import insert_request


class CostLogger:
    """
    Centralized logger for LLM API costs.
    
    Usage:
        logger = CostLogger()
        logger.log_request(
            agent_name="Researcher",
            model="anthropic/claude-3.5-sonnet",
            usage={"prompt_tokens": 150, "completion_tokens": 200},
            session_id="abc123"
        )
    """
    
    def __init__(self):
        """Initialize cost logger"""
        self.session_totals = {}  # Track totals per session
    
    def log_request(
        self,
        agent_name: str,
        model: str,
        usage: Dict[str, int],
        session_id: Optional[str] = None,
        duration_ms: Optional[int] = None,
        purpose: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Log an LLM API request with cost calculation.
        
        Args:
            agent_name: Name of the agent making the request
            model: Model identifier (e.g., "anthropic/claude-3.5-sonnet")
            usage: Dict with 'prompt_tokens' and 'completion_tokens'
            session_id: Optional session identifier
            duration_ms: Optional request duration in milliseconds
            purpose: Optional description of request purpose
            metadata: Optional additional data to store
            
        Returns:
            Dict with cost information and record ID
        """
        # Extract tokens
        prompt_tokens = usage.get('prompt_tokens', 0)
        completion_tokens = usage.get('completion_tokens', 0)
        total_tokens = usage.get('total_tokens', prompt_tokens + completion_tokens)
        
        # Calculate costs
        input_cost, output_cost, total_cost = calculate_cost(
            model, prompt_tokens, completion_tokens
        )
        
        # Insert to database
        record_id = insert_request(
            agent_name=agent_name,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=total_cost,
            session_id=session_id,
            duration_ms=duration_ms,
            purpose=purpose,
            metadata=metadata
        )
        
        # Update session totals
        if session_id:
            if session_id not in self.session_totals:
                self.session_totals[session_id] = {
                    'total_cost': 0.0,
                    'total_tokens': 0,
                    'request_count': 0
                }
            
            self.session_totals[session_id]['total_cost'] += total_cost
            self.session_totals[session_id]['total_tokens'] += total_tokens
            self.session_totals[session_id]['request_count'] += 1
        
        # Log to console
        print(f"💰 Cost: ${total_cost:.4f} | Agent: {agent_name} | Tokens: {total_tokens:,}")
        
        return {
            'record_id': record_id,
            'input_cost': input_cost,
            'output_cost': output_cost,
            'total_cost': total_cost,
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'total_tokens': total_tokens
        }
    
    def get_session_total(self, session_id: str) -> Dict[str, Any]:
        """
        Get cumulative costs for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dict with session cost totals
        """
        return self.session_totals.get(session_id, {
            'total_cost': 0.0,
            'total_tokens': 0,
            'request_count': 0
        })
    
    def reset_session(self, session_id: str):
        """Clear session totals for a given session"""
        if session_id in self.session_totals:
            del self.session_totals[session_id]


# Global logger instance
_global_logger = None


def get_logger() -> CostLogger:
    """Get or create global cost logger instance"""
    global _global_logger
    if _global_logger is None:
        _global_logger = CostLogger()
    return _global_logger


def log_llm_request(
    agent_name: str,
    model: str,
    usage: Dict[str, int],
    **kwargs
) ->Dict[str, Any]:
    """
    Convenience function to log request using global logger.
    
    Args:
        agent_name: Agent making request
        model: LLM model used
        usage: Token usage dict
        **kwargs: Additional arguments passed to logger
        
    Returns:
        Cost information dict
    """
    logger = get_logger()
    return logger.log_request(agent_name, model, usage, **kwargs)
