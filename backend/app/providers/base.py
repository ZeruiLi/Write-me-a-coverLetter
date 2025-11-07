from typing import Protocol


class LLMProvider(Protocol):
    def generate(self, prompt: str, *, temperature: float = 0.6, top_p: float = 1.0, seed: int = 0) -> str:
        ...

