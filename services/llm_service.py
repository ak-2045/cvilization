import os
import logging
from typing import Optional

logger = logging.getLogger("cvilization.llm_service")

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("langchain-google-genai package not installed.")

def get_llm(provider: str, api_key: str, model_name: Optional[str] = None):
    provider = provider.lower()
    
    if provider == "gemini":
        if not GEMINI_AVAILABLE:
            raise ImportError("langchain-google-genai is required but not installed.")
        key = api_key.strip() if api_key else os.environ.get("GEMINI_API_KEY", os.environ.get("GOOGLE_API_KEY", ""))
        if not key:
            raise ValueError("Gemini API Key is missing. Please configure it in the Configure AI settings at the top or .env file.")
        model = model_name if model_name else "gemini-1.5-flash"
        return ChatGoogleGenerativeAI(
            google_api_key=key,
            model=model,
            temperature=0.2
        )
    else:
        raise ValueError(f"Unsupported AI provider: {provider}")
