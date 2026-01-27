from agno.models.openai.like import OpenAILike
import os
from dotenv import load_dotenv

load_dotenv()

def get_minimax_model(model_id: str = "MiniMax-M2.1", max_tokens: int = 4096, temperature: float = 0.7) -> OpenAILike:
    """
    Retorna una instancia de modelo conectada directamente a la API de Minimax.
    """
    api_key = os.getenv("MINIMAX_API_KEY")
    return OpenAILike(
        id=model_id,
        api_key=api_key or "sk-placeholder",
        base_url="https://api.minimax.io/v1",
        max_tokens=max_tokens,
        temperature=temperature
    )

def get_openrouter_model(model_id: str = "nvidia/nemotron-3-nano-30b-a3b:free", max_tokens: int = 4096, temperature: float = 0.7) -> OpenAILike:
    """
    Retorna una instancia de modelo conectada a OpenRouter.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("WARNING: OPENROUTER_API_KEY no encontrada.")
        
    return OpenAILike(
        id=model_id,
        api_key=api_key or "sk-placeholder",
        base_url="https://openrouter.ai/api/v1",
        max_tokens=max_tokens,
        temperature=temperature
    )
