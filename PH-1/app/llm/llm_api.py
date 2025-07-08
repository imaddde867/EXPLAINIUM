"""
LLM integration utilities for EXPLAINIUM Phase 2
Supports both OpenAI API and local Ollama models.
"""
import requests
import os

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Example: Query Ollama local LLM (e.g., llama3, mistral, etc.)
def ask_llm(prompt: str, model: str = "qwen2.5:3b") -> str:
    """
    Query a local Ollama model for completion.
    Args:
        prompt: User prompt string
        model: Ollama model name (default: llama3)
    Returns:
        Model response as string
    """
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")
    except Exception as e:
        return f"[LLM Error: {e}]"

# Optionally, keep OpenAI API for cloud fallback
# def ask_llm_openai(prompt: str, model: str = "gpt-3.5-turbo") -> str:
#     ...
