"""
Centralized provider for the LLM client.
This ensures the client is initialized only once and can be easily swapped.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

_client = None

def get_llm_client() -> OpenAI:
    """
    Returns a singleton instance of the OpenAI client.
    Initializes the client on the first call.
    """
    global _client
    if _client is None:
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")
        _client = OpenAI(api_key=api_key)
    return _client 