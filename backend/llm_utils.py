import os
import logging
from typing import Tuple, Optional, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

logger = logging.getLogger(__name__)

def get_llm() -> Tuple[Any, str]:
    """
    Lazy initialization of LLM following the fallback chain:
    Gemini 1.5 Flash -> GPT-4o-mini -> Ollama llama3.2
    
    Returns:
        tuple: (llm_instance, provider_name)
    """
    # 1. Try Gemini
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash", 
                temperature=0.1, 
                google_api_key=gemini_key
            )
            # Smoke test
            return llm, "gemini"
        except Exception as e:
            logger.warning(f"Gemini initialization failed: {e}")

    # 2. Try OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            llm = ChatOpenAI(
                model="gpt-4o-mini", 
                temperature=0.1, 
                api_key=openai_key
            )
            return llm, "openai"
        except Exception as e:
            logger.warning(f"OpenAI initialization failed: {e}")

    # 3. Always fallback to Ollama
    try:
        llm = ChatOllama(model="llama3.2", temperature=0.1)
        return llm, "ollama"
    except Exception as e:
        logger.error(f"Ollama fallback failed: {e}")
        # Last resort fallback if even Ollama is not running
        raise RuntimeError("No LLM provider available (Gemini, OpenAI, or Ollama)")
