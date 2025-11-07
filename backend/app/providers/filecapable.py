from __future__ import annotations

import os
from typing import Any, List

from ..core.config import settings


class ProviderNotFileCapable(Exception):
    pass


class FileCapableLLM:
    def upload(self, path: str) -> str:  # returns provider-specific file token/id
        raise NotImplementedError

    def generate(self, prompt: str, files: List[str] | None = None, **params: Any) -> str:
        raise NotImplementedError


class GeminiFileCapable(FileCapableLLM):
    """Gemini provider using google-generativeai file API.

    Requires GEMINI_API_KEY and a model that supports file inputs (e.g., 'gemini-1.5-pro' or similar).
    """

    def __init__(self, model: str = "models/gemini-1.5-pro") -> None:
        # For now, we deliberately report not file capable due to dependency constraints.
        # When google-generativeai is available, implement upload/generate via Files API.
        self.model = model

    def upload(self, path: str) -> str:
        # Upload file; returns file uri
        raise ProviderNotFileCapable("Gemini file upload not available in current build")

    def generate(self, prompt: str, files: List[str] | None = None, **params: Any) -> str:
        raise ProviderNotFileCapable("Gemini model not invoked due to missing file capability")
