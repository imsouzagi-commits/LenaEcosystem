from __future__ import annotations


class ConversationalDisplacementDetector:

    REDIRECT_MARKERS = {
        "muda de assunto",
        "vamos falar de outra coisa",
        "vamos falar de música",
        "vamos falar de filme",
        "qual teu filme favorito",
        "fala de outra coisa",
        "troca de assunto",
        "me distrai",
        "quero mudar de assunto",
        "vamos falar de qualquer outra coisa",
    }

    @classmethod
    def detect(
        cls,
        text: str,
    ) -> bool:

        lowered = text.lower().strip()

        for marker in cls.REDIRECT_MARKERS:

            if marker in lowered:
                return True

        return False
