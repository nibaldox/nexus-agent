"""
Model Pricing Catalog for OpenRouter
Prices in $ per 1 million tokens
Updated: 2026-01-21
"""

from typing import Dict, Optional, Tuple

# OpenRouter Model Pricing ($ per 1M tokens)
MODEL_PRICING = {
    # Anthropic Models
    "anthropic/claude-3.5-sonnet": {
        "input": 3.00,
        "output": 15.00,
        "context": 200000
    },
    "anthropic/claude-3-opus": {
        "input": 15.00,
        "output": 75.00,
        "context": 200000
    },
    "anthropic/claude-3-sonnet": {
        "input": 3.00,
        "output": 15.00,
        "context": 200000
    },
    "anthropic/claude-3-haiku": {
        "input": 0.25,
        "output": 1.25,
        "context": 200000
    },
    
    # OpenAI Models
    "openai/gpt-4-turbo": {
        "input": 10.00,
        "output": 30.00,
        "context": 128000
    },
    "openai/gpt-4": {
        "input": 30.00,
        "output": 60.00,
        "context": 8192
    },
    "openai/gpt-3.5-turbo": {
        "input": 0.50,
        "output": 1.50,
        "context": 16385
    },
    
    # Mistral Models
    "mistralai/mixtral-8x7b-instruct": {
        "input": 0.24,
        "output": 0.24,
        "context": 32000
    },
    "mistralai/mistral-7b-instruct": {
        "input": 0.06,
        "output": 0.06,
        "context": 32000
    },
    
    # Google Models
    "google/gemini-pro": {
        "input": 0.50,
        "output": 1.50,
        "context": 32000
    },
    
    # Meta Models  
    "meta-llama/llama-3-70b-instruct": {
        "input": 0.59,
        "output": 0.79,
        "context": 8192
    },
    
    # Default fallback
    "default": {
        "input": 1.00,
        "output": 2.00,
        "context": 4096
    }
}


def get_model_pricing(model_name: str) -> Dict[str, float]:
    """
    Get pricing for a specific model.
    
    Args:
        model_name: Full model name (e.g., "anthropic/claude-3.5-sonnet")
        
    Returns:
        Dict with 'input' and 'output' prices per 1M tokens
    """
    # Try exact match first
    if model_name in MODEL_PRICING:
        return MODEL_PRICING[model_name]
    
    # Try partial match (e.g., "claude-3.5-sonnet" matches "anthropic/claude-3.5-sonnet")
    for key in MODEL_PRICING:
        if model_name.lower() in key.lower() or key.lower() in model_name.lower():
            return MODEL_PRICING[key]
    
    # Return default if no match
    print(f"Warning: Model '{model_name}' not found in pricing catalog, using default pricing")
    return MODEL_PRICING["default"]


def calculate_cost(
    model: str,
    prompt_tokens: int,
    completion_tokens: int
) -> Tuple[float, float, float]:
    """
    Calculate cost for a

 LLM API call.
    
    Args:
        model: Model name
        prompt_tokens: Number of input tokens
        completion_tokens: Number of output tokens
        
    Returns:
        Tuple of (input_cost, output_cost, total_cost) in USD
    """
    pricing = get_model_pricing(model)
    
    # Convert from "per 1M tokens" to actual cost
    input_cost = (prompt_tokens / 1_000_000) * pricing["input"]
    output_cost = (completion_tokens / 1_000_000) * pricing["output"]
    total_cost = input_cost + output_cost
    
    return round(input_cost, 6), round(output_cost, 6), round(total_cost, 6)


def get_pricing_info(model: str) -> str:
    """
    Get human-readable pricing information for a model.
    
    Args:
        model: Model name
        
    Returns:
        Formatted string with pricing info
    """
    pricing = get_model_pricing(model)
    return f"${pricing['input']:.2f} / ${pricing['output']:.2f} per 1M tokens"


def list_available_models() -> list:
    """
    Get list of all models with pricing information.
    
    Returns:
        List of model names (excluding 'default')
    """
    return [model for model in MODEL_PRICING.keys() if model != "default"]


def estimate_cost_for_tokens(model: str, total_tokens: int, output_ratio: float = 0.3) -> float:
    """
    Estimate cost given total tokens with assumed input/output ratio.
    
    Args:
        model: Model name
        total_tokens: Total tokens in conversation
        output_ratio: Ratio of output to total tokens (default 0.3 = 30% output)
        
    Returns:
        Estimated total cost in USD
    """
    output_tokens = int(total_tokens * output_ratio)
    input_tokens = total_tokens - output_tokens
    
    _, _, total_cost = calculate_cost(model, input_tokens, output_tokens)
    return total_cost
