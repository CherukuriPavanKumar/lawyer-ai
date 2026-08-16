from app.config import settings
from typing import List, Dict, Optional

async def generate_completion(messages: List[Dict[str, str]], model: str = "llama-3.3-70b-versatile", response_format: Optional[dict] = None) -> str:
    """
    Abstracted LLM provider interface.
    """
    if settings.llm_provider == "groq":
        from groq import AsyncGroq
        client = AsyncGroq(api_key=settings.groq_api_key)
        kwargs = {
            "messages": messages,
            "model": model,
        }
        if response_format:
            kwargs["response_format"] = response_format
            
        response = await client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    else:
        raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
