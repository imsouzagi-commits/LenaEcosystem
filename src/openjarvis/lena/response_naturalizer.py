from __future__ import annotations

from openjarvis.engine.ollama_engine import OllamaEngine


class LenaResponseNaturalizer:
    def __init__(self) -> None:
        self.ollama = OllamaEngine()

    def available(self) -> bool:
        return self.ollama.available

    def should_naturalize(self, text: str) -> bool:
        lowered = text.lower().strip()

        if len(lowered.split()) <= 8:
            return True

        robotic_markers = (
            "wikipédia",
            "enciclopédia livre",
            "foi fundada",
            "foi fundado",
            "pesquisei silenciosamente",
        )

        return any(marker in lowered for marker in robotic_markers)

    def naturalize(self, question: str, raw_answer: str) -> str:
        if not self.should_naturalize(raw_answer):
            return raw_answer

        cleaned = raw_answer.strip()

        if cleaned.endswith(".") and len(cleaned.split()) <= 12:
            return cleaned

        lowered = cleaned.lower()

        if "foi fundado por" in lowered or "foi fundada por" in lowered:
            return cleaned

        if "wikipédia" in lowered or "enciclopédia livre" in lowered:
            cleaned = cleaned.replace("Wikipédia, a enciclopédia livre.", "").strip(" -.")

        if len(cleaned.split()) <= 18:
            return cleaned

        if not self.available():
            return cleaned

        prompt = (
            "Reescreva a resposta abaixo em português brasileiro natural, objetiva e curta. "
            "No máximo 1 frase. Sem inventar fatos.\n\n"
            f"Pergunta: {question}\n"
            f"Base: {cleaned}\n\n"
            "Resposta:"
        )

        try:
            return self.ollama.complete(
                prompt,
                reflective=False,
                max_tokens=32,
            ).strip()
        except Exception:
            return cleaned
