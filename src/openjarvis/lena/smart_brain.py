from __future__ import annotations

from openjarvis.engine.azure_openai_engine import AzureOpenAIEngine
from openjarvis.engine.ollama_engine import OllamaEngine


class LenaSmartBrain:
    def __init__(self) -> None:
        self.azure_engine = AzureOpenAIEngine()
        self.ollama_engine = OllamaEngine()

    def available(self) -> bool:
        return self.ollama_engine.available or self.azure_engine.available

    def should_delegate(self, user_text: str) -> bool:
        lowered = user_text.lower().strip()

        blocked_prefixes = (
            "abre ",
            "abrir ",
            "fecha ",
            "fechar ",
            "cria arquivo ",
            "criar arquivo ",
            "lê arquivo ",
            "le arquivo ",
            "pesquisa no google ",
            "http://",
            "https://",
            "/lena ",
        )

        return not lowered.startswith(blocked_prefixes)