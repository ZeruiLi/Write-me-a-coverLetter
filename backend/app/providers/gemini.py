from ..core.config import settings
from .base import LLMProvider


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str | None = None, model: str = "gemini-2.5-flash") -> None:
        self.api_key = api_key or settings.gemini_api_key
        self.model = model

    def generate(self, prompt: str, *, temperature: float = 0.6, top_p: float = 1.0, seed: int = 0) -> str:
        if not self.api_key:
            # Fallback: raise to indicate missing key; higher layer may choose heuristic path
            raise RuntimeError("GEMINI_API_KEY not set")
        try:
            # Use langchain google genai wrapper
            from langchain_google_genai import ChatGoogleGenerativeAI
            llm = ChatGoogleGenerativeAI(google_api_key=self.api_key, model=self.model, temperature=temperature, top_p=top_p)
            resp = llm.invoke(prompt)
            # resp can be a AIMessage; access content
            text = getattr(resp, "content", None) or str(resp)
            return text.strip()
        except Exception as e:
            raise RuntimeError(f"Gemini provider error: {e}")

