from functools import lru_cache

from google import genai

from app.config.settings import settings


@lru_cache
def get_client() -> genai.Client:
    """
    One shared Gemini client for the whole process instead of one per call.
    """

    return genai.Client(api_key=settings.GEMINI_API_KEY)
